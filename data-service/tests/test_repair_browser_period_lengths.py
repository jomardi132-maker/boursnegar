import unittest

from scripts.repair_browser_period_lengths import title_period_months


class BrowserPeriodLengthTests(unittest.TestCase):
    def test_persian_interim_period(self):
        self.assertEqual(title_period_months("اطلاعات و صورت‌های مالی میاندوره‌ای دوره ۶ ماهه منتهی به ۱۴۰۴/۰۶/۳۱"), 6)

    def test_annual_period(self):
        self.assertEqual(title_period_months("صورت‌های مالی سال مالی منتهی به ۱۴۰۴/۱۲/۲۹"), 12)

    def test_unknown_title_is_not_inferred(self):
        self.assertIsNone(title_period_months("گزارش فعالیت ماهانه منتهی به ۱۴۰۴/۱۲/۲۹"))


if __name__ == "__main__":
    unittest.main()
