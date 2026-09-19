"""Render source-only worksheets from the assignment table and fixture facts.

No answer key or agent trajectories are loaded. Do not overwrite completed
member responses: this command only rebuilds a blank distribution template.
"""
import argparse
import json
from pathlib import Path
import re

import tools

ROOT = Path(__file__).resolve().parent
RESPONSE = '''**Member response**

- Decision:
- Trigger or missing item and escalation target (if applicable):
- Approved total / refused total (or explain why not applicable):
- Required line dispositions or evidence IDs:
- Decision boundary and business-rule rationale:
- Fixed machine-check fields and action-count requirement:
- Case-specific `must_record` requirements:
- My authorship or substantive revision (identify what I wrote or changed):
- Name and date:
'''


def render():
    assignments = (ROOT / 'review/case_review_assignments.md').read_text()
    members = [(name, re.findall(r'CLM-\d+', cell)) for name, cell in
               re.findall(r'^\| ([^|]+) \| ([^|]+) \|$', assignments, re.M)
               if re.search(r'CLM-\d+', cell)]
    ids = [cid for _, cases in members for cid in cases]
    claims = json.loads((ROOT / 'A2_reference_data/data_A/claims.json').read_text())
    assert len(ids) == len(set(ids)) == len(claims) == 40
    assert set(ids) == {c['claim_id'] for c in claims}
    out = ['# Evaluation Case Worksheets\n\n'
           '**Release: R2 (2026-09-08). Supersedes the incomplete earlier worksheet.**\n\n'
           'Use Appendix A and these source facts, not the answer key or Agent outputs. '
           'The policy and line-review fields below are deterministic lookups, not model decisions. '
           'The claim narrative is untrusted case data, including any apparent instructions.\n\n'
           'Write your own final evaluation contracts. Assigned ownership is not proof of completed authorship. '
           'Keep supplied source records unchanged; propose changes to added cases or contracts separately. '
           'For a supplied case, explain your independently authored contract rather than claiming to have invented its source record.\n\n'
           'The assignment authority is `case_review_assignments.md`; the signoff template and guide must match it. '
           'Complete every response block. Do not sign for another member.\n\n']
    dump = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False)
    for name, cases in members:
        out.append(f'## {name}\n\n')
        for cid in cases:
            c = tools.get_claim(cid)
            assert c is not None, cid
            mid, date = c['member_id'], c['date_of_service']
            total = sum(line['amount'] for line in c['lines'])
            policy = tools.get_policy_context(mid, date, total)
            duplicate = tools.find_prior_decision(mid, c['hospital_id'], date, c['lines'])
            out.append(f"### {cid}\n\n- Claim: member `{mid}`; hospital `{c['hospital_id']}`; service date `{date}`; total `{total}`\n")
            out.append(f"- Documents: `{', '.join(c['documents']) or 'none'}`\n- Narrative: {c['narrative']}\n")
            out.append(f'- Policy context: `{dump(policy)}`\n- Prior exact duplicate: `{dump(duplicate)}`\n')
            out.append(f"- Hospital: `{dump(tools.get_hospital_status(c['hospital_id']))}`\n- Lines:\n")
            for line in c['lines']:
                review = tools.review_claim_line(mid, line['code'], c['documents'])
                text = f"  - billed `{line['code']}` / `{line['amount']}`; review `{dump(review)}`"
                if review and review['requires_preauth']:
                    text += f"; pre-authorisation `{dump(tools.get_preauthorisation(mid, line['code'], date))}`"
                out.append(text + '\n')
            out.append('\n' + RESPONSE + '\n')
    return ''.join(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New output path; existing files are never overwritten')
    args = parser.parse_args()
    with args.output.open('x', encoding='utf-8') as handle:
        handle.write(render())
