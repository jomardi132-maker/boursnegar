import sqlite3
from scripts.recover_local_archive import integrity, merge_archive_database

SCHEMA = '''
CREATE TABLE notices(symbol TEXT,tracing_no TEXT,title TEXT,published_at TEXT,local_path TEXT,checksum TEXT,remote_present INTEGER,PRIMARY KEY(symbol,tracing_no));
CREATE TABLE notice_events(symbol TEXT,tracing_no TEXT,notice_type TEXT,title TEXT,published_at TEXT,period_end_jalali TEXT,payload TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no));
CREATE TABLE facts(symbol TEXT,tracing_no TEXT,output_type TEXT,period_end_jalali TEXT,fact_key TEXT,value TEXT,source_label TEXT,payload TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no,output_type,fact_key));
'''

def test_archive_merge_is_idempotent_and_preserves_current_rows(tmp_path):
    current, archive = tmp_path/'current.sqlite3', tmp_path/'archive.sqlite3'
    for path in (current, archive):
        connection=sqlite3.connect(path); connection.executescript(SCHEMA); connection.close()
    c=sqlite3.connect(current)
    c.execute("INSERT INTO notices VALUES('فولاد','1','current',NULL,NULL,NULL,0)"); c.commit(); c.close()
    a=sqlite3.connect(archive)
    a.execute("INSERT INTO notices VALUES('فولاد','1','archive',NULL,NULL,NULL,0)")
    a.execute("INSERT INTO notices VALUES('فملی','2','new',NULL,NULL,NULL,0)"); a.commit(); a.close()
    first=merge_archive_database(current,archive); second=merge_archive_database(current,archive)
    c=sqlite3.connect(current)
    assert c.execute("SELECT title FROM notices WHERE symbol='فولاد'").fetchone()[0]=='current'
    assert c.execute('SELECT COUNT(*) FROM notices').fetchone()[0]==2
    assert first['inserted']['notices']==1 and second['inserted']['notices']==0
    assert integrity(current)=='ok'
