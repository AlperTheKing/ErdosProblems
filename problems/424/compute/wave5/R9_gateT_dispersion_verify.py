#!/usr/bin/env python3
"""Exact finite checks for the GPT-Pro R9 Gate-T dispersion lemma.

This verifier checks the finite combinatorial kernel only.  The divisor-bound
and asymptotic estimates are proved separately in the audit note.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


Q = 360
BLOCK = (2, 2, 2, 3, 3, 5)
EXPECTED = (
    23, 25, 31, 38, 40, 43, 46, 49, 50, 58,
    61, 62, 68, 70, 73, 76, 79, 80, 83, 86,
    92, 97, 98, 100, 112, 115, 116, 121, 122, 124,
    128, 130, 133, 136, 139, 140, 143, 146, 152, 157,
    158, 160, 163, 166, 172, 184, 193, 194, 196, 200,
    220, 223, 224, 229, 230, 232, 241, 242, 244, 248,
)


def word_offset(word: tuple[int, ...]) -> int:
    d = 0
    for m in word:
        d = m * d + (m - 2)
    return d


def block_offsets() -> tuple[int, ...]:
    words = set(permutations(BLOCK))
    assert len(words) == 60
    values = tuple(sorted(word_offset(word) for word in words))
    assert len(set(values)) == 60
    assert values == EXPECTED
    assert all(0 <= d < Q for d in values)
    return values


def concatenated_offsets(digits: tuple[int, ...], k: int) -> set[int]:
    values = {
        sum(ds[pos] * Q ** (k - 1 - pos) for pos in range(k))
        for ds in product(digits, repeat=k)
    }
    assert len(values) == len(digits) ** k
    assert all(0 <= d < Q**k for d in values)
    return values


def majority_color(offsets: set[int], k: int) -> tuple[int, set[int]]:
    classes = {
        rho: {d for d in offsets if (8 * Q**k + d + 1) % 3 == rho}
        for rho in (0, 2)
    }
    assert sum(map(len, classes.values())) == len(offsets)
    rho = 2 if len(classes[2]) >= len(classes[0]) else 0
    assert len(classes[rho]) * 2 >= len(offsets)
    return rho, classes[rho]


def tau(n: int) -> int:
    assert n >= 1
    answer = 1
    p = 2
    while p * p <= n:
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        if exponent:
            answer *= exponent + 1
        p += 1 if p == 2 else 2
    if n > 1:
        answer *= 2
    return answer


def stripped_part(z: int) -> int:
    for p in (2, 3):
        while z % p == 0:
            z //= p
    return z


def selected_factors(offsets: set[int], k: int) -> tuple[set[int], set[int]]:
    rho, selected = majority_color(offsets, k)
    a = 2 if rho == 2 else 4
    u = {a * (8 * Q**k + d) + 1 for d in selected}
    v = {3 * (8 * Q**k + d) + 2 for d in selected}
    assert len(u) == len(v) == len(selected)
    assert all(x % 2 == 1 and x % 3 == 0 for x in u)
    assert all(x % 3 == 2 for x in v)
    return u, v


def labelled_fibre_check(offsets_by_k: dict[int, set[int]], K: int) -> dict[str, int]:
    lower = (K + 2) // 3
    upper = (2 * K) // 3
    multiplicities: Counter[int] = Counter()
    labels = 0
    for i in range(lower, upper + 1):
        u_set, _ = selected_factors(offsets_by_k[i], i)
        _, v_set = selected_factors(offsets_by_k[K - i], K - i)
        for u in u_set:
            for v in v_set:
                multiplicities[u * v] += 1
                labels += 1
    assert sum(multiplicities.values()) == labels
    assert all(mult <= tau(stripped_part(z)) for z, mult in multiplicities.items())
    return {
        "K": K,
        "labelled_edges": labels,
        "product_values": len(multiplicities),
        "max_fibre": max(multiplicities.values(), default=0),
    }


def iota(K: int) -> int:
    return (2 * K) // 3 - (K + 2) // 3 + 1


def main() -> None:
    digits = block_offsets()
    offsets_by_k = {k: concatenated_offsets(digits, k) for k in range(1, 4)}

    color_rows = []
    for k, offsets in offsets_by_k.items():
        rho, selected = majority_color(offsets, k)
        color_rows.append({
            "k": k,
            "block_offsets": len(offsets),
            "rho": rho,
            "selected": len(selected),
        })

    for K in range(2, 301):
        m, r = divmod(K, 3)
        expected = m + 1 if r in (0, 2) else m
        assert iota(K) == expected

    fibre = labelled_fibre_check(offsets_by_k, 3)
    source_hash = sha256(Path(__file__).read_bytes()).hexdigest().upper()
    result = {
        "status": "PASS",
        "Q": Q,
        "one_block_distinct_offsets": len(digits),
        "one_block_min": min(digits),
        "one_block_max": max(digits),
        "block_code_rows": color_rows,
        "labelled_fibre_check": fibre,
        "correct_N_lower_bound": "iota(K)*60^K/4",
        "correct_dispersion_ratio": "4*A_delta*60^(-delta*K/2)/iota(K)",
        "source_sha256": source_hash,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
