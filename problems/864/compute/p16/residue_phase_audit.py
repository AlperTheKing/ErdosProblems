"""Exact residue and wrap audit for the P16 signed-ruler lane.

All arithmetic is integral.  Besides verifying the exact wrap identities, the
script searches for a same-(p,G,W) lift twin: the indexed ruler residues,
difference-label residues, shifted-sum-label residues, and hence every
aggregate modular collision count are unchanged, while the lifted ruler is
still Sidon but violates the cross-family disjointness condition.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, product


WITNESSES = [
    (5, 30, [0, 1, 3, 8, 12]),
    (9, 116, [0, 1, 3, 11, 15, 20, 36, 43, 49]),
    (10, 152, [0, 1, 6, 10, 23, 26, 34, 41, 53, 55]),
    (11, 191, [0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84]),
    (12, 238, [0, 2, 6, 18, 21, 28, 29, 60, 69, 74, 94, 107]),
]


def normalize(theta: int, lower: list[int]) -> tuple[list[int], int]:
    width = lower[-1]
    return sorted(width - x for x in lower), theta - 2 * width


def label_families(z: list[int], gap: int) -> tuple[list[int], list[int]]:
    p = len(z)
    differences = [z[j] - z[i] for i in range(p) for j in range(i + 1, p)]
    shifted_sums = [gap + z[i] + z[j] for i in range(p) for j in range(i, p)]
    return differences, shifted_sums


def is_sidon(z: list[int]) -> bool:
    sums = [z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))]
    return len(sums) == len(set(sums))


def signed_ruler_check(z: list[int], gap: int) -> bool:
    differences, shifted_sums = label_families(z, gap)
    return (
        is_sidon(z)
        and len(differences) == len(set(differences))
        and len(shifted_sums) == len(set(shifted_sums))
        and set(differences).isdisjoint(shifted_sums)
    )


def residue_counter(values: list[int], modulus: int) -> Counter[int]:
    return Counter(value % modulus for value in values)


def shifted_intersections(left: set[int], right: set[int], modulus: int) -> dict[int, int]:
    """Return |left intersect (right + q*m)|, including every nonzero q."""
    out: Counter[int] = Counter()
    for x in left:
        for y in right:
            delta = x - y
            if delta and delta % modulus == 0:
                out[delta // modulus] += 1
    return dict(sorted(out.items()))


def internal_wraps(values: list[int], modulus: int) -> int:
    value_set = set(values)
    assert len(value_set) == len(values)
    return sum(
        1
        for x, y in combinations(values, 2)
        if (x - y) % modulus == 0
    )


def modulus_profile(z: list[int], gap: int, modulus: int) -> dict[str, object]:
    differences, shifted_sums = label_families(z, gap)
    d_hist = residue_counter(differences, modulus)
    s_hist = residue_counter(shifted_sums, modulus)
    z_hist = residue_counter(z, modulus)

    cross_hist = sum(d_hist[r] * s_hist[r] for r in range(modulus))
    cross_by_q = shifted_intersections(set(differences), set(shifted_sums), modulus)
    assert cross_hist == sum(cross_by_q.values())
    assert 0 not in cross_by_q

    d_internal_hist = sum(v * (v - 1) // 2 for v in d_hist.values())
    s_internal_hist = sum(v * (v - 1) // 2 for v in s_hist.values())
    assert d_internal_hist == internal_wraps(differences, modulus)
    assert s_internal_hist == internal_wraps(shifted_sums, modulus)

    self_fibres = 0
    p = len(z)
    for i in range(p):
        if (gap + 2 * z[i]) % modulus == 0:
            self_fibres += p - 1 - i
    assert cross_hist >= self_fibres

    return {
        "m": modulus,
        "z_hist": sorted(z_hist.items()),
        "d_hist": sorted(d_hist.items()),
        "s_hist": sorted(s_hist.items()),
        "cross": cross_hist,
        "cross_by_q": cross_by_q,
        "d_internal": d_internal_hist,
        "s_internal": s_internal_hist,
        "self_fibres": self_fibres,
    }


def center_congruence_profile(theta: int, lower: list[int]) -> dict[str, object]:
    """Audit b1+b2+b3-b4 == q*theta for all ordered quadruples."""
    q_counts: Counter[int] = Counter()
    for a, b, c, d in product(lower, repeat=4):
        value = a + b + c - d
        if value % theta == 0:
            q_counts[value // theta] += 1
    # The center hole removes the q=1 layer.  Exact q=0 relations such as
    # a+b+c=d are allowed and need not be trivial.
    assert set(q_counts) <= {0}
    return {"ordered_solution_count": sum(q_counts.values()), "q_counts": dict(q_counts)}


def same_profile(a: list[int], b: list[int], gap: int, modulus: int) -> bool:
    if [x % modulus for x in a] != [x % modulus for x in b]:
        return False
    ad, ac = label_families(a, gap)
    bd, bc = label_families(b, gap)
    return (
        residue_counter(ad, modulus) == residue_counter(bd, modulus)
        and residue_counter(ac, modulus) == residue_counter(bc, modulus)
    )


def cross_collisions(z: list[int], gap: int) -> list[tuple[int, int]]:
    differences, shifted_sums = label_families(z, gap)
    return sorted(set(differences).intersection(shifted_sums))


def find_lift_twin(z: list[int], gap: int, modulus: int) -> dict[str, object] | None:
    """Search one- and two-coordinate +/-m lifts with fixed endpoints."""
    p = len(z)
    interior = range(1, p - 1)
    for support_size in (1, 2):
        for support in combinations(interior, support_size):
            for signs in product((-1, 1), repeat=support_size):
                lifted = z.copy()
                for i, sign in zip(support, signs):
                    lifted[i] += sign * modulus
                if lifted != sorted(lifted) or len(set(lifted)) != p:
                    continue
                if lifted[0] != z[0] or lifted[-1] != z[-1]:
                    continue
                if not is_sidon(lifted):
                    continue
                collisions = cross_collisions(lifted, gap)
                if not collisions:
                    continue
                assert same_profile(z, lifted, gap, modulus)
                original_profile = modulus_profile(z, gap, modulus)
                lifted_profile = modulus_profile(lifted, gap, modulus)
                for key in ("z_hist", "d_hist", "s_hist", "cross", "d_internal", "s_internal"):
                    assert original_profile[key] == lifted_profile[key]
                return {
                    "m": modulus,
                    "lifted_z": lifted,
                    "support": list(support),
                    "signs": list(signs),
                    "cross_collisions": collisions,
                    "profile": original_profile,
                }
    return None


def audit_witness(p: int, theta: int, lower: list[int], find_twins: bool) -> dict[str, object]:
    z, gap = normalize(theta, lower)
    assert len(z) == p and signed_ruler_check(z, gap)
    profiles = [modulus_profile(z, gap, m) for m in range(p, p * p + 1)]
    cross_values = [record["cross"] for record in profiles]
    twin = None
    if find_twins:
        for modulus in range(p, p * p + 1):
            twin = find_lift_twin(z, gap, modulus)
            if twin is not None:
                break
    return {
        "p": p,
        "theta": theta,
        "theta_over_p2": f"{theta}/{p*p}",
        "lower": lower,
        "z": z,
        "gap": gap,
        "center_congruence": center_congruence_profile(theta, lower),
        "moduli_checked": [p, p * p],
        "cross_min": min(cross_values),
        "cross_min_moduli": [profiles[i]["m"] for i, x in enumerate(cross_values) if x == min(cross_values)],
        "cross_max": max(cross_values),
        "cross_max_moduli": [profiles[i]["m"] for i, x in enumerate(cross_values) if x == max(cross_values)],
        "cross_sum": sum(cross_values),
        "self_fibre_sum": sum(record["self_fibres"] for record in profiles),
        "lift_twin": twin,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-twins", action="store_true")
    args = parser.parse_args()
    for witness in WITNESSES:
        print(json.dumps(audit_witness(*witness, find_twins=not args.no_twins), sort_keys=True))


if __name__ == "__main__":
    main()
