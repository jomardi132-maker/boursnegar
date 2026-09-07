#!/usr/bin/env python3
"""Repair the historical OCF output-type classification without changing values."""
from __future__ import annotations
import argparse, json
from sqlalchemy import text
from app.database import engine

COUNT = text("""select output_type,count(*) n from codalpy_records
               where fact_key='operating_cash_flow' group by output_type order by output_type""")
UPDATE = text("""update codalpy_records
                 set output_type='cash_flow'
                 where fact_key='operating_cash_flow' and output_type='income_statement'""")

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--apply',action='store_true'); a=p.parse_args()
    with engine.begin() as c:
        before=[dict(x) for x in c.execute(COUNT).mappings()]
        changed=0
        if a.apply:
            changed=c.execute(UPDATE).rowcount
        after=[dict(x) for x in c.execute(COUNT).mappings()]
    print(json.dumps({'status':'applied' if a.apply else 'plan','before':before,'changed':changed,'after':after},ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
