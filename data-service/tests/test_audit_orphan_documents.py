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

    def test_cash_flow_label_with_soft_hyphen_is_extracted(self):
        frame = pd.DataFrame([
            ['جریان\u00ad خالص \u200cورود\u00ad (خروج) نقد حاصل از فعالیت\u200cهای عملیاتی', '۲۰۴,۴۳۶'],
        ])
        extract = MODULE.parse_financial_statement.__globals__['_extract_keys_from_table']
        self.assertEqual(extract(frame, ['operating_cash_flow'])['operating_cash_flow'], 204436.0)


if __name__ == '__main__':
    unittest.main()
