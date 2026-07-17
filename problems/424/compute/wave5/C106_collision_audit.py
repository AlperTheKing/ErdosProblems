"""Exact collision audit for the C102 scale-varying decoder.

The arithmetic is integer-only. NumPy is used only as a compact uint64 sorter;
all structural checks are repeated with Python arbitrary-precision integers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def offset_states(a_max: int, b_max: int, c_max: int) -> dict[tuple[int, int, int], set[int]]:
    states: dict[tuple[int, int, int], set[int]] = {(0, 0, 0): {0}}
    for total in range(1, a_max + b_max + c_max + 1):
        for a in range(a_max + 1):
            for b in range(b_max + 1):
                c = total - a - b
                if not 0 <= c <= c_max:
                    continue
                values: set[int] = set()
                if a:
                    values.update(2 * d for d in states[a - 1, b, c])
                if b:
                    values.update(3 * d + 1 for d in states[a, b - 1, c])
                if c:
                    values.update(5 * d + 3 for d in states[a, b, c - 1])
                states[a, b, c] = values
    return states


def valuation(n: int, prime: int) -> int:
    value = 0
    while n % prime == 0:
        n //= prime
        value += 1
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_layers(k_max: int) -> tuple[int, dict[int, dict[str, object]]]:
    a0, b0, c0 = 2, 1, 1
    q = 2**a0 * 3**b0 * 5**c0
    states = offset_states(a0 * k_max, b0 * k_max, c0 * k_max)
    layers: dict[int, dict[str, object]] = {}
    for k in range(1, k_max + 1):
        modulus = q**k
        ds = sorted(states[a0 * k, b0 * k, c0 * k])
        assert all(0 <= d <= modulus - 2 for d in ds)
        hs = [8 * modulus + d + 1 for d in ds]
        colors = Counter(h % 3 for h in hs)
        assert colors[1] == 0
        rho = 2 if colors[2] >= colors[0] else 0
        selected = [h for h in hs if h % 3 == rho]
        assert 2 * len(selected) >= len(ds)
        us = [2 * h - 1 if rho == 2 else 4 * h - 3 for h in selected]
        vs = [3 * h - 1 for h in selected]
        assert len(us) == len(set(us)) == len(vs) == len(set(vs))
        assert all(h > 5 for h in selected)
        assert all(u % 3 == 0 for u in us)
        assert all(v % 3 == 2 for v in vs)
        assert set(us).isdisjoint(vs)
        assert min(us) >= (16 if rho == 2 else 32) * modulus + 1
        assert max(us) <= (18 if rho == 2 else 36) * modulus - 3
        assert min(vs) >= 24 * modulus + 2
        assert max(vs) <= 27 * modulus - 4
        layers[k] = {"D": len(ds), "rho": rho, "U": us, "V": vs}
    return q, layers


def duplicate_values(products: np.ndarray) -> tuple[np.ndarray, Counter[int]]:
    products.sort()
    changes = np.empty(products.size, dtype=np.bool_)
    changes[0] = True
    changes[1:] = products[1:] != products[:-1]
    starts = np.flatnonzero(changes)
    counts = np.diff(np.append(starts, products.size))
    repeated = counts > 1
    values = products[starts[repeated]]
    multiplicities = Counter({int(z): int(r) for z, r in zip(values, counts[repeated], strict=True)})
    return values, multiplicities


def audit_k(q: int, layers: dict[int, dict[str, object]], K: int) -> dict[str, object]:
    first_i = (K + 2) // 3
    last_i = 2 * K // 3
    channels: list[tuple[int, list[int], list[int]]] = []
    blocks: list[np.ndarray] = []
    edges = 0
    for i in range(first_i, last_i + 1):
        us = layers[i]["U"]
        vs = layers[K - i]["V"]
        assert isinstance(us, list) and isinstance(vs, list)
        channel_edges = len(us) * len(vs)
        edges += channel_edges
        left = np.asarray(us, dtype=np.uint64)
        right = np.asarray(vs, dtype=np.uint64)
        block = np.multiply(left[:, None], right[None, :], dtype=np.uint64).reshape(-1)
        assert int(block.max(initial=0)) < 972 * q**K
        blocks.append(block)
        channels.append((i, us, vs))

    products = np.concatenate(blocks)
    assert products.size == edges
    repeated_values, repeated_counts = duplicate_values(products)
    repeated_set = set(map(int, repeated_values))

    representations: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for i, us, vs in channels:
        right = np.asarray(vs, dtype=np.uint64)
        for u in us:
            row = np.multiply(np.uint64(u), right, dtype=np.uint64)
            hits = np.flatnonzero(np.isin(row, repeated_values, assume_unique=False))
            for pos in hits:
                z = int(row[pos])
                representations[z].append((i, u, vs[int(pos)]))

    assert set(representations) == repeated_set
    assert all(len(representations[z]) == repeated_counts[z] for z in repeated_set)

    pair_count = 0
    cross_channel_pairs = 0
    same_channel_pairs = 0
    different_left_color_pairs = 0
    normal_forms = []
    for z in sorted(representations):
        reps = representations[z]
        for x in range(len(reps)):
            for y in range(x + 1, len(reps)):
                i, u, v = reps[x]
                j, up, vp = reps[y]
                pair_count += 1
                if i == j:
                    same_channel_pairs += 1
                else:
                    cross_channel_pairs += 1

                rho_i = int(layers[i]["rho"])
                rho_j = int(layers[j]["rho"])
                if rho_i != rho_j:
                    different_left_color_pairs += 1
                # The two left-color product bands are disjoint, so equality
                # forces the same U construction.
                assert rho_i == rho_j

                g = math.gcd(u, up)
                a = u // g
                b = up // g
                assert math.gcd(a, b) == 1
                assert v % b == 0 and vp % a == 0
                c = v // b
                assert vp == a * c
                assert math.gcd(v, vp) == c
                assert g * a * b * c == z

                # Since every V-value is prime to 3, equality forces equal
                # 3-adic orders on the two U-values.
                e = valuation(u, 3)
                assert e == valuation(up, 3)
                assert valuation(g, 3) == e
                assert a % 3 and b % 3 and c % 3

                # The reduced ratio lies in the exact scale annulus.
                if i >= j:
                    numerator, denominator, gap = a, b, i - j
                else:
                    numerator, denominator, gap = b, a, j - i
                scale = q**gap
                assert 8 * scale * denominator <= 9 * numerator
                assert 8 * numerator <= 9 * scale * denominator

                right_rho_i = int(layers[K - i]["rho"])
                right_rho_j = int(layers[K - j]["rho"])
                expected_v = 5 if right_rho_i == 2 else 8
                expected_vp = 5 if right_rho_j == 2 else 8
                assert v % 9 == expected_v and vp % 9 == expected_vp
                assert (b * c) % 9 == expected_v
                assert (a * c) % 9 == expected_vp
                if right_rho_i == right_rho_j:
                    assert a % 9 == b % 9

                if len(normal_forms) < 24:
                    normal_forms.append(
                        {
                            "z": z,
                            "first": [i, u, v],
                            "second": [j, up, vp],
                            "g": g,
                            "a": a,
                            "b": b,
                            "c": c,
                            "scale_gap": gap,
                            "v3_u": e,
                        }
                    )

    histogram = Counter(repeated_counts.values())
    singleton_products = edges - sum(repeated_counts.values())
    support = singleton_products + len(repeated_counts)
    return {
        "K": K,
        "i_range": [first_i, last_i],
        "edges": edges,
        "support": support,
        "multiplicity_histogram": {
            "1": singleton_products,
            **{str(r): n for r, n in sorted(histogram.items())},
        },
        "collision_pairs": pair_count,
        "same_channel_pairs": same_channel_pairs,
        "cross_channel_pairs": cross_channel_pairs,
        "different_left_color_pairs": different_left_color_pairs,
        "normal_form_samples": normal_forms,
    }


def audit_k_summary(q: int, layers: dict[int, dict[str, object]], K: int) -> dict[str, object]:
    """Histogram-only path for a substantially larger exact product block."""
    first_i = (K + 2) // 3
    last_i = 2 * K // 3
    blocks: list[np.ndarray] = []
    channel_rows = []
    edges = 0
    for i in range(first_i, last_i + 1):
        us = layers[i]["U"]
        vs = layers[K - i]["V"]
        assert isinstance(us, list) and isinstance(vs, list)
        channel_edges = len(us) * len(vs)
        edges += channel_edges
        channel_rows.append({"i": i, "j": K - i, "edges": channel_edges})
        left = np.asarray(us, dtype=np.uint64)
        right = np.asarray(vs, dtype=np.uint64)
        block = np.multiply(left[:, None], right[None, :], dtype=np.uint64).reshape(-1)
        assert int(block.max(initial=0)) < 972 * q**K
        blocks.append(block)
    products = np.concatenate(blocks)
    del blocks
    assert products.size == edges
    products.sort()
    changes = np.empty(products.size, dtype=np.bool_)
    changes[0] = True
    changes[1:] = products[1:] != products[:-1]
    starts = np.flatnonzero(changes)
    counts = np.diff(np.append(starts, products.size))
    histogram = Counter(map(int, counts))
    light = {}
    for cutoff in (1, 2, 3, 4, 8, 16):
        edge_mass = int(counts[counts <= cutoff].sum())
        light[str(cutoff)] = {
            "edge_mass": edge_mass,
            "numerator": edge_mass,
            "denominator": edges,
        }
    return {
        "K": K,
        "i_range": [first_i, last_i],
        "channels": channel_rows,
        "edges": edges,
        "support": int(counts.size),
        "max_multiplicity": int(counts.max()),
        "multiplicity_histogram": {str(r): n for r, n in sorted(histogram.items())},
        "light_edge_mass": light,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--k-max", type=int, default=5)
    parser.add_argument("--summary-K", type=int, default=0)
    args = parser.parse_args()
    if not 2 <= args.k_max <= 5:
        raise ValueError("the audited exact ray supports 2 <= k-max <= 5")

    largest_K = args.summary_K if args.summary_K else args.k_max
    if largest_K < 2:
        raise ValueError("summary-K must be zero or at least two")
    largest_layer = 2 * largest_K // 3
    q, layers = build_layers(largest_layer)
    audits = (
        [audit_k_summary(q, layers, args.summary_K)]
        if args.summary_K
        else [audit_k(q, layers, K) for K in range(2, args.k_max + 1)]
    )
    result = {
        "ray": [2, 1, 1],
        "Q": q,
        "layers": [
            {
                "k": k,
                "D": layers[k]["D"],
                "rho": layers[k]["rho"],
                "size": len(layers[k]["U"]),
            }
            for k in sorted(layers)
        ],
        "audits": audits,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(f"wrote {args.output}")
    print(f"sha256 {sha256(args.output)}")


if __name__ == "__main__":
    main()
