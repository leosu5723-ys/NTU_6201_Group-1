# Merge the six member branches

For SHI SHUYI, at the end, once all six batteries are in. Do this on GitHub or in the terminal — either works.

## Why this step matters

GitHub counts contributors from the **default branch** (`main`). Until each member's branch is merged, their commits exist but they do **not** appear in the repository's contributor list. The brief says the commit history must corroborate `CONTRIBUTIONS.md`, and that is exactly what the marker looks at. **Do not skip this.**

## Before you start

```bash
cd /Users/kyle/Projects/NTU/PE6201-A2-Group-B1
git fetch --all
git ls-remote --heads origin        # list every branch the team has pushed
```

Expect six: `member/meng-sijia`, `member/shi-shuyi`, `member/su-yang`, `member/isha-kirti-ghia`, `member/sun-hanyu`, `member/zhang-jiayang`.

## The easy way — GitHub web

For each branch:

1. Open `https://github.com/leosu5723-ys/NTU_6201_Group-1/branches`
2. Click **Compare & pull request** next to the branch
3. Base = `main`, compare = the member branch
4. **Create pull request** → **Merge pull request** → **Confirm merge**

Six times. The files do not overlap (each member adds `review/member_work/<name>.md` and `results/live/<model>.json`), so none of them should conflict.

## The terminal way

```bash
git checkout main
git pull

for b in meng-sijia su-yang isha-kirti-ghia sun-hanyu zhang-jiayang; do
  git merge --no-ff "origin/member/$b" -m "Merge member/$b"
done
git merge --no-ff origin/member/shi-shuyi -m "Merge member/shi-shuyi"

# Push. The -c option belongs BEFORE the subcommand: `git -c ... push`, never `git push -c ...`
# (the wrong order fails with a usage error and nothing is pushed).
git -c credential.helper='!gh auth git-credential' push origin main
# A plain `git push origin main` also works on this machine; the keychain helper is already configured.
```

If a merge conflicts, stop and look at which file collided before resolving anything. With six independent `member_work` files and six differently-named JSON results, a conflict would mean two people edited the same shared file — worth understanding before you force anything.

**The one shared file to watch:** `review/judgement_verdicts.json`. Six reviewers write into it, so if each member fills their own two rows on their own branch, every merge collides. The intended flow is that reviewers return their verdict, name and evidence to the group and SHI SHUYI fills the single file on `main` after the merge. Confirm that is what happened before merging, and if two branches do touch it, take both rows rather than one side's file.

## Verify afterwards

```bash
# 1. every contributor now appears
gh api repos/leosu5723-ys/NTU_6201_Group-1/contributors --jq '.[] | "\(.login): \(.contributions)"'

# 2. all six result files are on main
git ls-tree --name-only origin/main results/live/

# 3. all six batteries agree on the commit they ran
python3 -c "
import json, glob
for f in sorted(glob.glob('results/live/*.json')):
    d = json.load(open(f))
    m = d.get('metadata', {})
    print(f.split('/')[-1][:55], '|', m.get('git', {}).get('commit', '?')[:12], '| dirty:', m.get('git', {}).get('dirty'))
"

# 4. all six ran the same prompt version contract
python3 -c "
import json, glob
for f in sorted(glob.glob('results/live/*.json')):
    d = json.load(open(f))
    m = d.get('metadata', {})
    print(f.split('/')[-1][:55], '|', m.get('prompt_version'), '|', m.get('model'))
"
```

**All six recorded commits must be identical.** That is the requirement the brief calls out: *"same commit, same v2 prompt, MODEL the only string that differs."* If one differs, that member ran at the wrong time — their battery has to be rerun, not edited.

## After the merge

- `python3 verify_submission.py` and confirm what it reports.
- Run the official validation over the six batteries: `python3 live_analysis.py` (or the documented entry point) — this is where a mismatched commit, a duplicated battery or a tampered summary gets rejected.
- Only then fill the report's live numbers.

## If a member never pushes

Do not invent their commit. Record what actually happened in `CONTRIBUTIONS.md` and in the self-appraisal. A missing branch is a fact about the team's process, and the brief is explicit that the contribution record must be true.
