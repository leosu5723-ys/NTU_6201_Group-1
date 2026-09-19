import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PrivacyAndPortabilityTests(unittest.TestCase):
    def test_saved_evidence_contains_no_private_absolute_paths_or_secrets(self):
        targets = [ROOT / "artifacts", ROOT / "results", ROOT / "report", ROOT / "docs"]
        forbidden = [str(Path.home()), "/var" + "/folders/", "sk" + "-or-"]
        failures = []
        for directory in targets:
            if not directory.exists():
                continue
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix in {".json", ".md", ".txt", ".jsonl"}:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    for token in forbidden:
                        if token in text:
                            failures.append(f"{path.relative_to(ROOT)} contains {token}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
