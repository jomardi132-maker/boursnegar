#!/usr/bin/env python3
"""Classify unresolved coverage without repeating exhausted network work."""
from __future__ import annotations
import argparse,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True);parser.add_argument('--completion-status',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();status=json.loads(Path(args.completion_status).read_text(encoding='utf-8'));db=sqlite3.connect(args.db)
    for definition in ("coverage_model TEXT NOT NULL DEFAULT 'company_statements'","completion_state TEXT NOT NULL DEFAULT 'UNKNOWN'","last_attempt_at TEXT"):
        try: db.execute(f'ALTER TABLE symbols ADD COLUMN {definition}')
        except sqlite3.OperationalError: pass
    exhausted=[]
    if status.get('status')=='ATTENTION' and not status.get('hard_failures'):
        exhausted=list(status.get('unresolved_recoverable_companies') or [])
        stamp=datetime.now(timezone.utc).isoformat()
        db.executemany("UPDATE symbols SET completion_state='SOURCE_EXHAUSTED',last_attempt_at=? WHERE symbol=?",[(stamp,s) for s in exhausted])
    db.commit()
    counts=dict(db.execute('SELECT completion_state,COUNT(*) FROM symbols GROUP BY completion_state'))
    funds=[r[0] for r in db.execute("SELECT symbol FROM symbols WHERE completion_state IN ('FUND_MISSING','FUND_PARTIAL') ORDER BY symbol")]
    result={'schema':'boursnegar-smart-gap-audit-v1','generated_at':datetime.now(timezone.utc).isoformat(),'source_status':args.completion_status,
            'exhausted_companies':exhausted,'fund_queue':funds,'state_counts':counts,
            'next_action':'new evidence required for exhausted companies; fund queue requires fund/NAV sources'}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__': main()
