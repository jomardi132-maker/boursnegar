import unittest

from app.analytics.industry_valuation import health_score, value_company
from app.services.ratio_engine import evaluate_health_status


class IndustryValuationTests(unittest.TestCase):
    def test_non_financial_high_debt_is_explicitly_bad(self):
        result = evaluate_health_status({"debt_ratio_percent": 80}, "فلزات اساسی")
        debt = next(flag for flag in result["flags"] if flag["key"] == "debt")
        self.assertEqual(debt["status"], "bad")

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

    def test_values_food_company_with_disclosed_policy_scenario(self):
        value = value_company({
            "live_price": {"market_category": "محصولات غذایی و آشامیدنی به جز قند و شکر"},
            "financial_metrics": {"eps_basic": 200},
        })
        self.assertEqual(value["family"], "food")
        self.assertEqual(value["fairValueBase"], 1400)
        self.assertEqual(value["assumptions"]["multipleType"], "internal_policy_scenario")

    def test_values_bank_with_price_to_book(self):
        value = value_company({
            "live_price": {"market_category": "بانک‌ها و موسسات اعتباری", "total_shares": 1_000_000},
            "financial_metrics": {"total_equity": 2_000},
        })
        self.assertEqual(value["method"], "price_to_book")
        self.assertEqual(value["fairValueBase"], 8000)
        self.assertEqual(value["fairValueLow"], 8000)
        self.assertEqual(value["fairValueHigh"], 16000)
        self.assertEqual(value["assumptions"]["scenarioMultiples"]["bear"], 4.0)
        self.assertEqual(value["assumptions"]["scenarioMultiples"]["bull"], 8.0)

    def test_values_real_estate_with_explicit_book_value_proxy(self):
        value = value_company({
            "live_price": {"market_category": "انبوه‌سازی، املاک و مستغلات", "total_shares": 1_000_000},
            "financial_metrics": {"total_equity": 2_000},
        })
        self.assertEqual(value["family"], "real_estate")
        self.assertEqual(value["method"], "price_to_book")
        self.assertEqual(value["assumptions"]["basisSource"], "book_value_proxy")

    def test_values_holdings_only_with_explicit_book_value_proxy(self):
        value = value_company({
            "live_price": {"market_category": "شرکت‌های چند رشته‌ای صنعتی", "total_shares": 1_000_000},
            "financial_metrics": {"total_equity": 2_000},
        })
        self.assertEqual(value["family"], "holding")
        self.assertEqual(value["method"], "price_to_book")
        self.assertEqual(value["fairValueBase"], 8000)
        self.assertEqual(value["assumptions"]["basisSource"], "book_value_proxy")

    def test_holding_uses_nav_when_official_nav_is_supplied(self):
        value = value_company({
            "live_price": {"market_category": "شرکت های چند رشته ای صنعتی"},
            "valuation_inputs": {"nav_per_share": 5000},
            "financial_metrics": {},
        })
        self.assertEqual(value["method"], "nav")
        self.assertEqual(value["fairValueBase"], 5000)
        self.assertEqual(value["assumptions"]["basisSource"], "official_nav_per_share")

    def test_fund_uses_official_nav_only(self):
        value = value_company({
            "live_price": {"market_category": "صندوق سرمایه‌گذاری قابل معامله"},
            "valuation_inputs": {"nav_per_share": 2500},
            "financial_metrics": {},
        })
        self.assertEqual(value["family"], "fund")
        self.assertEqual(value["method"], "nav")
        self.assertEqual(value["fairValueBase"], 2500)

    def test_fund_without_official_nav_is_gated(self):
        self.assertIsNone(value_company({
            "live_price": {"market_category": "صندوق سرمایه‌گذاری قابل معامله"},
            "financial_metrics": {"eps_basic": 1000},
        }))

    def test_financial_uses_residual_income_only_with_complete_inputs(self):
        value = value_company({
            "live_price": {
                "market_category": "بانک ها و موسسات اعتباری",
                "total_shares": 1_000_000,
            },
            "valuation_inputs": {
                "net_income": 100,
                "book_equity": 1000,
                "cost_of_equity": 20,
                "terminal_growth": 5,
            },
            "financial_metrics": {},
        })
        self.assertEqual(value["method"], "residual_income")
        self.assertEqual(value["assumptions"]["basisSource"], "matched_residual_income_inputs")

    def test_operating_company_uses_dcf_only_with_complete_fcff_inputs(self):
        value = value_company({
            "live_price": {"market_category": "فلزات اساسی", "total_shares": 1_000_000},
            "valuation_inputs": {"fcff": 100, "wacc": 20, "terminal_growth": 5},
            "financial_metrics": {},
        })
        self.assertEqual(value["method"], "dcf")
        self.assertEqual(value["assumptions"]["basisSource"], "matched_fcff_dcf_inputs")

    def test_operating_company_uses_fcfe_only_with_complete_inputs(self):
        value = value_company({
            "live_price": {"market_category": "فلزات اساسی", "total_shares": 1_000_000},
            "valuation_inputs": {"fcfe": 100, "cost_of_equity": 20, "terminal_growth": 5},
            "financial_metrics": {},
        })
        self.assertEqual(value["method"], "fcfe")
        self.assertEqual(value["assumptions"]["basisSource"], "matched_fcfe_inputs")

    def test_rejects_negative_earnings_and_unknown_industry(self):
        self.assertIsNone(value_company({"live_price": {"market_category": "صنعت ناشناخته"}, "financial_metrics": {"eps_basic": 10}}))
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
