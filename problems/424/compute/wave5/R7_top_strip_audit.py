#!/usr/bin/env python3
"""Exact finite audit of GPT-Pro R7 top-strip perturbation.

The script builds the least arithmetic closure in ascending order, checks the
upper-shell identity at every cutoff, scans the decisive condition

    |B_X| > Q_G(X) - H_G(X),

and explicitly rebuilds selected perturbed closures to verify the claimed
local effect.  All arithmetic is integral.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
C74_PATH = HERE / "C74_injection_gate.py"
SPEC = importlib.util.spec_from_file_location("c74_for_r7", C74_PATH)
assert SPEC and SPEC.loader
C74 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C74
SPEC.loader.exec_module(C74)


def prefix(bits: bytearray) -> list[int]:
    out = [0] * len(bits)
    total = 0
    for index, value in enumerate(bits):
        total += int(value)
        out[index] = total
    return out


def count_range(pref: list[int], lower_exclusive: int, upper: int) -> int:
    if upper <= lower_exclusive:
        return 0
    return pref[upper] - pref[max(0, lower_exclusive)]


def rebuild_perturbation(
    cutoff: int,
    base_member: bytearray,
    pairs: dict[int, list[tuple[int, int]]],
    chosen: list[int],
) -> bytearray:
    member = bytearray(base_member[: cutoff + 1])
    for value in chosen:
        member[value] = 1
    for value in range(2, cutoff + 1):
        if member[value] or not C74.allowed(value):
            continue
        if any(member[left] and member[right] for left, right in pairs[value]):
            member[value] = 1
    return member


def counts_at(
    cutoff: int,
    member: bytearray,
    hard_shape: bytearray,
    pair_exists: bytearray,
) -> tuple[int, int]:
    hard = sum(
        hard_shape[value] and not member[value]
        for value in range(2, cutoff + 1)
    )
    boundary = 0
    for parent in range(2, (cutoff + 1) // 2 + 1):
        child = 2 * parent - 1
        if C74.allowed(parent) and member[child] and not member[parent]:
            boundary += 1
    return int(hard), boundary


def audit(limit: int, perturb_cutoffs: list[int]) -> dict:
    data = C74.build_census(limit, limit)
    generated = C74.GENERATED
    base_member = bytearray(value == generated for value in data["state"])
    pair_exists = bytearray(limit + 1)
    hard_shape = bytearray(limit + 1)
    splitless = bytearray(limit + 1)
    for value in range(2, limit + 1):
        if not C74.allowed(value):
            continue
        pairs = data["pairs"][value]
        pair_exists[value] = bool(pairs)
        hard_shape[value] = C74.predicted_hard_shape(value, bool(pairs))
        splitless[value] = not pairs and value not in (2, 3)

    hard_hole = bytearray(
        hard_shape[value] and not base_member[value] for value in range(limit + 1)
    )
    q_event = bytearray(limit + 1)
    eligible = bytearray(limit + 1)
    upper_odd_member = bytearray(limit + 1)
    hard_member = bytearray(limit + 1)
    lower_even_nonhard_member = bytearray(limit + 1)
    for value in range(2, limit + 1):
        if not C74.allowed(value):
            continue
        if value % 2 and base_member[value]:
            upper_odd_member[value] = 1
        if hard_shape[value] and base_member[value]:
            hard_member[value] = 1
        if value % 2 == 0 and not hard_shape[value] and base_member[value]:
            lower_even_nonhard_member[value] = 1
        if value % 2:
            parent = (value + 1) // 2
            if C74.allowed(parent) and base_member[value] and not base_member[parent]:
                q_event[value] = 1
        child = 2 * value - 1
        if (
            value % 2 == 0
            and pair_exists[value]
            and not hard_shape[value]
            and not base_member[value]
            and child <= limit
            and base_member[child]
        ):
            eligible[value] = 1

    p_hard_hole = prefix(hard_hole)
    p_q = prefix(q_event)
    p_eligible = prefix(eligible)
    p_upper_odd = prefix(upper_odd_member)
    p_hard_member = prefix(hard_member)
    p_lower_even = prefix(lower_even_nonhard_member)
    p_hard_shape = prefix(hard_shape)

    first_counterexample = None
    minimum_margin = None
    maximum_b = None
    shell_identity_failures = []
    checkpoints = {10**power for power in range(1, 10) if 10**power <= limit}
    checkpoints.add(limit)
    checkpoint_rows = []

    for cutoff in range(2, limit + 1):
        half = (cutoff + 1) // 2
        third_floor = (cutoff + 1) // 3
        # Strict m>(X+1)/3 means m>=floor((X+1)/3)+1.
        b_count = count_range(p_eligible, third_floor, half)
        hard = p_hard_hole[cutoff]
        boundary = p_q[cutoff]
        margin = boundary - hard - b_count
        row = {
            "X": cutoff,
            "B": b_count,
            "Q": boundary,
            "H": hard,
            "Q_minus_H_minus_B": margin,
        }
        if first_counterexample is None and margin < 0:
            first_counterexample = row
        if minimum_margin is None or margin < minimum_margin["Q_minus_H_minus_B"]:
            minimum_margin = row
        if maximum_b is None or b_count > maximum_b["B"]:
            maximum_b = row

        p_sum = count_range(p_upper_odd, half, cutoff)
        p_sum += count_range(p_hard_member, half, cutoff)
        n_sum = p_lower_even[half]
        identity_rhs = p_sum - n_sum - p_hard_shape[cutoff]
        if boundary - hard != identity_rhs:
            shell_identity_failures.append(
                {
                    "X": cutoff,
                    "Q_minus_H": boundary - hard,
                    "identity_rhs": identity_rhs,
                }
            )
            if len(shell_identity_failures) >= 20:
                break
        if cutoff in checkpoints:
            checkpoint_rows.append(row)

    perturbation_rows = []
    for cutoff in sorted(set(x for x in perturb_cutoffs if 2 <= x <= limit)):
        half = (cutoff + 1) // 2
        third_floor = (cutoff + 1) // 3
        chosen = [
            value
            for value in range(third_floor + 1, half + 1)
            if eligible[value]
        ]
        perturbed = rebuild_perturbation(cutoff, base_member, data["pairs"], chosen)
        changed = [
            value
            for value in range(2, cutoff + 1)
            if perturbed[value] != base_member[value]
        ]
        old_h, old_q = counts_at(cutoff, base_member, hard_shape, pair_exists)
        new_h, new_q = counts_at(cutoff, perturbed, hard_shape, pair_exists)
        assert changed == chosen
        assert new_h == old_h
        assert new_q == old_q - len(chosen)
        perturbation_rows.append(
            {
                "X": cutoff,
                "chosen": chosen,
                "changed": changed,
                "old_H": old_h,
                "new_H": new_h,
                "old_Q": old_q,
                "new_Q": new_q,
                "verified": True,
            }
        )

    return {
        "schema_version": 1,
        "limit": limit,
        "generated": sum(base_member),
        "hard_holes": p_hard_hole[limit],
        "boundary": p_q[limit],
        "eligible_total": p_eligible[limit],
        "first_counterexample": first_counterexample,
        "minimum_margin": minimum_margin,
        "maximum_B": maximum_b,
        "shell_identity_failures": shell_identity_failures,
        "checkpoints": checkpoint_rows,
        "perturbation_replays": perturbation_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--perturb-cutoffs", nargs="*", type=int, default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit(args.limit, args.perturb_cutoffs)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
