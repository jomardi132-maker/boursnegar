import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'audit_orphans', ROOT / 'data-service' / 'scripts' / 'audit_orphan_financial_documents.py'
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OrphanDocumentAuditTest(unittest.TestCase):
    def test_period_candidates_are_normalized_and_validated(self):
        content = 'دوره ۱۴۰۴/۰۶/۳۱ و 1403-12-29 و 1399/12/29'.encode()
        self.assertEqual(MODULE.period_candidates(content), ['1403/12/29', '1404/06/31'])

    def test_unique_sibling_capture_is_symbol_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            document = path / 'orphan.xls'
            document.write_bytes(b'<html></html>')
            (path / 'capture.jsonl').write_text(
                json.dumps({'symbol': 'فملی'}, ensure_ascii=False) + '\n', encoding='utf-8'
            )
            self.assertEqual(
                MODULE.batch_symbol(document), ('فملی', 'unique_symbol_in_sibling_capture')
            )


if __name__ == '__main__':
    unittest.main()
