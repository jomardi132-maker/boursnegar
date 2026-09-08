#!/usr/bin/env python3
"""Complete company/fund queues locally, then sync successful batches to Production."""
from __future__ import annotations
import argparse,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; PYTHON=sys.executable
sys.path.insert(0,str(ROOT/'data-service'))
from scripts.ingestion_console import discover_remote
from scripts.auto_local_to_production import is_fund_row,is_derived_symbol,local_symbol_rows

def stream(command,log):
    with log.open('a',encoding='utf-8') as h:
        h.write(json.dumps({'command':command,'started_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False)+'\n');h.flush()
        p=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        assert p.stdout is not None
        for line in p.stdout: print(line.rstrip(),flush=True);h.write(line);h.flush()
        code=p.wait();h.write(json.dumps({'exit_code':code,'finished_at':datetime.now(timezone.utc).isoformat()})+'\n')
        return code

def chunks(items,size): return [items[i:i+size] for i in range(0,len(items),size)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True);p.add_argument('--ssh-target',default='boursnegar')
    p.add_argument('--from-jalali',default='1402/01/01');p.add_argument('--to-jalali',required=True)
    p.add_argument('--batch-size',type=int,default=10);p.add_argument('--pause-seconds',type=int,default=30)
    p.add_argument('--run-root',default='data-service/artifacts/auto-sync');p.add_argument('--apply-production',action='store_true')
    a=p.parse_args();db=Path(a.db).resolve();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root=ROOT/'data-service/artifacts/database-completion'/stamp;root.mkdir(parents=True)
    log=root/'completion.log';status=root/'status.json'
    remote=discover_remote(a.ssh_target,lambda _:None);local=local_symbol_rows(db)
    company=[];fund=[];derived=[]
    for row in remote:
        symbol=row['symbol']
        if local.get(symbol,{}).get('status')!='incomplete':continue
        if is_derived_symbol(symbol): derived.append(symbol)
        elif is_fund_row(row): fund.append(symbol)
        else: company.append(symbol)
    queue={'company':company,'fund':fund,'derived_not_applicable':derived}
    (root/'queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8')
    state={'status':'RUNNING','phase':'local','queue_counts':{k:len(v) for k,v in queue.items()},'successful_local_batches':[],'failed_local_batches':[]}
    status.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    successful=[]
    all_batches=[('company',x) for x in chunks(company,a.batch_size)]+[('fund',x) for x in chunks(fund,a.batch_size)]
    for number,(kind,symbols) in enumerate(all_batches,1):
        symbol_file=root/f'{number:03d}-{kind}.txt';symbol_file.write_text('\n'.join(symbols)+'\n',encoding='utf-8')
        report=root/f'{number:03d}-{kind}-local.json'
        command=[PYTHON,str(ROOT/'data-service/scripts/auto_local_to_production.py'),'--db',str(db),
                 '--ssh-target',a.ssh_target,'--from-jalali',a.from_jalali,'--to-jalali',a.to_jalali,
                 '--limit',str(len(symbols)),'--run-root',str(Path(a.run_root).resolve()),
                 '--symbols-file',str(symbol_file),'--report',str(report),'--apply','--allow-download','--skip-production']
        code=stream(command,log)
        entry={'number':number,'kind':kind,'symbols':symbols,'exit_code':code,'report':str(report)}
        (state['successful_local_batches'] if code==0 else state['failed_local_batches']).append(entry)
        if code==0:successful.append((number,kind,symbol_file,symbols))
        state['phase']='local';state['current_batch']=number;status.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        if a.pause_seconds:time.sleep(a.pause_seconds)
    if a.apply_production:
        state['phase']='production';state['successful_production_batches']=[];state['failed_production_batches']=[]
        status.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        for number,kind,symbol_file,symbols in successful:
            report=root/f'{number:03d}-{kind}-production.json'
            command=[PYTHON,str(ROOT/'data-service/scripts/auto_local_to_production.py'),'--db',str(db),
                     '--ssh-target',a.ssh_target,'--from-jalali',a.from_jalali,'--to-jalali',a.to_jalali,
                     '--limit',str(len(symbols)),'--run-root',str(Path(a.run_root).resolve()),
                     '--symbols-file',str(symbol_file),'--report',str(report),'--apply','--allow-download']
            code=stream(command,log)
            entry={'number':number,'kind':kind,'symbols':symbols,'exit_code':code,'report':str(report)}
            (state['successful_production_batches'] if code==0 else state['failed_production_batches']).append(entry)
            status.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
            if a.pause_seconds:time.sleep(a.pause_seconds)
    failures=len(state['failed_local_batches'])+len(state.get('failed_production_batches',[]))
    state.update({'status':'PASSED' if failures==0 else 'ATTENTION','phase':'finished',
                  'finished_at':datetime.now(timezone.utc).isoformat(),'failures':failures})
    status.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':state['status'],'status_file':str(status),'failures':failures},ensure_ascii=False))

if __name__=='__main__':main()
