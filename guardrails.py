"""
PE6201 · A2 scaffold — THE GUARDRAIL LAYER  (D3a)
====================================================================
Four things, and NONE of them involve a model. That is the point.

    1. STEP CAP            stop after N turns
    2. BUDGET CEILING      stop after N tokens
    3. ACTION DE-DUPLICATION   stop repeating an action already taken
    4. AUTONOMY GATE       hold the irreversible step for a human

A model cannot influence whether these fire, which is why D3(b)'s ten
guardrail cases run on the SCRIPTED backend. They test your code.

MAKE THE STOP LOUD. A cap that silently returns an empty answer is
worse than the loop it prevented: it turns a visible cost problem into
an invisible correctness problem. Every stop below records WHY.
====================================================================
"""


import json
import re


class GuardrailStop(Exception):
    """Raised when the code layer halts a run. Carries the reason so the
    decision record can say what stopped it and at which turn."""

    def __init__(self, reason, detail=""):
        self.reason = reason
        self.detail = detail
        super().__init__("%s: %s" % (reason, detail) if detail else reason)


class Guardrails:
    """One instance per run. Never share one between cases - a shared
    instance leaks state and D4 requires every case to start clean."""

    def __init__(self, max_turns, max_tokens, autonomy):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.autonomy = autonomy
        self.seen_actions = set()     # for de-duplication
        self.fired = []               # every guardrail event, for the record

    # ---- 1 · step cap -----------------------------------------------
    def check_turns(self, turn):
        if turn > self.max_turns:
            self._fire("step_cap", "reached %d turns" % self.max_turns)
            raise GuardrailStop("step_cap",
                                "hit the %d-turn cap without a conclusion"
                                % self.max_turns)

    # ---- 2 · budget ceiling -----------------------------------------
    def check_budget(self, tokens_so_far):
        if tokens_so_far > self.max_tokens:
            self._fire("budget_ceiling", "%d tokens" % tokens_so_far)
            raise GuardrailStop("budget_ceiling",
                                "spent %d tokens, ceiling is %d"
                                % (tokens_so_far, self.max_tokens))

    # ---- 3 · action de-duplication ----------------------------------
    def check_duplicate(self, tool, args):
        """A loop has no memory of its own actions unless you give it one.

        This IS that memory. Class 4's loop failure was exactly this
        guard deleted: 8 turns, no answer, 1.6x the cost, and NO
        exception raised. It did not crash. It burned money in a circle.
        """
        signature = (tool, json.dumps(args, sort_keys=True, separators=(",", ":")))
        if signature in self.seen_actions:
            self._fire("duplicate_action", "%s repeated" % tool)
            raise GuardrailStop("duplicate_action",
                                "%s called again with identical arguments "
                                "- the loop is not progressing" % tool)
        self.seen_actions.add(signature)

    # ---- 4 · hostile untrusted text ---------------------------------
    def inspect_untrusted_text(self, text):
        """Detect explicit instructions or forged tool output in member text.

        This is a deliberately narrow code guard, not a claim that prompt
        injection is solved. It catches the known attack families and records
        the matched indicator so the stop is auditable.
        """
        lowered = (text or "").lower()
        indicators = (
            "system note:",
            "ignore the exclusions",
            "ignore previous",
            "override the policy",
            "authorised by claims supervisor",
            "authorized by claims supervisor",
            "[check_coverage returned:",
            "tool result:",
            "assistant instruction:",
        )
        matches = [indicator for indicator in indicators if indicator in lowered]
        instruction_patterns = (
            r"\b(?:disregard|ignore|override)\b.{0,60}\b(?:previous|prior|system|policy|rule|instruction|exclusion)s?\b",
            r"\b(?:bypass|skip|disable)\b.{0,60}\b(?:gate|check|rule|policy|tool|review|confirmation)s?\b",
        )
        matches.extend(
            f"instruction-pattern:{pattern}"
            for pattern in instruction_patterns
            if re.search(pattern, lowered)
        )
        if matches:
            self._fire("hostile_input", "matched: %s" % ", ".join(matches))
        return matches

    # ---- 5 · autonomy gate ------------------------------------------
    def gate(self, action_name, payload, approve=None):
        """Called ONLY in front of the irreversible step.

        Note where this sits: in front of the ACTION, not in front of the
        agent. An agent gated as a whole is not an agent, it is a form.

        `approve` is a callable the harness supplies. On the scripted
        backend it auto-approves so the run is deterministic - and the
        record still shows the gate was passed, which is what a marker
        checks for.
        """
        if self.autonomy == "act":
            self._fire("gate_passed", "%s (autonomy=act)" % action_name)
            return True
        if self.autonomy == "suggest":
            self._fire("gate_held", "%s (autonomy=suggest)" % action_name)
            return False
        # confirm
        ok = bool(approve and approve(action_name, payload))
        self._fire("gate_%s" % ("passed" if ok else "held"),
                   "%s (autonomy=confirm)" % action_name)
        return ok

    # ---- bookkeeping ------------------------------------------------
    def _fire(self, kind, detail):
        self.fired.append({"guardrail": kind, "detail": detail})
