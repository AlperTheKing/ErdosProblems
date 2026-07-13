#!/usr/bin/env python3
"""Exhaust reflected pair-deletion subsets of the strongest P20 seed."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from reflected_neighborhood import DEFAULT_SEED, coefficient, metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=int, default=583)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p33/reflected_subsets_e583.json"),
    )
    args = parser.parse_args()

    optional = DEFAULT_SEED[1:]
    best: dict[str, Any] | None = None
    failures: list[dict[str, Any]] = []
    checked = 0
    centered_checks = 0

    for mask in range(1 << len(optional)):
        lower = (DEFAULT_SEED[0],) + tuple(
            value for index, value in enumerate(optional) if mask & (1 << index)
        )
        record = metrics(lower, args.center)
        if record is None:
            raise AssertionError("a subset of an admissible set became inadmissible")
        checked += 1
        if record["Z"] != record["D"] - record["Q"]:
            raise AssertionError("centered convention failed")
        centered_checks += 1
        if best is None or coefficient(record) > coefficient(best):
            best = record
        if record["c20_margin6"] > 0:
            failures.append(record)

    if best is None:
        raise AssertionError("empty search")
    best_coefficient = coefficient(best)
    result = {
        "arithmetic": "integer/rational",
        "domain": (
            "every reflected pair-deletion subset of singer-ff6287916581 "
            "retaining the endpoint pair"
        ),
        "center": args.center,
        "checked": checked,
        "centered_checks": centered_checks,
        "c20_failure_count": len(failures),
        "best_required_coefficient": (
            f"{best_coefficient.numerator}/{best_coefficient.denominator}"
        ),
        "best": best,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}))


if __name__ == "__main__":
    main()
