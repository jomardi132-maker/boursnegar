import unittest

from scripts.audit_nav_consistency import FUND_READINESS_SQL, SQL


class NavConsistencyAuditContractTests(unittest.TestCase):
    def test_matching_contract_includes_period_unit_and_source(self):
        sql = str(SQL)
        self.assertIn("financial_periods", sql)
        self.assertIn("p.end_date_jalali=r.period_end_jalali", sql)
        self.assertIn("normalized_unit=unit", sql)
        self.assertIn("source_disclosure_id=source_action_id", sql)

    def test_matching_contract_does_not_join_on_value_alone(self):
        sql = str(SQL)
        self.assertNotIn("JOIN promoted p ON p.value=r.value", sql)
        self.assertIn("p.symbol=r.symbol", sql)
        self.assertIn("p.value=r.value", sql)

    def test_fund_readiness_requires_nav_and_units_in_one_period(self):
        sql = str(FUND_READINESS_SQL)
        self.assertIn("ind.model_family='fund'", sql)
        self.assertIn("ff.normalized_unit='IRR'", sql)
        self.assertIn("ff.normalized_unit='units'", sql)
        self.assertIn("bool_or(has_nav AND has_units)", sql)


if __name__ == "__main__":
    unittest.main()
