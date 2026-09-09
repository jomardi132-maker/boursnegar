import csv
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LocalCoverageToolsTest(unittest.TestCase):
    def test_promotion_report_audit_accepts_current_and_legacy_schemas(self):
        from importlib.util import module_from_spec, spec_from_file_location

        path = ROOT / 'data-service/scripts/audit_promotion_reports.py'
        spec = spec_from_file_location('promotion_audit', path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        current = {
            'schema': 'boursnegar-notice-promotion-v1', 'status': 'success',
            'backup': '/backup.dump',
            'idempotent_replay': '{"inserted": 0}',
            'ready': '{"status":"ready"}', 'health': '{"status":"ok"}',
        }
        legacy = {
            'schema': 'boursnegar-evidence-promotion-v1', 'status': 'success',
            'backup': '/backup.dump',
            'idempotent_replay': '{"inserted": 0}',
            'ready': '{"status":"ready"}',
        }
        self.assertTrue(module.ok_report(current))
        self.assertTrue(module.ok_report(legacy))

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
            db.executemany('INSERT INTO symbols(symbol,industry) VALUES(?,?)', [('A', 'صنعت الف'), ('B', 'صنعت الف'),
                ('Aح', 'صنعت الف'), ('F', 'صندوق سرمایه گذاری قابل معامله')])
            db.executemany('INSERT INTO facts(symbol,output_type,period_end_jalali,fact_key) VALUES(?,?,?,?)',
                           [('A', 'income_statement', '1404/12/29', f'f{i}') for i in range(4)] +
                           [('A', 'income_statement', '1405/03/31', f'g{i}') for i in range(3)] +
                           [('F', 'balance_sheet', period, 'nav_per_share') for period in ('1404/12/29','1405/03/31')])
            db.execute("INSERT INTO notices(symbol,tracing_no) VALUES('A','n1')")
            db.commit(); db.close()
            py = sys.executable
            subprocess.run([py, str(ROOT / 'data-service/scripts/recalculate_local_coverage.py'), '--db', str(db_path), '--export', str(export_path)], check=True)
            subprocess.run([py, str(ROOT / 'data-service/scripts/plan_local_recovery.py'), '--db', str(db_path), '--out', str(plan_path)], check=True)
            db = sqlite3.connect(db_path)
            self.assertEqual(db.execute("SELECT status FROM symbols WHERE symbol='A'").fetchone()[0], 'complete')
            self.assertIn('ترازنامه', db.execute("SELECT gap_summary FROM symbols WHERE symbol='A'").fetchone()[0])
            self.assertEqual(db.execute("SELECT status FROM symbols WHERE symbol='B'").fetchone()[0], 'incomplete')
            self.assertEqual(db.execute("SELECT status FROM symbols WHERE symbol='Aح'").fetchone()[0], 'not_applicable')
            self.assertEqual(db.execute("SELECT completion_state FROM symbols WHERE symbol='F'").fetchone()[0], 'FUND_COMPLETE')
            with export_path.open(encoding='utf-8-sig') as handle:
                self.assertEqual(len(list(csv.reader(handle))), 5)
            with plan_path.open(encoding='utf-8-sig') as handle:
                self.assertEqual(len(list(csv.reader(handle))), 2)

    def test_plan_uses_authoritative_coverage_priority(self):
        with tempfile.TemporaryDirectory() as temp:
            db_path = Path(temp) / 'local.sqlite3'
            coverage_path = Path(temp) / 'coverage-symbols.csv'
            plan_path = Path(temp) / 'adaptive-plan.csv'
            db = sqlite3.connect(db_path)
            db.execute('CREATE TABLE symbols(symbol TEXT PRIMARY KEY, industry TEXT, status TEXT NOT NULL DEFAULT "unknown", standard_count INTEGER NOT NULL DEFAULT 0, period_count INTEGER NOT NULL DEFAULT 0, gap_summary TEXT NOT NULL DEFAULT "", updated_at TEXT NOT NULL DEFAULT "now")')
            db.executemany('INSERT INTO symbols(symbol,industry) VALUES(?,?)', [('READY', 'x'), ('GAP', 'x')])
            db.commit(); db.close()
            coverage_path.write_text('\ufeffsymbol,coverage_tier,valid_periods,valid_fact_keys\nREADY,CORE_READY,5,20\nGAP,MISSING_COMPARABLE_PERIODS,1,2\n', encoding='utf-8')
            subprocess.run([sys.executable, str(ROOT / 'data-service/scripts/plan_local_recovery.py'), '--db', str(db_path), '--coverage-csv', str(coverage_path), '--out', str(plan_path)], check=True)
            with plan_path.open(encoding='utf-8-sig', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]['نماد'], 'GAP')
            self.assertEqual(rows[0]['coverage_tier'], 'MISSING_COMPARABLE_PERIODS')

    def test_orchestrator_latest_only_ignores_older_manifest_errors(self):
        from importlib.util import module_from_spec, spec_from_file_location

        path = ROOT / 'data-service/scripts/daily_orchestrator.py'
        spec = spec_from_file_location('daily_orchestrator_scope', path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            old = root / '1405' / 'cursor-0001' / 'browser'
            new = root / '1405' / 'cursor-0002' / 'browser'
            old.mkdir(parents=True); new.mkdir(parents=True)
            (old / 'manifest.json').write_text('{"errors":[{"symbol":"old"}]}', encoding='utf-8')
            (new / 'manifest.json').write_text('{"files":[]}', encoding='utf-8')
            now = time.time()
            old.touch(); new.touch()
            import os
            os.utime(old / 'manifest.json', (now - 2, now - 2))
            os.utime(new / 'manifest.json', (now, now))
            result = module.validate_artifacts(root, latest_only=True)
            self.assertTrue(result['valid'])
            self.assertEqual(result['manifests'], 1)


if __name__ == '__main__':
    unittest.main()
