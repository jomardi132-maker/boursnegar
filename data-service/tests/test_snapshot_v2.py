import unittest

from app.analytics.snapshot_v2 import build_snapshot_payload


class SnapshotV2Tests(unittest.TestCase):
    def test_missing_official_benchmarks_and_industry_model_are_insufficient(self):
        raw = {
            "symbol": "فولاد",
            "company_name": "فولاد مبارکه",
            "report_used": {
                "title": "صورت‌های مالی ۱۲ ماهه (حسابرسی شده)",
                "tracing_no": 123,
                "publish_datetime": "۱۴۰۵/۰۵/۰۷",
                "excel_url": "https://example.invalid/report.xlsx",
            },
            "live_price": {"last_price": 1000, "pe_ratio": 5},
            "financial_metrics": {
                "revenue": 100,
                "net_profit": 20,
                "operating_cash_flow": 18,
                "total_assets": 300,
                "total_liabilities": 100,
                "total_equity": 200,
                "eps_basic": 200,
            },
            "financial_metrics_missing": [],
            "ratios": {"pe_ratio": 5},
        }
        payload = build_snapshot_payload(raw, "audited")
        self.assertEqual(payload["decision"], "INSUFFICIENT_DATA")
        self.assertEqual(payload["dataCoverage"], 100)
        self.assertEqual(
            payload["coreQuestions"]["earnings_vs_bank"]["status"],
            "INSUFFICIENT_DATA",
        )
        self.assertEqual(len(payload["payloadChecksum"]), 64)

    def test_missing_metrics_reduce_coverage_without_becoming_zero_values(self):
        payload = build_snapshot_payload(
            {
                "symbol": "نماد",
                "report_used": {"title": "حسابرسی نشده"},
                "financial_metrics": {"revenue": 0, "net_profit": None},
                "financial_metrics_missing": ["net_profit"],
            },
            "latest_codal",
        )
        self.assertGreater(payload["dataCoverage"], 0)
        self.assertLess(payload["dataCoverage"], 30)
        self.assertEqual(payload["decision"], "INSUFFICIENT_DATA")

    def test_pilot_industry_can_produce_auditable_actionable_decision(self):
        payload = build_snapshot_payload({
            "symbol": "فولاد",
            "company_name": "فولاد مبارکه اصفهان",
            "report_used": {"title": "صورت‌های مالی ۱۲ ماهه حسابرسی شده", "publish_datetime": "2026-07-20"},
            "live_price": {"last_price": 700, "market_category": "فلزات اساسی", "total_shares": 1_000_000},
            "financial_metrics": {
                "revenue": 10_000, "net_profit": 2_000, "operating_cash_flow": 2_000,
                "total_assets": 8_000, "total_liabilities": 2_000,
                "total_equity": 6_000, "eps_basic": 200,
            },
            "financial_metrics_missing": [],
            "ratios": {"roe_percent": 25, "cash_to_profit_ratio_percent": 100,
                       "net_margin_percent": 20, "debt_ratio_percent": 25,
                       "pe_ratio": 3.5},
            "period_comparison": {"revenue_growth_percent": 80},
            "references": {"bankDepositRate": 20.5, "inflationRate": 61.4},
        }, "audited")
        self.assertEqual(payload["decision"], "BUY")
        self.assertEqual(payload["valuation"]["fairValueBase"], 1200)
        self.assertGreaterEqual(payload["healthScore"], 70)
        self.assertEqual(payload["keyMetrics"]["eps"], 200)
        self.assertEqual(payload["keyMetrics"]["roe"], 25)
        self.assertEqual(payload["keyMetrics"]["revenueGrowth"], 80)
        self.assertTrue(payload["report"]["audited"])


if __name__ == "__main__":
    unittest.main()
