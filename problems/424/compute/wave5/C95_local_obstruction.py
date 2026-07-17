#!/usr/bin/env python3
"""Exact verifier for the C95 factor-local amortization obstruction.

The verifier deliberately uses a small, direct constructor rather than the
fast C93/C95 sieve.  At X=186 it reconstructs the least generated set,
computes A_H(X), D(X), and A_H(floor(X/4)), and checks Hall's condition for
the natural graph that joins a persistent hard root to the seed-2 roots of
its missing factor endpoints.

All arithmetic is integral.  This falsifies the factor-local unit matching;
it does not falsify the global scalar inequality.
"""

from __future__ import annotations

import json
from math import isqrt


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    pairs: list[tuple[int, int]] = []
    for a in range(2, isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            pairs.append((a, b))
    return pairs


def chain_root(value: int) -> int:
    if value % 2 == 0:
        return value
    shifted = value - 1
    return (shifted >> ((shifted & -shifted).bit_length() - 1)) + 1


def chain_top(root: int, cutoff: int) -> int:
    value = root
    while 2 * value - 1 <= cutoff:
        value = 2 * value - 1
    return value


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def construct(cutoff: int) -> dict:
    generated = [False] * (cutoff + 1)
    pairs: dict[int, list[tuple[int, int]]] = {}
    splitless: set[int] = set()
    hard: set[int] = set()

    for n in range(2, cutoff + 1):
        if not allowed(n):
            continue
        row = admissible_pairs(n)
        pairs[n] = row
        if n in (2, 3) or any(generated[a] and generated[b] for a, b in row):
            generated[n] = True
        elif not row:
            splitless.add(n)
        elif hard_shape(n, row):
            hard.add(n)

    return {
        "generated": generated,
        "pairs": pairs,
        "splitless": splitless,
        "hard": hard,
    }


def active_hard(data: dict, cutoff: int) -> list[int]:
    generated = data["generated"]
    return sorted(
        root
        for root in data["hard"]
        if root <= cutoff and not generated[chain_top(root, cutoff)]
    )


def healed_splitless(data: dict, cutoff: int) -> list[int]:
    generated = data["generated"]
    return sorted(
        root
        for root in data["splitless"]
        if root % 2 == 0
        and root <= cutoff
        and generated[chain_top(root, cutoff)]
    )


def main() -> None:
    cutoff = 186
    quarter = cutoff // 4
    data = construct(cutoff)
    generated = data["generated"]
    sources = active_hard(data, cutoff)
    old_bank = active_hard(data, quarter)
    healed_bank = healed_splitless(data, cutoff)
    bank = set(old_bank) | set(healed_bank)

    raw_neighborhoods: dict[int, list[int]] = {}
    neighborhoods: dict[int, list[int]] = {}
    for source in sources:
        endpoint_roots = {
            chain_root(endpoint)
            for pair in data["pairs"][source]
            for endpoint in pair
            if not generated[endpoint]
        }
        raw_neighborhoods[source] = sorted(endpoint_roots)
        neighborhoods[source] = sorted(endpoint_roots & bank)

    full_source_neighborhood = sorted(
        {target for row in neighborhoods.values() for target in row}
    )
    result = {
        "schema": "C95-factor-local-obstruction-v1",
        "cutoff": cutoff,
        "quarter": quarter,
        "A_H": sources,
        "D": healed_bank,
        "A_H_quarter": old_bank,
        "missing_endpoint_root_neighborhoods": raw_neighborhoods,
        "factor_local_bank_neighborhoods": neighborhoods,
        "hall_witness_sources": sources,
        "hall_witness_targets": full_source_neighborhood,
        "hall_deficit": len(sources) - len(full_source_neighborhood),
        "global_scalar_defect": len(sources) - len(bank),
    }

    expected = {
        "A_H": [54, 74, 114, 144, 174, 186],
        "D": [6, 18, 20, 38, 66],
        "A_H_quarter": [],
        "missing_endpoint_root_neighborhoods": {
            54: [6], 74: [8], 114: [12], 144: [8], 174: [18], 186: [6]
        },
        "factor_local_bank_neighborhoods": {
            54: [6], 74: [], 114: [], 144: [], 174: [18], 186: [6]
        },
        "hall_witness_targets": [6, 18],
        "hall_deficit": 4,
        "global_scalar_defect": 1,
    }
    for key, value in expected.items():
        if result[key] != value:
            raise RuntimeError(f"mismatch for {key}: {result[key]!r} != {value!r}")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
