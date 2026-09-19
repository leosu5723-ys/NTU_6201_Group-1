# Live Battery Instructions

Each measured battery must use the same clean git commit, the same 40-case answer key, the same v2 prompt and one model string as the only changed variable. The Gemini v1 comparison uses the same model as the Gemini v2 run and changes only `--prompt-version`.

## Before any paid run

1. Pull the frozen commit selected by the team.
2. Run `python3 -m unittest discover -s tests -v`.
3. Run `python3 A2_reference_data/check_my_data.py`.
4. Run `python3 run_eval.py` and confirm 60 of 60 scripted trials pass.
5. Check that `git status --porcelain` prints nothing.
6. Check the current model ID and prices against OpenRouter. Update `config/model_catalog.json` only before the freeze, never during the battery.
7. Export the personal API key in the shell. Never paste it into Python, a notebook, the repository or a screenshot.
8. Record how much of the member's US$3 A2 allowance and US$25 calendar-month allowance has already been spent. Pass both values with `--spent-to-date` and `--monthly-spent-to-date`; the runner refuses a plan that would exceed either cap.

## Dry-run preflight

Replace the model with the assigned ID:

```bash
python3 live_battery.py --model MODEL_ID --prompt-version v2
```

This performs no network calls and spends no credit.

## Optional labelled smoke test

A smoke test is not part of measured results:

```bash
export OPENROUTER_API_KEY='...'
python3 live_battery.py \
  --model MODEL_ID \
  --prompt-version v2 \
  --smoke CLM-8850 \
  --allow-dirty \
  --spent-to-date 0.00 \
  --monthly-spent-to-date 0.00 \
  --execute \
  --output results/smoke/MODEL_NAME.json
```

Do not merge a smoke output into a battery file.

## Final v2 battery commands

```bash
export OPENROUTER_API_KEY='...'
python3 live_battery.py --model google/gemini-2.5-flash-lite --prompt-version v2 --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
python3 live_battery.py --model qwen/qwen3-30b-a3b-instruct-2507 --prompt-version v2 --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
python3 live_battery.py --model anthropic/claude-haiku-4.5 --prompt-version v2 --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
python3 live_battery.py --model meta-llama/llama-4-maverick --prompt-version v2 --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
python3 live_battery.py --model deepseek/deepseek-v3.2 --prompt-version v2 --spent-to-date 0.00 --monthly-spent-to-date 0.00 --execute
```

Each member runs only the assigned command on their own key.
Replace both `0.00` values with the member's real prior A2 and calendar-month spend.

## Gemini v1 comparison

```bash
export OPENROUTER_API_KEY='...'
python3 live_battery.py \
  --model google/gemini-2.5-flash-lite \
  --prompt-version v1 \
  --spent-to-date 0.00 \
  --monthly-spent-to-date 0.00 \
  --execute
```

The Gemini v2 result from the main battery is the comparison partner. Do not rerun or modify it to make the comparison look cleaner.

## Files to return

Return the generated JSON file under `results/live/`. It contains:

- Frozen git state
- Model and prompt version
- Per-trial decision and failures
- Raw API response payloads
- Request IDs
- Input and output token counts
- Latency and cost
- Code-check results
- Human judgement queue

The key itself is never stored. A paid result is atomically checkpointed after every trial. Re-running the identical command resumes only unfinished `(case_id, trial)` pairs; a checkpoint with a different commit, prompt or data hash is rejected.

If a request fails, keep the failure record. Do not silently delete it or rerun only failed cases without documenting the retry policy. Contact the integration owner before changing code, prompt, model, cases or provider routing.
