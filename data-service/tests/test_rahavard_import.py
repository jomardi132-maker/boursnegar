import unittest

from scripts.import_rahavard_public_reports import normalize_text


class RahavardImportTests(unittest.TestCase):
    def test_normalize_text_removes_rtl_markers_and_collapses_spaces(self):
        self.assertEqual(normalize_text("دارایی\u200fها   ۱۲۳"), "دارایی ها ۱۲۳")


if __name__ == "__main__":
    unittest.main()
