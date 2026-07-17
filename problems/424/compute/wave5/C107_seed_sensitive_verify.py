#!/usr/bin/env python3
"""Independent trial-divisor verification for the C107 seed census."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def root_of(n: int) -> int:
    while n % 2 == 1:
        n = (n + 1) // 2
    return n


def divisor_pairs(n: int) -> tuple[tuple[int, int], ...]:
    product = n + 1
    result = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return tuple(result)


def classify(n: int, state: bytearray, pair_rows: list[tuple[tuple[int, int], ...]]) -> int:
    row = pair_rows[n]
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in row):
        return GENERATED
    if not row:
        return SPLITLESS
    if n % 2 == 0:
        if (n + 1) % 3:
            return HARD
        cofactor = (n + 1) // 3
        if not allowed(cofactor) or cofactor == 3:
            return HARD
    return OTHER


def scan(
    seeds: tuple[int, ...],
    limit: int,
    pair_rows: list[tuple[tuple[int, int], ...]],
    base_margins: list[int] | None = None,
    keep_margins: bool = False,
) -> dict[str, object]:
    seed_set = set(seeds)
    state = bytearray(limit + 1)
    active = 0
    healed = 0
    prefix = [0] * (limit + 1)
    roots = {root_of(seed) for seed in seeds}
    required = -10**9
    required_at = 0
    first_failure = None
    hard_births: list[int] = []
    hard_deaths: dict[int, int] = {}
    splitless_deaths: dict[int, int] = {}
    margins = [0] * (limit + 1) if keep_margins else None
    minimum_delta = 10**9
    minimum_delta_at = 0

    for n in range(2, limit + 1):
        if n in seed_set:
            current = GENERATED
        elif allowed(n):
            current = classify(n, state, pair_rows)
        else:
            current = OTHER
        state[n] = current
        if current == HARD:
            active += 1
            hard_births.append(n)

        if n > 3 and n % 2 and current == GENERATED:
            parent = (n + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of(n)
                if state[root] == HARD:
                    active -= 1
                    hard_deaths.setdefault(root, n)
                elif state[root] == SPLITLESS:
                    healed += 1
                    splitless_deaths.setdefault(root, n)

        prefix[n] = active
        quarter = prefix[n // 4]
        need = active - healed - quarter
        quarter_margin = -need
        if margins is not None:
            margins[n] = quarter_margin
        if base_margins is not None:
            delta = quarter_margin - base_margins[n]
            if delta < minimum_delta:
                minimum_delta = delta
                minimum_delta_at = n
        if need > required:
            required = need
            required_at = n
        margin = len(roots) - need
        if margin < 0 and first_failure is None:
            first_failure = {
                "X": n,
                "A_H": active,
                "D": healed,
                "A_H_quarter": quarter,
                "k": len(roots),
                "margin": margin,
            }

    return {
        "seeds": list(seeds),
        "roots": sorted(roots),
        "k": len(roots),
        "required": required,
        "required_at": required_at,
        "first_failure": first_failure,
        "endpoint_A_H": active,
        "endpoint_D": healed,
        "endpoint_A_H_quarter": prefix[limit // 4],
        "endpoint_quarter_margin": healed + prefix[limit // 4] - active,
        "persistent_hard": [
            root for root in hard_births if hard_deaths.get(root, limit + 1) > limit
        ],
        "healed_splitless": sorted(splitless_deaths),
        "minimum_margin_delta": None if base_margins is None else minimum_delta,
        "minimum_margin_delta_at": None if base_margins is None else minimum_delta_at,
        "_margins": margins,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    claim = json.loads(args.claim.read_text(encoding="ascii"))
    limit = int(claim["limit"])
    if not 186 <= limit <= 10_000:
        raise ValueError("independent exhaustive replay is bounded at 10,000")

    pair_rows = [tuple() for _ in range(limit + 1)]
    for n in range(2, limit + 1):
        if allowed(n):
            pair_rows[n] = divisor_pairs(n)

    base_row = scan((2, 3), limit, pair_rows, keep_margins=True)
    base_margins = base_row.pop("_margins")
    assert isinstance(base_margins, list)
    rows = [base_row]
    for seed in range(5, limit + 1):
        if allowed(seed):
            row = scan((2, 3, seed), limit, pair_rows, base_margins=base_margins)
            row.pop("_margins")
            rows.append(row)

    failures = [row for row in rows if row["first_failure"] is not None]
    tight = [row for row in rows if row["k"] == row["required"]]
    minimum_slack = min(int(row["k"]) - int(row["required"]) for row in rows)
    claim_tight = {
        (int(row["seed"]), int(row["root"]), int(row["k"]),
         int(row["required"]), int(row["required_at"]))
        for row in claim["tight"]
    }
    replay_tight = set()
    for row in tight:
        seeds = list(row["seeds"])
        seed = 3 if seeds == [2, 3] else seeds[-1]
        replay_tight.add((
            seed,
            root_of(seed),
            int(row["k"]),
            int(row["required"]),
            int(row["required_at"]),
        ))

    checks = {
        "seed_system_count": int(claim["seed_systems"]) == len(rows),
        "failure_count": int(claim["failures"]) == len(failures) == 0,
        "minimum_slack": int(claim["minimum_slack"]) == minimum_slack == 0,
        "tight_rows": claim_tight == replay_tight,
        "base_is_sharp": rows[0]["required"] == 1 and rows[0]["required_at"] == 186,
    }
    perturbation_witness = None
    if "minimum_one_chain_margin_delta" in claim:
        replay_min_delta = min(
            int(row["minimum_margin_delta"])
            for row in rows[1:]
        )
        replay_delta_rows = [
            row for row in rows[1:]
            if int(row["minimum_margin_delta"]) == replay_min_delta
        ]
        replay_delta_first = min(
            replay_delta_rows,
            key=lambda row: (int(row["minimum_margin_delta_at"]), row["seeds"]),
        )
        checks["minimum_perturbation"] = (
            int(claim["minimum_one_chain_margin_delta"]) == replay_min_delta
        )
        checks["first_minimum_perturbation"] = (
            int(claim["negative_perturbations"][0]["delta"]) == replay_min_delta
            and int(claim["negative_perturbations"][0]["at"])
            == int(replay_delta_first["minimum_margin_delta_at"])
            and int(claim["negative_perturbations"][0]["seed"])
            == int(replay_delta_first["seeds"][-1])
        )
        witness_x = int(replay_delta_first["minimum_margin_delta_at"])
        witness_seed = int(replay_delta_first["seeds"][-1])
        base_witness = scan((2, 3), witness_x, pair_rows[: witness_x + 1])
        seeded_witness = scan(
            (2, 3, witness_seed), witness_x, pair_rows[: witness_x + 1]
        )
        quarter_x = witness_x // 4
        base_quarter = scan((2, 3), quarter_x, pair_rows[: quarter_x + 1])
        seeded_quarter = scan(
            (2, 3, witness_seed), quarter_x, pair_rows[: quarter_x + 1]
        )
        perturbation_witness = {
            "X": witness_x,
            "seed": witness_seed,
            "root": root_of(witness_seed),
            "base": {
                "A_H": base_witness["endpoint_A_H"],
                "D": base_witness["endpoint_D"],
                "A_H_quarter": base_witness["endpoint_A_H_quarter"],
                "margin": base_witness["endpoint_quarter_margin"],
            },
            "seeded": {
                "A_H": seeded_witness["endpoint_A_H"],
                "D": seeded_witness["endpoint_D"],
                "A_H_quarter": seeded_witness["endpoint_A_H_quarter"],
                "margin": seeded_witness["endpoint_quarter_margin"],
            },
            "delta": (
                int(seeded_witness["endpoint_quarter_margin"])
                - int(base_witness["endpoint_quarter_margin"])
            ),
            "lost_D_roots": sorted(
                set(base_witness["healed_splitless"])
                - set(seeded_witness["healed_splitless"])
            ),
            "gained_D_roots": sorted(
                set(seeded_witness["healed_splitless"])
                - set(base_witness["healed_splitless"])
            ),
            "lost_quarter_hard_roots": sorted(
                set(base_quarter["persistent_hard"])
                - set(seeded_quarter["persistent_hard"])
            ),
            "gained_quarter_hard_roots": sorted(
                set(seeded_quarter["persistent_hard"])
                - set(base_quarter["persistent_hard"])
            ),
            "lost_full_hard_roots": sorted(
                set(base_witness["persistent_hard"])
                - set(seeded_witness["persistent_hard"])
            ),
            "gained_full_hard_roots": sorted(
                set(seeded_witness["persistent_hard"])
                - set(base_witness["persistent_hard"])
            ),
        }

    row66 = next(row for row in rows if row["seeds"] == [2, 3, 66])
    pair_rows_186 = [tuple() for _ in range(187)]
    for n in range(2, 187):
        if allowed(n):
            pair_rows_186[n] = divisor_pairs(n)
    row66_186 = scan((2, 3, 66), 186, pair_rows_186)
    checks.update({
        "seed66_is_sharp": row66["k"] == row66["required"] == 2,
        "seed66_cutoff": row66["required_at"] == 186,
        "seed66_labels": (
            row66_186["persistent_hard"] == [54, 74, 114, 144, 174, 186]
            and row66_186["healed_splitless"] == [6, 18, 20, 38]
        ),
    })
    failed_checks = [name for name, ok in checks.items() if not ok]
    if failed_checks:
        raise RuntimeError(("C107 verification failed", failed_checks))

    # The containment of both distinguished seeds is load-bearing.  Search a
    # small exact family for the first failure when that hypothesis is dropped.
    nonbase_candidates = []
    small_seed_pool = [n for n in range(2, 16) if allowed(n)]
    for size in range(1, 4):
        for seed_tuple in itertools.combinations(small_seed_pool, size):
            if 2 in seed_tuple and 3 in seed_tuple:
                continue
            row = scan(seed_tuple, min(limit, 500), pair_rows[: min(limit, 500) + 1])
            if row["first_failure"] is not None:
                nonbase_candidates.append(row)
    nonbase_first = min(
        nonbase_candidates,
        key=lambda row: (
            int(row["first_failure"]["X"]),
            len(row["seeds"]),
            row["seeds"],
        ),
    )

    result = {
        "schema": "C107-seed-sensitive-independent-v1",
        "acceptance": "exact integer trial divisors",
        "claim": str(args.claim),
        "limit": limit,
        "seed_systems": len(rows),
        "failures": len(failures),
        "minimum_slack": minimum_slack,
        "tight": [
            {
                "seeds": row["seeds"],
                "roots": row["roots"],
                "required": row["required"],
                "required_at": row["required_at"],
            }
            for row in tight
        ],
        "checks": checks,
        "perturbation_witness": perturbation_witness,
        "false_corrections": {
            "k_minus_one": {
                "falsifier_seeds": [2, 3],
                "X": 186,
                "margin": -1,
            },
            "count_seed_values_as_components": {
                "status": "valid but nonsharp on {2,3}",
                "value": 2,
                "required": 1,
            },
            "drop_base_seed_hypothesis": {
                "falsifier_seeds": nonbase_first["seeds"],
                "first_failure": nonbase_first["first_failure"],
            },
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": limit,
        "seed_systems": len(rows),
        "failures": len(failures),
        "tight": len(tight),
        "checks": checks,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
