"""Class 4 reliability diagnostic."""


def implied_step_reliability(run_pass_rate: float, median_turns: float) -> float:
    if not 0 <= run_pass_rate <= 1:
        raise ValueError("run_pass_rate must be between 0 and 1")
    if median_turns <= 0:
        raise ValueError("median_turns must be positive")
    return run_pass_rate ** (1.0 / median_turns)


def projected_run_success(step_reliability: float, turns: float) -> float:
    if not 0 <= step_reliability <= 1:
        raise ValueError("step_reliability must be between 0 and 1")
    if turns <= 0:
        raise ValueError("turns must be positive")
    return step_reliability ** turns
