"""Exact audits for P17 signed-ruler amplification schemes.

A normalized signed ruler is a pair (Z,G), where Z is a finite set of
nonnegative integers containing 0 and

    D(Z) and G + S(Z)

are disjoint sets of distinct integers.  Here D uses positive differences
and S uses unordered sums, diagonals included.  Its reflected admissible set
has 2*|Z| points and span G + 2*max(Z).

This script uses integer arithmetic only.  It audits:
  * carry-free Cartesian/Minkowski products;
  * guarded unions Z union (T + c*Z) and one further recursive level;
  * Welch Costas-permutation integer flattenings;
  * Kronecker composition of permutations.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations


SEEDS: dict[str, tuple[list[int], int]] = {
    "p5": ([0, 4, 9, 11, 12], 6),
    "p9": ([0, 6, 13, 29, 34, 38, 46, 48, 49], 18),
}


def positive_differences(z: list[int]) -> list[int]:
    z = sorted(z)
    return [z[j] - z[i] for i in range(len(z)) for j in range(i + 1, len(z))]


def unordered_sums(z: list[int]) -> list[int]:
    z = sorted(z)
    return [z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))]


def duplicate_witness(values: list[int]) -> tuple[int, int] | None:
    counts = Counter(values)
    for value in sorted(counts):
        if counts[value] > 1:
            return value, counts[value]
    return None


def normalize(z: list[int]) -> list[int]:
    z = sorted(set(z))
    base = z[0]
    return [x - base for x in z]


def minimum_gap(z: list[int]) -> dict[str, object]:
    """Return the least positive G making (Z,G) a signed ruler, if possible."""

    z = normalize(z)
    d = positive_differences(z)
    s = unordered_sums(z)
    dup_d = duplicate_witness(d)
    dup_s = duplicate_witness(s)
    if dup_d is not None or dup_s is not None:
        return {
            "valid_base": False,
            "duplicate_difference": dup_d,
            "duplicate_sum": dup_s,
        }
    forbidden = {dv - sv for dv in d for sv in s if dv > sv}
    gap = 1
    while gap in forbidden:
        gap += 1
    shifted = {gap + sv for sv in s}
    assert not (set(d) & shifted)
    p = len(z)
    width = z[-1]
    span = gap + 2 * width
    return {
        "valid_base": True,
        "p": p,
        "Z": z,
        "G": gap,
        "W": width,
        "span": span,
        "span_over_p2": f"{span}/{p*p}",
    }


def cartesian_product_witness(x: list[int], y: list[int], radix: int) -> dict[str, object]:
    """Exhibit the canonical rectangle collision in X + radix*Y."""

    x = sorted(set(x))
    y = sorted(set(y))
    if len(x) < 2 or len(y) < 2:
        raise ValueError("both factors need at least two points")
    x0, x1 = x[:2]
    y0, y1 = y[:2]
    a = x0 + radix * y0
    b = x1 + radix * y1
    c = x0 + radix * y1
    d = x1 + radix * y0
    assert a + b == c + d and {a, b} != {c, d}
    product = normalize([u + radix * v for u in x for v in y])
    return {
        "radix": radix,
        "size": len(product),
        "collision_pairs": [sorted((a, b)), sorted((c, d))],
        "collision_sum": a + b,
        "base_check": minimum_gap(product),
    }


def affine_union(z: list[int], scale: int, translation: int, reverse: bool) -> list[int]:
    z = normalize(z)
    width = z[-1]
    upper = [width - x for x in z] if reverse else z
    return normalize(z + [translation + scale * x for x in upper])


def search_guarded_union(
    z: list[int], max_scale: int, max_translation_factor: int
) -> list[dict[str, object]]:
    z = normalize(z)
    width = z[-1]
    hits: list[dict[str, object]] = []
    for scale in range(1, max_scale + 1):
        for translation in range(width + 1, max_translation_factor * width + 1):
            for reverse in (False, True):
                candidate = affine_union(z, scale, translation, reverse)
                if len(candidate) != 2 * len(z):
                    continue
                check = minimum_gap(candidate)
                if check.get("valid_base"):
                    hits.append(
                        {
                            "scale": scale,
                            "translation": translation,
                            "reverse": reverse,
                            **check,
                        }
                    )
    hits.sort(key=lambda row: (int(row["span"]), row["scale"], row["translation"], row["reverse"]))
    return hits


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:
            return False
    return True


def primitive_roots(p: int) -> list[int]:
    if not is_prime(p):
        return []
    roots = []
    target = set(range(1, p))
    for g in range(2, p):
        if {pow(g, i, p) for i in range(p - 1)} == target:
            roots.append(g)
    return roots


def welch_permutation(p: int, primitive_root: int, shift: int = 0) -> list[int]:
    n = p - 1
    return [pow(primitive_root, i + shift, p) - 1 for i in range(n)]


def costas_flatten(pi: list[int], radix: int, transpose: bool) -> list[int]:
    if transpose:
        points = [radix * i + pi[i] for i in range(len(pi))]
    else:
        points = [i + radix * pi[i] for i in range(len(pi))]
    return normalize(points)


def search_welch(max_prime: int, radix_factor: int) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for p in range(3, max_prime + 1):
        if not is_prime(p):
            continue
        n = p - 1
        for root in primitive_roots(p):
            for shift in range(n):
                pi = welch_permutation(p, root, shift)
                for radix in range(1, radix_factor * n + 1):
                    for transpose in (False, True):
                        z = costas_flatten(pi, radix, transpose)
                        if len(z) != n:
                            continue
                        check = minimum_gap(z)
                        if check.get("valid_base"):
                            hits.append(
                                {
                                    "prime": p,
                                    "root": root,
                                    "shift": shift,
                                    "radix": radix,
                                    "transpose": transpose,
                                    **check,
                                }
                            )
    hits.sort(key=lambda row: (int(row["span"]) / int(row["p"]) ** 2, int(row["span"])))
    return hits


def kronecker_permutation(pi: list[int], tau: list[int]) -> list[int]:
    n = len(tau)
    return [n * pi[i] + tau[j] for i in range(len(pi)) for j in range(n)]


def kronecker_collision(pi: list[int], tau: list[int]) -> dict[str, object]:
    if len(pi) < 2 or len(tau) < 2:
        raise ValueError("both permutations need size at least two")
    rho = kronecker_permutation(pi, tau)
    n = len(tau)
    i0, i1 = 0, 1
    j0, j1 = 0, 1
    a = i0 * n + j0
    b = i0 * n + j1
    c = i1 * n + j0
    d = i1 * n + j1
    displacement_1 = (b - a, rho[b] - rho[a])
    displacement_2 = (d - c, rho[d] - rho[c])
    assert displacement_1 == displacement_2
    return {
        "size": len(rho),
        "index_pairs": [[a, b], [c, d]],
        "repeated_displacement": list(displacement_1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=31)
    parser.add_argument("--radix-factor", type=int, default=3)
    parser.add_argument("--max-scale", type=int, default=12)
    parser.add_argument("--translation-factor", type=int, default=8)
    args = parser.parse_args()

    report: dict[str, object] = {"seed_checks": {}}
    for name, (z, claimed_gap) in SEEDS.items():
        check = minimum_gap(z)
        report["seed_checks"][name] = {
            "claimed_gap": claimed_gap,
            "minimum_gap_check": check,
        }

    z5 = SEEDS["p5"][0]
    report["cartesian_p5_radix_100"] = cartesian_product_witness(z5, z5, 100)

    guarded = search_guarded_union(z5, args.max_scale, args.translation_factor)
    report["guarded_p5"] = {
        "candidate_count": len(guarded),
        "best_five": guarded[:5],
    }
    if guarded:
        second = search_guarded_union(
            list(guarded[0]["Z"]),
            min(args.max_scale, 8),
            min(args.translation_factor, 5),
        )
        report["guarded_best_second_level"] = {
            "candidate_count": len(second),
            "best_five": second[:5],
        }

    welch = search_welch(args.max_prime, args.radix_factor)
    report["welch"] = {
        "candidate_count": len(welch),
        "best_ten": welch[:10],
    }
    report["kronecker"] = kronecker_collision([0, 1], [0, 1])
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
