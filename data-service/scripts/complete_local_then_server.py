#!/usr/bin/env python3
"""Evidence-driven completion: classify gaps, fetch recoverable companies, sync only gains."""
from __future__ import annotations
import argparse,fcntl,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; PYTHON=sys.executable
sys.path.insert(0,str(ROOT/'data-service'))
from scripts.ingestion_console import discover_remote
from scripts.auto_local_to_production import is_fund_row,is_derived_symbol,local_symbol_rows

def write_json(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def stream(command,log):
    with log.open('a',encoding='utf-8') as handle:
        handle.write(json.dumps({'command':command,'started_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False)+'\n');handle.flush()
        process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        assert process.stdout is not None
        for line in process.stdout:
            print(line.rstrip(),flush=True);handle.write(line);handle.flush()
        code=process.wait();handle.write(json.dumps({'exit_code':code,'finished_at':datetime.now(timezone.utc).isoformat()})+'\n')
        return code

def chunks(items,size): return [items[start:start+size] for start in range(0,len(items),size)]

def classify(remote,local):
    queue={'recoverable_companies':[],'funds_separate_model':[],'derived_not_applicable':[],'already_sufficient':[]}
    for row in remote:
        symbol=str(row['symbol']); status=str(local.get(symbol,{}).get('status') or row.get('status') or 'incomplete')
        if status!='incomplete': queue['already_sufficient'].append(symbol)
        elif is_derived_symbol(symbol): queue['derived_not_applicable'].append(symbol)
        elif is_fund_row(row): queue['funds_separate_model'].append(symbol)
        else: queue['recoverable_companies'].append(symbol)
    return queue

def read_report(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: return {'status':'missing-or-invalid-report','error':str(exc)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True);parser.add_argument('--ssh-target',default='boursnegar')
    parser.add_argument('--from-jalali',default='1398/01/01');parser.add_argument('--to-jalali',required=True)
    parser.add_argument('--batch-size',type=int,default=5);parser.add_argument('--pause-seconds',type=int,default=45)
    parser.add_argument('--run-root',default='data-service/artifacts/auto-sync');parser.add_argument('--apply-production',action='store_true')
    parser.add_argument('--symbols-file', help='Optional resume queue; only listed recoverable companies are processed')
    args=parser.parse_args()
    if not 1<=args.batch_size<=25: raise SystemExit('batch-size must be between 1 and 25')
    lock_path=ROOT/'data-service/artifacts/database-completion/.operation.lock';lock_path.parent.mkdir(parents=True,exist_ok=True)
    lock_handle=lock_path.open('w');
    try: fcntl.flock(lock_handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('another database completion operation is already running')
    db=Path(args.db).resolve();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root=ROOT/'data-service/artifacts/database-completion'/stamp;root.mkdir(parents=True)
    log=root/'completion.log';status_path=root/'status.json'
    remote_before=discover_remote(args.ssh_target,lambda _:None);local_before=local_symbol_rows(db)
    queue=classify(remote_before,local_before)
    if args.symbols_file:
        requested=[line.strip() for line in Path(args.symbols_file).read_text(encoding='utf-8').splitlines() if line.strip()]
        recoverable=set(queue['recoverable_companies']);unknown=[symbol for symbol in requested if symbol not in recoverable]
        if unknown: raise SystemExit('Resume symbols are not recoverable active companies: '+', '.join(unknown))
        queue['recoverable_companies']=list(dict.fromkeys(requested))
    write_json(root/'queue.json',queue)
    state={'status':'RUNNING','phase':'recoverable-companies','started_at':datetime.now(timezone.utc).isoformat(),
           'configuration':{'db':str(db),'ssh_target':args.ssh_target,'from_jalali':args.from_jalali,
                            'to_jalali':args.to_jalali,'batch_size':args.batch_size,'pause_seconds':args.pause_seconds,
                            'run_root':str(Path(args.run_root).resolve()),'apply_production':args.apply_production},
           'queue_counts':{key:len(value) for key,value in queue.items()},'batches':[],
           'net_progress':{'changed_symbols':0,'fact_key_gain':0,'period_gain':0,'notice_gain':0}}
    write_json(status_path,state)
    for number,symbols in enumerate(chunks(queue['recoverable_companies'],args.batch_size),1):
        symbol_file=root/f'{number:03d}-company.txt';symbol_file.write_text('\n'.join(symbols)+'\n',encoding='utf-8')
        report=root/f'{number:03d}-execution.json'
        command=[PYTHON,str(ROOT/'data-service/scripts/auto_local_to_production.py'),'--db',str(db),'--ssh-target',args.ssh_target,
                 '--from-jalali',args.from_jalali,'--to-jalali',args.to_jalali,'--limit',str(len(symbols)),
                 '--run-root',str(Path(args.run_root).resolve()),'--symbols-file',str(symbol_file),'--report',str(report),
                 '--apply','--allow-download','--skip-preimport','--fresh-fetch']
        if not args.apply_production: command.append('--skip-production')
        code=stream(command,log);result=read_report(report);progress=result.get('local_progress') or {}
        entry={'number':number,'symbols':symbols,'exit_code':code,'result_status':result.get('status'),'progress':progress,'report':str(report)}
        state['batches'].append(entry)
        for key in state['net_progress']:
            source='changed_count' if key=='changed_symbols' else key
            state['net_progress'][key]+=int(progress.get(source) or 0)
        state['current_batch']=number;write_json(status_path,state)
        if args.pause_seconds: time.sleep(args.pause_seconds)
    subprocess.run([PYTHON,str(ROOT/'data-service/scripts/recalculate_local_coverage.py'),'--db',str(db),'--export',str(root/'final-local-coverage.csv')],cwd=ROOT,check=True)
    local_after=local_symbol_rows(db);remote_after=discover_remote(args.ssh_target,lambda _:None)
    final_queue=classify(remote_after,local_after);write_json(root/'final-classification.json',final_queue)
    hard_failures=[batch for batch in state['batches'] if batch['exit_code']!=0];unresolved=final_queue['recoverable_companies']
    state.update({'status':'COMPLETE' if not hard_failures and not unresolved else 'ATTENTION','phase':'finished',
                  'finished_at':datetime.now(timezone.utc).isoformat(),'hard_failures':hard_failures,
                  'final_counts':{key:len(value) for key,value in final_queue.items()},
                  'unresolved_recoverable_companies':unresolved,
                  'meaning':'COMPLETE means no recoverable company remains; funds and derived instruments are classified separately.'})
    write_json(status_path,state)
    print(json.dumps({'status':state['status'],'status_file':str(status_path),'net_progress':state['net_progress'],'unresolved':len(unresolved)},ensure_ascii=False))
    if hard_failures: raise SystemExit(2)

if __name__=='__main__': main()
