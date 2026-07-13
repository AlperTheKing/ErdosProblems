"""Exact finite algebraic-lift scans for P48."""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence

from audit_core import (
    best_lift_record,
    is_costas,
    is_sidon,
    normalize,
    pair_sum_collision,
    prime_factors,
    primes_through,
    primitive_root,
    ratio_record,
    signed_set,
    first_signed_gap,
    valid_same_parity_set,
)


def step_carry_parabola(p: int, a: int, b: int) -> tuple[int, ...]:
    return normalize(
        x + p * ((x * x) % p + (a * x + b) // p)
        for x in range(p)
    )


def parabola_carry_audit(max_prime: int) -> dict[str, object]:
    rows = []
    for p in [q for q in primes_through(max_prime) if q % 2 == 1]:
        compact = normalize(x + p * ((x * x) % p) for x in range(p))
        compact_collision = pair_sum_collision(compact)
        carry_free = normalize(x + 2 * p * ((x * x) % p) for x in range(p))
        assert is_sidon(carry_free)

        survivors = []
        for a in range(p):
            for b in range(p):
                ruler = step_carry_parabola(p, a, b)
                if not is_sidon(ruler):
                    continue
                gap = first_signed_gap(ruler)
                values = signed_set(ruler, gap)
                assert valid_same_parity_set(values)
                survivors.append(
                    {
                        "a": a,
                        "b": b,
                        "G": gap,
                        "W": ruler[-1],
                        "M": values[-1],
                        "ratio": ratio_record(values[-1], p * p),
                        "ruler": ruler,
                    }
                )
        survivors.sort(key=lambda row: (row["M"], row["a"], row["b"]))
        rows.append(
            {
                "p": p,
                "compact_sidon": compact_collision is None,
                "compact_collision": compact_collision,
                "carry_free_W": carry_free[-1],
                "carry_free_lower_ratio": ratio_record(2 * carry_free[-1] + 1, p * p),
                "affine_step_survivors": len(survivors),
                "best_step_survivor": survivors[0] if survivors else None,
            }
        )
    return {"max_prime": max_prime, "rows": rows}


def gf2_mul(
    x: tuple[int, int], y: tuple[int, int], p: int, d: int
) -> tuple[int, int]:
    return (
        (x[0] * y[0] + d * x[1] * y[1]) % p,
        (x[0] * y[1] + x[1] * y[0]) % p,
    )


def gf2_pow(
    x: tuple[int, int], exponent: int, p: int, d: int
) -> tuple[int, int]:
    out = (1, 0)
    while exponent:
        if exponent & 1:
            out = gf2_mul(out, x, p, d)
        x = gf2_mul(x, x, p, d)
        exponent >>= 1
    return out


def bose_prime(p: int) -> tuple[int, tuple[int, ...]]:
    d = next(x for x in range(2, p) if pow(x, (p - 1) // 2, p) == p - 1)
    order = p * p - 1
    factors = prime_factors(order)
    gamma = next(
        (a, b)
        for a in range(p)
        for b in range(p)
        if (a, b) != (0, 0)
        and all(
            gf2_pow((a, b), order // r, p, d) != (1, 0)
            for r in factors
        )
    )
    residues = []
    power = (1, 0)
    for exponent in range(order):
        if power[1] == gamma[1]:
            residues.append(exponent)
        power = gf2_mul(power, gamma, p, d)
    assert len(residues) == p
    return order, tuple(residues)


def modular_sidon(values: Sequence[int], modulus: int) -> bool:
    sums = [
        (values[i] + values[j]) % modulus
        for i in range(len(values))
        for j in range(i, len(values))
    ]
    return len(sums) == len(set(sums))


def bounded_height_lifts(
    residues: Sequence[int], modulus: int, heights: Sequence[int]
) -> tuple[int, dict[str, object]]:
    best: tuple[int, dict[str, object]] | None = None
    checked = 0
    for tail in itertools.product(heights, repeat=len(residues) - 1):
        placement = (0,) + tail
        ruler = normalize(c + modulus * h for c, h in zip(residues, placement))
        record = best_lift_record(ruler)
        checked += 1
        if best is None or record["M"] < best[0]:
            record["heights"] = placement
            best = (record["M"], record)
    assert best is not None
    return checked, best[1]


def bose_audit(max_prime: int) -> dict[str, object]:
    rows = []
    for p in [q for q in primes_through(max_prime) if q % 2 == 1]:
        modulus, residues = bose_prime(p)
        assert modular_sidon(residues, modulus)
        best: tuple[int, dict[str, object]] | None = None
        lifts = 0
        for unit in range(1, modulus):
            if math.gcd(unit, modulus) != 1:
                continue
            affine = tuple((unit * c) % modulus for c in residues)
            for cut in affine:
                ruler = tuple(sorted((c - cut) % modulus for c in affine))
                record = best_lift_record(ruler)
                record.update({"unit": unit, "cut": cut})
                lifts += 1
                if best is None or record["M"] < best[0]:
                    best = (record["M"], record)
        assert best is not None
        height_scan = None
        if p <= 7:
            checked, height_best = bounded_height_lifts(
                residues, modulus, (-1, 0, 1)
            )
            height_scan = {"placements": checked, "best": height_best}
        rows.append(
            {
                "p": p,
                "modulus": modulus,
                "residues": residues,
                "affine_cuts": lifts,
                "best_affine_cut": best[1],
                "ternary_height_scan": height_scan,
            }
        )
    return {"max_prime": max_prime, "rows": rows}


def ruzsa_residues(p: int) -> tuple[int, tuple[int, ...]]:
    g = primitive_root(p)
    modulus = p * (p - 1)
    residues = tuple(
        pow(g, i, p) + p * ((i - pow(g, i, p)) % (p - 1))
        for i in range(p - 1)
    )
    assert len(set(residues)) == p - 1
    assert modular_sidon(residues, modulus)
    return modulus, residues


def ruzsa_audit(max_prime: int) -> dict[str, object]:
    rows = []
    for p in [q for q in primes_through(max_prime) if q >= 5]:
        modulus, residues = ruzsa_residues(p)
        records = []
        for cut in residues:
            ruler = tuple(sorted((c - cut) % modulus for c in residues))
            record = best_lift_record(ruler)
            record["cut"] = cut
            records.append(record)
        records.sort(key=lambda row: (row["M"], row["cut"]))
        height_scan = None
        if p <= 7:
            checked, height_best = bounded_height_lifts(
                residues, modulus, (-1, 0, 1)
            )
            height_scan = {"placements": checked, "best": height_best}
        rows.append(
            {
                "p": p,
                "points": p - 1,
                "modulus": modulus,
                "natural_cuts": len(records),
                "best_natural_cut": records[0],
                "worst_natural_cut": records[-1],
                "ternary_height_scan": height_scan,
            }
        )
    return {"max_prime": max_prime, "rows": rows}


def welch_audit(max_prime: int) -> dict[str, object]:
    rows = []
    radices_tested = 0
    sidon_flattenings = 0
    for q in [p for p in primes_through(max_prime) if p >= 5]:
        n = q - 1
        g = primitive_root(q)
        base = tuple(pow(g, i, q) - 1 for i in range(n))
        best: tuple[int, dict[str, object]] | None = None
        for shift in range(n):
            permutation = tuple(base[(i + shift) % n] for i in range(n))
            assert is_costas(permutation)
            radices = sorted({n - 1, n, n + 1, 2 * n - 1, 2 * n})
            for radix in radices:
                for orientation in range(2):
                    if orientation == 0:
                        raw = tuple(
                            i + radix * permutation[i] for i in range(n)
                        )
                    else:
                        raw = tuple(
                            radix * i + permutation[i] for i in range(n)
                        )
                    radices_tested += 1
                    if len(set(raw)) != n:
                        continue
                    ruler = normalize(raw)
                    if not is_sidon(ruler):
                        continue
                    sidon_flattenings += 1
                    record = best_lift_record(ruler)
                    record.update(
                        {
                            "shift": shift,
                            "radix": radix,
                            "orientation": orientation,
                        }
                    )
                    if best is None or record["M"] < best[0]:
                        best = (record["M"], record)
        rows.append(
            {
                "q": q,
                "points": n,
                "best": None if best is None else best[1],
            }
        )
    return {
        "max_prime": max_prime,
        "radix_flattenings": radices_tested,
        "sidon_flattenings": sidon_flattenings,
        "rows": rows,
    }
