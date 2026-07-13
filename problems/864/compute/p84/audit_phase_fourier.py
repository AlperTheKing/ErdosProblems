import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


P75_B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]


def convolve(left, right):
    out = Counter()
    for i, a in left.items():
        for j, b in right.items():
            out[i + j] += a * b
    return out


def reverse(poly):
    return Counter({-i: a for i, a in poly.items()})


def shift(poly, amount):
    return Counter({i + amount: a for i, a in poly.items()})


def canonical_folds(B, h):
    pair_at_sum = {}
    for i, a in enumerate(B):
        for c in B[i:]:
            total = a + c
            assert total not in pair_at_sum
            pair_at_sum[total] = (a, c)

    folds = []
    for total, (a, c) in pair_at_sum.items():
        if total + h not in pair_at_sum:
            continue
        u, v = pair_at_sum[total + h]
        assert a <= c < u <= v
        folds.append((a, c, u, v))
    return sorted(folds)


def canonical_triangle_trace(B, folds):
    ac = {(a, c) for a, c, _, _ in folds}
    au = defaultdict(set)
    cu = defaultdict(set)
    for a, c, u, _ in folds:
        au[a].add(u)
        cu[c].add(u)
    return sum(len(au[a] & cu[c]) for a, c in ac)


def ordered_kernel_triangle_trace(B, h):
    marks = set(B)
    kernel = []
    for a in B:
        for c in B:
            for u in B:
                v = a + c + h - u
                if v in marks:
                    kernel.append((a, c, u))

    m_ac = defaultdict(int)
    n_au = defaultdict(int)
    l_cu = defaultdict(int)
    for a, c, u in kernel:
        m_ac[a, c] += 1
        n_au[a, u] += 1
        l_cu[c, u] += 1

    trace = sum(
        m_ac[a, c] * n_au[a, u] * l_cu[c, u]
        for a in B for c in B for u in B
    )
    return len(kernel), trace


def audit_p75():
    B = P75_B
    h, b = 988, 1
    p = len(B)
    P = Counter({x: 1 for x in B})
    A = convolve(P, reverse(P))
    Q = shift(convolve(P, P), b)
    common_ac = convolve(A, A)
    q_ac = convolve(Q, reverse(Q))
    cubic_linear = convolve(convolve(convolve(P, P), P), reverse(P))

    folds = canonical_folds(B, h)
    canonical_trace = canonical_triangle_trace(B, folds)
    ordered_fold_count, ordered_trace = ordered_kernel_triangle_trace(B, h)
    hadamard_hole = sum(A[n] * Q[n] for n in A.keys() & Q.keys())

    assert max(B) == h - 1
    assert hadamard_hole == cubic_linear[-b] == 0
    assert common_ac[h] == q_ac[h] == ordered_fold_count
    assert len(folds) == 51
    assert canonical_trace == 76
    assert canonical_trace - len(folds) == 25
    assert canonical_trace * canonical_trace <= len(folds) ** 3
    assert ordered_trace >= canonical_trace

    return {
        "p": p,
        "h": h,
        "hole_coefficient": cubic_linear[-b],
        "hadamard_hole": hadamard_hole,
        "C_S": len(folds),
        "weighted_fold_coefficient": common_ac[h],
        "canonical_triangle_trace": canonical_trace,
        "T_F": canonical_trace - len(folds),
        "ordered_kernel_size": ordered_fold_count,
        "ordered_kernel_triangle_trace": ordered_trace,
    }


def coefficient_profile_barrier(p):
    r = p * (p - 1) // 2
    F = Counter({2 * j: 1 for j in range(-r, r + 1)})
    F[0] = p
    H = shift(F, 1)
    ac_F = convolve(F, reverse(F))
    ac_H = convolve(H, reverse(H))
    lag = 2 * r
    expected = r - 1 + 2 * p

    assert not (set(F) & set(H))
    assert ac_F == ac_H
    assert ac_F[lag] == expected
    return {
        "p": p,
        "r": r,
        "lag": lag,
        "autocorrelation": ac_F[lag],
        "formula": expected,
        "ambient_endpoint": 4 * r + 1,
    }


def audit_p46_reports():
    path = Path(__file__).resolve().parents[1] / "p46/carry_statistics.json"
    reports = json.loads(path.read_text(encoding="ascii"))["p20"]["reports"]
    rows = []
    for row in reports:
        if row["delta"] <= 0:
            continue
        folds = canonical_folds(row["B"], row["h"])
        triangles = canonical_triangle_trace(row["B"], folds) - len(folds)
        assert len(folds) == row["sum_collision_residues"]
        assert triangles <= len(folds)
        rows.append({
            "source_id": row["source_id"],
            "p": row["p"],
            "C_S": len(folds),
            "T_F": triangles,
        })

    nonzero = [row for row in rows if row["T_F"]]
    max_triangles = max(rows, key=lambda row: row["T_F"])
    max_ratio = max(
        rows,
        key=lambda row: Fraction(row["T_F"], row["C_S"])
        if row["C_S"] else Fraction(0),
    )
    ratio = Fraction(max_ratio["T_F"], max_ratio["C_S"])
    return {
        "positive_defect_rows": len(rows),
        "nonzero_triangle_rows": len(nonzero),
        "T_F_gt_C_S_failures": 0,
        "max_T_F": max_triangles,
        "max_T_F_over_C_S": {
            "numerator": ratio.numerator,
            "denominator": ratio.denominator,
            "witness": max_ratio,
        },
    }


def main():
    print({"p75": audit_p75()})
    print({"p46_reports": audit_p46_reports()})
    print({
        "generic_barrier": [
            coefficient_profile_barrier(p) for p in (3, 10, 50)
        ]
    })


if __name__ == "__main__":
    main()
