import unittest
from pathlib import Path


class DataServiceContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1]

    def test_analysis_route_and_report_mode(self):
        source = self.root.joinpath("app", "main.py").read_text(encoding="utf-8")
        self.assertIn("/api/analyze/{symbol}", source)
        self.assertIn("report_mode", source)

    def test_no_external_ai_runtime(self):
        source = "\n".join(p.read_text(encoding="utf-8") for p in self.root.joinpath("app").rglob("*.py"))
        self.assertNotIn("gemini", source.lower())
        self.assertNotIn("anthropic", source.lower())


if __name__ == "__main__":
    unittest.main()
