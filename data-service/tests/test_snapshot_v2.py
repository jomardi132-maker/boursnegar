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


if __name__ == "__main__":
    unittest.main()
