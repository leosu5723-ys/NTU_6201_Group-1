import unittest

import backends


class ScriptedBackendInventoryTests(unittest.TestCase):
    def test_committed_script_inventory_covers_all_40_cases(self):
        self.assertEqual(len(backends.SCRIPTS), 40)
        self.assertIn("CLM-8842", backends.SCRIPTS)
        self.assertIn("CLM-9025", backends.SCRIPTS)


if __name__ == "__main__":
    unittest.main()
