import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

from scripts.daily_local_ingestion import run
from scripts.run_all_incomplete import cleanup_profile


class RecoverySupervisorTest(unittest.TestCase):
    def test_cleanup_profile_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            profile = Path(temp) / '.chrome-profile'
            (profile / 'Default').mkdir(parents=True)
            (profile / 'Default' / 'Preferences').write_text('{}', encoding='utf-8')
            cleanup_profile(profile)
            cleanup_profile(profile)
            self.assertFalse(profile.exists())

    @patch('scripts.browser_codal_fetch.cleanup_profile_processes')
    def test_run_timeout_cleans_profile_processes(self, cleanup):
        with tempfile.TemporaryDirectory() as temp:
            profile = Path(temp) / '.chrome-profile'
            result = run([sys.executable, '-c', 'import time; time.sleep(10)', '--profile', str(profile)], timeout=0.01)
            self.assertFalse(result)
            cleanup.assert_called_once_with(profile)


if __name__ == '__main__':
    unittest.main()
