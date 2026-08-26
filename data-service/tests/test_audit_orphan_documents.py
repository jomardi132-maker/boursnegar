import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd


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

    def test_value_period_comes_from_the_same_numeric_column(self):
        columns = pd.MultiIndex.from_tuples([
            ('شرح', 'شرح'), ('دوره منتهی به ۱۴۰۴/۱۲/۲۹', 'حسابرسی شده')
        ])
        frame = pd.DataFrame([['درآمد عملیاتی', '۱۲۳']], columns=columns)
        self.assertEqual(MODULE.parse_financial_statement.__globals__['_value_column_period'](frame), '1404/12/29')


if __name__ == '__main__':
    unittest.main()
