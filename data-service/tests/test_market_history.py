import unittest
from datetime import date

from app.ingestion.market_history import (
    filter_history,
    jalali_iso,
    model_family,
    normalize_persian,
)


class MarketHistoryTests(unittest.TestCase):
    def test_normalizes_persian_variants(self):
        self.assertEqual(normalize_persian("بانك\u200cها و موسسات اعتباري"), "بانک ها و موسسات اعتباری")

    def test_maps_five_pilot_industry_families(self):
        self.assertEqual(model_family("فلزات اساسی"), "metals")
        self.assertEqual(model_family("محصولات شیمیایی"), "petrochemical")
        self.assertEqual(model_family("فرآورده‌های نفتی، کک و سوخت هسته‌ای"), "refinery")
        self.assertEqual(model_family("بانک‌ها و موسسات اعتباری"), "bank")
        self.assertEqual(model_family("سیمان، آهک و گچ"), "cement")

    def test_converts_first_day_of_1404(self):
        self.assertEqual(jalali_iso(date(2025, 3, 21)), "1404-01-01")

    def test_filters_history_from_1404(self):
        rows = [{"dEven": 20250320}, {"dEven": 20250321}, {"dEven": 20260814}]
        self.assertEqual(len(filter_history(rows, date(2025, 3, 21))), 2)


if __name__ == "__main__":
    unittest.main()
