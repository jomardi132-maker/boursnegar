#!/usr/bin/env python3
"""Local Codalpy-first ingestion with browser fallback and artifact import."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PYTHON=sys.executable
def run(cmd,dry=False,timeout=None):
 print(json.dumps({'step':' '.join(map(str,cmd))},ensure_ascii=False),flush=True)
 if not dry:
  try: subprocess.run(cmd,cwd=ROOT,check=True,timeout=timeout)
  except subprocess.TimeoutExpired:
   print(json.dumps({'step_timeout':timeout,'command':cmd[0]},ensure_ascii=False),flush=True); return False
 return True
 def main():
 p=argparse.ArgumentParser(); p.add_argument('--symbol',action='append',required=True); p.add_argument('--to-jalali',required=True); p.add_argument('--from-jalali',default='1404/01/01'); p.add_argument('--out',default='artifacts/daily-local'); p.add_argument('--ssh-target',default='boursnegar'); p.add_argument('--remote-root',default='/var/lib/boursnegar/codalpy/daily'); p.add_argument('--chrome-port',type=int,default=9240); p.add_argument('--profile',default='.chrome-codal-profile'); p.add_argument('--import',dest='do_import',action='store_true'); p.add_argument('--download-documents',action='store_true'); p.add_argument('--download-all-documents',action='store_true'); p.add_argument('--professional-documents',action='store_true'); p.add_argument('--excel-only',action='store_true'); p.add_argument('--html-only',action='store_true'); p.add_argument('--defer-pdf',action='store_true'); p.add_argument('--precheck',action='store_true'); p.add_argument('--local-db',default='artifacts/local-ingestion.sqlite3'); p.add_argument('--codalpy-first',action='store_true'); p.add_argument('--codalpy-retries',type=int,default=2); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
 if a.precheck:
  from scripts.ingestion_console import discover_remote
  eligible={r['symbol'] for r in discover_remote(a.ssh_target,lambda _:None) if r['symbol'] in a.symbol and r['status']!='complete'}; a.symbol=[s for s in a.symbol if s in eligible]
  print(json.dumps({'precheck':'complete','symbols':a.symbol},ensure_ascii=False),flush=True)
  if not a.symbol: print(json.dumps({'status':'nothing-to-fetch'},ensure_ascii=False)); return
 out=Path(a.out); browser=out/'browser'; norm=out/'normalized'; codal=out/'codalpy'; events=out/'events'; browser_had_errors=False
 for d in (browser,norm,codal,events): d.mkdir(parents=True,exist_ok=True)
 if a.codalpy_first:
  codalpy_python=ROOT/'.venv-codalpy/bin/python'
  if not codalpy_python.exists(): raise SystemExit('local Codalpy environment is missing: .venv-codalpy')
  run([str(codalpy_python),'data-service/scripts/codalpy_local_fetch.py',*[x for s in a.symbol for x in ('--symbol',s)],'--out',str(codal),'--checkpoint',str(codal/'checkpoint.json'),'--today',a.to_jalali,'--retries',str(a.codalpy_retries)],a.dry_run,90)
  cp=json.loads((codal/'checkpoint.json').read_text()) if (codal/'checkpoint.json').exists() else {}; done=cp.get('completed',{}); from app.ingestion.codalpy_pipeline import ranges
  a.symbol=[s for s in a.symbol if any(not done.get(f'{s}|{x}|{y}|{k}') or not done[f'{s}|{x}|{y}|{k}'].get('records',0) for x,y in ranges(a.to_jalali) for k in ('income_statement','balance_sheet','monthly_activity'))]
  print(json.dumps({'codalpy':'completed','browser_fallback_symbols':a.symbol},ensure_ascii=False),flush=True)
 if a.symbol:
  cmd=[PYTHON,'data-service/scripts/browser_codal_fetch.py']; [cmd.extend(['--symbol',s]) for s in a.symbol]; cmd += ['--from-jalali',a.from_jalali,'--to-jalali',a.to_jalali,'--out',str(browser),'--port',str(a.chrome_port),'--profile',a.profile]
  if a.download_documents: cmd.append('--download-documents')
  if a.download_all_documents: cmd.append('--download-all-documents')
  if a.professional_documents: cmd.append('--professional-documents')
  if a.excel_only: cmd.append('--excel-only')
  if a.html_only: cmd.append('--html-only')
  if a.defer_pdf: cmd.append('--defer-pdf')
  run(cmd,a.dry_run,180); browser_cp=browser/'checkpoint.json'; browser_had_errors=bool(json.loads(browser_cp.read_text()).get('errors')) if browser_cp.exists() and not a.dry_run else False; run([PYTHON,'data-service/scripts/normalize_browser_statements.py','--capture',str(browser),'--out',str(norm)],a.dry_run); run([PYTHON,'data-service/scripts/normalize_notice_events.py','--capture',str(browser),'--out',str(events)],a.dry_run); run([PYTHON,'data-service/scripts/build_local_codal_db.py','--db',a.local_db,'--artifact',str(browser),'--artifact',str(norm),'--artifact',str(events)],a.dry_run)
 if a.dry_run: print(json.dumps({'status':'validated-plan'},ensure_ascii=False)); return
 if not a.do_import: print(json.dumps({'status':'ready-for-import'},ensure_ascii=False)); return
 folders=[(n,d) for n,d in (('codalpy',codal),('normalized',norm),('events',events)) if (d/'manifest.json').exists()]; run(['ssh',a.ssh_target,'mkdir -p '+a.remote_root+'/'+out.name]); remote=f'{a.ssh_target}:{a.remote_root}/{out.name}'
 for n,d in folders:
  run(['scp','-r',str(d),remote]); rm=f'{a.remote_root}/{out.name}/{n}/manifest.json'; run(['ssh',a.ssh_target,'cd /var/www/boursnegar-data-current && PYTHONPATH=. /var/www/boursnegar-data-current/venv/bin/python scripts/codalpy_remote_import.py --manifest '+rm+' --symbol "*" --batch-size 500'])
 print(json.dumps({'status':'imported','manifests':[n for n,_ in folders],'browser_errors':browser_had_errors},ensure_ascii=False))
 if browser_had_errors: raise SystemExit(2)
if __name__=='__main__': main()
