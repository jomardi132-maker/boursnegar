#!/usr/bin/env python3
"""Export promoted local facts as a checksum-backed remote-import artifact."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
import re

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.codal_excel_parser import extract_period_length_months
from scripts.normalize_browser_statements import detect_unit

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def capture_index(folder):
    out={}
    for bundle in folder.glob('*.jsonl'):
        for line in bundle.read_text(encoding='utf8',errors='replace').splitlines():
            try: row=json.loads(line); letter=row.get('letter') or {}
            except json.JSONDecodeError: continue
            tracing=str(letter.get('TracingNo') or '')
            if tracing: out[tracing]={'from':row.get('from_jalali'),'to':row.get('to_jalali'),'title':letter.get('Title'),'audited':'حسابرسی شده' in str(letter.get('Title') or '') and 'حسابرسی نشده' not in str(letter.get('Title') or '')}
    return out


def capture_range_for_symbol(folder, symbol):
    """Return a range only when every symbol-specific capture agrees on it."""
    ranges = set()
    for bundle in folder.glob('*.jsonl'):
        for line in bundle.read_text(encoding='utf8', errors='replace').splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            letter = row.get('letter') or {}
            row_symbol = row.get('symbol') or letter.get('Symbol')
            if str(row_symbol or '') != str(symbol):
                continue
            start, end = row.get('from_jalali'), row.get('to_jalali')
            if start and end:
                ranges.add((str(start), str(end)))
    return next(iter(ranges)) if len(ranges) == 1 else None


def companion_title(path, symbol, tracing):
    title = None
    for candidate in (path, path.with_name(f'{symbol}-{tracing}-html.html')):
        if not candidate.exists():
            continue
        match = re.search(r'<title[^>]*>(.*?)</title>', candidate.read_text(encoding='utf8', errors='replace'), flags=re.I | re.S)
        if match:
            title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', match.group(1))).strip()
            if title:
                return title
    return None

def main():
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    db=sqlite3.connect(a.db); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); target=out/'normalized.jsonl'
    rows=db.execute("""SELECT path,fact_key,checksum,inferred_symbol,period_end_jalali,value,tracing_no,report_scope
        FROM orphan_fact_candidates WHERE status='PROMOTED_LOCAL' AND tracing_no IS NOT NULL
        AND report_scope IS NOT NULL ORDER BY path,fact_key""").fetchall()
    type_map={'total_assets':'balance_sheet','total_liabilities':'balance_sheet','total_equity':'balance_sheet'}
    records=[]; errors=[]; caches={}
    for path,key,checksum,symbol,period,value,tracing,scope in rows:
        folder=Path(path).parent; index=caches.setdefault(folder,capture_index(folder)); meta=index.get(str(tracing))
        title = meta.get('title') if meta else None
        if not meta:
            date_range = capture_range_for_symbol(folder, symbol)
            title = companion_title(Path(path), symbol, str(tracing))
            meta = {
                'from': date_range[0] if date_range else None,
                'to': date_range[1] if date_range else None,
                'title': title,
                'audited': 'حسابرسی شده' in str(title or '') and 'حسابرسی نشده' not in str(title or ''),
            }
        if not meta or not meta.get('from') or not meta.get('to'):
            errors.append({'path':path,'fact_key':key,'error':'capture_range_missing'}); continue
        output_type=type_map.get(key,'cash_flow' if key == 'operating_cash_flow' else 'income_statement')
        period_length_months = extract_period_length_months(str(meta.get('title') or ''))
        document_unit = detect_unit(Path(path).read_bytes()) if Path(path).exists() else None
        records.append({'source':'browser/codal.ir','symbol':symbol,'from_jalali':meta['from'],'to_jalali':meta['to'],'retrieved_at':datetime.now(timezone.utc).isoformat(),'output_type':output_type,'source_action_id':f'{tracing}:{key}:{period}','tracing_no':str(tracing),'period_end_jalali':period,'fact_key':key,'source_label':key,'value':value,'raw_value':value,'unit':'IRR' if key=='eps_basic' else (document_unit or 'UNKNOWN'),'payload':{'title':meta.get('title'),'document_path':path,'document_sha256':checksum,'audited':meta['audited'],'scope':scope}})
        records[-1]['period_length_months'] = period_length_months
    target.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records),encoding='utf8')
    manifest={'schema':'boursnegar-codalpy-jsonl-v1','source':'browser/codal.ir','generated_at':datetime.now(timezone.utc).isoformat(),'files':[{'path':target.name,'records':len(records),'sha256':sha(target)}],'errors':errors}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'records':len(records),'errors':len(errors),'manifest':str(out/'manifest.json')},ensure_ascii=False))
if __name__=='__main__': main()
