import tempfile
import unittest
import sqlite3
from pathlib import Path

from scripts.auto_local_to_production import (
    base_symbol,
    existing_local_artifacts,
    import_existing_local_artifacts,
    select_symbols,
)


class AutoLocalToProductionTest(unittest.TestCase):
    def test_selection_prefers_comparable_and_defers_derived_symbols(self):
        remote = [
            {'symbol': 'کربن3', 'status': 'incomplete'},
            {'symbol': 'بنیرو', 'status': 'incomplete'},
            {'symbol': 'زکوثر', 'status': 'comparable'},
            {'symbol': 'کربن', 'status': 'incomplete'},
            {'symbol': 'کامل', 'status': 'complete'},
        ]
        local = {
            'کربن3': {'status': 'incomplete', 'standard_count': 0, 'period_count': 0, 'notice_count': 0},
            'بنیرو': {'status': 'incomplete', 'standard_count': 2, 'period_count': 1, 'notice_count': 3},
            'زکوثر': {'status': 'comparable', 'standard_count': 5, 'period_count': 2, 'notice_count': 7},
            'کربن': {'status': 'incomplete', 'standard_count': 1, 'period_count': 1, 'notice_count': 4},
            'کامل': {'status': 'complete', 'standard_count': 7, 'period_count': 2, 'notice_count': 5},
        }

        self.assertEqual(select_symbols(remote, local, 4), ['زکوثر', 'بنیرو', 'کربن', 'کربن3'])

    def test_base_symbol_handles_persian_and_ascii_digits(self):
        self.assertEqual(base_symbol('کربن3'), 'کربن')
        self.assertEqual(base_symbol('نماد۱۲'), 'نماد')
        self.assertEqual(base_symbol('ما'), 'ما')

    def test_existing_local_artifacts_skips_aggregate_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wanted = root / '20260826T000000Z' / 'فملی' / 'browser'
            skipped = root / '20260826T000000Z' / 'aggregate' / 'browser'
            wanted.mkdir(parents=True)
            skipped.mkdir(parents=True)
            (wanted / 'manifest.json').write_text('{}', encoding='utf-8')
            (skipped / 'manifest.json').write_text('{}', encoding='utf-8')

            self.assertEqual(existing_local_artifacts(root), [wanted])

    def test_preimport_skips_artifacts_recorded_in_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            db_path = root / 'local.sqlite3'
            artifact = root / '20260826T000000Z' / 'فملی' / 'normalized'
            artifact.mkdir(parents=True)
            (artifact / 'manifest.json').write_text('{}', encoding='utf-8')
            db = sqlite3.connect(db_path)
            db.executescript('''
                CREATE TABLE runs(source_path TEXT UNIQUE, records INTEGER, created_at TEXT);
            ''')
            db.execute('INSERT INTO runs(source_path, records, created_at) VALUES (?, 0, datetime("now"))', (str(artifact),))
            db.commit()
            db.close()

            self.assertEqual(import_existing_local_artifacts(db_path, root), 0)


if __name__ == '__main__':
    unittest.main()
