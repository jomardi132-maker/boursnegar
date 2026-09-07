import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'export_manifest', ROOT / 'data-service' / 'scripts' / 'export_promoted_remote_manifest.py'
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExportPromotedManifestTest(unittest.TestCase):
    def test_unique_symbol_capture_range_is_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'capture.jsonl').write_text(
                json.dumps({'symbol': 'کپرور', 'from_jalali': '1404/01/01', 'to_jalali': '1405/06/03', 'letter': {'Symbol': 'کپرور'}}) + '\n',
                encoding='utf-8',
            )
            self.assertEqual(
                MODULE.capture_range_for_symbol(root, 'کپرور'),
                ('1404/01/01', '1405/06/03'),
            )

    def test_operating_cash_flow_maps_to_cash_flow(self):
        self.assertEqual(MODULE.extract_period_length_months('صورت مالی دوره ۳ ماهه منتهی به ۱۴۰۵/۰۳/۳۱'), 3)

    def test_official_unit_detector_preserves_million_rial_evidence(self):
        self.assertEqual(MODULE.detect_unit('کلیه مبالغ درج شده به میلیون ریال می باشد'.encode()), 'IRR_million')


if __name__ == '__main__':
    unittest.main()
