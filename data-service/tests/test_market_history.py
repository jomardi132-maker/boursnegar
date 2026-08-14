import unittest
from datetime import date

from app.ingestion.market_history import (
    filter_history,
    jalali_iso,
    jalali_to_gregorian,
    model_family,
    normalize_persian,
)
from scripts.backfill_market_1404 import adjusted_closes


class MarketHistoryTests(unittest.TestCase):
    def test_back_adjusts_prices_across_official_corporate_action_gap(self):
        rows = [
            {"dEven": 20260729, "pClosing": 20020, "priceYesterday": 20020},
            {"dEven": 20260801, "pClosing": 14860, "priceYesterday": 14600},
            {"dEven": 20260802, "pClosing": 15300, "priceYesterday": 14860},
        ]
        adjusted = adjusted_closes(rows)
        self.assertAlmostEqual(adjusted[20260729], 14600)
        self.assertEqual(adjusted[20260801], 14860)
        self.assertEqual(adjusted[20260802], 15300)

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
        self.assertEqual(jalali_to_gregorian(1404, 1, 1), date(2025, 3, 21))

    def test_filters_history_from_1404(self):
        rows = [{"dEven": 20250320}, {"dEven": 20250321}, {"dEven": 20260814}]
        self.assertEqual(len(filter_history(rows, date(2025, 3, 21))), 2)


if __name__ == "__main__":
    unittest.main()
