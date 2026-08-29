#!/usr/bin/env python3
"""Production-side importer. This module intentionally contains no Codal/HTTP client."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from sqlalchemy import text
from app.database import engine
from app.ingestion.market_history import jalali_to_gregorian

SOURCES={'codalpy/codal.ir','browser/codal.ir'}; SCHEMA='boursnegar-codalpy-jsonl-v1'; NOTICE_SCHEMA='boursnegar-codal-notices-v1'
def months_between(start, end):
 sy,sm,sd=map(int,start.split('/')); ey,em,ed=map(int,end.split('/'))
 return max(1,(ey-sy)*12+em-sm+(1 if ed >= 15 else 0))
def sha256(path):
 h=hashlib.sha256();
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',required=True); p.add_argument('--batch-size',type=int,default=500); p.add_argument('--symbol',default='دکوثر'); args=p.parse_args()
 manifest_path=Path(args.manifest); manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 manifest_source=manifest.get('source')
 if manifest.get('schema') not in (SCHEMA,NOTICE_SCHEMA) or manifest_source not in SOURCES: raise SystemExit('manifest schema/source validation failed')
 if manifest.get('schema') == NOTICE_SCHEMA:
  files=[x for x in manifest.get('files',[]) if args.symbol=='*' or x.get('symbol') in (None,'*',args.symbol)]; inserted=0; invalid=[]
  with engine.begin() as db:
   if not db.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('boursnegar:codalpy-import',0))")).scalar(): raise SystemExit('advisory lock is held')
   for item in files:
    path=Path(item['path']); path=path if path.exists() else manifest_path.parent/path
    if not path.exists() or sha256(path)!=item.get('sha256'): invalid.append({'file':str(path),'error':'checksum'}); continue
    for line in path.read_text(encoding='utf8').splitlines():
     record=json.loads(line); required=('source','symbol','tracing_no','notice_type','raw_payload')
     if any(k not in record for k in required) or record['source']!=manifest_source: invalid.append({'file':str(path),'error':'record schema'}); continue
     inserted += db.execute(text("""INSERT INTO codal_notice_events(source,symbol,tracing_no,title,notice_type,published_at_jalali,period_end_jalali,raw_payload,content_checksum) VALUES(:source,:symbol,:tracing_no,:title,:notice_type,:published_at_jalali,:period_end_jalali,CAST(:raw_payload AS jsonb),:content_checksum) ON CONFLICT(source,symbol,tracing_no) DO NOTHING"""),{**record,'raw_payload':json.dumps(record['raw_payload'],ensure_ascii=False)}).rowcount
  print(json.dumps({'symbol':args.symbol,'files':len(files),'inserted':inserted,'standard_facts':0,'validation_errors':invalid},ensure_ascii=False)); return
 files=[x for x in manifest.get('files',[]) if args.symbol=='*' or x.get('symbol') in (None, '*', args.symbol)]
 inserted=0; standard=0; invalid=[]
 with engine.begin() as db:
  if not db.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('boursnegar:codalpy-import',0))")).scalar(): raise SystemExit('advisory lock is held')
  for item in files:
   path=Path(item['path']);
   if not path.exists(): path=manifest_path.parent / path
   expected=item.get('sha256')
   if not path.exists() or sha256(path) != expected: invalid.append({'file':str(path),'error':'checksum'}); continue
   with path.open(encoding='utf-8') as f:
    for line in f:
     record=json.loads(line); required=('source','symbol','from_jalali','to_jalali','output_type','source_action_id','source_label','value','payload')
     if any(k not in record for k in required) or record['source'] != manifest_source: invalid.append({'file':str(path),'error':'record schema'}); continue
     inserted += db.execute(text("""INSERT INTO codalpy_records(source,symbol,output_type,source_action_id,tracing_no,period_end_jalali,fact_key,source_label,value,raw_value,unit,payload) VALUES(:source,:symbol,:output_type,:source_action_id,:tracing_no,:period_end_jalali,:fact_key,:source_label,:value,:raw_value,:unit,CAST(:payload AS jsonb)) ON CONFLICT(source,source_action_id) DO NOTHING"""), {**record,'payload':json.dumps(record['payload'],ensure_ascii=False)}).rowcount
     if record.get('output_type') != 'monthly_activity' and record.get('fact_key') and record.get('period_end_jalali') and record.get('from_jalali'):
      issuer = db.execute(text("SELECT i.id AS instrument_id,i.issuer_id FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id WHERE sa.symbol=:symbol AND sa.valid_to IS NULL"), {'symbol':record['symbol']}).mappings().first()
      if not issuer: continue
      source_id=f"{record['tracing_no']}:{record['output_type']}"
      audited=bool(record['payload'].get('audited',False)); scope=record['payload'].get('scope') or 'unknown'
      disclosure=db.execute(text("""INSERT INTO disclosures(issuer_id,instrument_id,source,source_disclosure_id,disclosure_type,title,published_date_jalali,is_audited,scope) VALUES(:issuer,:instrument,:source,:source_id,'codal_statement',:title,:period,:audited,:scope) ON CONFLICT(source,source_disclosure_id) DO UPDATE SET title=excluded.title,is_audited=excluded.is_audited,scope=excluded.scope RETURNING id"""), {'issuer':issuer['issuer_id'],'instrument':issuer['instrument_id'],'source':record['source'],'source_id':source_id,'title':record['payload'].get('title',record['output_type']),'period':record['period_end_jalali'],'audited':audited,'scope':scope}).scalar_one()
      version=db.execute(text("""INSERT INTO disclosure_versions(disclosure_id,version_number,source_version_id,retrieved_at,content_checksum,metadata,is_current) VALUES(:disclosure,1,:source_id,NOW(),:checksum,CAST(:metadata AS jsonb),true) ON CONFLICT(disclosure_id,version_number) DO UPDATE SET metadata=excluded.metadata,is_current=true RETURNING id"""), {'disclosure':disclosure,'source_id':source_id,'checksum':hashlib.sha256(json.dumps(record['payload'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'metadata':json.dumps({'source':record['source'],'symbol':record['symbol'],'from':record['from_jalali'],'to':record['to_jalali'],'detail_url':record['payload'].get('detail_url'),'excel_url':record['payload'].get('excel_url')},ensure_ascii=False)}).scalar_one()
      y,m,d=[int(x) for x in record['period_end_jalali'].split('/')]
      end_date=jalali_to_gregorian(y,m,d)
      sy,sm,sd=[int(x) for x in record['from_jalali'].split('/')]
      start_date=jalali_to_gregorian(sy,sm,sd)
      length=months_between(record['from_jalali'],record['period_end_jalali'])
      period=db.execute(text("""INSERT INTO financial_periods(issuer_id,period_type,start_date,end_date,start_date_jalali,end_date_jalali,length_months,fiscal_year,audited,scope,disclosure_version_id) VALUES(:issuer,'interim',:start_date,:end_date,:start,:period,:length,:year,:audited,:scope,:version) ON CONFLICT(issuer_id,end_date,length_months,audited,scope,disclosure_version_id) DO UPDATE SET end_date=excluded.end_date RETURNING id"""), {'issuer':issuer['issuer_id'],'start_date':start_date,'end_date':end_date,'start':record['from_jalali'],'period':record['period_end_jalali'],'length':length,'year':y,'audited':audited,'scope':scope,'version':version}).scalar_one()
      parser_name='codal_browser_excel' if record['source']=='browser/codal.ir' else 'codalpy'
      parser_version='v2' if record['source']=='browser/codal.ir' else '0.4.5'
      parser=db.execute(text("""INSERT INTO parser_versions(parser_name,version,document_type,active) VALUES(:name,:version,'datasource',true) ON CONFLICT(parser_name,version,document_type) DO UPDATE SET active=true RETURNING id"""),{'name':parser_name,'version':parser_version}).scalar_one()
      unit='IRR' if record['fact_key']=='eps_basic' else (record.get('unit') or 'UNKNOWN'); quality='VALID' if unit != 'UNKNOWN' else 'UNIT_UNKNOWN'
      standard += db.execute(text("""INSERT INTO financial_facts(issuer_id,period_id,fact_key,raw_value,normalized_value,raw_unit,normalized_unit,unit_multiplier,parser_version_id,quality_status) VALUES(:issuer,:period,:key,:value,:value,:unit,:unit,1,:parser,:quality) ON CONFLICT(period_id,fact_key,parser_version_id) DO UPDATE SET raw_value=excluded.raw_value,normalized_value=excluded.normalized_value,raw_unit=excluded.raw_unit,normalized_unit=excluded.normalized_unit,quality_status=excluded.quality_status WHERE (financial_facts.raw_value,financial_facts.normalized_value,financial_facts.raw_unit,financial_facts.normalized_unit,financial_facts.quality_status) IS DISTINCT FROM (excluded.raw_value,excluded.normalized_value,excluded.raw_unit,excluded.normalized_unit,excluded.quality_status)"""), {'issuer':issuer['issuer_id'],'period':period,'key':record['fact_key'],'value':record['value'],'unit':unit,'quality':quality,'parser':parser}).rowcount
 print(json.dumps({'symbol':args.symbol,'files':len(files),'inserted':inserted,'standard_facts':standard,'validation_errors':invalid},ensure_ascii=False))
if __name__=='__main__': main()
