import unittest

from optimizer.candidate_windows import candidate_id, generate_feasible_candidates
from optimizer.cp_sat_optimizer import optimize_plan, recommend_single, reoptimize_after_rejection
from optimizer.priority_engine import priority_decision


TRAINS = [
    {"train_id": "T1", "section": "MAS-AJJ", "entry_time": "08:00", "exit_time": "08:30"},
    {"train_id": "T2", "section": "MAS-AJJ", "entry_time": "12:00", "exit_time": "12:30"},
]


def request(number: int, **overrides):
    base = {
        "request_id": f"MR-{number:03d}",
        "asset_id": f"TRK-{number:03d}",
        "department": "Engineering",
        "section": "MAS-AJJ",
        "duration_minutes": 60,
        "days_overdue": number * 2,
        "severity": "HIGH" if number == 1 else "MEDIUM",
        "asset_criticality": 0.9 if number == 1 else 0.5,
        "operational_impact": 0.5,
        "status": "PENDING",
        "block_type": "TRAFFIC",
    }
    return {**base, **overrides}


class AIOptimizationTests(unittest.TestCase):
    def test_priority_logic_is_explainable_and_can_be_critical(self):
        result = priority_decision(request(1, severity="CRITICAL", days_overdue=90), {"request_id": "MR-001", "failure_probability": 0.98, "model_version": "v1"})
        self.assertEqual(result["priority_band"], "CRITICAL")
        self.assertTrue(result["priority_reasons"])
        self.assertIn("failure_probability", result["decision_logic"])

    def test_candidate_windows_exclude_train_occupancy_and_existing_block(self):
        candidates = generate_feasible_candidates(
            request(1), TRAINS, available_start="08:00", available_end="11:00", interval_minutes=60,
            existing_blocks=[{"section": "MAS-AJJ", "start_time": "09:00", "end_time": "11:00", "block_type": "POWER"}],
        )
        self.assertEqual(candidates, [])

    def test_batch_plan_handles_ten_requests(self):
        requests = [request(number) for number in range(1, 11)]
        ml_outputs = [
            {"request_id": item["request_id"], "failure_probability": 0.95 if item["request_id"] == "MR-001" else 0.45, "model_version": "v1"}
            for item in requests
        ]
        result = optimize_plan(requests, ml_outputs, TRAINS, available_start="06:00", available_end="22:00", interval_minutes=60)
        self.assertEqual(result["solver"], "Google OR-Tools CP-SAT")
        self.assertEqual(len(result["plan"]) + len(result["unscheduled_items"]), 10)
        self.assertTrue(any(item["request_id"] == "MR-001" for item in result["plan"]))

    def test_reoptimization_does_not_return_rejected_window(self):
        job = request(1)
        ml = {"request_id": "MR-001", "failure_probability": 0.90, "model_version": "v1"}
        first = recommend_single(job, ml, TRAINS, available_start="06:00", available_end="11:00", interval_minutes=60)
        rejected = first["recommended_block"]
        next_plan = reoptimize_after_rejection(rejected, [job], [ml], TRAINS, available_start="06:00", available_end="11:00", interval_minutes=60)
        self.assertNotEqual(next_plan["plan"][0]["candidate_id"], rejected["candidate_id"])
        self.assertNotEqual(rejected["candidate_id"], candidate_id("MR-001", next_plan["plan"][0]["start_time"], next_plan["plan"][0]["end_time"]))


if __name__ == "__main__":
    unittest.main()
