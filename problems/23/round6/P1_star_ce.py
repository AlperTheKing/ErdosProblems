"""Examine the q=20 point that beats min(A,B) = 1/25, exactly, and find out what really closes it."""
from fractions import Fraction as F
from P1_engine import Meas, TARGET, gamma

cands = {
    "G20 w=1/8 at 0,1,6,7,12,13,14,19": (20, [0, 1, 6, 7, 12, 13, 14, 19]),
    "G20 w=1/8 at 0,5,6,7,12,13,14,19": (20, [0, 5, 6, 7, 12, 13, 14, 19]),
}
for name, (q, sup) in cands.items():
    w = [F(1, 8) if k in sup else F(0) for k in range(q)]
    mu = Meas([F(k, q) for k in range(q)], w)
    arc, argm = mu.arcbound(with_arg=True)
    print(f"{name}")
    print(f"   W={mu.W}={float(mu.W):.6f}  rho={mu.rho}  kappa={mu.kappa}")
    print(f"   A={mu.A}={float(mu.A):.6f}   B={mu.B}={float(mu.B):.6f}   "
          f"b0={mu.bound(0)}={float(mu.bound(0)):.6f}")
    print(f"   min(A,B)={float(min(mu.A, mu.B)):.6f}   ARCBOUND={arc}={float(arc):.6f} "
          f"at (start,len)={argm}")
    print(f"   degrees g = {[str(gg) for gg in mu.g]}")
    print(f"   Varg={mu.Varg}  bound_k k=0..5: {[float(mu.bound(k)) for k in range(6)]}")
    # value of every arc cut length
    n = mu.n
    print("   arc-cut values by (start index, #atoms in arc):")
    vals = {}
    for i in range(n):
        inI = [False] * n
        for L in range(n + 1):
            if L > 0:
                v = (i + L - 1) % n
                inI[v] = True
            Ein = sum(mu.wt[a] * mu.wt[b] for a in range(n) for b in range(a + 1, n)
                      if mu.adj[a][b] and inI[a] and inI[b])
            Eout = sum(mu.wt[a] * mu.wt[b] for a in range(n) for b in range(a + 1, n)
                       if mu.adj[a][b] and not inI[a] and not inI[b])
            vals.setdefault(L, []).append(Ein + Eout)
    for L in sorted(vals):
        print(f"      L={L}: min={min(vals[L])}={float(min(vals[L])):.6f}")
    print()
