#!/usr/bin/env python3
"""Fetch one local market snapshot; no database access."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date, datetime, timezone
from pathlib import Path
from app.services.tsetmc_service import get_all_symbols
def main():
 p=argparse.ArgumentParser(); p.add_argument('--date',default=str(date.today())); p.add_argument('--out',required=True); a=p.parse_args(); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
 rows=get_all_symbols(force_refresh=True); valid=[r for r in rows if str(r.get('id') or '').strip() and str(r.get('l18') or '').strip() and float(r.get('pc') or 0)>0 and float(r.get('py') or 0)>0]
 path=out; path.write_text(''.join(json.dumps({'source':'brsapi.ir/tsetmc','trading_date':a.date,'retrieved_at':datetime.now(timezone.utc).isoformat(),'quote':r},ensure_ascii=False,sort_keys=True)+'\n' for r in valid),encoding='utf8'); print(json.dumps({'quotes':len(valid),'date':a.date,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()},ensure_ascii=False))
if __name__=='__main__': main()
