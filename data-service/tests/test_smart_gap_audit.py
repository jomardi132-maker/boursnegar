import json,sqlite3,subprocess,sys
from pathlib import Path

def test_attention_without_failures_marks_only_unresolved_as_exhausted(tmp_path):
    db=tmp_path/'db.sqlite3';con=sqlite3.connect(db)
    con.execute("CREATE TABLE symbols(symbol TEXT PRIMARY KEY, completion_state TEXT DEFAULT 'RECOVERABLE')")
    con.executemany('INSERT INTO symbols(symbol) VALUES(?)',[('الف',),('ب',)]);con.commit();con.close()
    status=tmp_path/'status.json';status.write_text(json.dumps({'status':'ATTENTION','hard_failures':[],'unresolved_recoverable_companies':['الف']}),encoding='utf-8')
    out=tmp_path/'audit.json';script=Path(__file__).parents[1]/'scripts/smart_gap_audit.py'
    subprocess.run([sys.executable,str(script),'--db',str(db),'--completion-status',str(status),'--out',str(out)],check=True)
    con=sqlite3.connect(db)
    assert con.execute("SELECT completion_state FROM symbols WHERE symbol='الف'").fetchone()[0]=='SOURCE_EXHAUSTED'
    assert con.execute("SELECT completion_state FROM symbols WHERE symbol='ب'").fetchone()[0]=='RECOVERABLE'
