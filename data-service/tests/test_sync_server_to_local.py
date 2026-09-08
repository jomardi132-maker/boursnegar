import unittest

from scripts.sync_server_to_local import output_type, production_sql


class SyncServerToLocalTest(unittest.TestCase):
    def test_fact_keys_map_to_statement_families(self):
        self.assertEqual(output_type('revenue'), 'income_statement')
        self.assertEqual(output_type('total_assets'), 'balance_sheet')
        self.assertEqual(output_type('operating_cash_flow'), 'cash_flow')

    def test_export_is_valid_only_and_lineage_backed(self):
        sql = production_sql()
        self.assertIn("ff.quality_status='VALID'", sql)
        self.assertIn('d.source_disclosure_id IS NOT NULL', sql)
        self.assertIn('dv.content_checksum IS NOT NULL', sql)
        self.assertIn('parser_name', sql)


if __name__ == '__main__':
    unittest.main()
