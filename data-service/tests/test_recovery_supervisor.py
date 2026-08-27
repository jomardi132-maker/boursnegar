import tempfile
import unittest
from pathlib import Path

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


if __name__ == '__main__':
    unittest.main()
