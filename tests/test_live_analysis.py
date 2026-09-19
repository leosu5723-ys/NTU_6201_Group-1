import copy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from harness import run_set, summarise
from live_battery import artifact_hashes, load_catalog
from live_analysis import analyse, case_balanced_metrics, validate_battery_set


class LiveAnalysisTests(unittest.TestCase):
    # Unit-test repository identity only. Never emitted as measured evidence.
    TEST_COMMIT = "1" * 40

    def setUp(self):
        boundary = patch(
            "live_analysis._artifact_hashes_at_commit",
            side_effect=lambda _commit, _version: artifact_hashes(_version),
        )
        boundary.start()
        self.addCleanup(boundary.stop)
        catalog_boundary = patch(
            "live_analysis._catalog_at_commit", return_value=load_catalog()
        )
        catalog_boundary.start()
        self.addCleanup(catalog_boundary.stop)

    def test_case_balanced_metrics_do_not_triple_weight_negative_cases(self):
        results = [
            {"case_id": "ordinary", "passed": True, "record": {"cost_usd": 1.0}},
            {"case_id": "negative", "passed": False, "record": {"cost_usd": 3.0}},
            {"case_id": "negative", "passed": False, "record": {"cost_usd": 3.0}},
            {"case_id": "negative", "passed": False, "record": {"cost_usd": 3.0}},
        ]
        metrics = case_balanced_metrics(results)
        self.assertEqual(metrics["success_rate"], 0.5)
        self.assertEqual(metrics["variable_cost_per_task"], 2.0)

    def _payload(self, model, prompt, commit="abc"):
        results, queue = run_set(
            problem="A", backend_name="scripted", prompt_version=prompt
        )
        results = copy.deepcopy(results)
        for row in results:
            record = row["record"]
            record["backend"] = "live"
            record["model"] = model
            record["prompt_version"] = prompt
            record["provider_cost_usd"] = record["catalog_cost_usd"]
            record["provider_cost_delta_usd"] = 0.0
        summary = summarise(results)
        return {
            "metadata": {
                "kind": "measured_battery",
                "model": model,
                "prompt_version": prompt,
                "git": {"commit": commit, "dirty": False},
                "artifact_hashes": {
                    **artifact_hashes(prompt),
                },
                "price": load_catalog()["models"][model],
            },
            "summary": summary,
            "results": results,
            "judgement_queue": queue,
        }

    def _valid_payloads(self):
        commit = self.TEST_COMMIT
        return [
            self._payload("google/gemini-2.5-flash-lite", "v2", commit),
            self._payload("qwen/qwen3-30b-a3b-instruct-2507", "v2", commit),
            self._payload("anthropic/claude-haiku-4.5", "v2", commit),
            self._payload("meta-llama/llama-4-maverick", "v2", commit),
            self._payload("deepseek/deepseek-v3.2", "v2", commit),
            self._payload("google/gemini-2.5-flash-lite", "v1", commit),
        ]

    def test_validation_rejects_summary_without_item_results(self):
        payloads = [
            self._payload("google/gemini-2.5-flash-lite", "v2"),
            self._payload("qwen/qwen3-30b-a3b-instruct-2507", "v2"),
            self._payload("anthropic/claude-haiku-4.5", "v2"),
            self._payload("meta-llama/llama-4-maverick", "v2"),
            self._payload("deepseek/deepseek-v3.2", "v2"),
            self._payload("google/gemini-2.5-flash-lite", "v1"),
        ]
        for payload in payloads:
            payload.pop("results")
        with self.assertRaisesRegex(ValueError, "item-level"):
            validate_battery_set(payloads)

    def test_validation_requires_five_v2_families_and_one_gemini_v1_same_commit(self):
        payloads = self._valid_payloads()
        commit = payloads[0]["metadata"]["git"]["commit"]
        result = validate_battery_set(payloads)
        self.assertEqual(result["commit"], commit)
        self.assertEqual(len(result["v2_models"]), 5)

    def test_validation_accepts_historical_recorded_commit_without_matching_current_head(self):
        payloads = self._valid_payloads()
        result = validate_battery_set(payloads)
        self.assertEqual(result["commit"], self.TEST_COMMIT)

    def test_validation_rejects_recorded_commit_when_its_committed_fixture_differs(self):
        payloads = self._valid_payloads()
        with patch(
            "live_analysis._artifact_hashes_at_commit",
            side_effect=lambda _commit, version: {**artifact_hashes(version), "claims": "0" * 64},
        ):
            with self.assertRaisesRegex(ValueError, "recorded commit"):
                validate_battery_set(payloads)

    def test_zero_turns_has_null_step_reliability_and_note(self):
        payloads = self._valid_payloads()
        for row in payloads[0]["results"]:
            row["record"]["turns"] = 0
        payloads[0]["summary"] = summarise(payloads[0]["results"])
        result = analyse(payloads)
        row = next(item for item in result["models"] if item["model"] == "google/gemini-2.5-flash-lite" and item["prompt_version"] == "v2")
        self.assertIsNone(row["implied_step_reliability"])
        self.assertIn("zero", row["implied_step_reliability_note"])

    def test_cli_accepts_an_explicit_historical_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, "live_analysis.py", "--directory", directory],
                cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True,
            )
        self.assertIn("No measured live batteries", completed.stderr + completed.stdout)

    def test_validation_rejects_duplicate_trial_rows(self):
        payloads = self._valid_payloads()
        payloads[0]["results"][-1] = copy.deepcopy(payloads[0]["results"][0])
        with self.assertRaisesRegex(ValueError, "trial matrix"):
            validate_battery_set(payloads)

    def test_validation_rejects_self_declared_summary_tampering(self):
        payloads = self._valid_payloads()
        payloads[0]["summary"]["pass_rate"] = 0.123
        with self.assertRaisesRegex(ValueError, "summary"):
            validate_battery_set(payloads)

    def test_validation_rejects_decision_receipt_tampering(self):
        payloads = self._valid_payloads()
        ordinary = next(
            row for row in payloads[0]["results"] if row["record"]["action_count"] == 1
        )
        ordinary["record"]["action_receipt"]["receipt_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "receipt"):
            validate_battery_set(payloads)

    def test_validation_rejects_commit_drift(self):
        payloads = self._valid_payloads()
        payloads[-1]["metadata"]["git"]["commit"] = "different"
        with self.assertRaisesRegex(ValueError, "same commit"):
            validate_battery_set(payloads)

    def test_validation_rejects_fixture_hash_drift(self):
        payloads = [
            self._payload("google/gemini-2.5-flash-lite", "v2"),
            self._payload("qwen/qwen3-30b-a3b-instruct-2507", "v2"),
            self._payload("anthropic/claude-haiku-4.5", "v2"),
            self._payload("meta-llama/llama-4-maverick", "v2"),
            self._payload("deepseek/deepseek-v3.2", "v2"),
            self._payload("google/gemini-2.5-flash-lite", "v1"),
        ]
        payloads[-1]["metadata"]["artifact_hashes"]["claims"] = "changed"
        with self.assertRaisesRegex(ValueError, "artifact hashes"):
            validate_battery_set(payloads)

    def test_validation_rejects_duplicate_or_extra_batteries(self):
        payloads = self._valid_payloads()
        payloads.append(copy.deepcopy(payloads[0]))
        with self.assertRaisesRegex(ValueError, "exactly six"):
            validate_battery_set(payloads)


if __name__ == "__main__":
    unittest.main()
