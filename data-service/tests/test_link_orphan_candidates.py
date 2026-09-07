import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'link_orphans', ROOT / 'data-service' / 'scripts' / 'link_orphan_candidates.py'
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OrphanCandidateLinkTest(unittest.TestCase):
    def test_capture_index_requires_excel_and_explicit_period(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [
                {'symbol': 'فملی', 'letter': {'TracingNo': 123, 'HasExcel': True,
                 'Title': 'صورت مالی دوره منتهی به ۱۴۰۴/۱۲/۲۹'}},
                {'symbol': 'فملی', 'letter': {'TracingNo': 456, 'HasExcel': False,
                 'Title': 'صورت مالی دوره منتهی به ۱۴۰۴/۱۲/۲۹'}},
            ]
            (root / 'capture.jsonl').write_text(
                ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8'
            )
            self.assertEqual(
                MODULE.captured_excel_letters(root), {('فملی', '1404/12/29'): {'123'}}
            )

    def test_report_signature_distinguishes_consolidated_audited_report(self):
        signature = MODULE.report_signature('اطلاعات و صورت‌های مالی تلفیقی دوره ۶ ماهه منتهی به ۱۴۰۴/۱۲/۲۹ (حسابرسی شده)')
        self.assertEqual(signature, ('1404/12/29', 6, True, True, 'financial'))

    def test_document_title_reads_official_title_from_html_workbook(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'نماد-123-excel.xls'
            path.write_text(
                '<html><head><title>اطلاعات و صورت‌های مالی تلفیقی دوره ۶ ماهه منتهی به ۱۴۰۴/۱۲/۲۹</title></head></html>',
                encoding='utf-8',
            )
            self.assertIn('تلفیقی', MODULE.document_title(path))

    def test_companion_html_naming_is_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'کپرور-1571587-excel.xls'
            companion = path.with_name('کپرور-1571587-html.html')
            companion.write_text(
                '<html><head><title>صورت‌های مالی دوره ۳ ماهه منتهی به ۱۴۰۴/۱۲/۲۹</title></head></html>',
                encoding='utf-8',
            )
            self.assertTrue(companion.exists())
            self.assertIn('3 ماهه', MODULE.document_title(companion))
            self.assertIn('3 ماهه', MODULE.resolved_report_title(path, 'کپرور', '1571587'))


if __name__ == '__main__':
    unittest.main()
