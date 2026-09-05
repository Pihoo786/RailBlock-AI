import json
import unittest

from optimizer.optimization_engine import calculate_multi_asset_risk, optimize_multi_asset_plan


class Person1OptimizerTests(unittest.TestCase):
    def test_multi_asset_risk_is_bounded(self):
        result = calculate_multi_asset_risk({
            "asset_id": "TRK-01", "asset_type": "Track", "condition_score": 5,
            "age_years": 18, "expected_life_years": 20, "days_overdue": 120,
            "maintenance_cycle_days": 90, "criticality": 5, "failure_count": 3,
            "safety_importance": 5,
        })
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 1)
        self.assertIn(result["risk_band"], {"LOW", "MEDIUM", "HIGH", "CRITICAL"})

    def test_traffic_conflict_is_avoided(self):
        result = optimize_multi_asset_plan(
            [{"request_id": "MR-1", "asset_id": "TRK-1", "section": "MAS-AJJ",
              "duration_minutes": 120, "department": "Engineering", "block_type": "TRAFFIC"}],
            [{"train_id": "T1", "section": "MAS-AJJ", "entry_time": "06:00", "exit_time": "08:00"}],
            assets=[{"asset_id": "TRK-1", "asset_type": "Track", "condition_score": 4,
                     "criticality": 4, "days_overdue": 20}],
            ml_outputs=[{"request_id": "MR-1", "failure_probability": 0.8}],
        )
        self.assertEqual(result["recommended_blocks"][0]["start_time"], "08:00")

    def test_rolling_stock_matching(self):
        result = optimize_multi_asset_plan(
            [{"request_id": "MR-1", "asset_id": "TRK-1", "section": "MAS-AJJ",
              "duration_minutes": 60, "department": "Engineering", "block_type": "TRAFFIC"}],
            [],
            rolling_stock=[{"asset_id": "L-01", "asset_type": "Locomotive", "section": "MAS-AJJ",
                            "overhaul_due": True, "status": "AVAILABLE"}],
            ml_outputs=[{"request_id": "MR-1", "failure_probability": 0.8}],
        )
        self.assertEqual(result["rolling_stock_matches"][0]["matched_assets"], ["L-01"])

    def test_output_is_json_serializable(self):
        result = optimize_multi_asset_plan(
            [{"request_id": "MR-1", "asset_id": "TRK-1", "section": "MAS-AJJ",
              "duration_minutes": 60, "department": "Engineering", "block_type": "TRAFFIC"}],
            [], ml_outputs=[{"request_id": "MR-1", "failure_probability": 0.5}],
        )
        json.dumps(result)


if __name__ == "__main__":
    unittest.main()
