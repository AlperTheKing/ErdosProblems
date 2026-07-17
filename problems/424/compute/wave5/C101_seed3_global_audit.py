#!/usr/bin/env python3
"""Exact C101 audit of seed-3 healing events and global quarter ballots."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

GENERATED = 1
SPLITLESS = 2
HARD = 3
OTHER = 4


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def divisors_from_spf(n: int, spf: list[int]) -> list[int]:
    factors: list[tuple[int, int]] = []
    while n > 1:
        p = spf[n]
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        factors.append((p, exponent))
    divisors = [1]
    for p, exponent in factors:
        base = list(divisors)
        power = 1
        for _ in range(exponent):
            power *= p
            divisors.extend(d * power for d in base)
    return divisors


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for left in divisors_from_spf(product, spf):
        if left < 2:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            pairs.append((left, right))
    pairs.sort()
    return pairs


def root_of(n: int) -> int:
    while n & 1:
        n = (n + 1) // 2
    return n


def root_signature(root: int) -> str:
    """Coarse global arithmetic class from divisibility of root + 1 by 3."""
    return "three" if (root + 1) % 3 == 0 else "nonthree"


def classify(n: int, state: bytearray, spf: list[int]) -> tuple[int, list[tuple[int, int]]]:
    pairs = admissible_pairs(n, spf)
    if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
        return GENERATED, pairs
    if not pairs:
        return SPLITLESS, pairs
    if n % 2 == 0:
        product = n + 1
        if product % 3 != 0:
            return HARD, pairs
        parent = product // 3
        if not allowed(parent) or parent == 3:
            return HARD, pairs
    return OTHER, pairs


def first_row(rows: list[dict], predicate) -> dict | None:
    for row in rows:
        if predicate(row):
            return row
    return None


def build(limit: int) -> dict:
    spf = list(range(limit + 2))
    for p in range(2, int((limit + 1) ** 0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 2, p):
            if spf[multiple] == multiple:
                spf[multiple] = p

    state = bytearray(limit + 1)
    state[2] = state[3] = GENERATED
    hard_births: list[int] = []
    hard_death: dict[int, int] = {}
    splitless_heal: dict[int, int] = {}
    seed3_events: list[dict] = []
    active_hard: set[int] = set()
    active_history = [0] * (limit + 1)
    d_count = 0
    b3_count = 0
    ballot_rows: list[dict] = []
    image_fibres: dict[int, list[int]] = defaultdict(list)
    image_type_counts: Counter[str] = Counter()
    active_hard_by_signature: Counter[str] = Counter()
    active_history_by_signature = {
        "nonthree": [0] * (limit + 1),
        "three": [0] * (limit + 1),
    }
    d_by_signature: Counter[str] = Counter()
    typed_minima: dict[str, dict | None] = {"nonthree": None, "three": None}
    seed3_heal_time: dict[int, int] = {}

    for x in range(4, limit + 1):
        if allowed(x):
            current, pairs = classify(x, state, spf)
            state[x] = current
        else:
            current, pairs = 0, []

        if current == HARD:
            hard_births.append(x)
            active_hard.add(x)
            active_hard_by_signature[root_signature(x)] += 1

        if x & 1 and current == GENERATED and x > 3:
            parent = (x + 1) // 2
            if allowed(parent) and state[parent] != GENERATED:
                root = root_of(x)
                root_type = state[root]
                if root_type == HARD:
                    active_hard.remove(root)
                    active_hard_by_signature[root_signature(root)] -= 1
                    hard_death[root] = x
                elif root_type == SPLITLESS:
                    d_count += 1
                    d_by_signature[root_signature(root)] += 1
                    splitless_heal[root] = x
                elif root_type == OTHER:
                    b3_count += 1
                    seed3_heal_time[root] = x
                    cofactor = (root + 1) // 3
                    image = root_of(cofactor)
                    image_type = {
                        SPLITLESS: "splitless",
                        HARD: "hard",
                        OTHER: "seed3",
                        GENERATED: "generated",
                    }.get(state[image], "invalid")
                    image_fibres[image].append(root)
                    image_type_counts[image_type] += 1
                    seed3_events.append(
                        {
                            "healing_time": x,
                            "seed3_root": root,
                            "cofactor": cofactor,
                            "cofactor_root": image,
                            "cofactor_root_type": image_type,
                            "cofactor_root_state_at_quarter": (
                                "persistent_hard"
                                if state[image] == HARD
                                and image <= x // 4
                                and (image not in hard_death or hard_death[image] > x // 4)
                                else "not_persistent_hard"
                            ),
                            "generating_pairs": [
                                [a, b]
                                for a, b in pairs
                                if state[a] == GENERATED and state[b] == GENERATED
                            ],
                        }
                    )

        active_history[x] = len(active_hard)
        for signature in ("nonthree", "three"):
            active_history_by_signature[signature][x] = active_hard_by_signature[signature]
        q = x // 4
        ballot_rows.append(
            {
                "X": x,
                "A_H": len(active_hard),
                "D": d_count,
                "B3": b3_count,
                "A_H_quarter": active_history[q],
                "F": d_count + active_history[q] - len(active_hard),
                "root_boundary_margin": d_count + b3_count - len(active_hard),
                "seed3_quarter_margin": active_history[q] - b3_count,
            }
        )
        for signature in ("nonthree", "three"):
            typed_row = {
                "X": x,
                "signature": signature,
                "A_H": active_hard_by_signature[signature],
                "D": d_by_signature[signature],
                "A_H_quarter": active_history_by_signature[signature][q],
            }
            typed_row["F"] = (
                typed_row["D"] + typed_row["A_H_quarter"] - typed_row["A_H"]
            )
            if typed_minima[signature] is None or (
                typed_row["F"], typed_row["X"]
            ) < (typed_minima[signature]["F"], typed_minima[signature]["X"]):
                typed_minima[signature] = typed_row

    first_nonhard_image = first_row(
        seed3_events, lambda row: row["cofactor_root_type"] != "hard"
    )
    first_quarter_image_failure = first_row(
        seed3_events,
        lambda row: row["cofactor_root_state_at_quarter"] != "persistent_hard",
    )
    fibre_rows = []
    for image, roots in image_fibres.items():
        ordered = sorted(roots, key=seed3_heal_time.__getitem__)
        if len(ordered) > 1:
            fibre_rows.append(
                {
                    "cofactor_root": image,
                    "seed3_roots": ordered,
                    "healing_times": [seed3_heal_time[root] for root in ordered],
                }
            )
    first_fibre_collision = min(
        fibre_rows, key=lambda row: (row["healing_times"][1], row["cofactor_root"]), default=None
    )

    minima = {
        key: min(ballot_rows, key=lambda row, k=key: (row[k], row["X"]))
        for key in ("F", "root_boundary_margin", "seed3_quarter_margin")
    }
    maximum_fibre = max(image_fibres.items(), key=lambda item: (len(item[1]), -item[0]), default=(0, []))
    digest = hashlib.sha256(bytes(state[2:])).hexdigest().upper()
    return {
        "schema": "C101-seed3-global-audit-v1",
        "limit": limit,
        "exact_integer_acceptance": True,
        "counts": {
            "hard_births": len(hard_births),
            "A_H": len(active_hard),
            "D": d_count,
            "B3": b3_count,
            "seed3_image_types": dict(sorted(image_type_counts.items())),
        },
        "ballot_minima": minima,
        "typed_ballot_minima": typed_minima,
        "first_nonhard_cofactor_root": first_nonhard_image,
        "first_quarter_cofactor_root_failure": first_quarter_image_failure,
        "first_cofactor_root_fibre_collision": first_fibre_collision,
        "maximum_cofactor_root_fibre": {
            "cofactor_root": maximum_fibre[0],
            "multiplicity": len(maximum_fibre[1]),
            "seed3_roots": maximum_fibre[1],
        },
        "first_40_seed3_events": seed3_events[:40],
        "classification_sha256": digest,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise SystemExit("limit must be at least 100")
    result = build(args.limit)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({"limit": args.limit, **result["counts"], "ballot_minima": result["ballot_minima"]}, sort_keys=True))


if __name__ == "__main__":
    main()
