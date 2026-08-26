import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'data-service' / 'scripts' / 'reconcile_local_artifacts.py'


class ArtifactLedgerTest(unittest.TestCase):
    def test_inventory_verifies_quarantines_and_marks_missing_files(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as folder:
            base = Path(folder)
            good = base / 'good.jsonl'
            bad = base / 'bad.jsonl'
            good.write_text('{"symbol":"فملی"}\n', encoding='utf-8')
            bad.write_text('{broken json\n', encoding='utf-8')
            duplicate = base / 'duplicate.jsonl'
            duplicate.write_bytes(good.read_bytes())
            good_sha = hashlib.sha256(good.read_bytes()).hexdigest()
            manifest = {
                'schema': 'test-v1',
                'source': 'unit-test',
                'files': [
                    {'path': good.name, 'sha256': good_sha, 'records': 1},
                    {'path': bad.name, 'sha256': hashlib.sha256(bad.read_bytes()).hexdigest(), 'records': 1},
                    {'path': 'missing.jsonl', 'sha256': '0' * 64, 'records': 1},
                ],
                'errors': [],
            }
            (base / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            db_path = base / 'ledger.sqlite3'
            subprocess.run(
                ['python3', str(SCRIPT), '--db', str(db_path), '--root', str(base)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            db = sqlite3.connect(db_path)
            statuses = {Path(path).name: status for path, status in db.execute(
                'SELECT path,status FROM artifact_files'
            )}
            self.assertEqual(statuses['good.jsonl'], 'VERIFIED')
            self.assertEqual(statuses['duplicate.jsonl'], 'VERIFIED')
            self.assertEqual(statuses['bad.jsonl'], 'QUARANTINED')
            self.assertEqual(statuses['missing.jsonl'], 'FAILED')
            self.assertEqual(statuses['manifest.json'], 'INVENTORIED')
            run_status, = db.execute('SELECT status FROM ledger_runs ORDER BY id DESC LIMIT 1').fetchone()
            self.assertEqual(run_status, 'PASSED')


if __name__ == '__main__':
    unittest.main()
