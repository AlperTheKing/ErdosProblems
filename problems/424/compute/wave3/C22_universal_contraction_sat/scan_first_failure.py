#!/usr/bin/env python3
"""Locate the first cutoff where closure alone violates two-scale contraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from universal_contraction_sat import solve_cutoff


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=4)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit-per-cutoff", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.workers <= 64:
        raise ValueError("workers must lie in [1,64]")
    if args.start < 4 or args.stop < args.start:
        raise ValueError("require 4 <= start <= stop")

    summary = {
        "schema_version": 1,
        "start": args.start,
        "stop": args.stop,
        "workers": args.workers,
        "tested": 0,
        "first_failure": None,
    }
    for limit in range(args.start, args.stop + 1):
        result = solve_cutoff(limit, args.workers, args.time_limit_per_cutoff)
        summary["tested"] += 1
        if result["status"] != "OPTIMAL":
            summary["incomplete"] = result
            break
        if result["objective_excess"] > 0:
            summary["first_failure"] = result
            break
        if limit % 100 == 0:
            print(f"checked through {limit}", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="ascii")
    failure = summary["first_failure"]
    print(
        "first_failure="
        + ("none" if failure is None else str(failure["limit"]))
        + f" tested={summary['tested']}"
    )


if __name__ == "__main__":
    main()
