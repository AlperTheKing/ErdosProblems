"""Quotient enumeration for max-cut/Gamma-min sides of h_blowup(3).

The hard row-side H3 guardrail is the 3-fold blowup of the N=9 graph
`H?AFBo]`.  Brute force over all sides has size 2^26 after complementing.
Because clone classes are twins, cut size and Gamma depend only on the number
of clones of each base vertex placed on side 1.  For t=3 this is only 4^9
patterns.

This script enumerates those count patterns, keeps maximum cuts, checks
connected-B and Gamma, and then runs the Schur row-size gate on every
Gamma-minimal count representative.
"""

from itertools import product

from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, gamma_of
from _h import Bconn, dec
from _Rsize_gate import test_cut as schur_test_cut


def side_from_counts(counts, t=3):
    side = []
    for c in counts:
        side.extend([1] * c)
        side.extend([0] * (t - c))
    return side


def cut_value_from_counts(base_edges, counts, t=3):
    total = 0
    for u, v in base_edges:
        cu = counts[u]
        cv = counts[v]
        total += cu * (t - cv) + (t - cu) * cv
    return total


def main():
    t = 3
    n, edges, inherited_side = h_blowup(t)
    adj = adj_from_edges(n, edges)
    _bn, base_edges = dec("H?AFBo]")

    hard = [int(c) for c in "111111111111111100000000000"]
    hard_counts = tuple(sum(hard[i * t + a] for a in range(t)) for i in range(9))
    inherited_counts = tuple(
        sum(inherited_side[i * t + a] for a in range(t)) for i in range(9)
    )

    best_cut = -1
    max_patterns = []
    for counts in product(range(t + 1), repeat=9):
        cut = cut_value_from_counts(base_edges, counts, t)
        if cut > best_cut:
            best_cut = cut
            max_patterns = [counts]
        elif cut == best_cut:
            max_patterns.append(counts)

    best_gamma = None
    gamma_patterns = []
    bconn_max = 0
    gamma_hist = {}
    for counts in max_patterns:
        side = side_from_counts(counts, t)
        if not Bconn(n, adj, side):
            continue
        bconn_max += 1
        gamma = gamma_of(n, adj, side)
        if gamma is None:
            continue
        gamma_hist[gamma] = gamma_hist.get(gamma, 0) + 1
        if best_gamma is None or gamma < best_gamma:
            best_gamma = gamma
            gamma_patterns = [counts]
        elif gamma == best_gamma:
            gamma_patterns.append(counts)

    print("h_blowup(3) quotient enumeration")
    print("max cut value:", best_cut)
    print("max count patterns:", len(max_patterns))
    print("connected-B max patterns:", bconn_max)
    print("Gamma histogram on connected-B max patterns:", dict(sorted(gamma_hist.items())))
    print("Gamma min:", best_gamma)
    print("Gamma-min pattern count:", len(gamma_patterns))
    print("hard counts:", hard_counts, "cut", cut_value_from_counts(base_edges, hard_counts, t))
    print("hard Gamma:", gamma_of(n, adj, hard), "Bconn", Bconn(n, adj, hard))
    print(
        "inherited counts:",
        inherited_counts,
        "cut",
        cut_value_from_counts(base_edges, inherited_counts, t),
    )
    print("inherited Gamma:", gamma_of(n, adj, inherited_side), "Bconn", Bconn(n, adj, inherited_side))
    print("first Gamma-min patterns:", gamma_patterns[:20])

    acc = dict(
        cuts=0,
        Ononempty=0,
        Huu_singular=0,
        Mmat_fail=0,
        R_ge2=0,
        Rmax=0,
        Rhist={},
        S_notpsd=0,
        oneterm_fail=0,
        oneterm_singular=0,
        ot_min=None,
        Mmat_ex=None,
        R_ex=None,
        Snp_ex=None,
        ot_ex=None,
    )
    for counts in gamma_patterns:
        schur_test_cut("H3-gmin-quot", n, adj, side_from_counts(counts, t), acc)
    print("Schur on Gamma-min quotient representatives:")
    print("  O-nonempty:", acc["Ononempty"])
    print("  Rmax:", acc["Rmax"], "Rhist:", dict(sorted(acc["Rhist"].items())))
    print("  R>=2:", acc["R_ge2"], acc["R_ex"] or "")
    print("  S_notpsd:", acc["S_notpsd"], acc["Snp_ex"] or "")
    print("  oneterm_fail:", acc["oneterm_fail"], acc["ot_ex"] or "")


if __name__ == "__main__":
    main()
