#!/usr/bin/env python3
"""Normalize every captured Codal letter into an auditable event artifact."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from html import unescape
from pathlib import Path
SOURCE='browser/codal.ir'; SCHEMA='boursnegar-codal-notices-v1'
def classify(title):
 t=title or ''
 rules=(('amendment','اصلاحیه','الحاقیه'),('auditor_opinion','حسابرس','اظهارنظر'),('assembly','مجمع','تصمیمات مجمع'),('material_disclosure','افشا','اطلاعات بااهمیت'),('forecast_change','پیش‌بینی','پیش بینی','تغییر بااهمیت'),('management_explanation','توضیحات','دلایل تغییر'),('dividend','تقسیم سود','سود سهام'))
 for kind,*words in rules:
  if any(w in t for w in words): return kind
 return 'other'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text_of(path):
 try:
  if path.suffix.lower()=='.pdf':
   result=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,text=True,timeout=30)
   return result.stdout if result.returncode==0 else ''
  raw=path.read_text(encoding='utf8',errors='ignore')
  return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>',' ',raw))).strip()
 except (OSError,subprocess.SubprocessError): return ''
def impact(title, body):
 text=f'{title or ""} {body or ""}'
 high=('تعدیل مثبت','تعدیل منفی','افشای اطلاعات بااهمیت','توقف نماد','افزایش سرمایه','کاهش تولید','زیان')
 medium=('مجمع','حسابرس','تقسیم سود','قرارداد','فروش','تغییر نرخ','تغییر بااهمیت')
 level='high' if any(x in text for x in high) else 'medium' if any(x in text for x in medium) else 'low'
 return level, any(x in text for x in high+medium)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--capture',required=True); p.add_argument('--out',required=True); a=p.parse_args(); root=Path(a.capture); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); rows=[]
 for f in root.glob('*.jsonl'):
  for line in f.read_text(encoding='utf8').splitlines():
   try: x=json.loads(line); l=x.get('letter',{})
   except json.JSONDecodeError: continue
   tracing=str(l.get('TracingNo') or '')
   if not tracing: continue
   docs=x.get('documents') or []; bodies=[]; paths=[]
   for doc in docs:
    path=f.parent/doc.get('path','')
    if path.exists(): paths.append(str(path)); bodies.append(text_of(path))
   body=' '.join(bodies); level,relevant=impact(l.get('Title'),body)
   rows.append({'source':SOURCE,'symbol':x.get('symbol') or l.get('Symbol'),'tracing_no':tracing,'title':l.get('Title'),'notice_type':classify(l.get('Title')),'published_at_jalali':l.get('PublishDateTime'),'period_end_jalali':x.get('to_jalali'),'raw_payload':x,'content_checksum':sha(f),'document_paths':paths,'extracted_text_length':len(body),'impact_level':level,'requires_reanalysis':relevant})
 target=out/'notice-events.jsonl'; target.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf8'); manifest={'schema':SCHEMA,'source':SOURCE,'files':[{'path':target.name,'symbol':'*','records':len(rows),'sha256':sha(target)}]}; (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8'); print(json.dumps({'records':len(rows),'manifest':str(out/'manifest.json')},ensure_ascii=False))
if __name__=='__main__': main()
