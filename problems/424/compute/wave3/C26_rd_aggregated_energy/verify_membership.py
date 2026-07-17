"""Independent replay for C26 offset supports, G membership, colors, and small energies.

The C++ probe evaluates the set recursion (48). This verifier instead enumerates
every multiset word, replays the licensed maps x -> 2x-1, 3x-1, 5x-1 from
x=9, and forms the offset support from the terminal witnesses.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from math import comb, gcd
from pathlib import Path


def multinomial(a: int, b: int, c: int) -> int:
    return comb(a + b + c, a) * comb(b + c, b)


def fnv1a64_le(values: list[int]) -> str:
    value = 0xCBF29CE484222325
    for item in values:
        for shift in range(0, 64, 8):
            value ^= (item >> shift) & 0xFF
            value = (value * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def enumerate_word_witnesses(a: int, b: int, c: int, final_m: int) -> tuple[list[int], int]:
    support: set[int] = set()
    leaves = 0

    def visit(ra: int, rb: int, rc: int, t: int, d: int, slope: int) -> None:
        nonlocal leaves
        x = t + 1
        assert x % 3 in (0, 2)
        if ra + rb + rc == 0:
            assert slope == final_m
            assert t == 8 * slope + d
            assert 0 <= d < slope
            support.add(d)
            leaves += 1
            return

        for remaining, multiplier, bias, next_counts in (
            (ra, 2, 0, (ra - 1, rb, rc)),
            (rb, 3, 1, (ra, rb - 1, rc)),
            (rc, 5, 3, (ra, rb, rc - 1)),
        ):
            if remaining == 0:
                continue
            # multiplier and x are distinct G-elements, so multiplier*x-1 is licensed.
            assert x > 5 and x != multiplier
            next_t = multiplier * t + bias
            next_x = multiplier * x - 1
            assert next_t + 1 == next_x
            assert next_x % 3 in (0, 2)
            visit(*next_counts, next_t, multiplier * d + bias, multiplier * slope)

    visit(a, b, c, 8, 0, 1)
    return sorted(support), leaves


def replay_block(record: dict[str, object], tie_policy: str) -> dict[str, object]:
    a, b, c = (int(x) for x in record["counts"])
    M = int(record["M"])
    offsets, leaves = enumerate_word_witnesses(a, b, c, M)
    assert leaves == multinomial(a, b, c) == int(record["W"])
    assert len(offsets) == int(record["D"])
    assert offsets[0] == int(record["offset_min"])
    assert offsets[-1] == int(record["offset_max"])
    assert fnv1a64_le(offsets) == record["offset_fnv1a64_le"]
    assert sum(offsets) == int(record["offset_sum"])
    assert sum(d * d for d in offsets) == int(record["offset_sum_sq"])

    g0: list[int] = []
    g2: list[int] = []
    for d in offsets:
        h = 8 * M + d + 1
        assert 8 * M < h <= 9 * M
        if h % 3 == 0:
            g0.append(h)
        elif h % 3 == 2:
            g2.append(h)
        else:
            raise AssertionError("forbidden H residue")
    assert len(g0) == int(record["H_G0"])
    assert len(g2) == int(record["H_G2"])

    if len(g0) > len(g2):
        selected_color = "G0"
    elif len(g2) > len(g0):
        selected_color = "G2"
    else:
        selected_color = tie_policy.upper()
    assert selected_color == record["selected_color"]
    selected = g0 if selected_color == "G0" else g2
    assert 2 * len(selected) >= len(offsets)

    if selected_color == "G0":
        U = selected
        V = [3 * h - 1 for h in selected]
        for u, v in zip(U, V, strict=True):
            assert u > 5 and u != 3
            assert u % 3 == 0 and v % 3 == 2
            assert v == 3 * u - 1
    else:
        U = [2 * h - 1 for h in selected]
        V = selected
        for u, v in zip(U, V, strict=True):
            assert v > 5 and v != 2
            assert u % 3 == 0 and v % 3 == 2
            assert u == 2 * v - 1
    assert len(U) == int(record["U_size"])
    assert len(V) == int(record["V_size"])
    assert (U[0], U[-1]) == (int(record["U_min"]), int(record["U_max"]))
    assert (V[0], V[-1]) == (int(record["V_min"]), int(record["V_max"]))
    return {
        "k": int(record["k"]),
        "offsets": offsets,
        "U": U,
        "V": V,
        "word_witnesses": leaves,
        "selected_color": selected_color,
    }


def replay_energy(record: dict[str, object], blocks: dict[int, dict[str, object]]) -> dict[str, object]:
    source_k = [int(k) for k in record["source_k"]]
    K = int(record["K"])
    counters: list[Counter[int]] = []
    block_pairs: list[int] = []
    for k in source_k:
        U = blocks[k]["U"]
        V = blocks[K - k]["V"]
        counter = Counter(u * v for u in U for v in V)
        counters.append(counter)
        block_pairs.append(len(U) * len(V))
    assert block_pairs == [int(x) for x in record["block_pairs"]]
    assert sum(block_pairs) == int(record["N"])

    size = len(counters)
    matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        matrix[i][i] = sum(count * count for count in counters[i].values())
        for j in range(i + 1, size):
            left, right = counters[i], counters[j]
            if len(left) > len(right):
                left, right = right, left
            value = sum(count * right.get(product, 0) for product, count in left.items())
            matrix[i][j] = matrix[j][i] = value
    assert matrix == [[int(x) for x in row] for row in record["matrix"]]
    E = sum(sum(row) for row in matrix)
    assert E == int(record["E"])

    aggregate: Counter[int] = Counter()
    for counter in counters:
        aggregate.update(counter)
    assert len(aggregate) == int(record["distinct_products"])
    assert min(aggregate) == int(record["product_min"])
    assert max(aggregate) == int(record["product_max"])
    assert max(aggregate.values()) == int(record["max_r"])
    histogram = Counter(aggregate.values())
    expected_histogram = {
        int(row["r"]): int(row["products"])
        for row in record["multiplicity_histogram"]
    }
    assert histogram == expected_histogram
    return {"K": K, "N": sum(block_pairs), "E": E, "status": "verified"}


def audit_energy_identities(
    record: dict[str, object], blocks: dict[int, dict[str, object]]
) -> dict[str, object]:
    K = int(record["K"])
    source_k = [int(k) for k in record["source_k"]]
    block_pairs = [len(blocks[k]["U"]) * len(blocks[K - k]["V"]) for k in source_k]
    assert block_pairs == [int(x) for x in record["block_pairs"]]
    N = sum(block_pairs)
    assert N == int(record["N"])
    if record["status"] != "computed":
        return {"K": K, "N": N, "status": "pair-count-verified"}

    matrix = [[int(x) for x in row] for row in record["matrix"]]
    assert len(matrix) == len(source_k)
    assert all(len(row) == len(source_k) for row in matrix)
    assert all(matrix[i][j] == matrix[j][i]
               for i in range(len(matrix)) for j in range(len(matrix)))
    E = sum(sum(row) for row in matrix)
    assert E == int(record["E"])
    diagonal = sum(matrix[i][i] for i in range(len(matrix)))
    within = (diagonal - N) // 2
    cross = sum(matrix[i][j] for i in range(len(matrix)) for j in range(i + 1, len(matrix)))
    assert diagonal >= N and (diagonal - N) % 2 == 0
    assert within == int(record["within_collision_pairs"])
    assert cross == int(record["cross_collision_pairs"])
    assert E == N + 2 * (within + cross)

    histogram = {
        int(row["r"]): int(row["products"])
        for row in record["multiplicity_histogram"]
    }
    assert sum(histogram.values()) == int(record["distinct_products"])
    assert sum(r * count for r, count in histogram.items()) == N
    assert sum(r * r * count for r, count in histogram.items()) == E
    assert max(histogram) == int(record["max_r"])
    divisor = gcd(E, N)
    ratio = record["E_over_N"]
    assert int(ratio["numerator"]) == E // divisor
    assert int(ratio["denominator"]) == N // divisor
    return {"K": K, "N": N, "E": E, "status": "identities-verified"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-energy-pairs", type=int, default=1_000_000)
    args = parser.parse_args()

    data = json.loads(args.result.read_text(encoding="utf-8"))
    tie_policy = str(data["tie_policy"])
    blocks: dict[int, dict[str, object]] = {}
    block_summary: list[dict[str, object]] = []
    for record in data["blocks"]:
        block = replay_block(record, tie_policy)
        blocks[int(record["k"])] = block
        block_summary.append({
            "k": block["k"],
            "D": len(block["offsets"]),
            "word_witnesses": block["word_witnesses"],
            "selected_color": block["selected_color"],
            "status": "verified",
        })

    for i in blocks:
        for j in blocks:
            if i < j:
                assert set(blocks[i]["U"]).isdisjoint(blocks[j]["U"])

    identity_summary = [audit_energy_identities(record, blocks) for record in data["energies"]]
    energy_summary: list[dict[str, object]] = []
    for record in data["energies"]:
        if record["status"] == "computed" and int(record["N"]) <= args.max_energy_pairs:
            energy_summary.append(replay_energy(record, blocks))

    output = {
        "schema": "C26-independent-replay-v1",
        "input": args.result.name,
        "method": "explicit multiset-word witnesses from x=9",
        "blocks": block_summary,
        "energy_identities": identity_summary,
        "energies": energy_summary,
        "all_membership_and_color_checks": True,
        "all_energy_identities": True,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
