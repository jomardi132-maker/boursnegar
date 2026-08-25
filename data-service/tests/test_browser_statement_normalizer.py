import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "normalize_browser_statements.py"
SPEC = importlib.util.spec_from_file_location("normalize_browser_statements", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BrowserStatementNormalizerTests(unittest.TestCase):
    def test_detects_common_codal_units(self):
        self.assertEqual(MODULE.detect_unit("کلیه مبالغ به میلیون ریال است".encode()), "IRR_million")
        self.assertEqual(MODULE.detect_unit("ارقام به میلیارد ريال".encode()), "IRR_billion")
        self.assertEqual(MODULE.detect_unit("مبالغ به هزار ریال".encode()), "IRR_thousand")

    def test_unknown_unit_is_explicit(self):
        self.assertIsNone(MODULE.detect_unit(b"no declared currency unit"))

    def test_statement_metadata_does_not_confuse_unaudited(self):
        self.assertEqual(MODULE.statement_metadata("صورت مالی (حسابرسی شده) تلفیقی"), (True, "consolidated"))
        self.assertEqual(MODULE.statement_metadata("صورت مالی (حسابرسی نشده)"), (False, "separate"))

    def test_remote_importer_does_not_reference_removed_source_constant(self):
        importer = (SCRIPT.parent / "codalpy_remote_import.py").read_text(encoding="utf-8")
        self.assertNotIn("'source':SOURCE", importer)


if __name__ == "__main__":
    unittest.main()
