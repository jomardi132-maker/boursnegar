import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "reconcile_public_gate_registry",
    ROOT / "data-service" / "scripts" / "reconcile_public_gate_registry.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicGateRegistryReconcileTest(unittest.TestCase):
    def test_core_ready_sell_closes_stale_comparable_gate(self):
        gate, action = MODULE.operator_gate(
            {
                "all_active_coverage_tier": "CORE_READY",
                "all_active_valid_periods": 2,
                "public_snapshot_refresh": "success",
                "data_coverage": "100.0",
                "decision": "SELL",
            }
        )
        self.assertEqual(gate, "RECOVERY_CLOSED")
        self.assertIn("بسته شد", action)

    def test_zero_period_404_stays_first_report_gate(self):
        gate, action = MODULE.operator_gate(
            {
                "all_active_coverage_tier": "MISSING_COMPARABLE_PERIODS",
                "all_active_valid_periods": 0,
                "public_snapshot_refresh": "no_stored_report_404",
                "decision": "INSUFFICIENT_DATA",
            }
        )
        self.assertEqual(gate, "NO_KNOWN_DATA_GATE")
        self.assertIn("نخستین صورت مالی", action)

    def test_one_period_symbol_stays_comparable_gate(self):
        gate, action = MODULE.operator_gate(
            {
                "all_active_coverage_tier": "MISSING_COMPARABLE_PERIODS",
                "all_active_valid_periods": 1,
                "public_snapshot_refresh": "success",
                "data_coverage": "100.0",
                "decision": "SELL",
            }
        )
        self.assertEqual(gate, "MISSING_COMPARABLE_PERIODS")
        self.assertIn("دوره مالی معتبر دوم", action)

    def test_core_ready_insufficient_data_becomes_confidence_gate(self):
        gate, action = MODULE.operator_gate(
            {
                "all_active_coverage_tier": "CORE_READY",
                "all_active_valid_periods": 2,
                "public_snapshot_refresh": "success",
                "data_coverage": "100.0",
                "decision": "INSUFFICIENT_DATA",
            }
        )
        self.assertEqual(gate, "ANALYTICAL_CONFIDENCE_GATE")
        self.assertIn("تصمیم قطعی ساخته نشود", action)


if __name__ == "__main__":
    unittest.main()
