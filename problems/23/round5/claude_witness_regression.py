"""ROOT-AGENT REGRESSION SET (Claude, round 5).

Every candidate cut-selection rule for the arc-cut ceiling must be run against THIS file before any
claim is made about it.  Random sampling is not a substitute: on 2026-07-25 I proposed the
"antipodal h-bound", tested it on 1500 random measures with zero violations, and it was FALSE - the
random sample simply never generated witness W1 below, which had already been recorded as the
falsifier of the half-arc family.  The rule and the half-arc family turned out to be the same object
in different language.

Usage:  from claude_witness_regression import WITNESSES, check_rule
        check_rule(my_rule)      # my_rule(m, adj, x) -> Fraction, an upper bound on ARCBOUND
"""
from fractions import Fraction as F
from itertools import combinations


def gamma(m):
    return [[(u != v and 3 * min((u - v) % m, (v - u) % m) > m) for v in range(m)] for u in range(m)]


def mono(m, adj, x, inA):
    return sum(x[u] * x[v] for u, v in combinations(range(m), 2) if adj[u][v] and inA[u] == inA[v])


def arcbound(m, adj, x):
    best = None
    for i in range(m):
        for l in range(m + 1):
            inA = [False] * m
            for t in range(l):
                inA[(i + t) % m] = True
            v = mono(m, adj, x, inA)
            if best is None or v < best:
                best = v
    return best


def W_of(m, adj, x):
    return sum(x[u] * x[v] for u, v in combinations(range(m), 2) if adj[u][v])


# ---------------------------------------------------------------- the witnesses

WITNESSES = [
    # (name, m, integer weights, what it kills, the exact value that kills it)
    ("W1 half-arc killer", 8, [0, 1, 0, 1, 2, 0, 2, 1],
     "half-arc / antipodal family: its minimum is 2/49 > 1/25 while the full arc family gives 1/49"),
    ("W1' same on Gamma_11", 11, [0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 1],
     "same weighting embedded at unequal spacing"),
    ("W1'' same on Gamma_16", 16, [0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 1],
     "same weighting, wider circle"),
    ("W2 five-atom extremal", 5, [1, 1, 1, 1, 1],
     "everything: ARCBOUND = 1/25 exactly, so any rule must be TIGHT here"),
    ("W3 uniform Gamma_18", 18, [1] * 18,
     "the 1/3-arc family: all three thirds carry 1/18 > 1/25; only longer arcs save it"),
    ("W4 uniform Gamma_20", 20, [1] * 20, "same, even circle"),
    ("W5 three-atom near-path", 12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0],
     "averaging rules: W = 2/9 > 1/5 here while the truth is 0"),
    ("W6 seven-atom", 7, [1] * 7, "ARCBOUND = 1/49, equality case of the W-square form"),
    ("W8 far-regular Wagner", 14, [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
     "EVERY functional of {m(b)} plus A: m(b) = 3/64 for all b in the support (Var = 0) and "
     "A = 9/224 > 1/25, while the true ARCBOUND is 1/32 - refutes the R5-K18 criterion"),
    ("W7 unequal five-atom", 20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 1, 3],
     "unequally spaced and unequally weighted C5"),
]


def check_rule(rule, name="rule", verbose=True):
    """rule(m, adj, x) must return a Fraction that is a valid upper bound on ARCBOUND.
    Reports (i) whether it ever exceeds 1/25, (ii) whether it is tight where it must be."""
    bad = []
    for wname, m, w, why in WITNESSES:
        adj = gamma(m)
        q = sum(w)
        x = [F(wi, q) for wi in w]
        val = rule(m, adj, x)
        ab = arcbound(m, adj, x)
        ok = val <= F(1, 25)
        if verbose:
            print(f"  {wname:26s} m={m:3d}  rule={str(val):>10s} = {float(val):.6f}  "
                  f"ARCBOUND={str(ab):>8s}  {'OK' if ok else '*** EXCEEDS 1/25 ***'}")
        if not ok:
            bad.append((wname, val, why))
    if verbose:
        print(f"{name}: {'PASSES all witnesses' if not bad else 'FAILS on ' + ', '.join(b[0] for b in bad)}")
    return bad


if __name__ == '__main__':
    print("regression check of the three rules already refuted, plus the true minimum\n")

    def rule_half(m, adj, x):
        vals = []
        for i in range(m):
            for l in (m // 2, (m + 1) // 2):
                inA = [False] * m
                for t in range(l):
                    inA[(i + t) % m] = True
                vals.append(mono(m, adj, x, inA))
        return min(vals)

    def rule_third(m, adj, x):
        vals = []
        for i in range(m):
            for l in set([m // 3, (m + 2) // 3]):
                inA = [False] * m
                for t in range(l):
                    inA[(i + t) % m] = True
                vals.append(mono(m, adj, x, inA))
        return min(vals)

    def rule_full(m, adj, x):
        return arcbound(m, adj, x)

    print("RULE: half-arcs only (antipodal cuts) - equivalently the h(a)+h(a+1/2) bound")
    check_rule(rule_half, "half-arc")
    print("\nRULE: 1/3-arcs only")
    check_rule(rule_third, "third-arc")
    print("\nRULE: full two-parameter arc family (the surviving mechanism)")
    check_rule(rule_full, "full arc family")
