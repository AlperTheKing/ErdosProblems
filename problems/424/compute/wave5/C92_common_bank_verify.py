#!/usr/bin/env python3
"""Independent exact replay of the C92 common-bank ratio.

This verifier imports no project arithmetic code.  It reconstructs admissible
factor pairs by direct trial division and checks every cutoff through LIMIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def classify(n: int, state: bytearray) -> int:
    product = n + 1
    has_pair = False
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a >= b or not allowed(a) or not allowed(b):
            continue
        has_pair = True
        if state[a] == GENERATED and state[b] == GENERATED:
            return GENERATED
    if not has_pair:
        return SPLITLESS
    if n % 2 == 0:
        if product % 3:
            return HARD
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD
    return OTHER


def seed_root(generated_child: int) -> int:
    value = generated_child - 1
    while value % 2 == 0:
        value //= 2
    return value + 1


def scan(limit: int) -> dict:
    require(54 <= limit <= 200_000, ("limit", limit))
    state = bytearray(limit + 1)
    active_hard = 0
    d_count = 0
    hard_births = 0
    hard_deaths = 0
    splitless_births = 0
    splitless_deaths = 0
    failure_count = 0
    first_failure = None
    minimum_ratio = None
    minimum_margin = None
    minimum_margin_x = None
    checkpoints_wanted = {
        x for x in (54, 74, 114, 186, 204, 362, 1_000, 10_000, 100_000, limit)
        if x <= limit
    }
    checkpoints = []
    active_prefix = [0] * (limit + 1)
    scale_upper_failures = 0
    scale_lower_failures = 0
    scale_upper_minimum = None
    scale_upper_minimum_x = None
    scale_lower_minimum = None
    scale_lower_minimum_x = None
    trajectory = hashlib.sha256()

    for x in range(2, limit + 1):
        if x in (2, 3):
            current = GENERATED
        elif allowed(x):
            current = classify(x, state)
        else:
            current = OTHER
        state[x] = current

        if current == HARD:
            require(x % 2 == 0, ("odd-hard", x))
            hard_births += 1
            active_hard += 1
        elif current == SPLITLESS:
            require(x % 2 == 0, ("odd-splitless", x))
            splitless_births += 1

        if x > 3 and x % 2 == 1 and current != GENERATED and allowed(x):
            parent = (x + 1) // 2
            require(allowed(parent) and state[parent] != GENERATED,
                    ("odd-hole-parent", x, parent))

        if x > 3 and x % 2 == 1 and current == GENERATED:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = seed_root(x)
                require(root % 2 == 0 and state[root] != GENERATED,
                        ("death-root", x, root))
                if state[root] == HARD:
                    require(active_hard > 0, ("hard-underflow", x, root))
                    active_hard -= 1
                    hard_deaths += 1
                elif state[root] == SPLITLESS:
                    d_count += 1
                    splitless_deaths += 1

        if active_hard:
            margin = 6 * d_count - 5 * active_hard
            ratio = (d_count, active_hard)
            if minimum_ratio is None or (
                ratio[0] * minimum_ratio[1] < minimum_ratio[0] * ratio[1]
            ):
                minimum_ratio = ratio
                minimum_ratio_x = x
            if minimum_margin is None or margin < minimum_margin:
                minimum_margin = margin
                minimum_margin_x = x
            if margin < 0:
                failure_count += 1
                if first_failure is None:
                    first_failure = {
                        "X": x, "A_H": active_hard, "D": d_count,
                        "margin": margin,
                    }

        active_prefix[x] = active_hard
        quarter = active_prefix[x // 4]
        scale_upper = d_count + quarter + 1 - active_hard
        scale_lower = 2 * d_count - 7 * quarter
        if scale_upper_minimum is None or scale_upper < scale_upper_minimum:
            scale_upper_minimum = scale_upper
            scale_upper_minimum_x = x
        if scale_lower_minimum is None or scale_lower < scale_lower_minimum:
            scale_lower_minimum = scale_lower
            scale_lower_minimum_x = x
        if scale_upper < 0:
            scale_upper_failures += 1
        if scale_lower < 0:
            scale_lower_failures += 1

        trajectory.update(x.to_bytes(4, "little"))
        trajectory.update(active_hard.to_bytes(4, "little"))
        trajectory.update(d_count.to_bytes(4, "little"))
        if x in checkpoints_wanted:
            checkpoints.append({
                "X": x,
                "A_H": active_hard,
                "D": d_count,
                "margin_6D_minus_5A_H": 6 * d_count - 5 * active_hard,
            })

    require(hard_births == active_hard + hard_deaths,
            ("hard-accounting", hard_births, active_hard, hard_deaths))
    require(splitless_deaths == d_count <= splitless_births,
            ("splitless-accounting", splitless_births, splitless_deaths))
    require(minimum_ratio is not None, "empty-ratio")
    if limit >= 10_000:
        require((*minimum_ratio, minimum_ratio_x) == (5, 6, 186),
                ("C91-regression", minimum_ratio, minimum_ratio_x))

    return {
        "schema": "C92-common-bank-independent-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "failure_count_6D_lt_5A_H": failure_count,
        "first_failure": first_failure,
        "minimum_ratio": {
            "D": minimum_ratio[0],
            "A_H": minimum_ratio[1],
            "X": minimum_ratio_x,
        },
        "minimum_margin": {
            "value": minimum_margin,
            "X": minimum_margin_x,
        },
        "scale_quarter_upper": {
            "failure_count": scale_upper_failures,
            "minimum_margin": scale_upper_minimum,
            "minimum_margin_X": scale_upper_minimum_x,
        },
        "scale_quarter_lower": {
            "failure_count": scale_lower_failures,
            "minimum_margin": scale_lower_minimum,
            "minimum_margin_X": scale_lower_minimum_x,
        },
        "endpoint": {
            "A_H": active_hard,
            "D": d_count,
            "hard_births": hard_births,
            "hard_deaths": hard_deaths,
            "splitless_births": splitless_births,
            "splitless_deaths": splitless_deaths,
        },
        "checkpoints": checkpoints,
        "trajectory_sha256": trajectory.hexdigest().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "limit": result["limit"],
        "failures": result["failure_count_6D_lt_5A_H"],
        "minimum_ratio": result["minimum_ratio"],
        "endpoint": result["endpoint"],
        "trajectory_sha256": result["trajectory_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
