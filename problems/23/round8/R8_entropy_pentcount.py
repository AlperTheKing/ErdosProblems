"""A COUNTING proof that R(H) is empty, for And(4), And(5), And(6), N=14 extremal.

Let P = number of induced C5s of H and, for an edge e, p(e) = number of induced
C5s through e.  A rainbow-1 cut has monochromatic set F meeting every induced C5
exactly once, so the pentagons through distinct edges of F are disjoint and

        sum_{e in F} p(e)  =  P.                         (*)

If no subset F of E(H) satisfies (*) then H has no rainbow-1 cut, hence (THEOREM
R8-2) no averaging certificate of any kind.  (*) is a subset-sum condition on the
multiset {p(e)}, decided here exactly by dynamic programming.
"""

from itertools import combinations
from R8_entropy_targets import andrasfai, g6, mycielski, cyc, clebsch, petersen


def pentagon_degrees(n, E):
    eidx = {e: i for i, e in enumerate(E)}
    adj = [[False] * n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    P = 0
    p = [0] * len(E)
    for S in combinations(range(n), 5):
        if any(sum(1 for u in S if adj[v][u]) != 2 for v in S):
            continue
        seen, st = {S[0]}, [S[0]]
        while st:
            v = st.pop()
            for u in S:
                if adj[v][u] and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) != 5:
            continue
        P += 1
        for (u, v) in combinations(S, 2):
            if adj[u][v]:
                p[eidx[(u, v)]] += 1
    return P, p


def subset_sum_possible(vals, target):
    """Can some sub-multiset of vals sum to target?  Exact DP."""
    reach = 1                                   # bitset, bit t = t reachable
    for v in vals:
        if v == 0:
            continue
        reach |= reach << v
        reach &= (1 << (target + 1)) - 1
    return (reach >> target) & 1


if __name__ == "__main__":
    targets = [("And(3)=Wagner", andrasfai(3)),
               ("And(4)", andrasfai(4)),
               ("And(5)", andrasfai(5)),
               ("And(6)", andrasfai(6)),
               ("And(7)", andrasfai(7)),
               ("Petersen", petersen()),
               ("Grotzsch", mycielski(*cyc(5))),
               ("Clebsch", clebsch()),
               ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?")),
               ]
    print(f"{'graph':18s} {'n':>3s} {'|E|':>4s} {'P=#indC5':>9s} "
          f"{'pentagon-degree multiset':38s} {'subset-sum = P?':>16s}")
    for name, (n, E) in targets:
        P, p = pentagon_degrees(n, E)
        if P == 0:
            print(f"{name:18s} {n:3d} {len(E):4d} {P:9d}  no induced C5")
            continue
        multiset = {}
        for t in p:
            multiset[t] = multiset.get(t, 0) + 1
        ms = ", ".join(f"{k}^{v}" for k, v in sorted(multiset.items()))
        ok = subset_sum_possible(p, P)
        print(f"{name:18s} {n:3d} {len(E):4d} {P:9d}  {ms:38s} "
              f"{'YES' if ok else 'NO -> R(H) EMPTY':>16s}")
        assert sum(p) == 5 * P, (sum(p), 5 * P)
