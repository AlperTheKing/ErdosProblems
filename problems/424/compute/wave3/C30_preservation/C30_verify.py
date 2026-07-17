#!/usr/bin/env python3
"""Independent small enumeration and replay for the C30 artifacts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "c30_sat", HERE / "C30_preservation_sat.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load C30 preservation module")
SAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SAT)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="ascii"))


def brute_force(limit: int = 26) -> dict:
    values = [value for value in range(2, limit + 1) if SAT.allowed(value)]
    free = [value for value in values if value not in (2, 3)]
    pairs = {value: SAT.admissible_pairs(value) for value in values}
    hard = {
        value
        for value in values
        if SAT.hard_shape(value, pairs[value])
    }
    closed_count = 0
    identity_checks = 0
    image_failures = 0
    for mask in range(1 << len(free)):
        source = {2, 3}
        source.update(
            value
            for index, value in enumerate(free)
            if mask & (1 << index)
        )
        if any(
            left in source and right in source and value not in source
            for value in values
            for left, right in pairs[value]
        ):
            continue
        closed_count += 1
        image = {2, 3}
        image.update(
            value
            for value in values
            if value not in (2, 3)
            and any(
                left in source and right in source
                for left, right in pairs[value]
            )
        )
        removed = source - image
        for cutoff in range(2, limit + 1):
            old_h, old_q, _ = SAT.exact_counts(cutoff, source, pairs)
            new_h, new_q, _ = SAT.exact_counts(cutoff, image, pairs)
            half = (cutoff + 1) // 2
            removed_odd = sum(
                value <= cutoff and value % 2 for value in removed
            )
            removed_hard = sum(
                value <= cutoff and value % 2 == 0 and value in hard
                for value in removed
            )
            removed_births = sum(value <= half for value in removed)
            predicted = (
                len(old_q)
                - len(old_h)
                - removed_odd
                - removed_hard
                + removed_births
            )
            actual = len(new_q) - len(new_h)
            if predicted != actual:
                raise AssertionError((source, cutoff, predicted, actual))
            identity_checks += 1
            if actual < 0:
                image_failures += 1
    if image_failures:
        raise AssertionError(f"small image failures: {image_failures}")
    return {
        "limit": limit,
        "closed_sources": closed_count,
        "identity_checks": identity_checks,
        "image_failures": image_failures,
    }


def replay_artifacts() -> dict:
    expected = {
        "unconditional_500.json": ("OPTIMAL", -6),
        "unconditional_10000.json": ("OPTIMAL", -68),
        "unconditional_100000.json": ("OPTIMAL", -1555),
        "splitless_free_10000.json": ("OPTIMAL", -42),
        "splitless_free_100000.json": ("OPTIMAL", -1301),
    }
    for name, (status, excess) in expected.items():
        result = load(name)
        if (result["status"], result["objective_excess"]) != (
            status,
            excess,
        ):
            raise AssertionError(name)
    scan = load("unconditional_first_failure_2000.json")
    if scan != {
        "schema_version": 1,
        "stop": 2000,
        "tested": 147,
        "first_failure": None,
    }:
        raise AssertionError("unconditional scan")
    split_scan = load("splitless_free_first_failure_2000.json")
    if split_scan["tested"] != 147 or split_scan["first_failure"] is not None:
        raise AssertionError("splitless-free scan")
    if load("prefix_counterexample_500.json")["status"] != "INFEASIBLE":
        raise AssertionError("positive-prefix 500")
    if load("prefix_counterexample_10000.json")["status"] != "UNKNOWN":
        raise AssertionError("positive-prefix 10000")
    tail = load("tail_removal_1e8.json")
    terminal = tail["snapshots"][-1]
    if (
        tail["first_failure"],
        terminal["H"],
        terminal["Q"],
        terminal["R"],
        terminal["Q_minus_H_minus_R"],
    ) != (0, 3368726, 5948614, 25463, 2554425):
        raise AssertionError("tail-removal replay")
    return {
        "fixed_results": len(expected),
        "unconditional_scan_cutoffs": scan["tested"],
        "splitless_free_scan_cutoffs": split_scan["tested"],
        "tail_limit": tail["limit"],
    }


def main() -> None:
    brute = brute_force()
    artifacts = replay_artifacts()
    print(json.dumps({"brute_force": brute, "artifacts": artifacts}, indent=2))


if __name__ == "__main__":
    main()
