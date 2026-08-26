import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'data-service' / 'scripts' / 'promote_local_candidates.py'


class PromoteCandidateTest(unittest.TestCase):
    def test_dry_run_does_not_mutate_facts(self):
        with tempfile.NamedTemporaryFile(suffix='.sqlite3') as handle:
            db = sqlite3.connect(handle.name)
            db.executescript('''CREATE TABLE facts(symbol TEXT,tracing_no TEXT,output_type TEXT,period_end_jalali TEXT,fact_key TEXT,value TEXT,source_label TEXT,payload TEXT,checksum TEXT,PRIMARY KEY(symbol,tracing_no,output_type,fact_key));
                CREATE TABLE orphan_fact_candidates(path TEXT,fact_key TEXT,checksum TEXT,inferred_symbol TEXT,period_end_jalali TEXT,value REAL,status TEXT,evidence TEXT,tracing_no TEXT,linkage_evidence TEXT,report_scope TEXT);''')
            db.execute("INSERT INTO orphan_fact_candidates VALUES('x','net_profit','sha','فملی','1404/12/29',12,'READY_FOR_NORMALIZATION','{}','123','{}','separate')")
            db.commit(); db.close()
            result = subprocess.run(['python3', str(SCRIPT), '--db', handle.name], check=True, capture_output=True, text=True)
            self.assertIn('"inserted": 0', result.stdout)
            self.assertEqual(sqlite3.connect(handle.name).execute('SELECT COUNT(*) FROM facts').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
