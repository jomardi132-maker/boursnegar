#!/usr/bin/env python3
"""Tiny watchdog/status tool for resumable Boursnegar database completion."""
from __future__ import annotations
import argparse,fcntl,json,os,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
COMPLETIONS=ROOT/'data-service/artifacts/database-completion'
PYTHON=ROOT/'data-service/venv/bin/python'

def process_rows():
    rows=[]
    for item in Path('/proc').iterdir():
        if not item.name.isdigit(): continue
        try:
            argv=[part.decode(errors='replace') for part in (item/'cmdline').read_bytes().split(b'\0') if part]
        except OSError: continue
        if any(Path(part).name=='complete_local_then_server.py' for part in argv[:3]):
            rows.append({'pid':int(item.name),'command':' '.join(argv)})
    return rows

def latest_run():
    runs=sorted(path for path in COMPLETIONS.glob('*') if path.is_dir() and (path/'status.json').exists())
    return runs[-1] if runs else None

def load_status(path=None):
    path=path or latest_run()
    if not path: return None
    try: value=json.loads((path/'status.json').read_text(encoding='utf-8'))
    except Exception as exc: return {'status':'INVALID','error':str(exc),'run_dir':str(path)}
    value['run_dir']=str(path);return value

def summary():
    value=load_status() or {'status':'IDLE','batches':[],'queue_counts':{}}
    active=process_rows();total=int(value.get('queue_counts',{}).get('recoverable_companies',0));done=sum(len(x.get('symbols',[])) for x in value.get('batches',[]))
    elapsed=None;eta=None
    try: elapsed=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(value['started_at'])).total_seconds())
    except Exception: pass
    if elapsed and done and total>done: eta=round(elapsed/done*(total-done))
    display_status=value.get('status');audit_path=Path(value.get('run_dir',''))/'smart-gap-audit.json'
    if display_status=='ATTENTION' and audit_path.is_file(): display_status='CLASSIFIED_NO_ACTIONABLE_COMPANY_RETRY'
    return {'active':bool(active),'pids':[x['pid'] for x in active],'status':display_status,'phase':value.get('phase'),
            'done_symbols':done,'total_symbols':total,'remaining_symbols':max(0,total-done),'eta_seconds':eta,
            'net_progress':value.get('net_progress',{}),'run_dir':value.get('run_dir')}

def resume_interrupted():
    if process_rows(): return {'action':'already-running',**summary()}
    value=load_status()
    if not value or value.get('status')!='RUNNING': return {'action':'nothing-to-resume',**summary()}
    run_dir=Path(value['run_dir']);queue=json.loads((run_dir/'queue.json').read_text(encoding='utf-8'))
    completed={symbol for batch in value.get('batches',[]) for symbol in batch.get('symbols',[])}
    remaining=[symbol for symbol in queue.get('recoverable_companies',[]) if symbol not in completed]
    if not remaining: return {'action':'awaiting-final-audit',**summary()}
    resume_file=run_dir/'automatic-resume.txt';resume_file.write_text('\n'.join(remaining)+'\n',encoding='utf-8')
    config=value.get('configuration') or {'db':str(ROOT/'data-service/artifacts/local-ingestion.sqlite3'),'ssh_target':'boursnegar',
        'from_jalali':'1398/01/01','to_jalali':'1405/06/18','batch_size':3,'pause_seconds':60,
        'run_root':str(ROOT/'data-service/artifacts/auto-sync'),'apply_production':True}
    command=[str(PYTHON),str(ROOT/'data-service/scripts/complete_local_then_server.py'),'--db',config['db'],
             '--ssh-target',config['ssh_target'],'--from-jalali',config['from_jalali'],'--to-jalali',config['to_jalali'],
             '--batch-size',str(config['batch_size']),'--pause-seconds',str(config['pause_seconds']),
             '--run-root',config['run_root'],'--symbols-file',str(resume_file)]
    if config.get('apply_production'): command.append('--apply-production')
    log=(run_dir/'automatic-resume.log').open('a',encoding='utf-8')
    process=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                             start_new_session=True,preexec_fn=lambda:os.nice(10))
    return {'action':'resumed','pid':process.pid,'remaining_symbols':remaining,'log':log.name}

def cleanup_collector_chrome():
    for item in Path('/proc').iterdir():
        if not item.name.isdigit(): continue
        try: command=(item/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
        except OSError: continue
        if 'browser_codal_fetch.py' in command: return 0
    stopped=0
    for item in Path('/proc').iterdir():
        if not item.name.isdigit(): continue
        try:
            command=(item/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            cwd=(item/'cwd').resolve()
        except OSError: continue
        if command.startswith('/opt/google/chrome/chrome ') and '--user-data-dir=.chrome-codal-profile' in command and cwd==ROOT:
            try: os.kill(int(item.name),signal.SIGTERM);stopped+=1
            except ProcessLookupError: pass
    return stopped

def audit_finished_attention():
    value=load_status()
    if not value or value.get('status')!='ATTENTION' or process_rows(): return None
    run_dir=Path(value['run_dir']);output=run_dir/'smart-gap-audit.json'
    if output.exists(): return str(output)
    config=value.get('configuration') or {};db=config.get('db') or str(ROOT/'data-service/artifacts/local-ingestion.sqlite3')
    subprocess.run([str(PYTHON),str(ROOT/'data-service/scripts/recalculate_local_coverage.py'),'--db',db],cwd=ROOT,check=True)
    subprocess.run([str(PYTHON),str(ROOT/'data-service/scripts/smart_gap_audit.py'),'--db',db,
                    '--completion-status',str(run_dir/'status.json'),'--out',str(output)],cwd=ROOT,check=True)
    return str(output)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--watch',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--status',action='store_true');parser.add_argument('--interval',type=int,default=60)
    args=parser.parse_args()
    if args.watch:
        lock=(COMPLETIONS/'.manager.lock').open('w')
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return
        while True:
            result=resume_interrupted();audit_finished_attention();cleanup_collector_chrome()
            (COMPLETIONS/'manager-status.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'result':result},ensure_ascii=False,indent=2),encoding='utf-8')
            time.sleep(max(15,args.interval))
    result=resume_interrupted() if args.resume else summary();result['gap_audit']=audit_finished_attention();result['collector_chrome_stopped']=cleanup_collector_chrome()
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
