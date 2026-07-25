"""AUDIT of G8 sections 6.2, 6.3, 7 (cut structure).

Own maximum-matching routine (recursive branch on the lowest unmatched vertex,
different from the target's edge-subset branch and bound), own cut enumeration.

Checks:
  (i)   min over cuts S of nu(mono(S)) for And(k), k=2..5, and the star question;
  (ii)  the induced-C5 active-cut intersection for And(k), k=2..5;
  (iii) for And(3): the exact set of cuts active at every induced-C5 uniform point,
        and whether the 5 forms q1..q5 quoted in the report are genuine cuts.
"""
import sys, itertools
from fractions import Fraction
from audit_G8_core import and_circulant, edges_of


def max_matching(edges):
    """exact maximum matching, own recursion: branch on the lowest endpoint."""
    edges = list(edges)
    verts = sorted({v for e in edges for v in e})
    inc = {v: [e for e in edges if v in e] for v in verts}

    def rec(used, remaining_verts):
        # lowest available vertex with an incident free edge
        for v in remaining_verts:
            if v in used:
                continue
            opts = [e for e in inc[v] if e[0] not in used and e[1] not in used]
            if not opts:
                continue
            best = rec(used | {v}, remaining_verts)          # leave v unmatched
            for e in opts:
                w = e[0] if e[1] == v else e[1]
                r = 1 + rec(used | {v, w}, remaining_verts)
                if r > best:
                    best = r
            return best
        return 0

    return rec(frozenset(), verts)


def cuts_of(n, edges):
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        yield mask, side, [(u, v) for (u, v) in edges if side[u] == side[v]]


def induced_C5s(n, adjm, edges):
    out = []
    for S in itertools.combinations(range(n), 5):
        Ss = set(S)
        sub = [(u, v) for (u, v) in edges if u in Ss and v in Ss]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in S}
        for (u, v) in sub:
            deg[u] += 1
            deg[v] += 1
        if all(d == 2 for d in deg.values()):
            out.append((S, sub))
    return out


if __name__ == "__main__":
    for k in (2, 3, 4, 5):
        n, adjm = and_circulant(k)
        E = edges_of(n, adjm)
        # (i) min nu over cuts
        best = None
        stars = 0
        minmono = None
        for mask, side, mono in cuts_of(n, E):
            if not mono:
                print(f"   !!! And({k}) has a bipartition -- impossible")
                continue
            nu = max_matching(mono)
            vs = {v for e in mono for v in e}
            isstar = any(all(c in e for e in mono) for c in vs)
            if isstar:
                stars += 1
            if best is None or nu < best[0]:
                best = (nu, mask, mono, isstar)
            if minmono is None or len(mono) < minmono:
                minmono = len(mono)
        print(f"And({k}) n={n}: min |mono| over cuts = {minmono} (=bip); "
              f"min nu(mono) = {best[0]} (k-1 = {k-1}); #cuts with star mono = {stars}; "
              f"witness mono={best[2]}")
        print(f"   nu^2 = {best[0]**2}  vs  n^2/25 = {Fraction(n*n,25)} = {n*n/25:.4f}  "
              f"=> AM-GM two-linear-form scheme "
              f"{'POSSIBLE' if best[0]**2 <= Fraction(n*n,25) else 'BLOCKED'}")

        # (ii) induced-C5 active cut intersection
        C5s = induced_C5s(n, adjm, E)
        inter = None
        for (S, sub) in C5s:
            act = set()
            for mask, side, mono in cuts_of(n, E):
                cnt = sum(1 for (u, v) in sub if side[u] == side[v])
                if cnt == 1:
                    act.add(mask)
            inter = act if inter is None else (inter & act)
        print(f"   induced C5s: {len(C5s)}; |intersection of active cut sets| = "
              f"{len(inter) if inter is not None else 'n/a'}")
        if inter:
            for mask in sorted(inter):
                side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
                mono = [(u, v) for (u, v) in E if side[u] == side[v]]
                print(f"      cut {''.join(map(str,side))}  mono={mono}  nu={max_matching(mono)}")
        sys.stdout.flush()
        print()
