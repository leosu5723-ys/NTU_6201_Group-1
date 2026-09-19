"""Regression checks for the member-facing case allocation."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def sections(text):
    return {m.group(1): re.findall(r'^### (CLM-\d+)\s*$', m.group(2), re.M)
            for m in re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', text, re.M | re.S)}


class TeamReviewPackTests(unittest.TestCase):
    def test_worksheet_allocation_matches_all_authorities(self):
        members = json.loads((ROOT / 'review/case_author_signoff_template.json').read_text())['members']
        expected = {m['name']: m['case_ids'] for m in members}
        worksheet = (ROOT / 'review/CASE_WORKSHEETS.md').read_text()
        actual = sections(worksheet)
        self.assertEqual(actual, expected)
        ids = re.findall(r'^### (CLM-\d+)\s*$', worksheet, re.M)
        claims = json.loads((ROOT / 'A2_reference_data/data_A/claims.json').read_text())
        self.assertEqual(len(ids), 40)
        self.assertEqual(len(set(ids)), 40)
        self.assertEqual(set(ids), {c['claim_id'] for c in claims})
        assignment = (ROOT / 'review/case_review_assignments.md').read_text()
        table = {name: re.findall(r'CLM-\d+', cell) for name, cell in
                 re.findall(r'^\| ([^|]+) \| ([^|]+) \|$', assignment, re.M)
                 if name in expected}
        self.assertEqual(table, expected)
        guide = (ROOT / 'review/TEAM_ACTION_PACK.md').read_text()
        for member in members:
            name = member['name']
            match = re.search(r'^## ' + re.escape(name) + r'\n(.*?)(?=^## |\Z)', guide, re.M | re.S)
            assert match is not None, name
            block = match.group(1)
            cases = block.split('### Phase A cases')[1].split('### Phase B files')[0]
            self.assertEqual(re.findall(r'CLM-\d+', cases), expected[name])
            self.assertEqual([c['case_id'] for c in member['case_records']], expected[name])
            self.assertFalse(member['signed'])
            self.assertIsNone(member['date'])

    def test_blank_worksheet_matches_fixture_renderer(self):
        from build_case_worksheets import render
        text = (ROOT / 'review/CASE_WORKSHEETS.md').read_text()
        self.assertEqual(text, render())
        self.assertNotIn('OUTPUT ' + 'TRUNCATED', text)
        self.assertEqual(text.count('**Member response**'), 40)


if __name__ == '__main__':
    unittest.main()
