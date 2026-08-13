import unittest
from app.analytics.engine import Policy, core_questions, decide
from app.ingestion.codal import discover_pages, sha256_bytes

class EngineV1Tests(unittest.TestCase):
    def test_core_questions_and_missing_data(self):
        q=core_questions(ttm_eps=200,price=1000,bank_rate=18,operating_cash_flow=90,net_profit=100,nominal_growth=30,matched_inflation=25)
        self.assertEqual([q[x]["status"] for x in q],["PASS","PASS","PASS"])
        self.assertEqual(core_questions()["real_growth"]["status"],"INSUFFICIENT_DATA")
        self.assertEqual(core_questions(operating_cash_flow=-1,net_profit=-2)["cash_quality"]["status"],"INSUFFICIENT_DATA")
    def test_decision_boundaries(self):
        base=dict(health_score=80,coverage=90,confidence=90,current_price=70,fair_value_low=80,fair_value_base=100,fair_value_high=120,industry_model_ready=True)
        self.assertEqual(decide(**base),"BUY")
        self.assertEqual(decide(**{**base,"current_price":100}),"HOLD")
        self.assertEqual(decide(**{**base,"current_price":150}),"SELL")
        self.assertEqual(decide(**{**base,"coverage":69}),"INSUFFICIENT_DATA")
        self.assertEqual(decide(**{**base,"industry_model_ready":False}),"INSUFFICIENT_DATA")
    def test_pagination_dedup_checkpoint_revision_checksum(self):
        pages={1:{"Page":2,"Letters":[{"TracingNo":1,"Title":"اصل"}]},2:{"Page":2,"Letters":[{"TracingNo":1,"Title":"اصل"},{"TracingNo":2,"Title":"اصلاحیه"}]}}
        checkpoints=[]; rows=list(discover_pages(lambda p:pages[p],checkpoint=checkpoints.append))
        self.assertEqual([r.tracing_no for r in rows],["1","2"]); self.assertTrue(rows[1].revision_hint)
        self.assertEqual(checkpoints,[1,2]); self.assertEqual(sha256_bytes(b"x"),sha256_bytes(b"x"))

if __name__ == '__main__': unittest.main()
