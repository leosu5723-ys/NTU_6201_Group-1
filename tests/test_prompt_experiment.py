import unittest

from prompt_experiment import build_prompt_artifact


class PromptExperimentTests(unittest.TestCase):
    def test_rejected_nine_tool_block_is_measured_against_selected_seven(self):
        cut = build_prompt_artifact()["tool_block_cut"]
        self.assertEqual(cut["before"]["tool_count"], 9)
        self.assertEqual(cut["after"]["tool_count"], 7)
        self.assertGreater(cut["estimated_tokens_saved_chars_div_4"], 0)


if __name__ == "__main__":
    unittest.main()
