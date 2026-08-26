import csv
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LocalCoverageToolsTest(unittest.TestCase):
    def test_recalculate_and_plan_are_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            db_path = Path(temp) / 'local.sqlite3'
            export_path = Path(temp) / 'coverage.csv'
            plan_path = Path(temp) / 'plan.csv'
            db = sqlite3.connect(db_path)
            db.executescript('''
                CREATE TABLE symbols(symbol TEXT PRIMARY KEY, industry TEXT, status TEXT NOT NULL DEFAULT 'unknown',
                  standard_count INTEGER NOT NULL DEFAULT 0, period_count INTEGER NOT NULL DEFAULT 0,
                  gap_summary TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT 'now');
                CREATE TABLE facts(symbol TEXT, tracing_no TEXT, output_type TEXT, period_end_jalali TEXT,
                  fact_key TEXT, value TEXT, source_label TEXT, payload TEXT, checksum TEXT);
                CREATE TABLE notices(symbol TEXT, tracing_no TEXT);
            ''')
            db.executemany('INSERT INTO symbols(symbol,industry) VALUES(?,?)', [('A', 'صنعت الف'), ('B', 'صنعت الف')])
            db.executemany('INSERT INTO facts(symbol,output_type,period_end_jalali,fact_key) VALUES(?,?,?,?)',
                           [('A', 'income_statement', '1404/12/29', f'f{i}') for i in range(4)] +
                           [('A', 'income_statement', '1405/03/31', f'g{i}') for i in range(3)])
            db.execute("INSERT INTO notices(symbol,tracing_no) VALUES('A','n1')")
            db.commit(); db.close()
            py = sys.executable
            subprocess.run([py, str(ROOT / 'data-service/scripts/recalculate_local_coverage.py'), '--db', str(db_path), '--export', str(export_path)], check=True)
            subprocess.run([py, str(ROOT / 'data-service/scripts/plan_local_recovery.py'), '--db', str(db_path), '--out', str(plan_path)], check=True)
            db = sqlite3.connect(db_path)
            self.assertEqual(db.execute("SELECT status FROM symbols WHERE symbol='A'").fetchone()[0], 'complete')
            self.assertIn('ترازنامه', db.execute("SELECT gap_summary FROM symbols WHERE symbol='A'").fetchone()[0])
            self.assertEqual(db.execute("SELECT status FROM symbols WHERE symbol='B'").fetchone()[0], 'incomplete')
            with export_path.open(encoding='utf-8-sig') as handle:
                self.assertEqual(len(list(csv.reader(handle))), 3)
            with plan_path.open(encoding='utf-8-sig') as handle:
                self.assertEqual(len(list(csv.reader(handle))), 3)


if __name__ == '__main__':
    unittest.main()
