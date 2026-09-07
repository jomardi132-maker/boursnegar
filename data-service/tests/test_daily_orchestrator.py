import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import daily_orchestrator


class DailyOrchestratorTests(unittest.TestCase):
    def test_classification_keeps_review_distinct(self):
        self.assertEqual(daily_orchestrator.classify(0, 0, 0), "PASS")
        self.assertEqual(daily_orchestrator.classify(0, 2, 0), "REVIEW")
        self.assertEqual(daily_orchestrator.classify(0, 0, 0, no_notices=True), "REVIEW")
        self.assertEqual(daily_orchestrator.classify(0, 1, 0), "BLOCKED")

    def test_artifact_validation_detects_checksum_and_partial_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "payload.jsonl"
            payload.write_text("actual\n", encoding="utf-8")
            (root / "unfinished.xls.crdownload").write_bytes(b"partial")
            (root / "manifest.json").write_text(json.dumps({
                "files": [{"path": "payload.jsonl", "sha256": "wrong"}], "errors": []
            }), encoding="utf-8")
            result = daily_orchestrator.validate_artifacts(root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("checksum-mismatch" in issue for issue in result["issues"]))
            self.assertTrue(any("incomplete-download" in issue for issue in result["issues"]))

    def test_dry_run_writes_non_production_report(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "runs"
            argv = ["daily_orchestrator.py", "--dry-run", "--run-dir", str(run_dir),
                    "--lock-file", str(Path(directory) / "lock")]
            with patch("sys.argv", argv):
                self.assertEqual(daily_orchestrator.main(), 0)
            report = json.loads((run_dir / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS")
            self.assertFalse(report["production_write"])
            self.assertFalse(report["promotion"])

    def test_normal_run_is_collection_only_without_explicit_import_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "runs"
            argv = ["daily_orchestrator.py", "--run-dir", str(run_dir),
                    "--lock-file", str(Path(directory) / "lock")]
            completed = daily_orchestrator.subprocess.CompletedProcess(
                args=[], returncode=0, stdout="collection complete\n", stderr=""
            )
            with patch("sys.argv", argv), patch.object(
                daily_orchestrator.subprocess, "run", return_value=completed
            ) as run:
                self.assertEqual(daily_orchestrator.main(), 0)
            report = json.loads((run_dir / "latest.json").read_text(encoding="utf-8"))
            self.assertFalse(report["production_write"])
            self.assertIn("--no-import", report["commands"][0])
            self.assertIn("--no-import", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
