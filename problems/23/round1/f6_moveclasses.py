"""
F6 / Erdos #23.
(1) Verify that G(p,2) is locally optimal for the FULL star-move class
    (every S with S subset N[v] and v in S), for all neighbourhood moves N(v),
    all closed-neighbourhood moves N[v], and all S with |S| <= 4,
    while |M| = N^2/8 - N  and bip(G)=0.
(2) Verify Theorem A's chain on C5[n] and on the Wagner blow-up W8[n].
(3) Exact bip of blow-ups H[n] via the class-split formula.
All integer / Fraction arithmetic.
"""
import itertools
from fractions import Fraction
import sys
sys.path.insert(0, '.')
from f6_family_Gpt import build, stats, delta, triangle_free

def star_min_delta(n, adj, side, s):
    """min over v, over T subset N_C(v), of Delta({v} u T).
       Delta({v} u T) = s(v) + sum_{u in T n N_C} (s(u)-2) + sum_{u in T n N_M} (s(u)+2)
       -> minimiser T = {u in N_C(v): s(u) < 2}."""
    best = None; arg = None
    for v in range(n):
        NC = [u for u in adj[v] if side[u] != side[v]]
        d = s[v] + sum(s[u] - 2 for u in NC if s[u] < 2)
        if best is None or d < best: best = d; arg = (v, [u for u in NC if s[u] < 2])
    return best, arg

def nb_min_delta(n, adj, side, s, closed):
    best = None; arg = None
    for v in range(n):
        S = sorted(adj[v]) + ([v] if closed else [])
        if not S: continue
        d = delta(S, adj, side, s)
        if best is None or d < best: best = d; arg = (v, S)
    return best, arg

def check_family():
    print("=== G(p,2): |M| = N^2/8 - N, stalls |S|<=4 AND every star move ===")
    print(" p   N   |M|  N^2/8-N  N^2/25   minDelta|S|<=4  minDelta star  minDelta N(v)  minDelta N[v]")
    for p in range(2, 13):
        n, adj, side, _ = build(p, 2)
        edges, mono, s = stats(n, adj, side)
        N = n
        assert all(x == 2 for x in s)
        assert len(mono) == 2 * p * (p - 2)
        # |S|<=4 exhaustively
        m4 = min(delta(S, adj, side, s) for k in range(1, 5) for S in itertools.combinations(range(n), k))
        st, starg = star_min_delta(n, adj, side, s)
        nb, _a = nb_min_delta(n, adj, side, s, False)
        nc, _b = nb_min_delta(n, adj, side, s, True)
        print(f"{p:2d} {N:3d} {len(mono):5d}  {N*N//8-N:7d}  {Fraction(N*N,25)!s:>7}   {m4:12d}  {st:13d}  {nb:12d}  {nc:12d}"
              + ("   <-- |M| > N^2/25" if 25*len(mono) > N*N else ""))
        assert m4 >= 0 and st >= 0 and nb >= 0 and nc >= 0
        assert triangle_free(n, adj)
    print("ALL G(p,2) CHECKS PASSED (bip(G)=0 since G is bipartite: X=X1uX2 vs Y=Y1uY2)\n")

# ---------- blow-up machinery ----------
def blowup_bip(edges_H, nH, n):
    """exact bip(H[n]) = min over a in {0..n}^V(H) of sum_{ij in E(H)} a_i a_j + (n-a_i)(n-a_j).
       (Optimal cuts of a blow-up are class-split cuts: vertices in one class are twins.)"""
    best = None; arg = None
    for a in itertools.product(range(n + 1), repeat=nH):
        v = sum(a[i]*a[j] + (n-a[i])*(n-a[j]) for i, j in edges_H)
        if best is None or v < best: best = v; arg = a
    return best, arg

W8 = [(i, (i+1) % 8) for i in range(8)] + [(i, i+4) for i in range(4)]   # Wagner graph C8(1,4)
C5 = [(i, (i+1) % 5) for i in range(5)]

def check_blowups():
    print("=== exact bip of blow-ups (class-split formula, exact integers) ===")
    for name, E, nH in [("C5", C5, 5), ("W8=C8(1,4)", W8, 8)]:
        deg = [0]*nH
        for i, j in E: deg[i] += 1; deg[j] += 1
        for n in range(1, 5):
            N = nH*n; m = len(E)*n*n
            b, a = blowup_bip(E, nH, n)
            print(f"  {name}[{n}]: N={N} m={m} bip={b}  bip/N^2={Fraction(b,N*N)!s:>9}={b/N**2:.6f}"
                  f"  N^2/25={Fraction(N*N,25)!s:>8}  {'OK' if 25*b<=N*N else 'VIOLATION'}  split={a}")
    print()

def check_theoremA():
    print("=== Theorem A chain on C5[n] and W8[n] (exact) ===")
    for name, E, nH in [("C5", C5, 5), ("W8", W8, 8)]:
        adjH = {i: set() for i in range(nH)}
        for i, j in E: adjH[i].add(j); adjH[j].add(i)
        for n in [1, 2, 3, 10]:
            N = nH*n; m = len(E)*n*n
            # blow-up: deg(v in class i) = n*deg_H(i); D_v = sum_{u ~ v} d(u) = n * sum_{j~i} n*deg_H(j)
            Dmax = max(n*n*sum(len(adjH[j]) for j in adjH[i]) for i in range(nH))
            # max weight independent set (weights = degree) in the blow-up = n^2 * max_{I indep in H} sum deg_H
            wH = 0
            for r in range(1, nH+1):
                for I in itertools.combinations(range(nH), r):
                    if all(j not in adjH[i] for i in I for j in I if j != i):
                        wH = max(wH, sum(len(adjH[i]) for i in I))
            w = n*n*wH
            avg = Fraction(4*m*m, N*N)
            print(f"  {name}[{n}]: N={N} m={m}  m-Dmax={m-Dmax}  m-w={m-w}  m-4m^2/N^2={m-avg}"
                  f"  m/2={Fraction(m,2)}  N^2/25={Fraction(N*N,25)}  N^2/16={Fraction(N*N,16)}"
                  f"   IS-bound {'FAILS (> N^2/25)' if 25*(m-w) > N*N else 'ok'}")
    print()

if __name__ == "__main__":
    check_family()
    check_blowups()
    check_theoremA()
