"""Exact checks for the C111 Gate-T divisor-moment tail lemma.

The finite checks use Python integers only.  The asymptotic passage from the
nonasymptotic integer inequality is proved in the accompanying report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path


Q = 360
RAY = (3, 2, 1)
FULL_STATE = (6, 4, 2)


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


def layers(states: dict[tuple[int, int, int], set[int]]) -> dict[int, dict[str, object]]:
    answer: dict[int, dict[str, object]] = {}
    for k in (1, 2):
        ds = sorted(states[3 * k, 2 * k, k])
        hs = [8 * Q**k + d + 1 for d in ds]
        counts = Counter(h % 3 for h in hs)
        assert counts[1] == 0
        rho = 2 if counts[2] >= counts[0] else 0
        selected_pairs = [(d, h) for d, h in zip(ds, hs, strict=True) if h % 3 == rho]
        selected_ds = [d for d, _ in selected_pairs]
        selected_hs = [h for _, h in selected_pairs]
        us = [2 * h - 1 if rho == 2 else 4 * h - 3 for h in selected_hs]
        vs = [3 * h - 1 for h in selected_hs]
        assert len(us) == len(vs) == len(set(us)) == len(set(vs))
        assert all(u % 2 == 1 and u % 3 == 0 for u in us)
        assert all(v % 3 == 2 for v in vs)
        answer[k] = {"D": len(ds), "rho": rho, "offsets": selected_ds, "U": us, "V": vs}
    assert answer[1]["D"] == 60 and len(answer[1]["U"]) == 36
    assert answer[2]["D"] == 13068 and len(answer[2]["U"]) == 7779
    return answer


def valuation(n: int, prime: int) -> int:
    exponent = 0
    while n % prime == 0:
        n //= prime
        exponent += 1
    return exponent


def primes_through(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [p for p in range(2, limit + 1) if sieve[p]]


def tau(n: int, primes: list[int]) -> int:
    answer = 1
    remaining = n
    for p in primes:
        if p * p > remaining:
            break
        exponent = 0
        while remaining % p == 0:
            remaining //= p
            exponent += 1
        if exponent:
            answer *= exponent + 1
    if remaining > 1:
        answer *= 2
    return answer


def stripped(n: int) -> int:
    for p in (2, 3):
        while n % p == 0:
            n //= p
    return n


def ceil_log2(n: int) -> int:
    assert n >= 1
    return (n - 1).bit_length()


def word_offset(word: tuple[int, ...]) -> int:
    d = 0
    for multiplier in word:
        d = multiplier * d + (multiplier - 2)
    return d


def exact_envelope(K: int, q: int) -> int:
    j_k = 1 + ceil_log2(36 * Q**K)
    return 3888 * 6**K * j_k ** (2 * (2**q - 1))


def fibre_counter(layer_data: dict[int, dict[str, object]], K: int) -> Counter[int]:
    products: Counter[int] = Counter()
    for i in range((K + 2) // 3, 2 * K // 3 + 1):
        us = layer_data[i]["U"]
        vs = layer_data[K - i]["V"]
        assert isinstance(us, list) and isinstance(vs, list)
        products.update(u * v for u in us for v in vs)
    return products


def moment_kernel_checks() -> list[dict[str, int]]:
    rows = []
    for q in range(1, 9):
        m = 2**q
        minimum_margin: int | None = None
        minimum_e = -1
        for e in range(0, 257):
            margin = math.comb(e + m - 1, m - 1) - (e + 1) ** q
            assert margin >= 0
            if minimum_margin is None or margin < minimum_margin:
                minimum_margin = margin
                minimum_e = e
        assert minimum_margin is not None
        rows.append({"q": q, "m": m, "checked_exponent_max": 256,
                     "minimum_margin": minimum_margin, "minimum_at_e": minimum_e})
    return rows


def finite_tail_checks(
    layer_data: dict[int, dict[str, object]], collision_data: dict[str, object]
) -> tuple[list[dict[str, object]], dict[int, Counter[int]]]:
    products_by_k = {K: fibre_counter(layer_data, K) for K in (2, 3)}
    published_hist = {int(r): int(count) for r, count in collision_data["histogram"].items()}
    products_by_k[4] = Counter(published_hist)

    max_factor = max(max(layer_data[2]["U"]), max(layer_data[2]["V"]))
    primes = primes_through(math.isqrt(max_factor) + 1)
    tau_by_layer: dict[tuple[int, str], list[int]] = {}
    for k in (1, 2):
        for side in ("U", "V"):
            values = layer_data[k][side]
            assert isinstance(values, list)
            tau_by_layer[k, side] = [tau(value, primes) for value in values]

    # Check the label-preserving divisor bridge on every K=2,3 product.
    for products in products_by_k.values():
        if products is products_by_k[4]:
            continue
        for z, multiplicity in products.items():
            assert multiplicity <= tau(stripped(z), primes)

    rows: list[dict[str, object]] = []
    for K in (2, 3, 4):
        if K < 4:
            multiplicity_hist = Counter(products_by_k[K].values())
            edge_count = sum(products_by_k[K].values())
        else:
            multiplicity_hist = products_by_k[4]
            edge_count = int(collision_data["edges"])
        assert edge_count in (1296, 560088, 60512841)
        for q in (1, 2, 3, 4):
            actual_moment_sum = 0
            for i in range((K + 2) // 3, 2 * K // 3 + 1):
                actual_moment_sum += sum(x**q for x in tau_by_layer[i, "U"]) * sum(
                    x**q for x in tau_by_layer[K - i, "V"]
                )
            envelope = exact_envelope(K, q)
            assert actual_moment_sum <= envelope * edge_count
            for cutoff in (1, 2, 3):
                tail = sum(r * count for r, count in multiplicity_hist.items() if r > cutoff)
                assert tail * cutoff**q <= actual_moment_sum
                assert tail * cutoff**q <= envelope * edge_count
                rows.append(
                    {
                        "K": K,
                        "q": q,
                        "cutoff": cutoff,
                        "tail_edge_mass": tail,
                        "edges": edge_count,
                        "actual_divisor_moment_sum": str(actual_moment_sum),
                        "integer_envelope": str(envelope),
                    }
                )
    return rows, products_by_k


def suffix_audit(
    states: dict[tuple[int, int, int], set[int]], collision_data: dict[str, object]
) -> dict[str, object]:
    @lru_cache(maxsize=None)
    def word_witness(a: int, b: int, c: int, d: int) -> tuple[int, ...]:
        if (a, b, c) == (0, 0, 0):
            assert d == 0
            return ()
        candidates = (
            (2, a > 0 and d % 2 == 0, (a - 1, b, c), d // 2 if d % 2 == 0 else -1),
            (3, b > 0 and (d - 1) % 3 == 0, (a, b - 1, c), (d - 1) // 3),
            (5, c > 0 and (d - 3) % 5 == 0, (a, b, c - 1), (d - 3) // 5),
        )
        for multiplier, congruent, predecessor_state, predecessor in candidates:
            if congruent and min(predecessor_state) >= 0 and predecessor in states[predecessor_state]:
                return word_witness(*predecessor_state, predecessor) + (multiplier,)
        raise AssertionError("reachable offset has no predecessor")

    @lru_cache(maxsize=None)
    def suffixes(a: int, b: int, c: int, d: int, depth: int) -> frozenset[tuple[int, ...]]:
        if depth == 0:
            return frozenset({()})
        answers: set[tuple[int, ...]] = set()
        candidates = (
            (2, a > 0 and d % 2 == 0, (a - 1, b, c), d // 2 if d % 2 == 0 else -1),
            (3, b > 0 and (d - 1) % 3 == 0, (a, b - 1, c), (d - 1) // 3),
            (5, c > 0 and (d - 3) % 5 == 0, (a, b, c - 1), (d - 3) // 5),
        )
        for multiplier, congruent, predecessor_state, predecessor in candidates:
            if not congruent or min(predecessor_state) < 0:
                continue
            if predecessor not in states[predecessor_state]:
                continue
            for prefix in suffixes(*predecessor_state, predecessor, depth - 1):
                answers.add(prefix + (multiplier,))
        assert answers
        return frozenset(answers)

    depth_rows = []
    witness = None
    fibres = collision_data["fibres"]
    assert isinstance(fibres, list)
    for depth in range(1, 7):
        ambiguous_pairs = 0
        ambiguous_fibres = 0
        for fibre in fibres:
            edges = fibre["edges"]
            fibre_ambiguous = False
            for first, second in combinations(edges, 2):
                left_common = suffixes(*FULL_STATE, int(first["left_offset"]), depth) & suffixes(
                    *FULL_STATE, int(second["left_offset"]), depth
                )
                right_common = suffixes(*FULL_STATE, int(first["right_offset"]), depth) & suffixes(
                    *FULL_STATE, int(second["right_offset"]), depth
                )
                if left_common and right_common:
                    ambiguous_pairs += 1
                    fibre_ambiguous = True
                    if depth == 6 and witness is None:
                        left_suffix = min(left_common)
                        right_suffix = min(right_common)

                        def extend(offset: int, suffix: tuple[int, ...]) -> list[int]:
                            predecessor = offset
                            counts = Counter(suffix)
                            for multiplier in reversed(suffix):
                                addend = multiplier - 2
                                assert (predecessor - addend) % multiplier == 0
                                predecessor = (predecessor - addend) // multiplier
                            remaining = (
                                FULL_STATE[0] - counts[2],
                                FULL_STATE[1] - counts[3],
                                FULL_STATE[2] - counts[5],
                            )
                            assert predecessor in states[remaining]
                            word = word_witness(*remaining, predecessor) + suffix
                            assert tuple(Counter(word)[m] for m in (2, 3, 5)) == FULL_STATE
                            assert word_offset(word) == offset
                            return list(word)

                        witness = {
                            "product": fibre["product"],
                            "first": first,
                            "second": second,
                            "common_left_suffix": list(left_suffix),
                            "common_right_suffix": list(right_suffix),
                            "first_left_word": extend(int(first["left_offset"]), left_suffix),
                            "second_left_word": extend(int(second["left_offset"]), left_suffix),
                            "first_right_word": extend(int(first["right_offset"]), right_suffix),
                            "second_right_word": extend(int(second["right_offset"]), right_suffix),
                        }
            ambiguous_fibres += int(fibre_ambiguous)
        depth_rows.append(
            {"suffix_depth": depth, "ambiguous_collision_pairs": ambiguous_pairs,
             "ambiguous_fibres": ambiguous_fibres}
        )
    assert witness is not None
    return {"depth_rows": depth_rows, "six_letter_witness": witness,
            "meaning": "Both representations admit the same exact suffix word on each factor."}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    collision_data = json.loads(args.collisions.read_text(encoding="ascii"))
    assert collision_data["ray"] == [3, 2, 1]
    assert collision_data["edges"] == 60512841
    assert collision_data["histogram"] == {"1": 60480975, "2": 15927, "3": 4}

    states = offset_states(*FULL_STATE)
    layer_data = layers(states)
    kernel_rows = moment_kernel_checks()
    tail_rows, products_by_k = finite_tail_checks(layer_data, collision_data)
    suffix_result = suffix_audit(states, collision_data)

    result = {
        "status": "PASS",
        "ray": list(RAY),
        "Q": Q,
        "exact_tail_gate": (
            "tail(K,T)/N_K <= 3888*6^K*J_K^(2*(2^q-1))/T^q, "
            "J_K=1+ceil(log2(36*360^K))"
        ),
        "moment_kernel_checks": kernel_rows,
        "small_fibre_rows": [
            {"K": K, "edges": sum(products.values()), "support": len(products),
             "max_multiplicity": max(products.values())}
            for K, products in products_by_k.items() if K < 4
        ],
        "finite_tail_checks": tail_rows,
        "suffix_audit": suffix_result,
        "collision_source_sha256": sha256(args.collisions),
        "source_sha256": sha256(Path(__file__)),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"wrote {args.output}")
    print(f"sha256 {sha256(args.output)}")
    print(json.dumps(suffix_result, sort_keys=True))


if __name__ == "__main__":
    main()
