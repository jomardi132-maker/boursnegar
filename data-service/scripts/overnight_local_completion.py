#!/usr/bin/env python3
"""Run archive recovery and checkpointed Local completion unattended."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PYTHON=sys.executable

def stream(command, log):
    with log.open('a',encoding='utf-8') as handle:
        marker=json.dumps({'started':datetime.now(timezone.utc).isoformat(),'command':command},ensure_ascii=False)
        print(marker,flush=True); handle.write(marker+'\n'); handle.flush()
        process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                 text=True,encoding='utf-8',errors='replace')
        assert process.stdout is not None
        for line in process.stdout:
            print(line.rstrip(),flush=True); handle.write(line); handle.flush()
        code=process.wait()
        marker=json.dumps({'finished':datetime.now(timezone.utc).isoformat(),'exit_code':code},ensure_ascii=False)
        print(marker,flush=True); handle.write(marker+'\n')
        if code: raise SystemExit(code)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',default='data-service/artifacts/local-ingestion.sqlite3')
    parser.add_argument('--archive',default='/home/king/Boursnegar-artifacts-archive-20260906')
    parser.add_argument('--ssh-target',default='boursnegar')
    parser.add_argument('--from-jalali',default='1404/01/01')
    parser.add_argument('--to-jalali',required=True)
    parser.add_argument('--batch-size',type=int,default=10)
    parser.add_argument('--max-batches',type=int,default=100)
    parser.add_argument('--max-no-progress',type=int,default=10)
    args=parser.parse_args()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_root=ROOT/'data-service/artifacts/overnight'/stamp
    run_root.mkdir(parents=True,exist_ok=True)
    log=run_root/'overnight.log'
    status=run_root/'status.json'
    status.write_text(json.dumps({'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),
                                  'log':str(log)},ensure_ascii=False,indent=2),encoding='utf-8')
    try:
        stream([PYTHON,str(ROOT/'data-service/scripts/recover_local_archive.py'),
                '--db',str(Path(args.db).resolve()),'--archive',args.archive,'--apply'],log)
        stream([PYTHON,str(ROOT/'data-service/scripts/continuous_local_completion.py'),
                '--db',str(Path(args.db).resolve()),'--ssh-target',args.ssh_target,
                '--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,
                '--batch-size',str(args.batch_size),'--max-batches',str(args.max_batches),
                '--max-no-progress',str(args.max_no_progress),
                '--run-root',str(ROOT/'data-service/artifacts/auto-sync'),'--skip-production'],log)
        final={'status':'PASSED','finished_at':datetime.now(timezone.utc).isoformat(),'log':str(log)}
    except BaseException as exc:
        final={'status':'FAILED','finished_at':datetime.now(timezone.utc).isoformat(),
               'error':str(exc),'log':str(log)}
        status.write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
        raise
    status.write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(final,ensure_ascii=False))

if __name__=='__main__': main()
