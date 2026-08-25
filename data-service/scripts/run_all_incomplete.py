#!/usr/bin/env python3
"""Autonomous all-symbol supervisor; emits progress only at batch boundaries."""
from __future__ import annotations
import argparse, json, os, shutil, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PY=ROOT/'data-service/venv/bin/python'
sys.path.insert(0, str(ROOT/'data-service'))
def symbols(target):
    from scripts.ingestion_console import discover_remote
    rows=discover_remote(target,lambda _:None); seen=[]
    for row in rows:
        if row['status']!='complete' and row['symbol'] not in seen: seen.append(row['symbol'])
    return seen
def run(cmd,log,timeout):
    with log.open('a',encoding='utf-8') as out:
        p=subprocess.Popen(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':'data-service'},stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        try: return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM); time.sleep(3)
            try: os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            return 124
def main():
    p=argparse.ArgumentParser(); p.add_argument('--ssh-target',default='boursnegar'); p.add_argument('--from-jalali',default='1404/01/01'); p.add_argument('--to-jalali',required=True); p.add_argument('--out',default='artifacts/all-symbols'); p.add_argument('--batch-size',type=int,default=20); p.add_argument('--codalpy-timeout',type=int,default=300); p.add_argument('--max-batches',type=int,default=0); p.add_argument('--max-consecutive-failures',type=int,default=10); p.add_argument('--failure-cooldown',type=int,default=60); args=p.parse_args()
    root=ROOT/args.out; root.mkdir(parents=True,exist_ok=True)
    existing=[int(p.name.split('-')[1]) for p in root.glob('batch-*') if p.name.split('-')[-1].isdigit()]
    batch_no=max(existing,default=0); consecutive_failures=0
    no_notices_path=root/'no-notices.json'
    no_notices=set(json.loads(no_notices_path.read_text()) if no_notices_path.exists() else [])
    insufficient_path=root/'insufficient-standard-facts.json'
    insufficient=json.loads(insufficient_path.read_text()) if insufficient_path.exists() else {}
    stable_path=root/'stable-standard-facts.json'
    stable=json.loads(stable_path.read_text()) if stable_path.exists() else {}
    while True:
        pending=[s for s in symbols(args.ssh_target)
                 if s not in no_notices
                 and insufficient.get(s,{}).get('attempts',0) < 2
                 and stable.get(s,{}).get('attempts',0) < 2]
        if not pending: print('{"status":"complete","pending":0}',flush=True); return
        if args.max_batches and batch_no>=args.max_batches: print(f'{{"status":"paused","pending":{len(pending)}}}',flush=True); return
        batch=pending[:args.batch_size]; batch_no+=1; name=f'batch-{batch_no:04d}'; out=root/name; out.mkdir(parents=True,exist_ok=True); log=root/'supervisor.log'
        cmd=[str(PY),'data-service/scripts/daily_local_ingestion.py']
        for s in batch: cmd += ['--symbol',s]
        cmd += ['--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,'--out',str(out),'--ssh-target',args.ssh_target,'--profile',str(out/'.chrome-profile'),'--codalpy-first','--codalpy-retries','0','--professional-documents','--defer-pdf','--import','--precheck']
        rc=run(cmd,log,args.codalpy_timeout)
        if rc!=0:
            fallback=[str(PY),'data-service/scripts/daily_local_ingestion.py']
            for s in batch: fallback += ['--symbol',s]
            fallback += ['--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,'--out',str(out),'--ssh-target',args.ssh_target,'--profile',str(out/'.chrome-profile'),'--professional-documents','--defer-pdf','--import']
            rc=run(fallback,log,1800)
        print(f'{{"batch":"{name}","symbols":{len(batch)},"exit_code":{rc}}}',flush=True)
        discovered=[]
        browser_cp=out/'browser'/'checkpoint.json'
        if browser_cp.exists():
            data=json.loads(browser_cp.read_text())
            for entry in data.get('done',{}).values():
                if entry.get('status')=='NO_NOTICES':
                    symbol=entry.get('symbol')
                    if symbol: discovered.append(symbol)
            # Older checkpoints key entries by symbol|range; recover symbols from the batch.
            if data.get('done') and not discovered:
                for key, entry in data['done'].items():
                    if entry.get('status')=='NO_NOTICES': discovered.append(key.split('|',1)[0])
        if discovered:
            no_notices.update(discovered); no_notices_path.write_text(json.dumps(sorted(no_notices),ensure_ascii=False,indent=2),encoding='utf-8')
        if rc==0:
            normalized=out/'normalized'/'normalized.jsonl'; records_by_symbol={}
            if normalized.exists():
                for line in normalized.read_text(encoding='utf8').splitlines():
                    try: symbol=json.loads(line).get('symbol')
                    except json.JSONDecodeError: continue
                    if symbol: records_by_symbol[symbol]=records_by_symbol.get(symbol,0)+1
            for symbol in batch:
                records=records_by_symbol.get(symbol,0)
                if records < 3:
                    item=insufficient.setdefault(symbol,{'attempts':0,'last_records':records})
                    item['attempts'] += 1; item['last_records']=records
                else:
                    item=stable.setdefault(symbol,{'attempts':0,'last_records':records})
                    if item.get('last_records') == records:
                        item['attempts'] += 1
                    else:
                        item['attempts'] = 1
                    item['last_records'] = records
            if stable:
                stable_path.write_text(json.dumps(stable,ensure_ascii=False,indent=2),encoding='utf-8')
            if insufficient:
                insufficient_path.write_text(json.dumps(insufficient,ensure_ascii=False,indent=2),encoding='utf-8')
        if rc==0:
            consecutive_failures=0
            profile_dir=out/'.chrome-profile'
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
        else:
            consecutive_failures += 1
            if consecutive_failures >= args.max_consecutive_failures:
                print('{"status":"paused","reason":"failure_limit_reached"}',flush=True); return
            time.sleep(args.failure_cooldown * min(consecutive_failures, 5))
if __name__=='__main__': main()
