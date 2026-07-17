#!/usr/bin/env python3
"""Independent trial-division verifier for the C59 dyadic audit."""

from __future__ import annotations

import argparse
import json
from math import isqrt
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def shell_of(n: int) -> int:
    return (n - 1).bit_length()


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for a in range(2, isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return result


def prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % p for p in range(2, isqrt(n) + 1))


def capacity(x: int, p: int) -> int:
    return (x + 1) // p - (x // 2 + 1) // p


def reconstruct(limit: int) -> tuple[set[int], dict[int, dict[str, int | list[int]]]]:
    generated = {2, 3}
    holes: set[int] = set()
    rows: dict[int, dict[str, int | list[int]]] = {}
    for j in range(1, limit.bit_length()):
        rows[j] = {
            "m": 0,
            "e": 0,
            "r": 0,
            "odd": 0,
            "s": 0,
            "h": 0,
            "mass": 0,
            "hist": [0],
            "ap": 0,
            "ap_le_j": 0,
            "ap_max": 0,
        }

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = admissible_pairs(n)
        j = shell_of(n)
        if n % 30 == 24 and pairs:
            rows[j]["ap"] += 1
            rows[j]["ap_le_j"] += len(pairs) <= j
            rows[j]["ap_max"] = max(rows[j]["ap_max"], len(pairs))
        if any(a in generated and b in generated for a, b in pairs):
            generated.add(n)
            continue
        holes.add(n)
        rows[j]["m"] += 1
        if not pairs:
            rows[j]["e"] += 1
            continue
        rows[j]["r"] += 1
        if n % 2:
            rows[j]["odd"] += 1
        elif (n + 1) % 3 == 0 and allowed((n + 1) // 3) and (n + 1) // 3 != 3:
            rows[j]["s"] += 1
        else:
            rows[j]["h"] += 1
            rows[j]["mass"] += len(pairs)
            hist = rows[j]["hist"]
            if len(hist) <= len(pairs):
                hist.extend([0] * (len(pairs) + 1 - len(hist)))
            hist[len(pairs)] += 1
    return holes, rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--limit", type=int, default=65536)
    args = parser.parse_args()
    if args.limit < 128 or args.limit & (args.limit - 1):
        raise ValueError("limit must be a power of two at least 128")

    payload = json.loads(args.artifact.read_text(encoding="ascii"))
    by_j = {row["j"]: row for row in payload["shells"]}
    holes, rows = reconstruct(args.limit)
    checks = 0

    for j in range(7, args.limit.bit_length()):
        saved = by_j[j]
        row = rows[j]
        parent = rows[j - 1]
        expected = {
            "m_parent": parent["m"],
            "m": row["m"],
            "e": row["e"],
            "r": row["r"],
            "s": row["s"],
            "h": row["h"],
            "q": parent["m"] - row["odd"],
            "hard_pair_mass": row["mass"],
            "ap_hard_shape": row["ap"],
            "ap_pairs_le_shell_index": row["ap_le_j"],
            "ap_max_pairs": row["ap_max"],
        }
        for key, value in expected.items():
            assert saved[key] == value, (j, key, saved[key], value)
            checks += 1

        x = 1 << j
        umax = (x + 6) // 10
        actual = sum(
            capacity(x, 2 * u - 1)
            for u in holes
            if u <= umax
        )
        ambient = sum(
            capacity(x, 2 * u - 1)
            for u in range(2, umax + 1)
            if allowed(u)
        )
        structural = sum(
            capacity(x, 2 * u - 1)
            for u in range(2, umax + 1)
            if allowed(u) and (u + 1) % 3 == 1 and prime(u + 1)
        )
        assert saved["actual_hole_capacity"] == actual
        assert saved["ambient_allowed_capacity"] == ambient
        assert saved["structural_prime_capacity"] == structural
        assert row["mass"] <= actual
        checks += 4

        hist = row["hist"]
        low = 0
        for threshold in saved["thresholds"]:
            d = threshold["D"]
            if d < len(hist):
                low += hist[d]
            high = row["h"] - low
            assert threshold["low_pair_hard"] == low
            assert threshold["high_pair_hard"] == high
            assert (d + 1) * high <= actual
            checks += 3

        assert row["r"] == parent["m"] + row["s"] + row["h"] - expected["q"]
        checks += 1

    print(json.dumps({
        "status": "PASS",
        "limit": args.limit,
        "checks": checks,
        "method": "independent Python trial division",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
