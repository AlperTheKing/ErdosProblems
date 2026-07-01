"""Gate Codex's L=5-FORCING mechanism (Shared-Corridor Hit + Core Recut) on the stretched L/(L+2) cores.

For each odd L, build the canonical stretched nested core (intended 2-coloring with bad edges f0=(s,t), f1=(u,v)):
  s-a_i-c0-..-c_{L-5}-b_j-t  (f0, ell=L);  u-a1-c0-..-c_{L-5}-b_j-t-x-v  (f1, ell=L+2).
Check:
 (Hit) universal core hit = the set of B-edges lying on EVERY shortest blue row of BOTH f0 and f1.
       Prediction: empty for L=5 (no chain edges), nonempty (the chain edges) for L>=7.
 (Recut) the intended 2-bad-edge coloring is NOT a maximum cut for L>=7 (a recut making a hit edge bad
       gives a strictly larger cut / fewer core bad edges), so an L>=7 deficient core cannot sit on a
       gamma-min max cut. For L=5 the intended coloring IS a max cut (realizable).
EXACT (integer cut counts). Run from problems/23/writeup."""
from collections import deque
from _h import maxcut_all, Bconn, geos
from _codex_k2t_switch_probe import adj_from_edges


def edge(u, v):
    return (u, v) if u < v else (v, u)


def build(L):
    s, u, x, v, a0, a1 = 0, 1, 2, 3, 4, 5
    nchain = L - 4
    chain = [6 + i for i in range(nchain)]
    b0, b1, t = L + 2, L + 3, L + 4
    n = L + 5
    E = [(s, a0), (s, a1), (a0, chain[0]), (a1, chain[0])]
    E += [(chain[i], chain[i + 1]) for i in range(nchain - 1)]
    E += [(chain[-1], b0), (chain[-1], b1), (b0, t), (b1, t), (u, a1), (t, x), (x, v)]
    bad = [(s, t), (u, v)]
    E += bad
    adj = adj_from_edges(n, E)
    badset = set(edge(*e) for e in bad)
    blue_adj = [set() for _ in range(n)]
    for a, b in E:
        if edge(a, b) not in badset:
            blue_adj[a].add(b); blue_adj[b].add(a)
    side = [-1] * n; side[0] = 0; q = deque([0]); bip = True
    while q:
        z = q.popleft()
        for w in blue_adj[z]:
            if side[w] == -1:
                side[w] = 1 - side[z]; q.append(w)
            elif side[w] == side[z]:
                bip = False
    return n, E, side, (s, t), (u, v), adj, bip


def edgeset(P):
    return set(edge(P[i], P[i + 1]) for i in range(len(P) - 1))


def universal_hit(adj, side, f0, f1):
    G0 = geos(adj, side, f0[0], f0[1])
    G1 = geos(adj, side, f1[0], f1[1])
    common = None
    for P in G0 + G1:
        es = edgeset(P)
        common = es if common is None else (common & es)
    return (common or set()), len(G0), len(G1)


def cutval(E, side):
    return sum(1 for a, b in E if side[a] != side[b])


def main():
    print("L | n | intended bad edges | cut | maxcut | is_max | B-conn | universal_hit | (#geo f0,f1)")
    for L in [5, 7, 9, 11, 13, 15]:
        n, E, side, f0, f1, adj, bip = build(L)
        if not bip:
            print("L=%d: blue subgraph NOT bipartite -- construction invalid" % L); continue
        badreal = [edge(a, b) for a, b in E if side[a] == side[b]]
        ic = cutval(E, side)
        cuts = maxcut_all(n, adj)
        mc = max(cutval(E, c) for c in cuts)
        hit, g0, g1 = universal_hit(adj, side, f0, f1)
        bconn = Bconn(n, adj, side)
        print("L=%d | n=%d | bad=%s | cut=%d | maxcut=%d | is_max=%s | Bconn=%s | hit=%s | geos=(%d,%d)" %
              (L, n, badreal, ic, mc, ic == mc, bconn, sorted(hit), g0, g1))
    print()
    print("Mechanism holds iff: L=5 -> hit EMPTY and is_max True (realizable); L>=7 -> hit NONEMPTY and is_max False (recut beats the 2-bad-edge core => not gamma-min realizable).")


if __name__ == '__main__':
    main()
