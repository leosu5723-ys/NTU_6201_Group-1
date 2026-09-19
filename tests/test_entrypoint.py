import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EntryPointTests(unittest.TestCase):
    def test_default_entry_point_reproduces_full_scripted_set(self):
        completed = subprocess.run(
            ["python3", "run_eval.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        payload = json.loads((ROOT / "results/scripted/results.json").read_text())
        self.assertEqual(payload["summary"]["trials"], 60)
        self.assertEqual(payload["summary"]["passed"], 60)
        self.assertEqual(payload["summary"]["backend"], "scripted")


if __name__ == "__main__":
    unittest.main()
