#!/usr/bin/env python3
"""Independent trial-divisor verifier for the C101 3-adic ballot witness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

GENERATED = 1
SPLITLESS = 2
HARD = 3
OTHER = 4
SIGNATURES = ("nonthree", "three")


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs_trial(n: int) -> list[tuple[int, int]]:
    result = []
    divisor = 2
    while divisor * divisor <= n + 1:
        if (n + 1) % divisor == 0:
            other = (n + 1) // divisor
            if divisor < other and allowed(divisor) and allowed(other):
                result.append((divisor, other))
        divisor += 1
    return result


def signature(root: int) -> str:
    return "three" if (root + 1) % 3 == 0 else "nonthree"


def root_of(n: int) -> int:
    while n % 2 == 1:
        n = (n + 1) // 2
    return n


def classify(n: int, state: bytearray) -> int:
    pairs = pairs_trial(n)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        product = n + 1
        if product % 3 != 0:
            return HARD
        cofactor = product // 3
        if not allowed(cofactor) or cofactor == 3:
            return HARD
    return OTHER


def verify(limit: int) -> dict:
    state = bytearray(limit + 1)
    state[2] = state[3] = GENERATED
    hard_births = {kind: [] for kind in SIGNATURES}
    hard_deaths: dict[int, int] = {}
    splitless_heals = {kind: [] for kind in SIGNATURES}
    history = {kind: [0] * (limit + 1) for kind in SIGNATURES}
    active = {kind: 0 for kind in SIGNATURES}
    first_type_failure = None
    first_type_preserving_failure = None
    minimum_by_type = {kind: None for kind in SIGNATURES}
    total_minimum = None
    witness = None

    for x in range(4, limit + 1):
        current = classify(x, state) if allowed(x) else 0
        state[x] = current
        if current == HARD:
            kind = signature(x)
            hard_births[kind].append(x)
            active[kind] += 1

        if x % 2 == 1 and current == GENERATED:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of(x)
                if state[root] == HARD:
                    kind = signature(root)
                    active[kind] -= 1
                    hard_deaths[root] = x
                elif state[root] == SPLITLESS:
                    splitless_heals[signature(root)].append((root, x))

        for kind in SIGNATURES:
            history[kind][x] = active[kind]

        q = x // 4
        typed_rows = []
        for kind in SIGNATURES:
            row = {
                "X": x,
                "signature": kind,
                "A_H": active[kind],
                "D": len(splitless_heals[kind]),
                "A_H_quarter": history[kind][q],
            }
            row["F"] = row["D"] + row["A_H_quarter"] - row["A_H"]
            typed_rows.append(row)
            if minimum_by_type[kind] is None or (row["F"], x) < (
                minimum_by_type[kind]["F"], minimum_by_type[kind]["X"]
            ):
                minimum_by_type[kind] = row.copy()
            if row["F"] < -1 and first_type_failure is None:
                first_type_failure = row.copy()

        total_row = {
            "X": x,
            "A_H": sum(row["A_H"] for row in typed_rows),
            "D": sum(row["D"] for row in typed_rows),
            "A_H_quarter": sum(row["A_H_quarter"] for row in typed_rows),
        }
        total_row["F"] = total_row["D"] + total_row["A_H_quarter"] - total_row["A_H"]
        type_preserving_deficit = sum(max(0, -row["F"]) for row in typed_rows)
        if type_preserving_deficit > 1 and first_type_preserving_failure is None:
            first_type_preserving_failure = {
                "X": x,
                "required_exceptions": type_preserving_deficit,
                "rows": [row.copy() for row in typed_rows],
            }
        if total_minimum is None or (total_row["F"], x) < (
            total_minimum["F"], total_minimum["X"]
        ):
            total_minimum = total_row.copy()

        if x == 186:
            q = x // 4
            witness = {
                "X": x,
                "quarter": q,
                "persistent_hard": {
                    kind: [
                        root
                        for root in hard_births[kind]
                        if root <= x and (root not in hard_deaths or hard_deaths[root] > x)
                    ]
                    for kind in SIGNATURES
                },
                "healed_splitless": {
                    kind: [root for root, heal in splitless_heals[kind] if heal <= x]
                    for kind in SIGNATURES
                },
                "quarter_persistent_hard": {
                    kind: [
                        root
                        for root in hard_births[kind]
                        if root <= q and (root not in hard_deaths or hard_deaths[root] > q)
                    ]
                    for kind in SIGNATURES
                },
                "rows": typed_rows,
                "total": total_row,
                "type_preserving_required_exceptions": type_preserving_deficit,
            }

    if first_type_failure is None or first_type_failure["X"] != 186:
        raise RuntimeError(f"unexpected first type failure: {first_type_failure}")
    if first_type_preserving_failure is None or first_type_preserving_failure["X"] != 186:
        raise RuntimeError(
            f"unexpected first type-preserving failure: {first_type_preserving_failure}"
        )
    if witness is None:
        raise RuntimeError("missing X=186 witness")
    if witness["persistent_hard"]["nonthree"] != [54, 114, 144, 174, 186]:
        raise RuntimeError("unexpected nonthree hard witness set")
    if witness["persistent_hard"]["three"] != [74]:
        raise RuntimeError("unexpected three hard witness set")
    if witness["healed_splitless"]["nonthree"] != [6, 18, 66]:
        raise RuntimeError("unexpected nonthree bank set")
    if witness["healed_splitless"]["three"] != [20, 38]:
        raise RuntimeError("unexpected three bank set")
    if witness["total"]["F"] != -1:
        raise RuntimeError("total quarter margin at X=186 is not -1")

    return {
        "schema": "C101-type-ballot-independent-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "first_typewise_plus_one_failure": first_type_failure,
        "first_type_preserving_one_exception_failure": first_type_preserving_failure,
        "minimum_by_type": minimum_by_type,
        "total_minimum": total_minimum,
        "witness_186": witness,
        "classification_sha256": hashlib.sha256(bytes(state[2:])).hexdigest().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 186:
        raise SystemExit("limit must be at least 186")
    result = verify(args.limit)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": args.limit,
        "first": result["first_typewise_plus_one_failure"],
        "minimum_by_type": result["minimum_by_type"],
        "total_minimum": result["total_minimum"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
