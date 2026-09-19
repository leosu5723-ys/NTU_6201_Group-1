import unittest
import tempfile
import json
from pathlib import Path

from live_battery import (
    artifact_hashes,
    check_member_budget,
    check_live_budgets,
    dirty_paths_are_only_run_outputs,
    load_catalog,
    plan_battery,
    normalise_git_state_for_run,
    run_resumable_battery,
    validate_catalog,
)


class LiveBatteryPreparationTests(unittest.TestCase):
    def test_catalog_has_five_distinct_v2_families_and_two_tiers(self):
        catalog = load_catalog()
        validate_catalog(catalog)
        models = catalog["models"]
        self.assertEqual(len(models), 5)
        self.assertEqual(len({row["family"] for row in models.values()}), 5)
        self.assertGreaterEqual(len({row["tier"] for row in models.values()}), 2)
        self.assertTrue(all(row["supports_tools"] for row in models.values()))

    def test_plan_uses_40_cases_and_60_trials_without_spending(self):
        plan = plan_battery("google/gemini-2.5-flash-lite", "v2")
        self.assertEqual(plan["cases"], 40)
        self.assertEqual(plan["trials"], 60)
        self.assertGreater(plan["estimated_cost_usd_from_scripted_tokens"], 0)
        self.assertFalse(plan["executes_network_calls"])

    def test_artifact_hashes_freeze_fixtures_labels_scripts_and_prompt(self):
        hashes = artifact_hashes("v2")
        self.assertEqual(set(hashes), {"claims", "answer_key", "scripts", "system_prompt"})
        self.assertTrue(all(len(value) == 64 for value in hashes.values()))

    def test_member_a2_budget_blocks_planned_overspend(self):
        self.assertEqual(__import__("config").A2_API_BUDGET_PER_MEMBER_USD, 3.0)
        with self.assertRaises(ValueError):
            check_member_budget(estimated_run_cost=0.6, spent_to_date=2.5)
        self.assertAlmostEqual(
            check_member_budget(estimated_run_cost=0.4, spent_to_date=2.5),
            0.1,
        )

    def test_member_budget_cap_cannot_be_overridden_by_caller(self):
        with self.assertRaises(TypeError):
            check_member_budget(
                estimated_run_cost=50.0,
                spent_to_date=0.0,
                budget_cap=100.0,
            )

    def test_monthly_member_cap_is_enforced_independently(self):
        config = __import__("config")
        self.assertEqual(config.MONTHLY_API_BUDGET_PER_MEMBER_USD, 25.0)
        with self.assertRaisesRegex(ValueError, "monthly"):
            check_live_budgets(
                estimated_run_cost=0.4,
                a2_spent_to_date=0.5,
                monthly_spent_to_date=24.8,
            )

    def test_resumable_battery_keeps_completed_paid_trials(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.json"
            calls = []

            def interrupted(case_id, trial):
                calls.append((case_id, trial))
                if len(calls) == 3:
                    raise RuntimeError("temporary outage")
                return {"case_id": case_id, "trial": trial, "passed": True, "record": {}}, None

            with self.assertRaises(RuntimeError):
                run_resumable_battery(
                    ["A", "B"], lambda _case: 2, interrupted, checkpoint, {"key": "same"}
                )
            resumed_calls = []

            def resumed(case_id, trial):
                resumed_calls.append((case_id, trial))
                return {"case_id": case_id, "trial": trial, "passed": True, "record": {}}, None

            results, _ = run_resumable_battery(
                ["A", "B"], lambda _case: 2, resumed, checkpoint, {"key": "same"}
            )
            self.assertEqual(len(results), 4)
            self.assertEqual(resumed_calls, [("B", 1), ("B", 2)])

    def test_resume_rejects_duplicate_checkpoint_trial_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.json"
            checkpoint.write_text(
                json.dumps(
                    {
                        "resume_metadata": {"key": "same"},
                        "results": [
                            {"case_id": "A", "trial": 1, "record": {}},
                            {"case_id": "A", "trial": 1, "record": {}},
                        ],
                        "judgement_queue": [],
                    }
                )
            )
            with self.assertRaisesRegex(ValueError, "checkpoint trial matrix"):
                run_resumable_battery(
                    ["A"],
                    lambda _case: 2,
                    lambda *_: ({}, None),
                    checkpoint,
                    {"key": "same"},
                )

    def test_runtime_budget_guard_stops_before_next_trial_and_keeps_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.json"
            calls = []

            def run_one(case_id, trial):
                calls.append((case_id, trial))
                return (
                    {
                        "case_id": case_id,
                        "trial": trial,
                        "passed": True,
                        "record": {"cost_usd": 0.2},
                    },
                    None,
                )

            def before_run(completed):
                if completed:
                    raise ValueError("runtime budget exhausted")

            with self.assertRaisesRegex(ValueError, "runtime budget"):
                run_resumable_battery(
                    ["A"],
                    lambda _case: 2,
                    run_one,
                    checkpoint,
                    {"key": "same"},
                    before_run=before_run,
                )
            saved = json.loads(checkpoint.read_text())
            self.assertEqual(calls, [("A", 1)])
            self.assertEqual(len(saved["results"]), 1)

    def test_resume_revalidates_each_checkpoint_row(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.json"
            checkpoint.write_text(
                json.dumps(
                    {
                        "resume_metadata": {"key": "same"},
                        "results": [{"case_id": "A", "trial": 1, "record": {}}],
                        "judgement_queue": [],
                    }
                )
            )

            def reject_fabricated(_row):
                raise ValueError("checkpoint row failed validation")

            with self.assertRaisesRegex(ValueError, "checkpoint row"):
                run_resumable_battery(
                    ["A"],
                    lambda _case: 1,
                    lambda *_: ({}, None),
                    checkpoint,
                    {"key": "same"},
                    validate_existing=reject_fabricated,
                )

    def test_generated_only_dirty_state_is_recorded_as_source_clean(self):
        normalised = normalise_git_state_for_run(
            {
                "commit": "abc",
                "dirty": True,
                "changed_paths": ["?? results/live/model.json.checkpoint"],
            },
            generated_only=True,
        )
        self.assertFalse(normalised["dirty"])
        self.assertTrue(normalised["generated_outputs_present"])

    def test_resume_allows_only_its_own_generated_paths_to_be_dirty(self):
        self.assertTrue(
            dirty_paths_are_only_run_outputs(
                [
                    "?? results/live/model.json.checkpoint",
                    "?? results/live/model-logs/CLM/log.jsonl",
                    "?? results/live/prior-model.json",
                    "?? results/live/prior-model-logs/CLM/log.jsonl",
                ],
                Path("results/live/model.json"),
            )
        )
        self.assertFalse(
            dirty_paths_are_only_run_outputs(
                [" M agent.py", "?? results/live/model.json.checkpoint"],
                Path("results/live/model.json"),
            )
        )


if __name__ == "__main__":
    unittest.main()
