#!/usr/bin/env python3
"""Artifact-only Production market importer."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from sqlalchemy import text
from app.database import engine
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',required=True); a=p.parse_args(); m=json.loads(Path(a.manifest).read_text()); path=Path(a.manifest).parent/m['file'];
 if sha(path)!=m['sha256']: raise SystemExit('checksum failed')
 count=0
 with engine.begin() as db:
  if not db.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('boursnegar:market-import',0))")).scalar(): raise SystemExit('lock held')
  for line in path.open():
   x=json.loads(line); q=x['quote']; ins=db.execute(text('SELECT id FROM instruments WHERE market_instrument_id=:id'),{'id':str(q['id'])}).scalar()
   if not ins: continue
   count+=db.execute(text("""INSERT INTO daily_prices(instrument_id,trading_date,trading_date_jalali,open,high,low,close,last,volume,value,trade_count,market_cap,shares_outstanding,source,retrieved_at) VALUES(:i,:d,:d,:o,:h,:l,:c,:last,:v,:val,:tc,:mc,:sh,'brsapi.ir/tsetmc',:r) ON CONFLICT(instrument_id,trading_date,source,adjustment_version) DO UPDATE SET close=excluded.close,last=excluded.last,volume=excluded.volume,value=excluded.value,retrieved_at=excluded.retrieved_at"""),{'i':ins,'d':x['trading_date'],'o':q.get('pf'),'h':q.get('pmax'),'l':q.get('pmin'),'c':q.get('pc'),'last':q.get('pl'),'v':q.get('tvol'),'val':q.get('tval'),'tc':q.get('tno'),'mc':q.get('mv'),'sh':q.get('z'),'r':x['retrieved_at']}).rowcount
 print(json.dumps({'imported':count},ensure_ascii=False))
if __name__=='__main__': main()
