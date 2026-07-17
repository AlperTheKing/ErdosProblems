#!/usr/bin/env python3
"""Exact finite audit of the C73 hard-tail inclusions."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_c67():
    path = HERE / "C67_weak_scb.py"
    spec = importlib.util.spec_from_file_location("c73_c67", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(max_limit: int) -> dict:
    c67 = load_c67()
    data = c67.build_arithmetic(max_limit)
    hard = data["hard"]
    holes = data["holes"]

    first_failure = None
    maximum_lower_slack = 0
    maximum_upper_slack = 0
    for limit in range(2, max_limit + 1):
        half = (limit + 1) // 2
        hard_count = sum(r <= limit for r in hard)
        hard_half = sum(r <= half for r in hard)
        active = 0
        for root in hard:
            if root > limit:
                continue
            top = root
            while 2 * top - 1 <= limit:
                top = 2 * top - 1
            active += int(top in holes)

        lower = hard_count - hard_half
        if not lower <= active <= hard_count:
            first_failure = {
                "limit": limit,
                "lower": lower,
                "active": active,
                "hard": hard_count,
            }
            break
        maximum_lower_slack = max(maximum_lower_slack, active - lower)
        maximum_upper_slack = max(maximum_upper_slack, hard_count - active)

    return {
        "max_limit": max_limit,
        "checked_cutoffs": max_limit - 1,
        "first_failure": first_failure,
        "maximum_lower_slack": maximum_lower_slack,
        "maximum_upper_slack": maximum_upper_slack,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-limit", type=int, default=5000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.max_limit)
    if result["first_failure"] is not None:
        raise AssertionError(result["first_failure"])
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="ascii")
    print(text)


if __name__ == "__main__":
    main()
