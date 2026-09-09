import tempfile
import unittest
import sqlite3
import json
from pathlib import Path

from scripts.auto_local_to_production import (
    DEFAULT_RUN_ROOT,
    DEFAULT_ARTIFACT_ROOT,
    aggregate_events,
    aggregate_manifests,
    base_symbol,
    existing_local_artifacts,
    import_existing_local_artifacts,
    pending_local_artifacts,
    validate_artifact_directory,
    select_explicit_symbols,
    select_symbols,
    is_fund_row,
    attempted_symbols,
    symbol_run_root,
    symbol_failure_exit_code,
    parse_import_result,
    snapshot_delta,
)


class AutoLocalToProductionTest(unittest.TestCase):
    def test_full_pipeline_records_refresh_health_and_retention_gates(self):
        source = (Path(__file__).parents[1] / 'scripts' / 'auto_local_to_production.py').read_text(encoding='utf-8')
        self.assertIn('boursnegar-snapshot-refresh.service', source)
        self.assertIn('/usr/local/sbin/boursnegar-backup-retention', source)
        self.assertIn("'retention':", source)

    def test_default_run_root_is_canonical_data_service_artifact_root(self):
        self.assertTrue(str(DEFAULT_RUN_ROOT).endswith('data-service/artifacts/auto-sync'))
        self.assertTrue(str(DEFAULT_ARTIFACT_ROOT).endswith('data-service/artifacts'))

    def test_import_summary_rejects_validation_errors(self):
        result = parse_import_result('{"inserted": 2, "validation_errors": []}\n')
        self.assertEqual(result['inserted'], 2)
        with self.assertRaises(SystemExit):
            parse_import_result('{"inserted": 0, "validation_errors": [{"error": "checksum"}]}\n')

    def test_symbol_failure_is_nonzero_without_discarding_successful_imports(self):
        self.assertEqual(symbol_failure_exit_code([]), 0)
        self.assertEqual(symbol_failure_exit_code([{'symbol': 'ثبهساز'}]), 2)

    def test_automatic_selection_defers_etf_until_fund_model_exists(self):
        self.assertTrue(is_fund_row({'market_category': 'صندوق سرمایه‌گذاری قابل معامله'}))
        remote = [
            {'symbol': 'اکتان', 'status': 'incomplete', 'market_category': 'صندوق سرمایه‌گذاری قابل معامله'},
            {'symbol': 'فملی', 'status': 'incomplete', 'market_category': 'فلزات اساسی'},
        ]
        local = {s['symbol']: {'status': 'incomplete', 'standard_count': 0, 'period_count': 0, 'notice_count': 0} for s in remote}
        self.assertEqual(select_symbols(remote, local, 10), ['فملی'])

    def test_automatic_selection_skips_checkpointed_symbols(self):
        remote = [{'symbol': 'فملی', 'status': 'incomplete'}, {'symbol': 'شپنا', 'status': 'incomplete'}]
        local = {s['symbol']: {'status': 'incomplete', 'standard_count': 0, 'period_count': 0, 'notice_count': 0} for s in remote}
        self.assertEqual(select_symbols(remote, local, 10, {'فملی'}), ['شپنا'])

    def test_attempted_symbols_reads_checkpoint_run_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'run-1' / 'فملی').mkdir(parents=True)
            (root / 'aggregate' / 'codalpy').mkdir(parents=True)
            self.assertEqual(attempted_symbols(root), {'فملی'})

    def test_aggregation_streams_valid_records_into_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'run' / 'فملی' / 'codalpy'
            source.mkdir(parents=True)
            record = {
                'symbol': 'فملی', 'from_jalali': '1404/01/01', 'to_jalali': '1404/12/29',
                'output_type': 'income_statement', 'payload': {'revenue': 10},
                'source': 'codalpy/codal.ir', 'retrieved_at': '2026-08-27T00:00:00Z',
            }
            (source / 'one.jsonl').write_text(json.dumps(record) + '\n', encoding='utf-8')
            manifest = aggregate_manifests(root / 'run', root / 'out', 'codalpy')
            self.assertEqual(manifest['files'][0]['records'], 1)
            self.assertEqual((root / 'out' / 'codalpy.jsonl').read_text(encoding='utf-8').count('\n'), 1)

    def test_event_aggregation_streams_and_validates_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'run' / 'فملی' / 'events'
            source.mkdir(parents=True)
            event = {'symbol': 'فملی', 'tracing_no': '123', 'source': 'browser/codal.ir'}
            (source / 'notice-events.jsonl').write_text(json.dumps(event) + '\n', encoding='utf-8')
            manifest = aggregate_events(root / 'run', root / 'out')
            self.assertEqual(manifest['files'][0]['records'], 1)

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

        self.assertEqual(select_symbols(remote, local, 4), ['زکوثر', 'بنیرو', 'کربن'])

    def test_base_symbol_handles_persian_and_ascii_digits(self):
        self.assertEqual(base_symbol('کربن3'), 'کربن')
        self.assertEqual(base_symbol('نماد۱۲'), 'نماد')
        self.assertEqual(base_symbol('ما'), 'ما')
        self.assertEqual(base_symbol('فولادح'), 'فولاد')

    def test_progress_requires_real_evidence_delta(self):
        before={'فملی':{'status':'incomplete','fact_keys':2,'periods':1,'notices':3}}
        unchanged={'فملی':{'status':'incomplete','fact_keys':2,'periods':1,'notices':3}}
        changed={'فملی':{'status':'complete','fact_keys':8,'periods':2,'notices':3}}
        self.assertEqual(snapshot_delta(before,unchanged,['فملی'])['changed_count'],0)
        result=snapshot_delta(before,changed,['فملی'])
        self.assertEqual(result['changed_count'],1)
        self.assertEqual(result['fact_key_gain'],6)

    def test_explicit_selection_validates_active_symbols_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'symbols.txt'
            path.write_text('فملی\nفملی\nشپنا\n', encoding='utf-8')
            remote = [{'symbol': 'فملی'}, {'symbol': 'شپنا'}]
            self.assertEqual(select_explicit_symbols(path, remote), ['فملی', 'شپنا'])

    def test_checkpoint_root_does_not_duplicate_symbol_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'run-1' / 'شپنا').mkdir(parents=True)
            self.assertEqual(symbol_run_root(root, 'شپنا'), root / 'run-1')

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

            self.assertEqual(import_existing_local_artifacts(db_path, root)['imported_dirs'], 0)

    def test_pending_artifact_requires_valid_manifest_checksum(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            db_path = root / 'local.sqlite3'
            db_path.touch()
            artifact = root / 'run' / 'فملی' / 'normalized'
            artifact.mkdir(parents=True)
            payload = artifact / 'normalized.jsonl'
            payload.write_text('{}\n', encoding='utf-8')
            (artifact / 'manifest.json').write_text(json.dumps({
                'files': [{'path': payload.name, 'sha256': 'wrong'}]
            }), encoding='utf-8')
            valid, invalid = pending_local_artifacts(db_path, root)
            self.assertEqual(valid, [])
            self.assertEqual(len(invalid), 1)
            self.assertIn('checksum mismatch', invalid[0]['errors'][0])

    def test_valid_artifact_manifest_passes_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / 'normalized'
            artifact.mkdir()
            payload = artifact / 'normalized.jsonl'
            payload.write_text('{}\n', encoding='utf-8')
            import hashlib
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            (artifact / 'manifest.json').write_text(json.dumps({
                'files': [{'path': payload.name, 'sha256': digest}]
            }), encoding='utf-8')
            self.assertEqual(validate_artifact_directory(artifact), [])


if __name__ == '__main__':
    unittest.main()
