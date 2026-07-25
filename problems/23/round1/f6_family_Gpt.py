"""
F6 / Erdos #23.  Verification of the family G(p,t) which stalls every
bounded-size local-search move class at |M| = N^2/8 - t*N/2.

G(p,t):  V = X1 u X2 u Y1 u Y2, each of size p, N = 4p.
         E = all pairs (X_i, Y_j) EXCEPT the t-regular circulant
             R_i = { (x^i_a, y^i_b) : (b-a) mod p in {0,...,t-1} }  for i = 1,2.
         So G is bipartite (X = X1 u X2 versus Y = Y1 u Y2), hence triangle free,
         and bip(G) = 0.

Cut:     A = X1 u Y1,  B = X2 u Y2.
         Mono edges M = E(X1,Y1) u E(X2,Y2),  |M| = 2p(p-t) = N^2/8 - tN/2.

Claim (Theorem B): for every S subset V with |S| <= 2t,  Delta(S) >= 0,
i.e. flipping S does not decrease the number of monochromatic edges;
and there is an S with |S| = 2t+1 (t>=1) with Delta(S) < 0.

Delta(S) = sum_{v in S} s(v) - 2*( cut_in(S) - mono_in(S) ),
with s(v) = d_C(v) - d_M(v).

Everything is exact integer arithmetic.
"""
import itertools, sys

def build(p, t):
    assert 0 <= t <= p
    # vertex ids: X1 = 0..p-1, Y1 = p..2p-1, X2 = 2p..3p-1, Y2 = 3p..4p-1
    n = 4 * p
    X1 = list(range(0, p)); Y1 = list(range(p, 2 * p))
    X2 = list(range(2 * p, 3 * p)); Y2 = list(range(3 * p, 4 * p))
    adj = [set() for _ in range(n)]
    def add(u, v):
        adj[u].add(v); adj[v].add(u)
    X = X1 + X2; Y = Y1 + Y2
    for u in X:
        for v in Y:
            add(u, v)
    # remove the two t-regular circulants
    for a in range(p):
        for r in range(t):
            b = (a + r) % p
            adj[X1[a]].discard(Y1[b]); adj[Y1[b]].discard(X1[a])
            adj[X2[a]].discard(Y2[b]); adj[Y2[b]].discard(X2[a])
    side = [0] * n           # 0 = side A, 1 = side B
    for v in X2 + Y2:
        side[v] = 1
    return n, adj, side, (X1, Y1, X2, Y2)

def stats(n, adj, side):
    edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
    mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
    s = [0] * n
    for v in range(n):
        dm = sum(1 for u in adj[v] if side[u] == side[v])
        dc = len(adj[v]) - dm
        s[v] = dc - dm
    return edges, mono, s

def delta(S, adj, side, s):
    Sset = set(S)
    tot = sum(s[v] for v in S)
    cut_in = mono_in = 0
    for u, v in itertools.combinations(S, 2):
        if v in adj[u]:
            if side[u] == side[v]:
                mono_in += 1
            else:
                cut_in += 1
    return tot - 2 * (cut_in - mono_in)

def brute_delta_min(n, adj, side, s, kmax):
    """exhaustive minimum of Delta(S) over 1 <= |S| <= kmax, returns (k -> (min, argmin))"""
    out = {}
    for k in range(1, kmax + 1):
        best = None; arg = None
        for S in itertools.combinations(range(n), k):
            d = delta(S, adj, side, s)
            if best is None or d < best:
                best = d; arg = S
        out[k] = (best, arg)
    return out

def triangle_free(n, adj):
    for u in range(n):
        for v in adj[u]:
            if u < v and (adj[u] & adj[v]):
                return False
    return True

if __name__ == "__main__":
    print("p  t   N   |E|    |M|   N^2/8-tN/2   trifree   min Delta over |S|<=k  (k=1..2t+1)")
    for (p, t) in [(2,1),(3,1),(3,2),(4,1),(4,2),(4,3),(5,2),(5,1),(6,3),(6,2)]:
        n, adj, side, parts = build(p, t)
        edges, mono, s = stats(n, adj, side)
        N = n
        pred = N * N // 8 - t * N // 2
        kmax = min(2 * t + 1, 8)
        res = brute_delta_min(n, adj, side, s, kmax)
        row = []
        for k in range(1, kmax + 1):
            row.append(f"k={k}:{res[k][0]}")
        ok = triangle_free(n, adj)
        print(f"{p}  {t}  {N:3d} {len(edges):5d} {len(mono):5d}   {pred:6d}      {ok}   " + "  ".join(row))
        assert len(mono) == 2 * p * (p - t) == pred, (len(mono), pred)
        assert all(x == t for x in s), sorted(set(s))
        # exact claim: Delta >= 0 for |S| <= 2t ; violated at |S| = 2t+1 when t>=1
        for k in range(1, 2 * t + 1):
            assert res[k][0] >= 0, (p, t, k, res[k])
        if t >= 1 and 2 * t + 1 <= kmax:
            assert res[2 * t + 1][0] < 0, (p, t, res[2 * t + 1])
            print(f"     first improving set has size {2*t+1}: {res[2*t+1][1]}  Delta={res[2*t+1][0]}")
    print("\nALL ASSERTIONS PASSED")
