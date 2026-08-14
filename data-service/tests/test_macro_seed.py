import unittest

from app.ingestion.macro_seed import validate_dataset


class MacroSeedTests(unittest.TestCase):
    def dataset(self):
        return {
            "series": {
                "code": "cpi_year_over_year",
                "title_fa": "تورم سالانه",
                "source": "https://amar.org.ir/example",
                "unit": "percent",
                "frequency": "monthly",
                "base_year": "1400",
            },
            "observations": [
                {
                    "reference_start": "2026-06-22",
                    "reference_end": "2026-07-22",
                    "reference_period_jalali": "1405/04",
                    "publication_date": "2026-07-25",
                    "effective_date": "2026-07-22",
                    "value": "25.1",
                    "source_reference": "https://amar.org.ir/example/report",
                }
            ],
        }

    def test_validates_and_checksums_official_observations(self):
        result = validate_dataset(self.dataset())
        self.assertEqual(len(result["observations"][0]["checksum"]), 64)

    def test_rejects_non_https_or_impossible_dates(self):
        dataset = self.dataset()
        dataset["observations"][0]["source_reference"] = "file:///tmp/value"
        with self.assertRaises(ValueError):
            validate_dataset(dataset)


if __name__ == "__main__":
    unittest.main()
