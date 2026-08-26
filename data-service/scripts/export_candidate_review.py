#!/usr/bin/env python3
"""Export unresolved local fact candidates for evidence-based manual review."""
from __future__ import annotations
import argparse, csv, sqlite3
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); p.add_argument('--out',required=True); a=p.parse_args()
    db=sqlite3.connect(a.db)
    rows=db.execute('''SELECT path,inferred_symbol,period_end_jalali,status,report_scope,
        COUNT(*) AS facts,COUNT(DISTINCT fact_key) AS keys,MAX(linkage_evidence)
        FROM orphan_fact_candidates WHERE status IN ('READY_FOR_LINKAGE','NEEDS_DISAMBIGUATION','READY_FOR_NORMALIZATION')
        GROUP BY path,inferred_symbol,period_end_jalali,status,report_scope ORDER BY status,path''')
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8-sig') as h:
        w=csv.writer(h); w.writerow(('مسیر','نماد','دوره','وضعیت','scope','تعداد fact','کلید یکتا','شواهد اتصال')); w.writerows(rows)
    print(f'rows={sum(1 for _ in db.execute("select 1 from orphan_fact_candidates where status in (\'READY_FOR_LINKAGE\',\'NEEDS_DISAMBIGUATION\',\'READY_FOR_NORMALIZATION\') group by path"))} out={out}')
if __name__=='__main__': main()
