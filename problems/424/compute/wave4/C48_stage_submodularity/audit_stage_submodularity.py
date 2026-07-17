#!/usr/bin/env python3
"""Exact C48 audit of descending stages and candidate submodularity laws.

The least set G is reconstructed in increasing order.  Independently, the
descending approximants S_0, S_1, ... are built literally.  The script then
checks the exact modular rewrite

  H_{<=d}(X) - Q_{<=d}(X)
    = sum_{n in A \\ S_{d+1}} (1_{n in K_X} - 1_{n in P_X}),

where K_X is the hard-shape prefix and P_X consists of parents q whose
seed-2 child is in G and at most X.

It also finds first counterexamples to several tempting stage monotonicity
and submodularity strengthenings.  All arithmetic is integral.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            out.append((a, b))
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def build_increasing(limit: int, pairs: list[list[tuple[int, int]]]) -> dict:
    member = [False] * (limit + 1)
    rank: list[int | None] = [None] * (limit + 1)
    member[2] = member[3] = True
    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = True
            continue
        if not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in pairs[n]
            )
    return {"member": member, "rank": rank}


def build_descending(
    limit: int,
    pairs: list[list[tuple[int, int]]],
) -> list[list[bool]]:
    current = [allowed(n) for n in range(limit + 1)]
    current[0] = current[1] = False
    stages = [current]
    while True:
        following = [False] * (limit + 1)
        following[2] = following[3] = True
        for n in range(4, limit + 1):
            if allowed(n) and any(current[a] and current[b] for a, b in pairs[n]):
                following[n] = True
        stages.append(following)
        if following == current:
            return stages
        current = following
        if len(stages) > limit + 2:
            raise AssertionError("descending stages did not stabilize")


def first_local_submodularity_failure(
    limit: int,
    pairs: list[list[tuple[int, int]]],
) -> dict | None:
    """Find a local unsupported-indicator failure of submodularity.

    For a nonseed n define u_n(D)=1 iff D hits every parent pair of n.
    With two disjoint admissible pairs, singleton deletion sets hitting
    different pairs give u(A)=u(B)=0, u(A union B)=1, u(A cap B)=0.
    """
    for n in range(4, limit + 1):
        if len(pairs[n]) < 2:
            continue
        (a, _), (c, _) = pairs[n][:2]
        if a in (2, 3) or c in (2, 3):
            continue
        return {
            "n": n,
            "pairs": pairs[n],
            "D1": [a],
            "D2": [c],
            "u_D1": 0,
            "u_D2": 0,
            "u_union": 1,
            "u_intersection": 0,
            "violated_inequality": "u(D1)+u(D2)>=u(D1_union_D2)+u(D1_intersection_D2)",
        }
    return None


def audit(limit: int) -> dict:
    pairs = [factor_pairs(n) if n >= 2 else [] for n in range(limit + 1)]
    inc = build_increasing(limit, pairs)
    stages = build_descending(limit, pairs)
    member = inc["member"]
    rank = inc["rank"]

    stage_mismatches: list[dict] = []
    for n in range(2, limit + 1):
        if not allowed(n):
            continue
        stable = stages[-1][n]
        if stable != member[n]:
            stage_mismatches.append({"n": n, "kind": "membership"})
        if not member[n]:
            death = next(i for i in range(1, len(stages)) if not stages[i][n]) - 1
            if death != rank[n]:
                stage_mismatches.append(
                    {"n": n, "kind": "rank", "stage": death, "recursive": rank[n]}
                )

    hard = [(n, rank[n]) for n in range(2, limit + 1)
            if hard_shape(n, pairs[n]) and not member[n]]
    target = []
    for q in range(2, (limit + 1) // 2 + 1):
        child = 2 * q - 1
        if allowed(q) and not member[q] and member[child]:
            target.append((child, q, rank[q]))

    max_rank = max([0] + [r for _, r in hard] + [r for _, _, r in target])
    formula_checks = 0
    formula_failures: list[dict] = []
    ao_failures: list[dict] = []
    strict_failures: list[dict] = []
    first_rank_monotonicity_failure = None
    first_positive_descent_failure = None
    first_layer_nonpositive_failure = None

    # Evaluate only at event cutoffs; this covers every prefix extremum.
    cutoffs = sorted({n for n, _ in hard} | {c for c, _, _ in target})
    prior_by_x: dict[int, int] = {}
    for d in range(max_rank + 1):
        Sd1 = stages[d + 1] if d + 1 < len(stages) else stages[-1]
        for X in cutoffs:
            if X > limit:
                continue
            H = sum(n <= X and r <= d for n, r in hard)
            Q = sum(c <= X and r <= d for c, _, r in target)
            direct = H - Q
            Y = (X + 1) // 2
            modular = 0
            for n in range(2, X + 1):
                if allowed(n) and not Sd1[n] and hard_shape(n, pairs[n]):
                    modular += 1
            for q in range(2, min(Y, limit) + 1):
                if allowed(q) and not Sd1[q] and member[2 * q - 1]:
                    modular -= 1
            formula_checks += 1
            if direct != modular and len(formula_failures) < 20:
                formula_failures.append(
                    {"X": X, "d": d, "direct": direct, "modular": modular}
                )
            if direct > 1 and len(ao_failures) < 20:
                ao_failures.append({"X": X, "d": d, "excess": direct})
            if direct > 0 and len(strict_failures) < 20:
                strict_failures.append({"X": X, "d": d, "excess": direct})

            if d > 0:
                previous = prior_by_x[X]
                if direct > previous and first_rank_monotonicity_failure is None:
                    first_rank_monotonicity_failure = {
                        "X": X, "d": d, "B_d_minus_1": previous, "B_d": direct
                    }
                if direct > 0 and previous < direct and first_positive_descent_failure is None:
                    first_positive_descent_failure = {
                        "X": X, "d": d, "B_d_minus_1": previous, "B_d": direct
                    }
                if direct - previous > 0 and first_layer_nonpositive_failure is None:
                    first_layer_nonpositive_failure = {
                        "X": X,
                        "layer_rank": d,
                        "layer_H_minus_Q": direct - previous,
                    }
            prior_by_x[X] = direct

    return {
        "schema_version": 1,
        "limit": limit,
        "stage_count_including_fixed_repeat": len(stages),
        "stage_mismatches": stage_mismatches,
        "hard": len(hard),
        "targets": len(target),
        "maximum_rank": max_rank,
        "modular_identity": {
            "checks": formula_checks,
            "failures": formula_failures,
            "formula": "B_d(X)=sum_{n notin S_(d+1)}(1_KX(n)-1_PX(n))",
        },
        "additive_one_failures": ao_failures,
        "strict_failures_sample": strict_failures,
        "candidate_failures": {
            "B_d_nonincreasing_in_d": first_rank_monotonicity_failure,
            "positive_rank_descent": first_positive_descent_failure,
            "each_exact_layer_nonpositive": first_layer_nonpositive_failure,
            "death_operator_submodular": first_local_submodularity_failure(limit, pairs),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 200:
        raise ValueError("limit must be at least 200")
    result = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": result["limit"],
        "stage_mismatches": len(result["stage_mismatches"]),
        "identity_failures": len(result["modular_identity"]["failures"]),
        "ao_failures": len(result["additive_one_failures"]),
        "candidate_failures": result["candidate_failures"],
    }, indent=2))


if __name__ == "__main__":
    main()
