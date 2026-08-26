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


if __name__ == '__main__':
    unittest.main()
