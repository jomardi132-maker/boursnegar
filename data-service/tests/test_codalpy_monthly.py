import unittest

from app.ingestion.codalpy_pipeline import standardize


class Result:
    status = "success"
    data = {
        "tracing_no": "123",
        "period_end_to_date": "1405/02/31",
        "sheets": [{"code": 1, "title_fa": "گزارش فعالیت ماهانه", "tables": [{
            "meta_table_id": 1, "title_fa": "تولید و فروش", "cells": [
                {"row_sequence": 10, "row_code": 4, "value": "مبلغ فروش", "cell_group_name": "Body"},
                {"row_sequence": 10, "row_code": 4, "value": "1,160,746", "address": "F10", "cell_group_name": "Body"},
                {"row_sequence": 11, "row_code": 4, "value": "مقدار فروش", "cell_group_name": "Body"},
                {"row_sequence": 11, "row_code": 4, "value": "20", "address": "F11", "cell_group_name": "Body"},
            ],
        }]}],
    }


class CodalpyMonthlyTests(unittest.TestCase):
    def test_monthly_labels_join_by_row_sequence_not_reused_row_code(self):
        rows = standardize([Result()], "monthly_activity")
        self.assertEqual([row["source_label"] for row in rows], ["مبلغ فروش", "مقدار فروش"])


if __name__ == "__main__":
    unittest.main()
