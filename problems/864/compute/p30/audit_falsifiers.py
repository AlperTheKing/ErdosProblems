"""Independent exact audit for the P30 Ruzsa carry falsifiers.

This file intentionally imports no P12 or other P30 code.  It emits concrete
integer witnesses for centers that are hit and reruns the reflected census for
a delayed canonical carry hole.  Unordered pair sums always include diagonals.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Sequence


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
    raise AssertionError(p)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def crt_coordinate(index: int, exponential: int, p: int) -> int:
    return exponential + p * ((index - exponential) % (p - 1))


def cut_points(p: int, e: int) -> tuple[tuple[int, int], ...]:
    g = primitive_root(p)
    power = 1
    points: list[tuple[int, int]] = []
    for index in range(p - 1):
        exponential = (e * (power - 1)) % p
        points.append((crt_coordinate(index, exponential, p), index))
        power = (power * g) % p
    return tuple(sorted(points))


def support_maps(
    points: Sequence[tuple[int, int]],
) -> tuple[dict[int, tuple[int, int]], dict[int, tuple[int, int]]]:
    sums: dict[int, tuple[int, int]] = {}
    differences: dict[int, tuple[int, int]] = {}
    for i, (x, hx) in enumerate(points):
        for y, hy in points[i:]:
            value = x + y
            if value in sums:
                raise AssertionError(("sum collision", value))
            sums[value] = (hx, hy)
        for y, hy in points[i + 1 :]:
            value = y - x
            if value in differences:
                raise AssertionError(("difference collision", value))
            differences[value] = (hy, hx)

    size = len(points)
    if len(sums) != size * (size + 1) // 2:
        raise AssertionError("diagonal-aware sum support has wrong size")
    if len(differences) != size * (size - 1) // 2:
        raise AssertionError("difference support has wrong size")
    return sums, differences


def hit_witness(p: int, e: int, center: int) -> dict[str, object] | None:
    points = cut_points(p, e)
    by_index = {index: value for value, index in points}
    sums, differences = support_maps(points)
    for pair_sum, (a, b) in sums.items():
        difference = center - pair_sum
        if difference not in differences:
            continue
        c, d = differences[difference]
        values = (by_index[a], by_index[b], by_index[c], by_index[d])
        if values[0] + values[1] + values[2] - values[3] != center:
            raise AssertionError((p, e, center, a, b, c, d, values))
        return {
            "indices": [a, b, c, d],
            "values": list(values),
            "pair_diagonal": a == b,
            "difference_positive": values[2] > values[3],
        }
    return None


def audit_all_cut_hits(p: int, numerator: int, denominator: int) -> dict[str, object]:
    modulus = p * (p - 1)
    offset = (numerator * modulus) // denominator
    center = 2 * modulus + offset
    witnesses: list[dict[str, object]] = []
    diagonal_count = 0
    for e in range(1, p):
        witness = hit_witness(p, e, center)
        if witness is None:
            raise AssertionError(("unexpected fixed-center hole", p, e, center))
        diagonal_count += int(bool(witness["pair_diagonal"]))
        witnesses.append({"e": e, **witness})
    return {
        "p": p,
        "offset": f"{numerator}/{denominator}",
        "center": center,
        "cuts": p - 1,
        "hit_cuts": len(witnesses),
        "diagonal_witness_count": diagonal_count,
        "first_witness": witnesses[0],
        "last_witness": witnesses[-1],
    }


def first_hole_and_reflection(p: int, e: int) -> dict[str, object]:
    points_with_indices = cut_points(p, e)
    points = tuple(value for value, _ in points_with_indices)
    sums, differences = support_maps(points_with_indices)

    sum_bits = 0
    for pair_sum in sums:
        sum_bits |= 1 << pair_sum
    forbidden = 0
    for difference in differences:
        forbidden |= sum_bits << difference

    span = points[-1]
    lo = 2 * span + 1
    hi = 3 * (p - 1) * (p - 1) - 1
    center = next(
        value for value in range(lo, hi + 1) if ((forbidden >> value) & 1) == 0
    )
    if any(((forbidden >> value) & 1) == 0 for value in range(lo, center)):
        raise AssertionError("reported center is not the first hole")

    reflected = sorted(set(points) | {center - value for value in points})
    reflected_counts: Counter[int] = Counter()
    for i, x in enumerate(reflected):
        for y in reflected[i:]:
            reflected_counts[x + y] += 1
    repeats = sorted(
        (value, count) for value, count in reflected_counts.items() if count > 1
    )
    if repeats != [(center, p - 1)]:
        raise AssertionError((p, e, center, repeats))

    return {
        "p": p,
        "e": e,
        "span": span,
        "search_lo": lo,
        "search_hi": hi,
        "first_hole": center,
        "first_hole_over_size2": f"{center}/{(p - 1) ** 2}",
        "reflected_size": len(reflected),
        "repeated_sums": repeats,
    }


def difference_rectangle(p: int, e: int) -> dict[str, object]:
    modulus = p * (p - 1)
    values = [value for value, _ in cut_points(p, e)]
    actual = {
        (x - y) % modulus
        for x in values
        for y in values
        if x != y
    }
    expected = {
        residue
        for residue in range(1, modulus)
        if residue % (p - 1) != 0 and residue % p != 0
    }
    if actual != expected:
        raise AssertionError((p, len(actual - expected), len(expected - actual)))
    return {
        "p": p,
        "e": e,
        "actual_size": len(actual),
        "expected_size": (p - 1) * (p - 2),
        "missing_nonzero": modulus - 1 - len(actual),
    }


def modular_surface_minimum(p: int) -> dict[str, object]:
    minimum = None
    argmin = None
    for lam in range(1, p):
        for target in range(p):
            count = 0
            for x in range(1, p):
                for y in range(1, p):
                    for z in range(1, p):
                        if (x + y + z - lam * x * y * z - target) % p == 0:
                            count += 1
            if minimum is None or count < minimum:
                minimum = count
                argmin = (lam, target)
    bound = (p - 1) * (p - 3)
    if minimum is None or minimum < bound:
        raise AssertionError((p, minimum, bound, argmin))
    return {
        "p": p,
        "minimum_surface_count": minimum,
        "lower_bound": bound,
        "argmin": argmin,
    }


def singular_rule_witness() -> dict[str, object]:
    p = 19
    r = (2 * p) // 3
    e = (r * pow(4, -1, p)) % p
    modulus = p * (p - 1)
    center = 2 * modulus + (p - 1) * r
    witness = hit_witness(p, e, center)
    if witness is None:
        raise AssertionError("singular rule unexpectedly gives a hole")
    return {
        "p": p,
        "r": r,
        "e": e,
        "center": center,
        "crt_index_coordinate": center % (p - 1),
        "cayley_parameter": -2,
        "witness": witness,
    }


def singular_rule_scan() -> dict[str, object]:
    holes: list[int] = []
    hits: list[int] = []
    for p in range(5, 258):
        if not is_prime(p):
            continue
        r = (2 * p) // 3
        e = (r * pow(4, -1, p)) % p
        modulus = p * (p - 1)
        center = 2 * modulus + (p - 1) * r
        if hit_witness(p, e, center) is None:
            holes.append(p)
        else:
            hits.append(p)
    return {
        "prime_max": 257,
        "hole_primes": holes,
        "hit_count": len(hits),
        "first_hit_primes": hits[:12],
        "all_primes_at_least_19_hit": all(
            p in hits for p in range(19, 258) if is_prime(p)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = {
        "fixed_two_thirds_p71": audit_all_cut_hits(71, 2, 3),
        "fixed_four_fifths_p191": audit_all_cut_hits(191, 4, 5),
        "singular_two_thirds_p19": singular_rule_witness(),
        "singular_two_thirds_scan": singular_rule_scan(),
        "delayed_canonical_p199": first_hole_and_reflection(199, 198),
        "difference_rectangles": [
            difference_rectangle(19, 1),
            difference_rectangle(71, 70),
        ],
        "surface_minima": [
            modular_surface_minimum(5),
            modular_surface_minimum(7),
            modular_surface_minimum(11),
        ],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="ascii")


if __name__ == "__main__":
    main()
