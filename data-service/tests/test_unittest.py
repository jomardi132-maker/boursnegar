import unittest
import importlib.util
from pathlib import Path

from fastapi import HTTPException

from app.ingestion.market_history import model_family
from app.analytics.period_comparison import build_period_comparison
from app.analytics.ttm import build_ttm_metrics
from app.services.codal_excel_parser import extract_period_end_jalali


class DataServiceContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1]

    def test_analysis_route_and_report_mode(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("/api/analyze/{symbol}", source)
        self.assertIn("report_mode", source)

    def test_long_provider_tracing_url_is_compacted_deterministically(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("hashlib.sha256", source)
        self.assertIn('[:44]', source)
        self.assertIn("tracing_no = _safe_tracing_no(rec)", source)

    def test_no_external_ai_runtime(self):
        source = "\n".join(p.read_text(encoding="utf-8") for p in self.root.joinpath("app").rglob("*.py"))
        self.assertNotIn("gemini", source.lower())
        self.assertNotIn("anthropic", source.lower())

    def test_comparable_period_is_real_and_graceful(self):
        source = "\n".join(
            (
                self.root.joinpath("app", "main.py").read_text(encoding="utf-8"),
                self.root.joinpath("app", "analytics", "period_comparison.py").read_text(encoding="utf-8"),
            )
        )
        self.assertIn("period_comparison", source)
        self.assertIn("previous_revenue", source)
        self.assertIn("revenue_growth_percent", source)
        self.assertIn("except HTTPException", source)
        self.assertNotIn("random", source.lower())

    def test_unusable_comparable_period_does_not_abort_analysis(self):
        candidate = {"Title": "صورت های مالی ۱۲ ماهه حسابرسی شده", "TracingNo": "1"}
        previous = {"Title": "صورت های مالی ۱۲ ماهه حسابرسی نشده", "TracingNo": "2"}
        parsed = {"metrics": {"revenue": 100, "net_profit": 20}}

        def parse_previous(_candidates):
            raise HTTPException(status_code=422, detail="گزارش قبلی فاقد اقلام اصلی بود.")

        comparison, reason = build_period_comparison(
            candidate, parsed, [previous], parse_previous
        )
        self.assertIsNone(comparison)
        self.assertIn("قابل دریافت", reason)

        def parse_ok(_candidates):
            return previous, "https://example.invalid/prev.xls", {
                "metrics": {"revenue": 80, "net_profit": 10},
            }

        comparison, reason = build_period_comparison(
            candidate, parsed, [previous], parse_ok
        )
        self.assertIsNone(reason)
        self.assertEqual(comparison["previous_report"], "2")
        self.assertAlmostEqual(comparison["revenue_growth_percent"], 25)

    def test_ttm_uses_annual_plus_current_minus_prior_without_fabricating_missing_values(self):
        result = build_ttm_metrics(
            {"revenue": 60, "net_profit": 12, "operating_cash_flow": None},
            {"revenue": 100, "net_profit": 20, "operating_cash_flow": 18},
            {"revenue": 50, "net_profit": 10, "operating_cash_flow": 9},
        )
        self.assertEqual(result["revenue"], 110)
        self.assertEqual(result["net_profit"], 22)
        self.assertIsNone(result["operating_cash_flow"])

    def test_persian_codal_dates_are_normalized_for_history_sync(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("_DATE_DIGITS", source)
        self.assertIn("translate(_DATE_DIGITS)", source)
        self.assertIn('jdatetime.date.fromgregorian', source)
        self.assertIn('gregorian_date.today()', source)
        self.assertNotIn('datetime.date.today()', source)
        self.assertNotIn('"years": [1404, 1405]', source)

    def test_analysis_uses_provenance_cache_when_codal_is_throttled(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("def _stored_codal_letters", source)
        self.assertIn("letters = _stored_codal_letters(db, symbol)", source)

    def test_analysis_uses_stored_real_market_snapshot_when_provider_is_down(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("def _stored_live_snapshot", source)
        self.assertIn("live_data = _stored_live_snapshot(db, symbol)", source)

    def test_html_codal_parser_dependencies_are_pinned(self):
        requirements = self.root.joinpath("requirements.txt").read_text(encoding="utf-8")
        self.assertIn("beautifulsoup4==", requirements)
        self.assertIn("html5lib==", requirements)

    def test_analysis_falls_back_from_broken_codal_amendments(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("def _parse_first_usable_report", source)
        self.assertIn("metrics.get(\"revenue\") is not None", source)
        self.assertIn("Production is artifact-only", source)
        self.assertNotIn("codal_service.fetch_all_letters", source)

    def test_historical_codal_backfill_never_uses_brsapi_fallback(self):
        service = self.root.joinpath("app", "services", "codal_service.py").read_text(encoding="utf-8")
        importer = self.root.joinpath("scripts", "backfill_codal_1404.py").read_text(encoding="utf-8")
        self.assertIn("def fetch_direct_letters_page", service)
        self.assertIn("fetch_direct_letters_page", importer)
        self.assertNotIn("fetch_letters_page(symbol, page)", importer)

    def test_codal_period_requires_explicit_valid_persian_date(self):
        self.assertEqual(
            extract_period_end_jalali("صورت‌های مالی دوره ۶ ماهه منتهی به ۱۴۰۴/۰۶/۳۱"),
            "1404/06/31",
        )
        self.assertIsNone(extract_period_end_jalali("گزارش عملکرد ماهانه بدون تاریخ دوره"))
        self.assertIsNone(extract_period_end_jalali("دوره منتهی به ۱۴۰۴/۱۳/۴۰"))

    def test_financial_ingest_treats_annual_reports_as_twelve_month_periods(self):
        from scripts.ingest_codal_financials import period_months
        self.assertEqual(period_months("صورت‌های مالی سال مالی منتهی به ۱۴۰۳/۱۲/۳۰"), 12)

    def test_codalpy_ranges_and_lossless_numeric_mapping(self):
        from app.ingestion.codalpy_pipeline import ranges, _number
        self.assertEqual(ranges("1405/06/01"), (("1404/01/01", "1404/12/29"), ("1405/01/01", "1405/06/01")))
        self.assertEqual(_number("۱٬۲۳۴"), 1234)
        self.assertIsNone(_number("نامشخص"))

    def test_remote_importer_has_no_codal_client(self):
        source = self.root.joinpath("scripts", "codalpy_remote_import.py").read_text(encoding="utf-8")
        self.assertNotIn("from codalpy", source)
        self.assertIn("pg_try_advisory_xact_lock", source)
        self.assertIn("ON CONFLICT(source,source_action_id) DO NOTHING", source)

    def test_daily_market_adjustment_and_fingerprint_are_deterministic(self):
        path = self.root.joinpath("scripts", "update_market_daily.py")
        spec = importlib.util.spec_from_file_location("update_market_daily", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self.assertAlmostEqual(module.adjusted_close(100, 100, 110, 100), 110)
        self.assertAlmostEqual(module.adjusted_close(100, 100, 80, 50), 160)
        first = [{"id": "2", "l18": "ب", "pc": 20, "py": 19, "pl": 20, "tvol": 2, "tval": 40, "tno": 1},
                 {"id": "1", "l18": "الف", "pc": 10, "py": 9, "pl": 10, "tvol": 1, "tval": 10, "tno": 1}]
        self.assertEqual(module.market_fingerprint(first), module.market_fingerprint(list(reversed(first))))

    def test_corporate_action_sync_only_promotes_registered_notices(self):
        source = self.root.joinpath("scripts", "sync_corporate_action_notices.py").read_text(encoding="utf-8")
        self.assertIn("آگهی ثبت افزایش سرمایه%", source)
        self.assertNotIn("پیشنهاد هیئت مدیره", source)
        self.assertIn("registered_notice_without_inferred_ratio", source)

    def test_metal_ore_miners_use_the_metals_valuation_family(self):
        self.assertEqual(model_family("استخراج کانه‌های فلزی"), "metals")

    def test_ceramics_use_a_supported_industry_family(self):
        self.assertEqual(model_family("کاشی و سرامیک"), "ceramics")

    def test_codalpy_maps_real_balance_sheet_totals(self):
        from app.ingestion.codalpy_pipeline import FACT_LABELS, _label_key
        self.assertEqual(FACT_LABELS[next(k for k in FACT_LABELS if _label_key(k) == _label_key("جمع دارايي‌ها"))], "total_assets")
        self.assertEqual(FACT_LABELS[next(k for k in FACT_LABELS if _label_key(k) == _label_key("جمع حقوق مالکانه"))], "total_equity")

    def test_codalpy_maps_reported_eps(self):
        from app.ingestion.codalpy_pipeline import FACT_LABELS, _label_key
        self.assertEqual(FACT_LABELS[next(k for k in FACT_LABELS if _label_key(k) == _label_key("سود (زیان) خالص هر سهم – ریال"))], "eps_basic")


if __name__ == "__main__":
    unittest.main()
