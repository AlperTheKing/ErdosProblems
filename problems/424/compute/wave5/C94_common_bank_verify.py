#!/usr/bin/env python3
"""Independent exact replay for the C94 common-bank census.

This implementation imports neither C67 nor C94.  It constructs the least
closure in ascending order, enumerates factor pairs from its own SPF table,
and updates seed-chain deaths online.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
HOLE = 4


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    p = 2
    while p * p <= limit:
        if spf[p] == p:
            for n in range(p * p, limit + 1, p):
                if spf[n] == n:
                    spf[n] = p
        p += 1
    return spf


def divisors(value: int, spf: list[int]) -> list[int]:
    out = [1]
    while value > 1:
        p = spf[value]
        exponent = 0
        while value % p == 0:
            value //= p
            exponent += 1
        old = out
        out = []
        power = 1
        for _ in range(exponent + 1):
            out.extend(power * d for d in old)
            power *= p
    return out


def classify(n: int, state: bytearray, spf: list[int]) -> int:
    product = n + 1
    has_pair = False
    generated = False
    for a in divisors(product, spf):
        if a < 2 or a * a >= product:
            continue
        b = product // a
        if not allowed(a) or not allowed(b):
            continue
        has_pair = True
        if state[a] == GENERATED and state[b] == GENERATED:
            generated = True
            break
    if generated:
        return GENERATED
    if not has_pair:
        return SPLITLESS
    if n % 2 == 0:
        if product % 3 != 0:
            return HARD
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return HOLE


def seed_root(n: int) -> int:
    while n % 2:
        n = (n + 1) // 2
    return n


def replay(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    state = bytearray(limit + 1)
    active_hard = 0
    healed_splitless = 0
    hard_count = 0
    splitless_count = 0
    generated_count = 0
    holes_count = 0
    hard_dead = bytearray(limit + 1)
    splitless_dead = bytearray(limit + 1)
    minimum_ratio = None
    last_failure = None
    maximum_deficit = (-(10**18), 0, 0, 0)
    active_hard_history = [0] * (limit + 1)
    healed_bank_history = [0] * (limit + 1)

    for x in range(2, limit + 1):
        if x in (2, 3):
            current = GENERATED
        elif allowed(x):
            current = classify(x, state, spf)
        else:
            current = OTHER
        state[x] = current

        if current == GENERATED:
            generated_count += 1
        elif allowed(x):
            holes_count += 1
        if current == SPLITLESS:
            if x % 2:
                raise RuntimeError(("odd splitless root", x))
            splitless_count += 1
        if current == HARD:
            if x % 2:
                raise RuntimeError(("odd hard root", x))
            hard_count += 1
            active_hard += 1

        if (x > 3 and x % 2 and current == GENERATED and
                state[(x + 1) // 2] != GENERATED):
            root = seed_root(x)
            if state[root] == HARD:
                if hard_dead[root]:
                    raise RuntimeError(("second hard death", root, x))
                hard_dead[root] = 1
                active_hard -= 1
            elif state[root] == SPLITLESS:
                if splitless_dead[root]:
                    raise RuntimeError(("second splitless death", root, x))
                splitless_dead[root] = 1
                healed_splitless += 1

        deficit = 3 * active_hard - 4 * healed_splitless
        if deficit > maximum_deficit[0]:
            maximum_deficit = (deficit, x, active_hard, healed_splitless)
        if deficit > 0:
            last_failure = (x, active_hard, healed_splitless, deficit)
        if active_hard and healed_splitless:
            candidate = (healed_splitless, active_hard, x)
            if minimum_ratio is None or candidate[0] * minimum_ratio[1] < minimum_ratio[0] * candidate[1]:
                minimum_ratio = candidate
        active_hard_history[x] = active_hard
        healed_bank_history[x] = healed_splitless

    maximum_additive_quarter_defect = None
    maximum_weighted_quarter_defect = None
    quarter_scale_samples = []
    sample_points = {10**power for power in range(1, 10) if 10**power <= limit}
    for x in range(2, limit + 1):
        active = active_hard_history[x]
        healed = healed_bank_history[x]
        quarter = active_hard_history[x // 4]
        additive = active - healed - quarter
        weighted = 7 * quarter - 2 * healed
        additive_record = {
            "value": additive, "X": x, "A_H": active, "D": healed,
            "A_H_floor_X_over_4": quarter,
        }
        weighted_record = {
            "value": weighted, "X": x, "A_H": active, "D": healed,
            "A_H_floor_X_over_4": quarter,
        }
        if (maximum_additive_quarter_defect is None or
                additive > maximum_additive_quarter_defect["value"]):
            maximum_additive_quarter_defect = additive_record
        if (maximum_weighted_quarter_defect is None or
                weighted > maximum_weighted_quarter_defect["value"]):
            maximum_weighted_quarter_defect = weighted_record
        if x in sample_points:
            quarter_scale_samples.append({
                "X": x, "A_H": active, "D": healed,
                "A_H_floor_X_over_4": quarter,
                "additive_defect": additive, "weighted_defect": weighted,
            })

    bounded_depth_probe = None
    if limit >= 1_000_000:
        chain = []
        value = 2340
        while value <= limit:
            chain.append(value)
            value = 2 * value - 1
        if state[2340] != SPLITLESS or any(state[value] == GENERATED for value in chain):
            raise RuntimeError(("bounded-depth probe changed", chain))
        bounded_depth_probe = {
            "root": 2340,
            "visible_depth": len(chain) - 1,
            "chain": chain,
            "all_holes": True,
        }

    local_shadow_probe = None
    if limit >= 186:
        source_chain = [74, 147]
        shadow_chain = [8, 15, 29, 57, 113]
        if classify(74, state, spf) != HARD or classify(15, state, spf) != HOLE:
            raise RuntimeError("independent local-shadow classification changed")
        if state[8] != SPLITLESS:
            raise RuntimeError("independent local-shadow root changed")
        if any(state[value] == GENERATED for value in source_chain + shadow_chain):
            raise RuntimeError("independent local-shadow persistence changed")
        if active_hard_history[46] != 0:
            raise RuntimeError("independent quarter-scale carry changed")
        local_shadow_probe = {
            "cutoff": 186,
            "source": 74,
            "source_chain": source_chain,
            "factor_descent": [74, 15, 8],
            "complete_splitless_shadow": [8],
            "shadow_chain": shadow_chain,
            "shadow_healed_by_cutoff": False,
            "A_H_floor_cutoff_over_4": 0,
        }

    return {
        "limit": limit,
        "counts": {
            "generated": generated_count,
            "holes": holes_count,
            "hard": hard_count,
            "A_H": active_hard,
            "splitless": splitless_count,
            "D": healed_splitless,
            "persistent_splitless": splitless_count - healed_splitless,
        },
        "all_cutoff_three_quarter_gate": {
            "last_failure": None if last_failure is None else {
                "X": last_failure[0], "A_H": last_failure[1],
                "D": last_failure[2], "deficit": last_failure[3],
            },
            "maximum_deficit": {
                "value": maximum_deficit[0], "X": maximum_deficit[1],
                "A_H": maximum_deficit[2], "D": maximum_deficit[3],
            },
            "minimum_positive_D_over_A_H": None if minimum_ratio is None else {
                "numerator": minimum_ratio[0],
                "denominator": minimum_ratio[1],
                "X": minimum_ratio[2],
            },
        },
        "quarter_scale_gates": {
            "maximum_additive_defect": maximum_additive_quarter_defect,
            "maximum_weighted_defect": maximum_weighted_quarter_defect,
            "power_of_ten_samples": quarter_scale_samples,
            "local_shadow_probe": local_shadow_probe,
        },
        "bounded_depth_probe": bounded_depth_probe,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = replay(args.limit)
    if args.expected:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        for field in ("counts", "all_cutoff_three_quarter_gate", "quarter_scale_gates"):
            if result[field] != expected[field]:
                raise RuntimeError(("independent replay mismatch", field, result[field], expected[field]))
        result["expected_comparison"] = "exact_match"
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
