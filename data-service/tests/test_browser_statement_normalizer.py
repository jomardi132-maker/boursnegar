import importlib.util
from pathlib import Path
import unittest
import pandas as pd
from app.services.codal_excel_parser import TARGET_ITEMS


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "normalize_browser_statements.py"
SPEC = importlib.util.spec_from_file_location("normalize_browser_statements", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BrowserStatementNormalizerTests(unittest.TestCase):
    def test_detects_common_codal_units(self):
        self.assertEqual(MODULE.detect_unit("کلیه مبالغ به میلیون ریال است".encode()), "IRR_million")
        self.assertEqual(MODULE.detect_unit("ارقام به میلیارد ريال".encode()), "IRR_billion")
        self.assertEqual(MODULE.detect_unit("مبالغ به هزار ریال".encode()), "IRR_thousand")

    def test_unknown_unit_is_explicit(self):
        self.assertIsNone(MODULE.detect_unit(b"no declared currency unit"))

    def test_fund_nav_label_is_a_distinct_fact(self):
        self.assertIn("nav_per_share", TARGET_ITEMS)
        labels = TARGET_ITEMS["nav_per_share"]
        self.assertIn("خالصداراییهایهرواحدسرمایهگذاری", labels)

    def test_ending_fund_assets_row_supports_nav_and_units(self):
        label = "خالص دارایی‌ها (واحدهای سرمایه‌گذاری) پایان دوره"
        frame = pd.DataFrame([[label, "1,500", "12,500"]])
        values = MODULE.parse_financial_statement.__globals__["_extract_keys_from_table"](
            frame, ["nav_per_share", "units_outstanding"]
        )
        self.assertEqual(values["units_outstanding"], 1500)
        self.assertEqual(values["nav_per_share"], 12500)

    def test_units_outstanding_has_counting_unit(self):
        self.assertEqual(MODULE.fact_output_type("units_outstanding", "x"), "balance_sheet")

    def test_operating_cash_flow_has_cash_flow_output_type(self):
        self.assertEqual(MODULE.fact_output_type("operating_cash_flow", "صورت‌های مالی میاندوره‌ای"), "cash_flow")

    def test_net_borrowing_does_not_accept_a_single_debt_flow(self):
        labels = TARGET_ITEMS["net_borrowing"]
        self.assertNotIn("دریافتتسهیلات", labels)
        self.assertNotIn("بازپرداختتسهیلات", labels)
        self.assertIn("دریافت(پرداخت)تسهیلات", labels)

    def test_official_url_rejects_untrusted_or_non_https_values(self):
        self.assertEqual(MODULE.official_url('/Reports/Decision.aspx?id=1', 'codal.ir'), 'https://codal.ir/Reports/Decision.aspx?id=1')
        self.assertEqual(MODULE.official_url('https://codal.ir/Reports/Decision.aspx?id=1', 'codal.ir'), 'https://codal.ir/Reports/Decision.aspx?id=1')
        self.assertIsNone(MODULE.official_url('http://example.test/report', 'codal.ir'))
        self.assertIsNone(MODULE.official_url('javascript:alert(1)', 'codal.ir'))

    def test_statement_metadata_does_not_confuse_unaudited(self):
        self.assertEqual(MODULE.statement_metadata("صورت مالی (حسابرسی شده) تلفیقی"), (True, "consolidated"))
        self.assertEqual(MODULE.statement_metadata("صورت مالی (حسابرسی نشده)"), (False, "separate"))

    def test_rejects_explicit_child_entity_financial_statement(self):
        self.assertTrue(MODULE.has_child_entity_qualifier(
            "اطلاعات و صورت‌های مالی میاندوره‌ای دوره ۶ ماهه منتهی به ۱۴۰۴/۰۳/۳۱ (حسابرسی شده) (شرکت بافکار)"
        ))
        self.assertFalse(MODULE.has_child_entity_qualifier(
            "اطلاعات و صورت‌های مالی میاندوره‌ای تلفیقی دوره ۶ ماهه منتهی به ۱۴۰۴/۰۳/۳۱ (حسابرسی شده)"
        ))

    def test_period_start_comes_from_end_and_official_length(self):
        self.assertEqual(MODULE.derive_period_start_jalali("1404/09/30", 6), "1404/04/01")
        self.assertEqual(MODULE.derive_period_start_jalali("1404/03/31", 6), "1403/10/01")
        self.assertEqual(MODULE.derive_period_start_jalali("1404/09/30", 3), "1404/07/01")

    def test_remote_importer_does_not_reference_removed_source_constant(self):
        importer = (SCRIPT.parent / "codalpy_remote_import.py").read_text(encoding="utf-8")
        self.assertNotIn("'source':SOURCE", importer)
        self.assertIn("source,symbol,output_type", importer)
        self.assertIn("args.symbol=='*' or", importer)


if __name__ == "__main__":
    unittest.main()
