"""Targeted CRT/carry scan for the Ruzsa lane of Erdos Problem 864.

This script only studies the natural Ruzsa set and the canonical cyclic cuts
whose base has exponential coordinate e=1 or e=-1.  It includes diagonal
pair sums in every Sidon and reflected-admissibility check.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_factors(n: int) -> tuple[int, ...]:
    out: list[int] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return tuple(out)


def primitive_root(p: int) -> int:
    factors = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g
    raise AssertionError(f"no primitive root modulo {p}")


def crt_coordinate(index: int, exponential: int, p: int) -> int:
    """Least x with x=index mod p-1 and x=exponential mod p."""
    return exponential + p * ((index - exponential) % (p - 1))


def ruzsa_residues(p: int, g: int) -> tuple[int, ...]:
    return tuple(crt_coordinate(i, pow(g, i, p), p) for i in range(p - 1))


def unordered_sums(values: Sequence[int]) -> Counter[int]:
    return Counter(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def modular_unordered_sums(values: Sequence[int], modulus: int) -> Counter[int]:
    return Counter(
        (values[i] + values[j]) % modulus
        for i in range(len(values))
        for j in range(i, len(values))
    )


def first_zero(bits: int, lo: int, hi: int) -> int | None:
    for value in range(lo, hi + 1):
        if ((bits >> value) & 1) == 0:
            return value
    return None


def reflected_check(points: Sequence[int], center: int) -> dict[str, object]:
    reflected = sorted(set(points) | {center - x for x in points})
    counts = unordered_sums(reflected)
    repeats = sorted((value, count) for value, count in counts.items() if count > 1)
    return {
        "size": len(reflected),
        "repeated_sums": repeats,
        "admissible": repeats == [(center, len(points))],
    }


def modular_cover(values: Sequence[int], modulus: int) -> dict[str, object]:
    pair_bits = 0
    for a in values:
        for b in values:
            pair_bits |= 1 << ((a + b) % modulus)

    differences = {(a - b) % modulus for a in values for b in values}
    mask = (1 << modulus) - 1
    cover = 0
    for difference in differences:
        if difference == 0:
            shifted = pair_bits
        else:
            shifted = (
                (pair_bits << difference) | (pair_bits >> (modulus - difference))
            ) & mask
        cover |= shifted
        if cover == mask:
            break

    holes = [
        residue
        for residue in range(modulus)
        if ((cover >> residue) & 1) == 0
    ]
    return {
        "pair_sum_support": pair_bits.bit_count(),
        "difference_support": len(differences),
        "three_c_minus_c_coverage": cover.bit_count(),
        "three_c_minus_c_hole_count": len(holes),
        "three_c_minus_c_first_holes": holes[:12],
    }


def analyze_cut(
    p: int,
    g: int,
    residues: Sequence[int],
    base_index: int,
) -> dict[str, object]:
    modulus = p * (p - 1)
    size = p - 1
    base = residues[base_index]
    points = tuple(sorted((value - base) % modulus for value in residues))
    if points[0] != 0:
        raise AssertionError("cut is not normalized")

    modular_counts = modular_unordered_sums(points, modulus)
    literal_counts = unordered_sums(points)
    if max(modular_counts.values(), default=0) != 1:
        raise AssertionError((p, base_index, "modular Sidon failure"))
    if max(literal_counts.values(), default=0) != 1:
        raise AssertionError((p, base_index, "literal Sidon failure"))

    sum_bits = 0
    for value in literal_counts:
        sum_bits |= 1 << value
    differences = {
        points[j] - points[i]
        for i in range(size)
        for j in range(i + 1, size)
    }
    if len(differences) != size * (size - 1) // 2:
        raise AssertionError((p, base_index, "positive difference collision"))

    forbidden = 0
    for difference in differences:
        forbidden |= sum_bits << difference

    span = points[-1]
    lo = 2 * span + 1
    hi = 3 * size * size - 1
    center = first_zero(forbidden, lo, hi)
    predecessor = max((value for value in residues if value < base), default=max(residues))
    cut_gap = (base - predecessor) % modulus

    record: dict[str, object] = {
        "p": p,
        "primitive_root": g,
        "modulus": modulus,
        "size": size,
        "base_index": base_index,
        "base_exponential": pow(g, base_index, p),
        "cut_base": base,
        "cut_gap": cut_gap,
        "span": span,
        "modular_unordered_sum_support": len(modular_counts),
        "literal_unordered_sum_support": len(literal_counts),
        "positive_difference_support": len(differences),
        "first_center_below_3size2": center,
    }
    if center is not None:
        check = reflected_check(points, center)
        if not check["admissible"]:
            raise AssertionError((p, base_index, center, check))
        record.update(
            {
                "center_over_size2": str(Fraction(center, size * size)),
                "hole_offset_above_2span": center - 2 * span,
                "center_layer": center // modulus,
                "center_residue": center % modulus,
                "center_mod_p": center % p,
                "center_mod_p_minus_1": center % (p - 1),
                "reflected_check": check,
            }
        )
    return record


def selected_primes(lo: int, hi: int) -> Iterable[int]:
    for p in range(max(5, lo), hi + 1):
        if is_prime(p):
            yield p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-min", type=int, default=5)
    parser.add_argument("--prime-max", type=int, default=257)
    parser.add_argument("--all-cuts", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    modular: list[dict[str, object]] = []
    for p in selected_primes(args.prime_min, args.prime_max):
        g = primitive_root(p)
        residues = ruzsa_residues(p, g)
        if len(set(residues)) != p - 1:
            raise AssertionError((p, "residue collision"))

        modular_counts = modular_unordered_sums(residues, p * (p - 1))
        if max(modular_counts.values(), default=0) != 1:
            raise AssertionError((p, "strong modular Sidon failure"))
        modular.append({"p": p, **modular_cover(residues, p * (p - 1))})

        indices: tuple[int, ...] | range = (
            range(p - 1) if args.all_cuts else (0, (p - 1) // 2)
        )
        for index in indices:
            record = analyze_cut(p, g, residues, index)
            records.append(record)
            print(
                f"p={p} e={record['base_exponential']} "
                f"L={record['span']} M={record['first_center_below_3size2']} "
                f"ratio={record.get('center_over_size2')}"
            )

    payload = {
        "prime_min": args.prime_min,
        "prime_max": args.prime_max,
        "cut_rule": (
            "all natural cyclic cuts"
            if args.all_cuts
            else "base exponential coordinate e in {1,-1}"
        ),
        "records": records,
        "modular_profiles": modular,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )


if __name__ == "__main__":
    main()
