# Pull, run, and push — step by step

**Frozen experiment commit: the current tip of `main`**
**Repository: https://github.com/leosu5723-ys/NTU_6201_Group-1**

Two separate things, do not mix them up:

- **Pull** — needed so you can run your battery on the frozen version.
- **Push** — needed so the commit history shows your own work. Without it, there is no trace of your contribution.

Everyone pushes to **their own branch**. Nobody pushes to `main`. That is what keeps six people from colliding.

---

## Step 0 · Tell Git who you are (do this before anything else)

GitHub decides who a commit belongs to by matching the **commit author email** against the emails registered on a GitHub account. If you commit with an email that is not on your account, your commits show up as unlinked and **you will not appear in the repository's contributor list**, even though your name is in the log.

Set your identity once, in this repository:

```bash
git config user.name "Your Name"
git config user.email "YOUR_GITHUB_EMAIL"
```

Use the email registered on your own GitHub account. If you would rather not publish your real address, use your GitHub noreply address instead — find it under GitHub → Settings → Emails → "Keep my email addresses private".

Check it worked:

```bash
git config user.email
```

If you have already made commits with the wrong email, you can still add that email to your GitHub account (Settings → Emails → Add email address, then verify) and GitHub will link the existing commits to you. That is easier and safer than rewriting history.

## Step 1 · Get the code

First time:

```bash
git clone https://github.com/leosu5723-ys/NTU_6201_Group-1.git
cd NTU_6201_Group-1
```

Then create your own branch from the frozen commit:

```bash
git checkout -b member/YOUR_NAME main
```

If you already cloned the repository:

```bash
cd NTU_6201_Group-1
git fetch --all
git checkout -b member/YOUR_NAME main
```

Replace `YOUR_NAME` with your name in lowercase, for example `member/meng-sijia`.

## Step 2 · Check that it runs

```bash
python3 -m unittest discover -s tests -q   # expect: OK (101 tests)
python3 A2_reference_data/check_my_data.py # expect: Your data hangs together.
python3 run_eval.py                        # expect: "passed": 60
git status --porcelain                     # expect: nothing
```

If any of these fail, stop and tell SHI SHUYI. Do not run the paid battery on a broken checkout.

## Step 3 · Dry run (free, no network, no cost)

Replace the model with yours:

```bash
python3 live_battery.py --model YOUR_MODEL_ID --prompt-version v2
```

Zhang Jiayang uses `--prompt-version v1`.

## Step 4 · Run the real battery

```bash
export OPENROUTER_API_KEY='your-own-key'
python3 live_battery.py --model YOUR_MODEL_ID --prompt-version v2 \
  --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
```

Replace both `0.00` values with your real prior spending if you have already used your key this month.

- Never put your key in a file, a commit, a screenshot or the group.
- Do not edit the result JSON.
- Do not delete failing trials.
- If the run is interrupted, run the same command again — it resumes only the unfinished trials.

Your result appears under `results/live/`.

## Step 5 · Push your work

Put your own materials in the repository as well, so your contribution is visible in the history:

```bash
mkdir -p review/member_work
# copy your Phase A document and your Phase B strand review into review/member_work/
git add review/member_work results/live
git commit -m "Meng Sijia: Phase A cases, Phase B strand review and Gemini v2 battery"
git push -u origin member/YOUR_NAME
```

Then tell SHI SHUYI your branch name.

**If the push is rejected** because you do not have write access, do not fight it — send the result JSON and your documents to SHI SHUYI directly and say so. The work still counts; it just cannot be traced through your own commit.

## Step 6 · Report back

Send these four answers with your result:

```
Model and prompt version:
Observed pass rate:
Most important failure or surprising behaviour:
Was the quality worth the measured cost? Why?
Name and date:
```

---

## Summary

| Step | Command | Why |
|---|---|---|
| 1 | `git checkout -b member/YOUR_NAME main` | get the frozen version on your own branch |
| 2 | `python3 -m unittest discover -s tests -q` | confirm the checkout works |
| 3 | `python3 live_battery.py --model ID --prompt-version v2` | free dry run |
| 4 | the same command with `--execute` and your key | the real measurement |
| 5 | `git push -u origin member/YOUR_NAME` | leave your contribution traceable |
| 6 | send the four answers | feed the report and the video |
