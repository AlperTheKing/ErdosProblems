"""Item 3 says the exhaustive check found "equality exactly at five-atom configurations".
The exhaustive re-run (P4_arcexhaust.exe) finds equality cases with 6, 7, ... atoms on
Gamma_11, Gamma_17, Gamma_18.  This script classifies every equality configuration:
is it a TWIN-SPLIT C5, i.e. does the support-induced graph, quotiented by twins, equal C5 with
equal total weight per class?

If yes, the correct statement of the equality case is "C5 blow-ups, with each blow-up class free to
be spread over several circle positions" - a positive-dimensional family, not isolated points.
"""
import sys
from fractions import Fraction as F
from P4_core import from_gamma, sort_cyclic, adjacency, arcbound, TARGET


def classify(m, w):
    pos, wt = sort_cyclic(*from_gamma(m, w))
    adj = adjacency(pos)
    n = len(pos)
    # twin classes inside the support
    classes = []
    assigned = [-1] * n
    for u in range(n):
        if assigned[u] >= 0:
            continue
        cls = [u]
        assigned[u] = len(classes)
        for v in range(u + 1, n):
            if assigned[v] < 0 and adj[u] == adj[v]:
                cls.append(v)
                assigned[v] = len(classes)
        classes.append(cls)
    k = len(classes)
    cw = [sum(wt[u] for u in c) for c in classes]
    # quotient adjacency
    qadj = [[adj[classes[a][0]][classes[b][0]] for b in range(k)] for a in range(k)]
    deg = [sum(r) for r in qadj]
    is_c5 = (k == 5 and deg == [2] * 5)
    equalw = all(c == cw[0] for c in cw)
    return n, k, is_c5, equalw, cw


if __name__ == '__main__':
    for fn, m in (("P4_eq_gamma11_q15.txt", 11), ("P4_eq_gamma18_q10.txt", 18)):
        rows = [l.split()[1:] for l in open(fn) if l.startswith("EQ")]
        stats = {}
        bad = []
        for r in rows:
            w = [int(t) for t in r]
            n, k, is_c5, equalw, cw = classify(m, w)
            stats[(n, k, is_c5, equalw)] = stats.get((n, k, is_c5, equalw), 0) + 1
            if not (is_c5 and equalw):
                bad.append((w, n, k, is_c5, equalw, cw))
        print(f"\n{fn}  ({len(rows)} equality configurations on Gamma_{m})")
        for key in sorted(stats):
            n, k, is_c5, equalw = key
            print(f"   atoms={n}  twin classes={k}  quotient is C5: {is_c5}  "
                  f"class weights equal: {equalw}   count={stats[key]}")
        if bad:
            print(f"   configurations that are NOT balanced twin-split C5s: {len(bad)}")
            for b in bad[:5]:
                print("     ", b)
        else:
            print("   => every equality case is a BALANCED C5 BLOW-UP with classes spread over "
                  "several circle positions")
    # spot check: one 6-atom equality case, verified exactly
    w = [0, 0, 3, 0, 1, 2, 3, 0, 0, 3, 3]
    pos, wt = sort_cyclic(*from_gamma(11, w))
    ab = arcbound(pos, wt, adjacency(pos))
    print(f"\n  spot check Gamma_11 w={w}: {len(pos)} atoms, ARCBOUND = {ab} "
          f"(= 1/25 ? {ab == TARGET})")
