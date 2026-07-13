#!/usr/bin/env python3
"""Exact support/duplicate verifier and adversarial constructions for P23.

All mathematical decisions in this file use integers. Decimal strings are
display-only fields derived after the exact comparisons have been made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


def canonical_set(values: Iterable[int]) -> tuple[int, ...]:
    values = tuple(values)
    if any(type(x) is not int for x in values):
        raise TypeError("set entries must be literal integers")
    result = tuple(sorted(values))
    if len(result) != len(set(result)):
        raise ValueError("set entries must be distinct")
    return result


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def decimal_text(value: Fraction, places: int = 12) -> str:
    with localcontext() as ctx:
        ctx.prec = places + 8
        answer = Decimal(value.numerator) / Decimal(value.denominator)
        return f"{answer:.{places}f}"


def set_sha256(a: Sequence[int]) -> str:
    payload = ",".join(str(x) for x in a).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def unordered_sum_counts(a: Sequence[int]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for i, x in enumerate(a):
        for y in a[i:]:
            counts[x + y] += 1
    return counts


def positive_difference_counts(a: Sequence[int]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for i, x in enumerate(a):
        for y in a[:i]:
            counts[x - y] += 1
    return counts


def verify_admissible(a: Iterable[int], ambient_n: int | None = None) -> dict:
    a = canonical_set(a)
    errors: list[str] = []
    if ambient_n is not None:
        if ambient_n <= 0:
            errors.append("ambient_n must be positive")
        if any(x < 0 or x >= ambient_n for x in a):
            errors.append("set is not contained in [0, ambient_n-1]")

    sums = unordered_sum_counts(a)
    repeated = sorted((s, count) for s, count in sums.items() if count >= 2)
    differences = positive_difference_counts(a)
    admissible = not errors and len(repeated) <= 1
    if admissible and any(count > 2 for count in differences.values()):
        errors.append("admissible set has a positive difference multiplicity above 2")
        admissible = False

    return {
        "admissible": admissible,
        "errors": errors,
        "size": len(a),
        "ambient_n": ambient_n,
        "min": a[0] if a else None,
        "max": a[-1] if a else None,
        "span": a[-1] - a[0] if a else 0,
        "unordered_pairs": len(a) * (len(a) + 1) // 2,
        "sum_support": len(sums),
        "repeated_sums": [[s, count] for s, count in repeated],
        "exceptional_sum": repeated[0][0] if len(repeated) == 1 else None,
        "exceptional_multiplicity": repeated[0][1] if len(repeated) == 1 else 0,
        "max_positive_difference_multiplicity": max(differences.values(), default=0),
        "duplicated_positive_differences": sum(
            1 for count in differences.values() if count == 2
        ),
    }


def support_size(a: Sequence[int], h: int) -> int:
    """Return |A - {0,...,h-1}| by the exact interval-union formula."""
    if h <= 0:
        raise ValueError("h must be positive")
    if not a:
        return 0
    return h + sum(min(h, y - x) for x, y in zip(a, a[1:]))


def support_size_explicit(a: Sequence[int], h: int) -> int:
    if h <= 0:
        raise ValueError("h must be positive")
    return len({x - t for x in a for t in range(h)})


def duplicate_mass_explicit(a: Sequence[int], h: int) -> int:
    """Return sum_{d<h} (h-d)(nu_A(d)-1), with no admissibility assumption."""
    if h <= 0:
        raise ValueError("h must be positive")
    differences = positive_difference_counts(a)
    return sum((h - d) * (count - 1) for d, count in differences.items() if d < h)


@dataclass(frozen=True)
class MetricEngine:
    a: tuple[int, ...]
    ambient_n: int
    gaps: tuple[int, ...]
    extra_labels: tuple[int, ...]
    extra_prefix: tuple[int, ...]
    weighted_prefix: tuple[int, ...]

    @classmethod
    def build(cls, a: Iterable[int], ambient_n: int) -> "MetricEngine":
        a = canonical_set(a)
        if ambient_n <= 0 or any(x < 0 or x >= ambient_n for x in a):
            raise ValueError("A must be contained in [0, ambient_n-1]")
        differences = positive_difference_counts(a)
        items = sorted((d, count - 1) for d, count in differences.items() if count > 1)
        labels = tuple(d for d, _ in items)
        extra_prefix = [0]
        weighted_prefix = [0]
        for d, extra in items:
            extra_prefix.append(extra_prefix[-1] + extra)
            weighted_prefix.append(weighted_prefix[-1] + d * extra)
        return cls(
            a=a,
            ambient_n=ambient_n,
            gaps=tuple(y - x for x, y in zip(a, a[1:])),
            extra_labels=labels,
            extra_prefix=tuple(extra_prefix),
            weighted_prefix=tuple(weighted_prefix),
        )

    def support(self, h: int) -> int:
        if h <= 0:
            raise ValueError("h must be positive")
        if not self.a:
            return 0
        return h + sum(min(h, gap) for gap in self.gaps)

    def duplicate_mass(self, h: int) -> int:
        if h <= 0:
            raise ValueError("h must be positive")
        index = bisect_left(self.extra_labels, h)
        return h * self.extra_prefix[index] - self.weighted_prefix[index]

    def metric(self, h: int) -> dict:
        m_h = self.support(h)
        z_h = self.duplicate_mass(h)
        h2 = h * h
        support_ratio = Fraction(m_h, self.ambient_n)
        duplicate_ratio = Fraction(z_h, h2)
        product = support_ratio * (1 + 2 * duplicate_ratio)
        margin = 3 * m_h * (h2 + 2 * z_h) - 4 * self.ambient_n * h2
        if (product > Fraction(4, 3)) != (margin > 0):
            raise AssertionError("integer margin and Fraction comparison disagree")
        return {
            "H": h,
            "M_H": m_h,
            "Z_H": z_h,
            "ambient_thickening_size": self.ambient_n + h - 1,
            "support_holes": self.ambient_n + h - 1 - m_h,
            "M_H_over_N": fraction_text(support_ratio),
            "M_H_over_N_decimal": decimal_text(support_ratio),
            "Z_H_over_H2": fraction_text(duplicate_ratio),
            "Z_H_over_H2_decimal": decimal_text(duplicate_ratio),
            "coupled_product": fraction_text(product),
            "coupled_product_decimal": decimal_text(product),
            "margin_over_4_3": margin,
            "product_gt_4_3": margin > 0,
            "product_eq_4_3": margin == 0,
        }


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors


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


def primitive_root(p: int) -> int:
    if not is_prime(p) or p < 3:
        raise ValueError("Ruzsa constructor requires an odd prime")
    factors = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p - 1) // factor, p) != 1 for factor in factors):
            return g
    raise AssertionError("primitive root not found")


def ruzsa_cyclic_sidon(p: int, g: int | None = None) -> tuple[int, tuple[int, ...], int]:
    """Return (m, C, g), where C is Sidon in Z/mZ and m=p(p-1)."""
    if not is_prime(p) or p < 3:
        raise ValueError("p must be an odd prime")
    if g is None:
        g = primitive_root(p)
    factors = prime_factors(p - 1)
    if not (1 < g < p) or any(pow(g, (p - 1) // factor, p) == 1 for factor in factors):
        raise ValueError("g is not a primitive root modulo p")
    modulus = p * (p - 1)
    values = []
    for x in range(1, p):
        gx = pow(g, x, p)
        value = gx + p * ((x - gx) % (p - 1))
        values.append(value % modulus)
    return modulus, canonical_set(values), g


def verify_cyclic_sidon(c: Sequence[int], modulus: int) -> dict:
    c = canonical_set(c)
    if modulus <= 0 or any(x < 0 or x >= modulus for x in c):
        raise ValueError("cyclic set must use least nonnegative residues")
    owner: dict[int, tuple[int, int]] = {}
    collision = None
    for x in c:
        for y in c:
            if x == y:
                continue
            difference = (x - y) % modulus
            if difference in owner:
                collision = [difference, list(owner[difference]), [x, y]]
                break
            owner[difference] = (x, y)
        if collision is not None:
            break
    return {
        "cyclic_sidon": collision is None,
        "modulus": modulus,
        "size": len(c),
        "oriented_nonzero_differences": len(owner),
        "collision": collision,
    }


def affine_phase(c: Sequence[int], modulus: int, unit: int, translation: int) -> tuple[int, ...]:
    if math.gcd(unit, modulus) != 1:
        raise ValueError("affine multiplier must be a unit modulo the modulus")
    return canonical_set((unit * x + translation) % modulus for x in c)


def compressed_congruence_reflection(
    c: Sequence[int], modulus: int, dilation: int = 2, core: Sequence[int] | None = None
) -> tuple[tuple[int, ...], int, int]:
    """Return A=B union (sigma-D), with B=dilation*C and D subset B.

    The center sigma=2*dilation*(modulus-1)+1 is not divisible by dilation.
    If C is Sidon and D is a subset of B, the resulting set is admissible.
    """
    c = canonical_set(c)
    if dilation < 2:
        raise ValueError("dilation must be at least 2")
    if any(x < 0 or x >= modulus for x in c):
        raise ValueError("C must lie in [0, modulus-1]")
    b = tuple(dilation * x for x in c)
    if core is None:
        d = b
    else:
        d = canonical_set(core)
        if not set(d).issubset(b):
            raise ValueError("core must be a subset of dilation*C")
    sigma = 2 * dilation * (modulus - 1) + 1
    a = canonical_set((*b, *(sigma - x for x in d)))
    return a, sigma + 1, sigma


def reflected_erdos_freud(c: Sequence[int]) -> tuple[tuple[int, ...], int, int]:
    c = canonical_set(c)
    if len(c) < 2:
        raise ValueError("base Sidon set must contain at least two points")
    base = tuple(x - c[0] for x in c)
    width = base[-1]
    sigma = 3 * width + 1
    a = canonical_set((*base, *(sigma - x for x in base)))
    return a, sigma + 1, sigma


def unbalanced_reflection(
    c: Sequence[int], core_indices: Sequence[int]
) -> tuple[tuple[int, ...], int, int]:
    c = canonical_set(c)
    base = tuple(x - c[0] for x in c)
    core = tuple(base[i] for i in core_indices)
    if len(core) < 2:
        raise ValueError("unbalanced reflected core must have at least two points")
    sigma = 3 * base[-1] + 1
    a = canonical_set((*base, *(sigma - x for x in core)))
    return a, sigma + 1, sigma


def inverse_conic(p: int) -> tuple[tuple[int, ...], int]:
    if not is_prime(p) or p % 2 == 0:
        raise ValueError("inverse conic requires an odd prime")
    original = [x + 2 * p * pow(x, -1, p) for x in range(1, p)]
    a = canonical_set(x - 1 for x in original)
    ambient_n = 2 * p * p - p - 1
    return a, ambient_n


def residue_multicluster_subset(c: Sequence[int], modulus: int, bins: int = 8) -> tuple[int, ...]:
    if bins < 4 or bins % 2:
        raise ValueError("bins must be an even integer at least 4")
    selected = tuple(x for x in c if ((x * bins) // modulus) % 2 == 0)
    if len(selected) < 2:
        raise ValueError("multicluster selection contains fewer than two points")
    return selected


def candidate_record(
    name: str,
    a: Sequence[int],
    ambient_n: int,
    h_values: Sequence[int],
    constructor: dict,
) -> dict:
    a = canonical_set(a)
    verification = verify_admissible(a, ambient_n)
    engine = MetricEngine.build(a, ambient_n)
    metrics = [engine.metric(h) for h in sorted(set(h_values))]
    return {
        "record_type": "candidate",
        "name": name,
        "constructor": constructor,
        "A": list(a),
        "A_sha256": set_sha256(a),
        "verification": verification,
        "metrics": metrics,
    }


def exact_exhaustive_search(ambient_n: int, h_values: Sequence[int]) -> dict:
    """Enumerate every admissible A with min(A)=0 and max(A)=ambient_n-1."""
    if ambient_n < 2:
        raise ValueError("ambient_n must be at least 2")
    h_values = tuple(sorted(set(h_values)))
    if not h_values or h_values[0] <= 0:
        raise ValueError("at least one positive H is required")

    a = [0]
    sum_counts: dict[int, int] = {0: 1}
    admissible_count = 0
    pruned_additions = 0
    best_by_h: dict[int, tuple[Fraction, tuple[int, ...], dict]] = {}
    best_minimax: tuple[Fraction, tuple[int, ...], list[dict]] | None = None

    def visit_leaf() -> None:
        nonlocal admissible_count, best_minimax
        if a[-1] != ambient_n - 1:
            return
        admissible_count += 1
        frozen = tuple(a)
        engine = MetricEngine.build(frozen, ambient_n)
        metrics = [engine.metric(h) for h in h_values]
        products = [Fraction(metric["coupled_product"]) for metric in metrics]
        minimax = min(products)
        if best_minimax is None or minimax > best_minimax[0]:
            best_minimax = (minimax, frozen, metrics)
        for h, product, metric in zip(h_values, products, metrics):
            current = best_by_h.get(h)
            if current is None or product > current[0]:
                best_by_h[h] = (product, frozen, metric)

    def recurse(x: int, repeated_labels: int) -> None:
        nonlocal pruned_additions
        if x == ambient_n:
            visit_leaf()
            return

        recurse(x + 1, repeated_labels)

        changed: list[tuple[int, int]] = []
        new_repeated = repeated_labels
        valid = True
        for old_point in (*a, x):
            pair_sum = x + old_point
            old_count = sum_counts.get(pair_sum, 0)
            sum_counts[pair_sum] = old_count + 1
            changed.append((pair_sum, old_count))
            if old_count == 1:
                new_repeated += 1
            if new_repeated > 1:
                valid = False
                break
        if valid:
            a.append(x)
            recurse(x + 1, new_repeated)
            a.pop()
        else:
            pruned_additions += 1
        for pair_sum, old_count in reversed(changed):
            if old_count:
                sum_counts[pair_sum] = old_count
            else:
                del sum_counts[pair_sum]

    recurse(1, 0)
    if best_minimax is None:
        raise AssertionError("endpoint-normalized domain unexpectedly empty")

    return {
        "record_type": "finite_exhaustive_certificate",
        "ambient_n": ambient_n,
        "domain": "all A subset [0,N-1] with min(A)=0 and max(A)=N-1",
        "total_endpoint_normalized_subsets": 1 << (ambient_n - 2),
        "admissible_endpoint_normalized_sets": admissible_count,
        "pruned_invalid_additions": pruned_additions,
        "H_values": list(h_values),
        "best_minimax": {
            "minimum_product": fraction_text(best_minimax[0]),
            "minimum_product_decimal": decimal_text(best_minimax[0]),
            "A": list(best_minimax[1]),
            "A_sha256": set_sha256(best_minimax[1]),
            "metrics": best_minimax[2],
        },
        "best_by_H": [
            {
                "H": h,
                "product": fraction_text(best_by_h[h][0]),
                "A": list(best_by_h[h][1]),
                "metric": best_by_h[h][2],
            }
            for h in h_values
        ],
    }


def self_test() -> dict:
    checked_sets = 0
    checked_profiles = 0
    for ambient_n in range(1, 9):
        for mask in range(1 << ambient_n):
            a = tuple(i for i in range(ambient_n) if mask & (1 << i))
            engine = MetricEngine.build(a, ambient_n)
            for h in range(1, ambient_n + 3):
                assert engine.support(h) == support_size_explicit(a, h)
                assert engine.duplicate_mass(h) == duplicate_mass_explicit(a, h)
                checked_profiles += 1
            checked_sets += 1

    seed = (0, 2, 3, 7, 16, 22, 31, 35, 36, 38)
    seed_check = verify_admissible(seed, 39)
    assert seed_check["admissible"]
    assert seed_check["repeated_sums"] == [[38, 5]]

    for p in (5, 7, 11, 23):
        modulus, c, g = ruzsa_cyclic_sidon(p)
        cyclic = verify_cyclic_sidon(c, modulus)
        assert cyclic["cyclic_sidon"]
        a, ambient_n, sigma = compressed_congruence_reflection(c, modulus, 2)
        check = verify_admissible(a, ambient_n)
        assert check["admissible"]
        assert check["repeated_sums"] == [[sigma, p - 1]]
        assert g == primitive_root(p)

    bad = verify_admissible((0, 1, 2, 3), 4)
    assert not bad["admissible"]
    return {
        "record_type": "self_test",
        "status": "PASS",
        "sets_checked": checked_sets,
        "profiles_checked": checked_profiles,
        "ruzsa_primes_checked": [5, 7, 11, 23],
        "compressed_seed_checked": True,
        "nonadmissible_control_checked": True,
    }


def affine_scan_record(p: int, h_values: Sequence[int]) -> dict:
    modulus, c, g = ruzsa_cyclic_sidon(p)
    units = [u for u in range(1, modulus) if math.gcd(u, modulus) == 1][:16]
    translations = sorted({0, modulus // 7, 2 * modulus // 7, modulus // 2})
    winner = None
    scanned = 0
    for unit in units:
        for translation in translations:
            phase = affine_phase(c, modulus, unit, translation)
            a, ambient_n, sigma = compressed_congruence_reflection(phase, modulus, 2)
            engine = MetricEngine.build(a, ambient_n)
            metrics = [engine.metric(h) for h in h_values]
            score = min(Fraction(metric["coupled_product"]) for metric in metrics)
            scanned += 1
            if winner is None or score > winner[0]:
                winner = (score, unit, translation, a, ambient_n, sigma, metrics)
    assert winner is not None
    score, unit, translation, a, ambient_n, sigma, metrics = winner
    check = verify_admissible(a, ambient_n)
    if not check["admissible"]:
        raise AssertionError("affine scan produced an inadmissible winner")
    return {
        "record_type": "affine_phase_scan",
        "prime": p,
        "primitive_root": g,
        "modulus": modulus,
        "units": units,
        "translations": translations,
        "candidates_scanned": scanned,
        "H_values": list(h_values),
        "winning_minimum_product": fraction_text(score),
        "winning_unit": unit,
        "winning_translation": translation,
        "sigma": sigma,
        "A": list(a),
        "A_sha256": set_sha256(a),
        "verification": check,
        "metrics": metrics,
    }


def certificate_suite(primes: Sequence[int]) -> list[dict]:
    records: list[dict] = [self_test()]
    seed = (0, 2, 3, 7, 16, 22, 31, 35, 36, 38)
    records.append(
        candidate_record(
            "finite_compressed_reflection_seed",
            seed,
            39,
            (4, 7, 10),
            {"source": "P05", "base": [0, 2, 3, 7, 16], "sigma": 38},
        )
    )

    for p in primes:
        modulus, c, g = ruzsa_cyclic_sidon(p)
        cyclic = verify_cyclic_sidon(c, modulus)
        if not cyclic["cyclic_sidon"]:
            raise AssertionError("Ruzsa construction failed cyclic Sidon check")
        h0 = p * math.isqrt(p)
        h_values = sorted({h0, min(2 * h0, modulus // 4)})
        a, ambient_n, sigma = compressed_congruence_reflection(c, modulus, 2)
        records.append(
            candidate_record(
                f"ruzsa_parity_compressed_p{p}",
                a,
                ambient_n,
                h_values,
                {
                    "family": "Ruzsa cyclic Sidon, dilation 2, odd compressed center",
                    "prime": p,
                    "primitive_root": g,
                    "modulus": modulus,
                    "sigma": sigma,
                    "cyclic_verification": cyclic,
                },
            )
        )

    comparison_p = primes[0]
    modulus, c, g = ruzsa_cyclic_sidon(comparison_p)
    h0 = comparison_p * math.isqrt(comparison_p)
    comparison_h = (h0,)

    records.append(
        candidate_record(
            "ordinary_ruzsa_sidon",
            c,
            modulus,
            comparison_h,
            {"prime": comparison_p, "primitive_root": g, "modulus": modulus},
        )
    )

    ef, ef_n, ef_sigma = reflected_erdos_freud(c)
    records.append(
        candidate_record(
            "reflected_erdos_freud",
            ef,
            ef_n,
            comparison_h,
            {"prime": comparison_p, "sigma": ef_sigma, "range_separated": True},
        )
    )

    half_indices = tuple(range(0, len(c), 2))
    unbalanced, unbalanced_n, unbalanced_sigma = unbalanced_reflection(c, half_indices)
    records.append(
        candidate_record(
            "unbalanced_reflection_half_core",
            unbalanced,
            unbalanced_n,
            comparison_h,
            {
                "prime": comparison_p,
                "sigma": unbalanced_sigma,
                "core_indices": list(half_indices),
            },
        )
    )

    full_b = tuple(2 * x for x in c)
    half_core = tuple(full_b[i] for i in half_indices)
    residual, residual_n, residual_sigma = compressed_congruence_reflection(
        c, modulus, 2, half_core
    )
    records.append(
        candidate_record(
            "compressed_reflected_core_plus_residual",
            residual,
            residual_n,
            comparison_h,
            {
                "prime": comparison_p,
                "sigma": residual_sigma,
                "lower_block_size": len(c),
                "reflected_core_size": len(half_core),
            },
        )
    )

    multicluster = residue_multicluster_subset(c, modulus, 8)
    multi_a, multi_n, multi_sigma = compressed_congruence_reflection(
        multicluster, modulus, 2
    )
    records.append(
        candidate_record(
            "four_arc_multicluster_reflection",
            multi_a,
            multi_n,
            comparison_h,
            {
                "prime": comparison_p,
                "sigma": multi_sigma,
                "bins": 8,
                "kept_even_bins": True,
                "base_size": len(multicluster),
            },
        )
    )

    for dilation in (2, 3, 4):
        mixed, mixed_n, mixed_sigma = compressed_congruence_reflection(
            c, modulus, dilation
        )
        records.append(
            candidate_record(
                f"affine_mixed_dilation_{dilation}",
                mixed,
                mixed_n,
                comparison_h,
                {
                    "prime": comparison_p,
                    "dilation": dilation,
                    "sigma": mixed_sigma,
                    "center_residue": 1,
                },
            )
        )

    conic, conic_n = inverse_conic(comparison_p)
    records.append(
        candidate_record(
            "inverse_conic",
            conic,
            conic_n,
            comparison_h,
            {"prime": comparison_p, "formula": "x+2p*x^{-1} mod p"},
        )
    )

    records.append(affine_scan_record(comparison_p, (h0, 2 * h0)))
    return records


def write_jsonl(path: Path, records: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def parse_int_list(text: str) -> tuple[int, ...]:
    if not text.strip():
        return ()
    return tuple(int(part.strip()) for part in text.split(","))


def command_self_test(_args: argparse.Namespace) -> None:
    print(json.dumps(self_test(), sort_keys=True, indent=2))


def command_verify(args: argparse.Namespace) -> None:
    a = parse_int_list(args.set)
    record = candidate_record(
        "command_line_set", a, args.ambient_n, args.h, {"source": "command line"}
    )
    print(json.dumps(record, sort_keys=True, indent=2))


def command_family(args: argparse.Namespace) -> None:
    modulus, c, g = ruzsa_cyclic_sidon(args.prime, args.primitive_root)
    phase = affine_phase(c, modulus, args.unit, args.translation)
    a, ambient_n, sigma = compressed_congruence_reflection(
        phase, modulus, args.dilation
    )
    record = candidate_record(
        f"ruzsa_compressed_p{args.prime}_r{args.dilation}",
        a,
        ambient_n,
        args.h,
        {
            "prime": args.prime,
            "primitive_root": g,
            "modulus": modulus,
            "unit": args.unit,
            "translation": args.translation,
            "dilation": args.dilation,
            "sigma": sigma,
        },
    )
    print(json.dumps(record, sort_keys=True, indent=2))


def command_exhaustive(args: argparse.Namespace) -> None:
    result = exact_exhaustive_search(args.ambient_n, args.h)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True, indent=2))


def command_suite(args: argparse.Namespace) -> None:
    records = certificate_suite(args.primes)
    write_jsonl(Path(args.output), records)
    summary = {
        "record_type": "certificate_suite_summary",
        "output": str(Path(args.output)),
        "records": len(records),
        "candidate_records": sum(record["record_type"] == "candidate" for record in records),
        "all_candidates_admissible": all(
            record.get("verification", {}).get("admissible", True) for record in records
        ),
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    test_parser = subparsers.add_parser("self-test")
    test_parser.set_defaults(func=command_self_test)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--set", required=True, help="comma-separated zero-based set")
    verify_parser.add_argument("--ambient-n", type=int, required=True)
    verify_parser.add_argument("--h", type=int, nargs="+", required=True)
    verify_parser.set_defaults(func=command_verify)

    family_parser = subparsers.add_parser("family")
    family_parser.add_argument("--prime", type=int, required=True)
    family_parser.add_argument("--primitive-root", type=int)
    family_parser.add_argument("--dilation", type=int, default=2)
    family_parser.add_argument("--unit", type=int, default=1)
    family_parser.add_argument("--translation", type=int, default=0)
    family_parser.add_argument("--h", type=int, nargs="+", required=True)
    family_parser.set_defaults(func=command_family)

    exhaustive_parser = subparsers.add_parser("exhaustive")
    exhaustive_parser.add_argument("--ambient-n", type=int, required=True)
    exhaustive_parser.add_argument("--h", type=int, nargs="+", required=True)
    exhaustive_parser.add_argument("--output")
    exhaustive_parser.set_defaults(func=command_exhaustive)

    suite_parser = subparsers.add_parser("certificate-suite")
    suite_parser.add_argument("--primes", type=int, nargs="+", default=[101, 211, 401])
    suite_parser.add_argument(
        "--output",
        default=str(Path(__file__).with_name("certificates.jsonl")),
    )
    suite_parser.set_defaults(func=command_suite)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
