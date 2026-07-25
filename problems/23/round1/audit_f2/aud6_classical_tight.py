"""AUDIT 6.  Which CLASSICAL local families are (non-trivially) TIGHT at C5[n]?
The report (Sec.3 bullets, Sec.4.3, Sec.5) claims the only tight linear-size sets are the
sweep chains and that they are "neither balls, nor stars, nor neighbourhoods, nor independent".
Test that directly for n = 1..8, on the explicit graph.
"""
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import blowup, sigma_set, adj_of

C5_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
COL = [0, 1, 0, 1, 1]           # side0 = V1,V3 ; side1 = V2,V4,V5 ; M-pair = (V4,V5)


def build(n):
    N, E, part, start = blowup(C5_EDGES, [n] * 5)
    side = [COL[part[v]] for v in range(N)]
    return N, E, part, side


def prof(S, part):
    x = [0] * 5
    for v in S:
        x[part[v]] += 1
    return tuple(x)


def main():
    for n in (1, 2, 3, 4, 6, 8):
        N, E, part, side = build(n)
        adj = adj_of(N, E)
        print(f"\n=== C5[{n}]  N={N} ===")
        seen = {}
        # balls
        for v in range(N):
            ball = set([v]) | set(adj[v])
            for a in list(adj[v]):
                ball |= adj[a]
            seen.setdefault(("B(v,2)", prof(ball, part)), sigma_set(ball, E, side))
            nb = set(adj[v]) | {v}
            seen.setdefault(("N[v]", prof(nb, part)), sigma_set(nb, E, side))
            seen.setdefault(("N(v)", prof(set(adj[v]), part)), sigma_set(set(adj[v]), E, side))
            NB = {a for a in adj[v] if side[a] != side[v]}
            st = NB | {v}
            seen.setdefault(("star {v}uN_B(v)", prof(st, part)), sigma_set(st, E, side))
        for (u, v) in E:
            en = set(adj[u]) | set(adj[v]) | {u, v}
            seen.setdefault((f"N[u]uN[v] (parts {part[u]+1},{part[v]+1})", prof(en, part)),
                            sigma_set(en, E, side))
        for k in sorted(seen):
            tag = "  <<< TIGHT" if seen[k] == 0 else ""
            trivial = " (trivial: S=V)" if k[1] == (n,) * 5 else ""
            print(f"   {k[0]:34s} profile={k[1]}  sigma={seen[k]}{tag}{trivial}")


if __name__ == "__main__":
    main()
