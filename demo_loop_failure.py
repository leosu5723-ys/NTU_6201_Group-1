#!/usr/bin/env python3
"""Convenience entry point for the required D7 loop-control failure."""
import json

from failure_experiments import run_failure_experiments


if __name__ == "__main__":
    print(json.dumps(run_failure_experiments()["loop_control"], indent=2))
