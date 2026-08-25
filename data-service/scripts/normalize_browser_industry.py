#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
import pandas as pd
from normalize_browser_statements import detect_unit, statement_metadata

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
    root=Path(a.capture); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); rows=[]; errors=[]
    for jf in root.rglob('*.jsonl'):
        for line in jf.read_text(encoding='utf8').splitlines():
            x=json.loads(line); letter=x.get('letter',{}); title=fix(letter.get('Title',''))
            dates=re.findall(r'14\d{2}/\d{2}/\d{2}',title.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789')))
            typ='balance_sheet' if ('وضعیت مالی' in title or 'وضعيت مالي' in title) else ('income_statement' if 'صورت' in title and 'مالی' in title else None)
            if not typ or not dates: continue
            html=next((d.get('path') for d in x.get('documents',[]) if d.get('kind') in ('html','excel')),None)
            if not html: continue
            document=jf.parent/html
            if not document.exists(): continue
            content=document.read_bytes(); unit=detect_unit(content); audited,scope=statement_metadata(title)
            try: tables=pd.read_html(document)
            except IndexError:
                # Some Codal HTML documents contain malformed/empty tables. Keep the
                # raw notice and event, but do not invent facts or fail the whole batch.
                continue
            except Exception as exc: errors.append({'symbol':x.get('symbol'),'tracing_no':letter.get('TracingNo'),'error':str(exc)}); continue
            for table in tables:
                for _,record in table.iterrows():
                    if len(record.index) == 0:
                        continue
                    label=fix(str(record.iloc[0])); fact=MAP.get(key(label))
                    if not fact: continue
                    value=next((num(v) for v in record.iloc[1:].tolist() if num(v) is not None),None)
                    if value is None: continue
                    tracing=str(letter.get('TracingNo')); symbol=x.get('symbol') or letter.get('Symbol')
                    fact_type='balance_sheet' if fact in ('total_assets','total_liabilities','total_equity') else 'income_statement'
                    rows.append({'source':'browser/codal.ir','symbol':symbol,'from_jalali':x.get('from_jalali'),'to_jalali':x.get('to_jalali'),'retrieved_at':x.get('retrieved_at'),'output_type':fact_type,'source_action_id':f'{tracing}:{fact_type}:{fact}','tracing_no':tracing,'period_end_jalali':dates[0],'fact_key':fact,'source_label':label,'value':value,'raw_value':value,'unit':unit or 'UNKNOWN','payload':{'title':title,'document':html,'label':label,'audited':audited,'scope':scope}})
    path=out/'normalized.jsonl'; path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf8')
    manifest={'schema':'boursnegar-codalpy-jsonl-v1','source':'browser/codal.ir','files':[{'path':'normalized.jsonl','symbol':'*','records':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}],'errors':errors}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8'); print(json.dumps({'records':len(rows),'errors':len(errors)},ensure_ascii=False))
if __name__=='__main__': main()
