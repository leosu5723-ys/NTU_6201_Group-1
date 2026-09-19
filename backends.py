"""Scripted and live backends behind one vendor-neutral interface."""
from __future__ import annotations

import copy
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import config


SCRIPT_PATH = Path(__file__).resolve().parent / "fixtures" / "scripted_trajectories_A.json"


def _load_committed_scripts() -> dict[str, list[dict[str, Any]]]:
    if not SCRIPT_PATH.exists():
        raise RuntimeError(
            "Missing fixtures/scripted_trajectories_A.json; run python3 script_builder.py"
        )
    return json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))


SCRIPTS = _load_committed_scripts()


class ScriptedBackend:
    name = "scripted"

    def __init__(self, case_id: str, system_prompt: str = "", scripts=None) -> None:
        inventory = scripts or SCRIPTS
        if case_id not in inventory:
            raise KeyError(f"No scripted trajectory for {case_id}")
        self.case_id = case_id
        self.steps = inventory[case_id]
        self.index = 0
        self.system_prompt = system_prompt
        self.last_usage = {"input_tokens": 0, "output_tokens": 0, "request_id": None}

    def next_move(self, transcript: list[dict[str, Any]]) -> dict[str, Any]:
        if self.index >= len(self.steps):
            move = {
                "thought": "The scripted trajectory ended without a conclusion.",
                "final": {
                    "decision": "escalate",
                    "trigger": "script_exhausted",
                    "reason": "No scripted conclusion was available.",
                },
            }
        else:
            move = copy.deepcopy(self.steps[self.index])
            self.index += 1
        history_chars = sum(len(str(item)) for item in transcript)
        input_tokens = max(1, (len(self.system_prompt) + history_chars) // 4)
        output_tokens = max(1, len(json.dumps(move)) // 4)
        self.last_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "request_id": f"scripted:{self.case_id}:{self.index}",
        }
        return move


class LiveBackend:
    name = "live"

    def __init__(self, case_id: str, system_prompt: str) -> None:
        self.case_id = case_id
        self.system_prompt = system_prompt
        self.last_usage = {"input_tokens": 0, "output_tokens": 0, "request_id": None}
        self.raw_responses: list[dict[str, Any]] = []

    def _messages(self, transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Process claim_id {self.case_id}. Begin by retrieving the claim."},
            *transcript,
        ]

    def estimated_next_input_tokens(self, transcript: list[dict[str, Any]]) -> int:
        return max(
            1,
            len(json.dumps(self._messages(transcript), ensure_ascii=False)) // 4,
        )

    def next_move(self, transcript: list[dict[str, Any]]) -> dict[str, Any]:
        messages = self._messages(transcript)
        payload = _live_call(messages)
        self.raw_responses.append(payload)
        usage = payload.get("usage") or {}
        self.last_usage = {
            "input_tokens": int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
            "output_tokens": int(usage.get("completion_tokens") or usage.get("output_tokens") or 0),
            "request_id": payload.get("id"),
            "provider_cost_usd": (
                float(usage["cost"]) if usage.get("cost") is not None else None
            ),
            "usage_details": dict(usage),
            "http_attempts": int(payload.get("_http_attempts", 1)),
        }
        content = payload["choices"][0]["message"].get("content") or ""
        return _parse_move(content)


def _parse_move(text: str) -> dict[str, Any]:
    fenced = re.fullmatch(r"```(?:json)?[ \t]*\r?\n(.*?)\r?\n```[ \t]*", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        move = json.loads(text)
    except json.JSONDecodeError as error:
        return {
            "thought": f"Unparseable model response: {text[:160]}",
            "parse_error": f"Model output was not valid JSON: {error.msg}",
        }
    if not isinstance(move, dict) or not ({"calls", "final"} & set(move)):
        return {
            "thought": "Model response had no calls or final object.",
            "parse_error": "Model response did not match the move schema.",
        }
    return move


def _live_call(messages: list[dict[str, Any]]) -> dict[str, Any]:
    if not config.API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is required only for BACKEND=live")
    body = json.dumps(
        {
            "model": config.MODEL,
            "messages": messages,
            "temperature": 0,
            "max_tokens": config.MAX_OUTPUT_TOKENS,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        config.BASE_URL.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": "Bearer " + config.API_KEY,
            "Content-Type": "application/json",
            "HTTP-Referer": getattr(config, "PROJECT_URL", "https://github.com/leosu5723-ys/NTU_6201_Group-1"),
            "X-Title": "PE6201 A2 Group B-1",
        },
    )
    started = time.perf_counter()
    retryable = {429, 500, 502, 503, 504}
    last_error = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.load(response)
            payload["_latency_seconds"] = round(time.perf_counter() - started, 6)
            payload["_http_attempts"] = attempt
            return payload
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenRouter HTTP {error.code}: {detail[:500]}")
            if error.code not in retryable or attempt == 3:
                raise last_error from error
        except urllib.error.URLError as error:
            last_error = RuntimeError(f"OpenRouter network error: {error.reason}")
            if attempt == 3:
                raise last_error from error
        time.sleep(2 ** (attempt - 1))
    raise last_error or RuntimeError("OpenRouter request failed")


def make_backend(
    case_id: str,
    *,
    system_prompt: str,
    backend_name: str | None = None,
    scripted_scripts=None,
) -> ScriptedBackend | LiveBackend:
    selected = backend_name or config.BACKEND
    if selected == "scripted":
        return ScriptedBackend(case_id, system_prompt, scripts=scripted_scripts)
    if selected == "live":
        return LiveBackend(case_id, system_prompt)
    raise ValueError(f"Unknown backend: {selected}")
