"""AUDIT 7.  The report's Sec.5 "exact missing statement" asks for a family F, defined
graph-theoretically at a maximum cut, with
   (alpha) sigma(S)=0 on C5[n] for every S in F, and
   (beta)  some S in F(W_b) has sigma(S) < 0.
Test the SIMPLEST candidate the report itself names but never tries:
   F = { W u N_B(W) : W a side of a connected component of the monochromatic graph M }.
"""
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import blowup, sigma_set, adj_of, is_triangle_free


def make(edges, col, sizes):
    N, E, part, start = blowup(edges, sizes)
    side = [col[part[v]] for v in range(N)]
    return N, E, part, side


def M_component_sides(N, E, side):
    """Connected components of the monochromatic graph; return their bipartition classes."""
    M = [e for e in E if side[e[0]] == side[e[1]]]
    adjM = [set() for _ in range(N)]
    for (u, v) in M:
        adjM[u].add(v)
        adjM[v].add(u)
    seen = [False] * N
    out = []
    for s in range(N):
        if seen[s] or not adjM[s]:
            continue
        colr = {s: 0}
        seen[s] = True
        q = [s]
        while q:
            u = q.pop()
            for w in adjM[u]:
                if w not in colr:
                    colr[w] = 1 - colr[u]
                    seen[w] = True
                    q.append(w)
        out.append(({v for v in colr if colr[v] == 0}, {v for v in colr if colr[v] == 1}))
    return out


def sweep(W, N, E, side):
    adj = adj_of(N, E)
    NB = set()
    for w in W:
        NB |= {a for a in adj[w] if side[a] != side[w]}
    return frozenset(W) | NB


def show(name, N, E, part, side):
    print(f"\n--- {name}: N={N}, |E|={len(E)}, "
          f"|M|={sum(1 for e in E if side[e[0]]==side[e[1]])}, triangle-free={is_triangle_free(N,E)}")
    for (A, B) in M_component_sides(N, E, side):
        for W, tag in ((A, "A"), (B, "B")):
            S = sweep(W, N, E, side)
            pr = [0] * (max(part) + 1)
            for v in S:
                pr[part[v]] += 1
            print(f"    W = M-side {tag} (|W|={len(W)}, parts {sorted(set(part[w] for w in W))}):  "
                  f"S = W u N_B(W), |S|={len(S)} (= {len(S)/N:.3f} N), profile={tuple(pr)},  "
                  f"sigma(S) = {sigma_set(S, E, side)}")


if __name__ == "__main__":
    # C5[n]
    for n in (1, 2, 3, 5, 8):
        N, E, part, side = make([(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)],
                                [0, 1, 0, 1, 1], [n] * 5)
        show(f"C5[{n}] canonical MAXIMUM cut", N, E, part, side)
    # W_b
    for b in (3, 5, 8):
        N, E, part, side = make([(0, 1), (1, 2), (2, 3)], [0, 1, 1, 0],
                                [b + 1, b, b, b + 1])
        show(f"W_b (b={b}) = P4[{b+1},{b},{b},{b+1}]", N, E, part, side)
    # W'_{L,b}
    for (L, b) in ((9, 8), (9, 12), (11, 10)):
        sizes = [b] + [b + 1] + [1] * (L - 4) + [b + 1, b]
        col = [i % 2 for i in range(L)]
        edges = [(i, i + 1) for i in range(L - 1)] + [(0, L - 1)]
        N, E, part, side = make(edges, col, sizes)
        show(f"W'_(L={L},b={b})", N, E, part, side)
