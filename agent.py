"""Instrumented single-agent ReAct loop for Problem A."""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

import config
import prompt
import tools
from backends import make_backend
from guardrails import GuardrailStop, Guardrails

ApprovalCallback = Callable[[str, dict[str, Any]], bool]


def _validate_move(move: Any) -> None:
    if not isinstance(move, dict):
        raise ValueError("model move must be one JSON object")
    if set(move) - {"thought", "calls", "final"}:
        raise ValueError("model move contains unsupported top-level fields")
    has_calls = "calls" in move
    has_final = "final" in move
    if has_calls == has_final:
        raise ValueError("model move must contain exactly one of calls or final")
    if "thought" in move and not isinstance(move["thought"], str):
        raise ValueError("thought must be a string when present")
    if has_calls:
        _normalise_calls(move)
        return

    final = move["final"]
    if not isinstance(final, dict):
        raise ValueError("final must be an object")
    decision = final.get("decision")
    allowed_by_decision = {
        "approve_in_principle": {
            "decision", "reason", "approved_total", "refused_total", "line_dispositions"
        },
        "request_document": {"decision", "reason", "missing", "line_dispositions"},
        "escalate": {"decision", "reason", "trigger", "escalate_to"},
    }
    if decision not in allowed_by_decision:
        raise ValueError("final decision is not one of the three allowed outcomes")
    if set(final) - allowed_by_decision[decision]:
        raise ValueError("final contains fields that do not belong to its decision")
    if not isinstance(final.get("reason"), str) or not final["reason"].strip():
        raise ValueError("final reason must be a non-empty string")
    if decision == "approve_in_principle":
        if not all(isinstance(final.get(name), (int, float)) for name in ("approved_total", "refused_total")):
            raise ValueError("approval totals must be numeric")
        if not isinstance(final.get("line_dispositions"), list):
            raise ValueError("approval requires line_dispositions")
    elif decision == "request_document":
        if not isinstance(final.get("missing"), str) or not final["missing"].strip():
            raise ValueError("document request requires one named missing item")
        if not isinstance(final.get("line_dispositions"), list):
            raise ValueError("document request requires a line_dispositions list")
    else:
        if not isinstance(final.get("trigger"), str) or not final["trigger"].strip():
            raise ValueError("escalation requires one trigger")
        if final.get("escalate_to") != "human claims assessor":
            raise ValueError("escalation must route to a human claims assessor")


def _normalise_calls(move: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    raw = move.get("calls")
    if raw is None and "tool" in move:
        raw = [[move["tool"], move.get("args", {})]]
    if not isinstance(raw, list) or not raw:
        raise ValueError("a tool move must contain a non-empty calls list")
    calls: list[tuple[str, dict[str, Any]]] = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"invalid tool call: {item!r}")
        name, args = item
        if not isinstance(name, str) or not isinstance(args, dict):
            raise ValueError(f"invalid tool call: {item!r}")
        calls.append((name, args))
    return calls


def _fallback_log_path(case_id: str) -> Path:
    directory = Path(tempfile.mkdtemp(prefix="pe6201-a2-"))
    return directory / f"{case_id}.jsonl"


def _portable_log_reference(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return path.name


def _outcome_projection(payload: dict[str, Any], *, action: bool) -> dict[str, Any]:
    """Return business fields that must agree across the write and final output."""
    decision = payload.get("decision")
    projected: dict[str, Any] = {
        "decision": decision,
        "reason": payload.get("reason"),
    }
    if decision == "approve_in_principle":
        projected.update(
            {
                "approved_total": payload.get("approved_total"),
                "refused_total": payload.get("refused_total"),
                "line_dispositions": payload.get(
                    "lines" if action else "line_dispositions"
                ),
            }
        )
    elif decision == "request_document":
        projected.update(
            {
                "missing": payload.get("missing"),
                "line_dispositions": payload.get(
                    "lines" if action else "line_dispositions"
                ),
            }
        )
    elif decision == "escalate":
        projected.update(
            {
                "trigger": payload.get("trigger"),
                "escalate_to": payload.get("escalate_to"),
            }
        )
    return projected


def run_case(
    case_id: str,
    *,
    problem: str | None = None,
    approve: ApprovalCallback | None = None,
    verbose: bool = False,
    decision_log_path: str | Path | None = None,
    backend_name: str | None = None,
    prompt_version: str | None = None,
    scripted_scripts=None,
    backend_instance=None,
) -> dict[str, Any]:
    """Run one isolated case and return a fully instrumented decision record."""
    problem = problem or config.PROBLEM
    if problem != "A":
        raise ValueError("This submission implements Problem A only")
    selected_backend = backend_name or config.BACKEND
    prompt_version = prompt_version or getattr(config, "PROMPT_VERSION", "v2")
    system_prompt = prompt.build_system_prompt(problem, version=prompt_version)
    backend = backend_instance or make_backend(
        case_id,
        system_prompt=system_prompt,
        backend_name=selected_backend,
        scripted_scripts=scripted_scripts,
    )
    selected_backend = backend.name
    guards = Guardrails(config.MAX_TURNS, config.MAX_TOKENS_PER_RUN, config.AUTONOMY)
    if approve is None:
        approve = (lambda _name, _payload: selected_backend == "scripted")

    log_path = Path(decision_log_path) if decision_log_path else _fallback_log_path(case_id)
    transcript: list[dict[str, Any]] = []
    evidence: list[str] = []
    trusted_evidence_trace: list[dict[str, Any]] = []
    observation_metrics: list[dict[str, Any]] = []
    request_ids: list[str] = []
    turns = 0
    tokens_in = 0
    tokens_out = 0
    provider_cost_total = 0.0
    provider_cost_seen = False
    provider_usage: list[dict[str, Any]] = []
    http_attempts: list[int] = []
    action_count = 0
    action_payload: dict[str, Any] | None = None
    action_receipt: dict[str, Any] | None = None
    persisted_decision: dict[str, Any] | None = None
    stopped_by: str | None = None
    started = time.perf_counter()
    record: dict[str, Any] | None = None

    try:
        while record is None:
            estimator = getattr(backend, "estimated_next_input_tokens", None)
            if callable(estimator):
                estimated_input: Any = estimator(transcript)
                projected_tokens = (
                    tokens_in
                    + tokens_out
                    + int(estimated_input)
                    + config.MAX_OUTPUT_TOKENS
                )
                guards.check_budget(projected_tokens)
            move = backend.next_move(transcript)
            usage = backend.last_usage
            tokens_in += int(usage.get("input_tokens", 0))
            tokens_out += int(usage.get("output_tokens", 0))
            if usage.get("provider_cost_usd") is not None:
                provider_cost_total += float(usage["provider_cost_usd"])
                provider_cost_seen = True
            if usage.get("usage_details"):
                provider_usage.append(dict(usage["usage_details"]))
            if usage.get("http_attempts") is not None:
                http_attempts.append(int(usage["http_attempts"]))
            if usage.get("request_id"):
                request_ids.append(str(usage["request_id"]))
            guards.check_budget(tokens_in + tokens_out)
            _validate_move(move)

            if "final" in move:
                record = dict(move["final"])
                break

            turns += 1
            guards.check_turns(turns)
            calls = _normalise_calls(move)
            observations: list[dict[str, Any]] = []

            for name, args in calls:
                guards.check_duplicate(name, args)
                gate_record: dict[str, Any] = {}
                if name == tools.GATED_ACTION[problem]:
                    approved = guards.gate(name, args, approve)
                    gate_record = {
                        "autonomy": config.AUTONOMY,
                        "approved": approved,
                        "turn": turns,
                    }
                    if not approved:
                        raise GuardrailStop(
                            "gate_held",
                            f"{name} awaits operator confirmation",
                        )

                result = tools.call(
                    problem,
                    name,
                    args,
                    internal={
                        "evidence": evidence + [name],
                        "evidence_trace": trusted_evidence_trace,
                        "gate": gate_record,
                        "log_path": log_path,
                        "timestamp": "2026-09-09T00:00:00Z" if selected_backend == "scripted" else None,
                        "telemetry": {
                            "turns": turns + 1,
                            "tokens_in": tokens_in,
                            "tokens_out": tokens_out,
                            "cost_usd": round(
                                provider_cost_total
                                if provider_cost_seen
                                else (tokens_in / 1_000_000) * config.PRICE_IN
                                + (tokens_out / 1_000_000) * config.PRICE_OUT,
                                8,
                            ),
                        },
                        "interface_version": prompt_version,
                    },
                )
                evidence.append(name)
                trusted_evidence_trace.append(
                    {"tool": name, "args": dict(args), "observation": result}
                )
                observation_text = json.dumps(result, sort_keys=True, default=str)
                observation_metrics.append(
                    {
                        "turn": turns,
                        "tool": name,
                        "characters": len(observation_text),
                        "tokens_estimate_chars_div_4": len(observation_text) // 4,
                    }
                )
                if name == tools.GATED_ACTION[problem]:
                    action_count += 1
                    action_payload = dict(args)
                    action_receipt = dict(result)
                    persisted_decision = dict(result["record"])
                observations.append({"tool": name, "args": args, "observation": result})

                if name == "get_claim" and result:
                    hostile = guards.inspect_untrusted_text(result.get("narrative", ""))
                    if hostile:
                        record = {
                            "decision": "escalate",
                            "trigger": "instruction_in_member_narrative",
                            "escalate_to": "human claims assessor",
                            "reason": "Member-supplied narrative contained instruction-like text and was treated as untrusted data.",
                        }
                        break

            transcript.append({"role": "assistant", "content": json.dumps(move)})
            transcript.append({"role": "user", "content": json.dumps(observations)})
            if verbose:
                print(f"turn {turns}: {len(calls)} call(s): {', '.join(name for name, _ in calls)}")

    except (
        GuardrailStop,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
        OSError,
        IndexError,
        AttributeError,
    ) as error:
        if isinstance(error, GuardrailStop):
            stopped_by = error.reason
            trigger = error.reason
        elif isinstance(error, (RuntimeError, OSError, IndexError, AttributeError)):
            stopped_by = "backend_error"
            trigger = "backend_error"
        else:
            stopped_by = "tool_or_schema_error"
            trigger = "tool_or_schema_error"
        record = {
            "decision": "escalate",
            "trigger": trigger,
            "escalate_to": "human claims assessor",
            "reason": f"Run halted loudly: {error}",
        }

    assert record is not None
    hostile_stop = record.get("trigger") == "instruction_in_member_narrative"
    if stopped_by is None and not hostile_stop and action_count != 1:
        record = {
            "decision": "escalate",
            "trigger": "action_integrity_error",
            "escalate_to": "human claims assessor",
            "reason": f"First response concluded with action_count={action_count}; exactly one recorded decision is required.",
        }
        stopped_by = "action_integrity_error"
    if hostile_stop and action_count:
        record = {
            "decision": "escalate",
            "trigger": "action_integrity_error",
            "escalate_to": "human claims assessor",
            "reason": "A hostile-input path attempted the gated action.",
        }
        stopped_by = "action_integrity_error"
    if (
        stopped_by is None
        and action_payload is not None
        and _outcome_projection(record, action=False)
        != _outcome_projection(persisted_decision or action_payload, action=True)
    ):
        record = {
            "decision": "escalate",
            "trigger": "action_integrity_error",
            "escalate_to": "human claims assessor",
            "reason": "The model's final outcome did not match the gated decision record.",
        }
        stopped_by = "action_integrity_error"

    catalog_cost = (tokens_in / 1_000_000) * config.PRICE_IN + (
        tokens_out / 1_000_000
    ) * config.PRICE_OUT
    cost = provider_cost_total if provider_cost_seen else catalog_cost
    record.update(
        {
            "case_id": case_id,
            "evidence": evidence,
            "turns": turns,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": round(cost, 8),
            "catalog_cost_usd": round(catalog_cost, 8),
            "provider_cost_usd": round(provider_cost_total, 8) if provider_cost_seen else None,
            "provider_cost_delta_usd": (
                round(provider_cost_total - catalog_cost, 8) if provider_cost_seen else None
            ),
            "provider_usage": provider_usage,
            "http_attempts": http_attempts,
            "seconds": (
                0.0
                if selected_backend == "scripted"
                else round(time.perf_counter() - started, 6)
            ),
            "guardrails_fired": guards.fired,
            "stopped_by": stopped_by,
            "backend": selected_backend,
            "model": config.MODEL if selected_backend == "live" else None,
            "prompt_version": prompt_version,
            "action_count": action_count,
            "action_receipt": action_receipt,
            "persisted_decision": persisted_decision,
            "request_ids": request_ids,
            "decision_log": _portable_log_reference(log_path) if action_count else None,
            "observation_metrics": observation_metrics,
            "observation_tokens_estimate": sum(
                item["tokens_estimate_chars_div_4"] for item in observation_metrics
            ),
        }
    )
    if hasattr(backend, "raw_responses"):
        record["raw_responses"] = backend.raw_responses
    return record
