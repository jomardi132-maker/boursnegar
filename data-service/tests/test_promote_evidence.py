import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("promote_evidence", ROOT / "scripts/promote_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PromoteEvidenceUnitGateTests(unittest.TestCase):
    def test_standard_import_does_not_force_notice_only_symbol_wildcard(self):
        source = (ROOT / "scripts/promote_evidence.py").read_text(encoding="utf-8")
        self.assertNotIn("codalpy_remote_import.py --manifest {remote_manifest} --symbol '*'", source)

    def test_nav_irr_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "facts.jsonl"
            path.write_text('{"fact_key":"nav_per_share","unit":"IRR"}\n', encoding="utf-8")
            MODULE.validate_normalized_units(path)

    def test_nav_non_irr_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "facts.jsonl"
            path.write_text('{"fact_key":"nav_per_share","unit":"IRR_million"}\n', encoding="utf-8")
            with self.assertRaises(SystemExit):
                MODULE.validate_normalized_units(path)


if __name__ == "__main__":
    unittest.main()
