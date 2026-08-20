import unittest

from app.analytics.industry_valuation import health_score, value_company


class IndustryValuationTests(unittest.TestCase):
    def test_values_pharmaceuticals_from_current_market_eps(self):
        result = value_company({
            "live_price": {"market_category": "مواد و محصولات دارویی", "eps": 1030},
            "financial_metrics": {"eps_basic": 5945},
        })
        self.assertEqual(result["family"], "pharmaceutical")
        self.assertEqual(result["fairValueBase"], 7210)
        self.assertEqual(result["assumptions"]["basisSource"], "market_ttm_eps")
    def test_values_metal_company_with_normalized_pe(self):
        value = value_company({
            "live_price": {"market_category": "فلزات اساسی", "total_shares": 1000},
            "financial_metrics": {"eps_basic": 200},
        })
        self.assertEqual(value["method"], "normalized_pe")
        self.assertEqual(value["fairValueBase"], 1200)

    def test_values_bank_with_price_to_book(self):
        value = value_company({
            "live_price": {"market_category": "بانک‌ها و موسسات اعتباری", "total_shares": 1_000_000},
            "financial_metrics": {"total_equity": 2_000},
        })
        self.assertEqual(value["method"], "price_to_book")
        self.assertEqual(value["fairValueBase"], 2000)

    def test_values_real_estate_with_explicit_book_value_proxy(self):
        value = value_company({
            "live_price": {"market_category": "انبوه‌سازی، املاک و مستغلات", "total_shares": 1_000_000},
            "financial_metrics": {"total_equity": 2_000},
        })
        self.assertEqual(value["family"], "real_estate")
        self.assertEqual(value["method"], "price_to_book")
        self.assertEqual(value["assumptions"]["basisSource"], "book_value_proxy")

    def test_rejects_negative_earnings_and_unknown_industry(self):
        self.assertIsNone(value_company({"live_price": {"market_category": "خودرو و ساخت قطعات"}, "financial_metrics": {"eps_basic": 10}}))
        self.assertIsNone(value_company({"live_price": {"market_category": "فلزات اساسی"}, "financial_metrics": {"eps_basic": -10}}))

    def test_health_score_requires_enough_dimensions(self):
        score, dimensions = health_score({}, {"roe_percent": 20}, "metals", None, None)
        self.assertIsNone(score)
        self.assertIn("profitability", dimensions)
        score, _ = health_score({}, {
            "roe_percent": 20, "cash_to_profit_ratio_percent": 100,
            "net_margin_percent": 20, "debt_ratio_percent": 30,
        }, "metals", 40, 60)
        self.assertGreaterEqual(score, 70)


if __name__ == "__main__":
    unittest.main()
