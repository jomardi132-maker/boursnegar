#!/usr/bin/env python3
"""Build/update the local SQLite Codal mirror from existing artifacts."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from pathlib import Path
SCHEMA='''CREATE TABLE IF NOT EXISTS notices(symbol TEXT NOT NULL,tracing_no TEXT NOT NULL,title TEXT,published_at TEXT,source_path TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no)); CREATE TABLE IF NOT EXISTS notice_events(symbol TEXT NOT NULL,tracing_no TEXT NOT NULL,notice_type TEXT NOT NULL,title TEXT,published_at TEXT,period_end_jalali TEXT,payload TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no)); CREATE TABLE IF NOT EXISTS facts(symbol TEXT NOT NULL,tracing_no TEXT NOT NULL,output_type TEXT NOT NULL,period_end_jalali TEXT,fact_key TEXT NOT NULL,value TEXT,source_label TEXT,payload TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no,output_type,fact_key)); CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY,source_path TEXT UNIQUE,records INTEGER NOT NULL,created_at TEXT NOT NULL);'''
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--db',required=True); p.add_argument('--artifact',action='append',required=True); a=p.parse_args(); db=sqlite3.connect(a.db); db.executescript(SCHEMA); notices=facts=0
 for root_name in a.artifact:
  root=Path(root_name); count=0
  for jf in root.rglob('*.jsonl'):
   for line in jf.read_text(encoding='utf8').splitlines():
    try: x=json.loads(line)
    except json.JSONDecodeError: continue
    if 'letter' in x:
     l=x['letter']; symbol=x.get('symbol') or l.get('Symbol'); tracing=str(l.get('TracingNo') or '')
     if symbol and tracing:
      notices+=db.execute('INSERT OR IGNORE INTO notices(symbol,tracing_no,title,published_at,local_path,checksum) VALUES(?,?,?,?,?,?)',(symbol,tracing,l.get('Title'),l.get('PublishDateTime'),str(jf),sha(jf))).rowcount
    if x.get('fact_key'):
     facts+=db.execute('INSERT OR IGNORE INTO facts VALUES(?,?,?,?,?,?,?,?,?)',(x.get('symbol',''),str(x.get('tracing_no','')),x.get('output_type',''),x.get('period_end_jalali'),x['fact_key'],str(x.get('value')),x.get('source_label'),json.dumps(x.get('payload'),ensure_ascii=False),sha(jf))).rowcount
    if x.get('notice_type') and x.get('tracing_no'):
     db.execute('INSERT OR IGNORE INTO notice_events VALUES(?,?,?,?,?,?,?,?)',(x.get('symbol',''),str(x.get('tracing_no')),x['notice_type'],x.get('title'),x.get('published_at_jalali'),x.get('period_end_jalali'),json.dumps(x.get('raw_payload'),ensure_ascii=False),sha(jf)))
    count+=1
  cols={row[1] for row in db.execute('PRAGMA table_info(runs)')}
  if {'source_path','records','created_at'} <= cols:
   db.execute('INSERT OR IGNORE INTO runs(source_path,records,created_at) VALUES(?,?,datetime(\'now\'))',(str(root),count))
  else:
   db.execute('INSERT OR IGNORE INTO runs(started_at,finished_at,status,stage,summary) VALUES(datetime(\'now\'),datetime(\'now\'),\'PASSED\',\'local-artifact-import\',?)',(json.dumps({'source_path':str(root),'records':count},ensure_ascii=False),))
 db.commit(); print(json.dumps({'db':a.db,'new_notices':notices,'new_facts':facts},ensure_ascii=False))
if __name__=='__main__': main()
