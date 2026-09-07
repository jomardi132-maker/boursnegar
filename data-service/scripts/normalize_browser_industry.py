#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from normalize_browser_statements import detect_unit, statement_metadata
from app.services.codal_excel_parser import parse_financial_statement, extract_period_length_months, derive_period_start_jalali

MAP = {
    'درآمدهایعملیاتی':'revenue','درآمدهايعملياتي':'revenue',
    'بهایتمامشدهدرآمدهایعملیاتی':'cogs','بهاىتمامشدهدرآمدهايعملياتي':'cogs',
    'سود(زیان)ناخالص':'gross_profit','سود(زيان)ناخالص':'gross_profit',
    'سود(زیان)عملیاتی':'operating_profit','سود(زيان)عملياتى':'operating_profit',
    'سود(زیان)خالص':'net_profit','سود(زيان)خالص':'net_profit',
    'جمعداراییها':'total_assets','جمعدارایی‌ها':'total_assets','جمعداراييها':'total_assets','جمعدارايي‌ها':'total_assets',
    'جمعبدهیها':'total_liabilities','جمعبدهی‌ها':'total_liabilities','جمعبدهیهاوحقوقمالکانه':'total_liabilities',
    'جمعحقوقمالکانه':'total_equity','جمعحقوقصاحبانسهام':'total_equity',
}
DIG = str.maketrans('۰۱۲۳۴۵۶۷۸۹٬','0123456789,')
def fix(v):
    if not isinstance(v, str): return v
    try: v=v.encode('latin1').decode('utf8')
    except UnicodeError: pass
    return v.replace('\u200f','').replace('\u200c','').strip()
def key(v): return fix(v).replace('ي','ی').replace('ى','ی').replace('ك','ک').replace(' ','').replace('‌','')
def num(v):
    s=fix(str(v)).translate(DIG).replace(',','').replace('(','-').replace(')','').strip()
    return s if re.fullmatch(r'-?\d+(?:\.\d+)?',s) else None
def main():
    p=argparse.ArgumentParser(); p.add_argument('--capture',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    root=Path(a.capture); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); rows=[]; errors=[]; seen_source_actions=set()
    for jf in root.rglob('*.jsonl'):
        for line in jf.read_text(encoding='utf8').splitlines():
            x=json.loads(line); letter=x.get('letter',{}); title=fix(letter.get('Title',''))
            dates=re.findall(r'14\d{2}/\d{2}/\d{2}',title.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789')))
            typ='balance_sheet' if ('وضعیت مالی' in title or 'وضعيت مالي' in title) else ('income_statement' if 'صورت' in title and 'مالی' in title else None)
            if not typ or not dates: continue
            tracing=str(letter.get('TracingNo')); symbol=x.get('symbol') or letter.get('Symbol')
            # Codal symbol searches can include subsidiary statements. Their
            # parenthetical company/group name must not be attributed to the
            # listed symbol being normalized.
            if re.search(r'\((?:شرکت|گروه)\s', title):
                continue
            # Prefer one Excel-compatible statement when available. If Excel
            # was unavailable, process every HTML sheet captured from the
            # official page; the browser fetcher records the hidden balance
            # sheet as `html-sheet`.
            documents=[d for d in x.get('documents',[]) if d.get('kind') == 'excel']
            if not documents:
                documents=[d for d in x.get('documents',[]) if str(d.get('kind','')).startswith('html')]
            audited,scope=statement_metadata(title)
            period_length_months=extract_period_length_months(title)
            period_start=derive_period_start_jalali(dates[0], period_length_months)
            for document_meta in documents:
                html=document_meta.get('path')
                if not html: continue
                document=jf.parent/html
                if not document.exists(): continue
                content=document.read_bytes(); unit=detect_unit(content)
                try:
                    parsed = parse_financial_statement(content)
                except Exception as exc:
                    errors.append({'symbol':x.get('symbol'),'tracing_no':letter.get('TracingNo'),'document':html,'error':str(exc)})
                    continue
                for fact, value in parsed['metrics'].items():
                    if value is None:
                        continue
                    fact_type='balance_sheet' if fact in ('total_assets','total_liabilities','total_equity') else 'income_statement'
                    source_action_id=f'{tracing}:{fact_type}:{fact}'
                    if source_action_id in seen_source_actions:
                        continue
                    seen_source_actions.add(source_action_id)
                    rows.append({'source':'browser/codal.ir','symbol':symbol,'from_jalali':period_start or x.get('from_jalali'),'to_jalali':dates[0],'period_length_months':period_length_months,'retrieved_at':x.get('retrieved_at'),'output_type':fact_type,'source_action_id':source_action_id,'tracing_no':tracing,'period_end_jalali':dates[0],'fact_key':fact,'source_label':fact,'value':value,'raw_value':value,'unit':unit or 'UNKNOWN','payload':{'title':title,'document':html,'label':fact,'audited':audited,'scope':scope,'capture_range':{'from':x.get('from_jalali'),'to':x.get('to_jalali')}}})
    path=out/'normalized.jsonl'; path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf8')
    manifest={'schema':'boursnegar-codalpy-jsonl-v1','source':'browser/codal.ir','files':[{'path':'normalized.jsonl','symbol':'*','records':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}],'errors':errors}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8'); print(json.dumps({'records':len(rows),'errors':len(errors)},ensure_ascii=False))
if __name__=='__main__': main()
