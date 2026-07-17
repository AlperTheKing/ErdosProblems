#!/usr/bin/env python3
"""Independent trial-divisor and literal-stage replay of the C46 witness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_for(n: int) -> list[tuple[int, int]]:
    pairs = []
    a = 2
    while a * a < n + 1:
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if allowed(a) and allowed(b):
                pairs.append((a, b))
        a += 1
    return pairs


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def structural_parent(n: int) -> int | None:
    if n > 3 and n % 2:
        return (n + 1) // 2
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q
    return None


def audit(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: pairs_for(n) for n in values}
    member = {2, 3}
    rank: dict[int, int] = {}
    hard = []
    targets = []

    for n in values:
        if n in (2, 3):
            continue
        if any(a in member and b in member for a, b in pairs[n]):
            member.add(n)
            if n % 2:
                q = (n + 1) // 2
                if q not in member:
                    targets.append({"child": n, "parent": q, "rank": rank[q]})
            continue
        if not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if x not in member)
                for a, b in pairs[n]
            )
        if hard_shape(n, pairs[n]):
            hard.append({"source": n, "rank": rank[n]})

    stage = set(values)
    first_absent = {}
    stage_count = 0
    while True:
        following = {2, 3}
        for n in values:
            if n not in (2, 3) and any(
                a in stage and b in stage for a, b in pairs[n]
            ):
                following.add(n)
        for n in stage - following:
            first_absent[n] = stage_count + 1
        stage_count += 1
        if following == stage:
            break
        stage = following
    stage_mismatches = [
        {
            "n": n,
            "in_increasing_ground": n in member,
            "in_stage_intersection": n in stage,
            "rank": rank.get(n),
            "death_stage": first_absent.get(n),
        }
        for n in values
        if (n in member) != (n in stage)
        or (n not in member and first_absent[n] != rank[n] + 1)
    ]

    root_cache = {}

    def structural_root(n: int) -> int:
        path = []
        while n not in root_cache:
            path.append(n)
            parent = structural_parent(n)
            if parent is None:
                root_cache[n] = n
                break
            n = parent
        root = root_cache[n]
        for value in path:
            root_cache[value] = root
        return root

    ordinal = Counter()
    for target in targets:
        root = structural_root(target["parent"])
        ordinal[root] += 1
        target["root"] = root
        target["ordinal"] = ordinal[root]

    x = 186
    hard_x = [row for row in hard if row["source"] <= x]
    target_x = [row for row in targets if row["child"] <= x]
    expected_hard = [
        {"source": 54, "rank": 2},
        {"source": 74, "rank": 2},
        {"source": 114, "rank": 2},
        {"source": 144, "rank": 3},
        {"source": 174, "rank": 2},
        {"source": 186, "rank": 2},
    ]
    expected_targets = [
        {"child": 41, "parent": 21, "rank": 2, "root": 6, "ordinal": 1},
        {"child": 69, "parent": 35, "rank": 1, "root": 18, "ordinal": 1},
        {"child": 77, "parent": 39, "rank": 1, "root": 20, "ordinal": 1},
        {"child": 125, "parent": 63, "rank": 3, "root": 6, "ordinal": 2},
        {"child": 131, "parent": 66, "rank": 0, "root": 66, "ordinal": 1},
        {"child": 149, "parent": 75, "rank": 1, "root": 38, "ordinal": 1},
    ]

    t = Fraction(19, 20)
    hard_mass = sum(t ** row["rank"] for row in hard_x)
    target_mass = sum(
        Fraction(1, 2 ** (row["ordinal"] - 1)) * t ** row["rank"]
        for row in target_x
    )
    deficit = hard_mass - target_mass
    boundary = 1 - t
    polynomial = lambda u: Fraction(1, 2) * u**3 + 4 * u**2 - 3 * u - 1

    x_additive = 2064
    t_additive = Fraction(99, 100)
    hard_additive = [row for row in hard if row["source"] <= x_additive]
    target_additive = [row for row in targets if row["child"] <= x_additive]
    maximum_rank = max(
        [0]
        + [row["rank"] for row in hard_additive]
        + [row["rank"] for row in target_additive]
    )
    coefficients = [Fraction(0) for _ in range(maximum_rank + 1)]
    for row in hard_additive:
        coefficients[row["rank"]] += 1
    for row in target_additive:
        coefficients[row["rank"]] -= Fraction(
            1, 2 ** (row["ordinal"] - 1)
        )
    additive_deficit = sum(
        coefficient * t_additive**d
        for d, coefficient in enumerate(coefficients)
    )

    running = Fraction(0)
    first_over_one = None
    maximum_event = (Fraction(0), None)
    weighted_events = [
        (row["source"], t_additive ** row["rank"]) for row in hard
    ] + [
        (
            row["child"],
            -Fraction(1, 2 ** (row["ordinal"] - 1))
            * t_additive ** row["rank"],
        )
        for row in targets
    ]
    for coordinate, increment in sorted(weighted_events):
        running += increment
        if first_over_one is None and running > 1:
            first_over_one = (coordinate, running)
        if running > maximum_event[0]:
            maximum_event = (running, coordinate)

    transport = {
        "r3_parent": 15,
        "r3_child": 44,
        "bridge_parent": 66,
        "q_child": 131,
        "checks": {
            "15_is_hole": 15 not in member,
            "44_is_generated": 44 in member,
            "66_is_hole": 66 not in member,
            "131_is_generated": 131 in member,
            "131_is_target": any(row["child"] == 131 for row in targets),
            "identities": 44 == 3 * 15 - 1
            and 66 == 3 * 44 // 2
            and 131 == 3 * 44 - 1 == 2 * 66 - 1,
        },
    }

    assertions = {
        "literal_stages_match_increasing_ground": not stage_mismatches,
        "hard_ledger_at_186": hard_x == expected_hard,
        "target_ledger_at_186": target_x == expected_targets,
        "geometric_rank_deficit_is_3019_over_16000": (
            deficit == Fraction(3019, 16000)
        ),
        "deficit_exceeds_one_minus_t_by_2219_over_16000": (
            deficit - boundary == Fraction(2219, 16000)
        ),
        "threshold_is_between_917_and_918_over_1000": (
            polynomial(Fraction(917, 1000)) < 0
            and polynomial(Fraction(918, 1000)) > 0
        ),
        "additive_one_fails_first_at_1644": (
            first_over_one
            == (1644, Fraction(2070022193351, 2000000000000))
        ),
        "maximum_through_limit_is_at_2064": (
            maximum_event
            == (Fraction(358639165423, 100000000000), 2064)
        ),
        "additive_witness_coefficients_are_exact": coefficients == [
            -44,
            -14,
            Fraction(109, 2),
            Fraction(-5, 4),
            2,
            Fraction(11, 4),
            5,
        ],
        "r3_bridge_is_exact": all(transport["checks"].values()),
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    return {
        "schema_version": 1,
        "limit": limit,
        "algorithm": "trial divisors plus literal descending stages",
        "stages_to_fixpoint": stage_count,
        "stage_mismatches": stage_mismatches,
        "witness_X": x,
        "hard_events": hard_x,
        "target_events": target_x,
        "potential": {
            "rank_parameter": str(t),
            "target_component_weight": "2^(1-ordinal)",
            "hard_mass": str(hard_mass),
            "target_mass": str(target_mass),
            "deficit": str(deficit),
            "one_minus_t_boundary": str(boundary),
            "deficit_over_boundary": str(deficit - boundary),
            "exact_deficit_polynomial": "t^3/2 + 4*t^2 - 3*t - 1",
            "polynomial_at_917_over_1000": str(
                polynomial(Fraction(917, 1000))
            ),
            "polynomial_at_918_over_1000": str(
                polynomial(Fraction(918, 1000))
            ),
        },
        "additive_one_falsifier": {
            "rank_parameter": str(t_additive),
            "target_component_weight": "2^(1-ordinal)",
            "first_over_one_X": first_over_one[0],
            "first_over_one_deficit": str(first_over_one[1]),
            "maximum_X_through_limit": maximum_event[1],
            "maximum_deficit_through_limit": str(maximum_event[0]),
            "witness_X": x_additive,
            "hard_count": len(hard_additive),
            "target_count": len(target_additive),
            "coefficient_by_rank": [str(value) for value in coefficients],
            "deficit": str(additive_deficit),
            "deficit_over_one": str(additive_deficit - 1),
        },
        "r3_transport_example": transport,
        "assertions": assertions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 2064:
        raise ValueError("limit must be at least 2064")
    payload = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": payload["limit"],
        "stages": payload["stages_to_fixpoint"],
        "deficit": payload["potential"]["deficit"],
        "deficit_over_boundary": payload["potential"]["deficit_over_boundary"],
        "additive_one_deficit": payload["additive_one_falsifier"]["deficit"],
        "assertions": payload["assertions"],
    }, indent=2))


if __name__ == "__main__":
    main()
