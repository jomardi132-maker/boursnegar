import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_codal_monitor import (
    CANONICAL_ARTIFACTS,
    ROOT,
    STATE,
    atomic_write,
    cleanup_browser_profile,
    discover_local,
    load_state,
)


class DailyCodalMonitorTests(unittest.TestCase):
    def test_state_write_is_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            atomic_write(path, {"cursor": 4, "last_symbols": ["فولاد"]})
            self.assertEqual(load_state(path)["cursor"], 4)
            self.assertEqual(json.loads(path.read_text())["last_symbols"], ["فولاد"])

    def test_missing_state_starts_at_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            state = load_state(Path(directory) / "missing.json")
            self.assertEqual(state["cursor"], 0)

    def test_state_can_record_a_daily_run(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            atomic_write(path, {"cursor": 1, "last_date": "1405/06/15"})
            self.assertEqual(load_state(path)["last_date"], "1405/06/15")

    def test_cleanup_removes_only_disposable_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            profile = output / ".chrome-profile"
            profile.mkdir()
            (profile / "Cache").write_text("temporary")
            (output / "manifest.json").write_text("evidence")
            cleanup_browser_profile(output)
            self.assertFalse(profile.exists())
            self.assertTrue((output / "manifest.json").exists())

    def test_discovery_uses_local_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.sqlite3"
            import sqlite3
            with sqlite3.connect(path) as connection:
                connection.execute("CREATE TABLE symbols(symbol TEXT PRIMARY KEY)")
                connection.executemany("INSERT INTO symbols VALUES (?)", [("ب",), ("الف",)])
            self.assertEqual(discover_local(path), ["الف", "ب"])

    def test_same_day_forced_runs_use_separate_output_directory(self):
        # The path policy is intentionally kept in the supervisor: a forced
        # retry must never overwrite the day's manifest.
        day = Path("artifacts") / "daily-codal" / "14050615"
        self.assertNotEqual(day, day / "cursor-0010")

    def test_default_artifact_paths_use_canonical_data_service_root(self):
        self.assertEqual(CANONICAL_ARTIFACTS, ROOT / "data-service" / "artifacts")
        self.assertEqual(STATE, CANONICAL_ARTIFACTS / "daily-codal-monitor.json")


if __name__ == "__main__":
    unittest.main()
