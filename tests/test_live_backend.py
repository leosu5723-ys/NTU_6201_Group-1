import unittest

import backends


class LiveBackendContractTests(unittest.TestCase):
    def test_live_backend_sends_case_id_and_preserves_measured_usage(self):
        captured = {}
        original = backends._live_call

        def fake_live_call(messages):
            captured["messages"] = messages
            return {
                "id": "req-test",
                "usage": {
                    "prompt_tokens": 321,
                    "completion_tokens": 45,
                    "cost": 0.0123,
                    "prompt_tokens_details": {"cached_tokens": 20},
                },
                "choices": [{"message": {"content": '{"thought":"fetch","calls":[["get_claim",{"claim_id":"CLM-8842"}]]}'}}],
                "_latency_seconds": 0.1,
            }

        backends._live_call = fake_live_call
        try:
            backend = backends.LiveBackend("CLM-8842", "system prompt")
            self.assertGreater(backend.estimated_next_input_tokens([]), 0)
            move = backend.next_move([])
        finally:
            backends._live_call = original

        self.assertIn("CLM-8842", captured["messages"][1]["content"])
        self.assertEqual(move["calls"][0][0], "get_claim")
        self.assertEqual(backend.last_usage["input_tokens"], 321)
        self.assertEqual(backend.last_usage["output_tokens"], 45)
        self.assertEqual(backend.last_usage["request_id"], "req-test")
        self.assertEqual(backend.last_usage["provider_cost_usd"], 0.0123)
        self.assertEqual(backend.last_usage["usage_details"]["prompt_tokens_details"]["cached_tokens"], 20)
        self.assertEqual(len(backend.raw_responses), 1)

    def test_live_request_sets_provider_side_output_limit(self):
        captured = {}
        original_urlopen = backends.urllib.request.urlopen
        original_key = backends.config.API_KEY

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"id":"req","choices":[{"message":{"content":"{}"}}],"usage":{}}'

        def fake_urlopen(request, timeout):
            captured.update(__import__("json").loads(request.data.decode("utf-8")))
            return Response()

        try:
            backends.config.API_KEY = "test-only"
            backends.urllib.request.urlopen = fake_urlopen
            backends._live_call([])
        finally:
            backends.urllib.request.urlopen = original_urlopen
            backends.config.API_KEY = original_key
        self.assertEqual(captured["max_tokens"], backends.config.MAX_OUTPUT_TOKENS)


if __name__ == "__main__":
    unittest.main()
