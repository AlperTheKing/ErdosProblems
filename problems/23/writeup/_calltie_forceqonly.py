"""Force a Q-only K-component containing a saturated vertex, IGNORING gamma-min stability,
to test the structural implication: must such a component be CRITICAL (T==N on all of it)?

We take a FIXED (not nec. gamma-min) max-cut-like side assignment that yields:
  - an overloaded region O (so Q-only is meaningful)
  - a SEPARATE K-component (no shared geodesics) that contains a saturated vertex.

Construction: take C5 (gives uniform T=5 -- every vertex saturated if N=5, but we need N>5).
Use disjoint union of an overloaded gadget and a C5; on the union with N=total, C5 vertices have
T=5 < N, NOT saturated. To get a saturated vertex in a SMALL component we need T(v)=N=total,
which requires the small component to carry ~N load alone. Hard in a disjoint union.

Instead: directly test the IMPLICATION abstractly. A K-closed component C has K|_C row-sum at w = T(w).
If v in C has T(v)=N=rho-bound, then by Perron on the irreducible sub-block of C containing v,
rho(block)=N forces T==N on that block. So:
  CLAIM(C2): the irreducible K-sub-block containing a saturated vertex is critical (T==N on it).
This is PROVABLE (Perron max-rowsum equality). Test it numerically on the load-bearing comp by
looking at irreducible sub-blocks... but K|_C is itself irreducible (it's a K-component).
So CLAIM(C2) => if v saturated and Kcomp(v)=C is a single irreducible block, T==N on ALL of C.
Then C-alltie contrapositive C subset Q => C critical => NO-CRITICAL (irreducibility lever) => done,
PROVIDED Kcomp(v) is irreducible (always true: a K-component IS connected => irreducible).

VERIFY CLAIM(C2) exactly: for the load-bearing K-component L of real graphs (which DOES contain O),
restrict to L cap Q and check: if a saturated vertex v in L exists, is T==N forced on its
K-component? (It's NOT, because L contains O with T>N, so L is NOT all-saturated -- but L is
irreducible with rho(K|_L) >= max T(o) > N, so the row-sum-equality argument does NOT apply to L.)
The point: a Q-only component has rho <= N, and a saturated v forces rho=N (Perron lower bound
rho >= min... no, rho >= row-sum only via Perron for the MAX). Let me test the exact Perron claim.
"""
from fractions import Fraction as F
from _h import dec, loads
from _satzmu_conn import struct_for_side, kcomponents

def buildK(n, cyc):
    K = [[F(0)]*n for _ in range(n)]
    for f, Ps in cyc.items():
        nf = len(Ps)
        cnt = [0]*n
        for P in Ps:
            for v in P: cnt[v] += 1
        pf = [F(cnt[v], nf) for v in range(n)]
        for a in range(n):
            if pf[a] == 0: continue
            for b in range(n):
                if pf[b] == 0: continue
                K[a][b] += pf[a]*pf[b]
    return K

def perron_frac(M, iters=2000):
    """Power iteration in float for rho estimate (M nonneg symmetric)."""
    m = len(M)
    if m == 0: return 0.0
    Mf = [[float(M[i][j]) for j in range(m)] for i in range(m)]
    x = [1.0]*m
    for _ in range(iters):
        y = [sum(Mf[i][j]*x[j] for j in range(m)) for i in range(m)]
        nrm = max(abs(v) for v in y) or 1.0
        x = [v/nrm for v in y]
    # Rayleigh
    Mx = [sum(Mf[i][j]*x[j] for j in range(m)) for i in range(m)]
    num = sum(x[i]*Mx[i] for i in range(m)); den = sum(x[i]*x[i] for i in range(m))
    return num/den

if __name__ == "__main__":
    print("=== Perron structure of K-components: does a saturated vertex force rho(K|_C)=N? ===")
    # On the load-bearing component L (contains O), rho(K|_L) >= max_o T(o) > N.
    # A Q-only component C (hypothetical) has all T<=N so rho(K|_C) <= N (max row sum).
    # If v in C is saturated, row sum at v = T(v)=N = the max possible, so the MAX row sum is N.
    # For an IRREDUCIBLE nonneg symmetric matrix, rho = max row sum  IFF  all row sums equal (=N).
    # => C critical. This is the PROVABLE chain. Verify the 'rho=maxrowsum iff const rowsum' fact
    # on small K-blocks empirically (sanity), and confirm a K-component is always irreducible.
    for g6 in ["J??CBAPFvo?", "I?BD@g]Qo", "G?bF`w"]:
        n, E = dec(g6); info = loads(n, E)
        if info is None: print(f"  {g6}: None"); continue
        st = struct_for_side(n, info['adj'], info['side'])
        if st is None: continue
        M, ell, T, mu, cyc = st; N = n
        comp, find = kcomponents(n, cyc)
        comps = {}
        for v in range(n): comps.setdefault(find(v), set()).add(v)
        for root, C in comps.items():
            if len(C) <= 1: continue
            Cl = sorted(C)
            sub = [[buildK(n, cyc)[i][j] for j in Cl] for i in Cl]
            rho = perron_frac(sub)
            rowsums = [float(sum(sub[i])) for i in range(len(Cl))]
            print(f"  {g6}: K-comp |C|={len(Cl)} rho~={rho:.4f} N={N} rowsums(min,max)=({min(rowsums):.3f},{max(rowsums):.3f}) const={max(rowsums)-min(rowsums)<1e-9}")
