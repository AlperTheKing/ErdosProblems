"""AUDIT G12: exact M1 = min_v e(G-N(v)) for the scan argmaxima, showing that the
target's scan skipped bipartite graphs (`if b == 0: continue`) and therefore
under-reported max M1 at N = 8."""
from fractions import Fraction as Fr
import audit_G12_core as A

for s in ["G?qa`_", "G?`F`w", "H?bB@_W", "I??FCpSJ?", "I?bFB_wF?", "J??CB`gd?[?"]:
    n, E = A.g6(s)
    m = len(E)
    d = A.degrees(n, E)
    a = [set() for _ in range(n)]
    for u, v in E:
        a[u].add(v)
        a[v].add(u)
    M1 = min(sum(1 for (p, q) in E if p not in a[v] and q not in a[v]) for v in range(n))
    print(f"{s}: N={n} m={m} degs={sorted(d)} bip={A.bip(n,E)} "
          f"bipartite={A.is_bipartite(n,E)} M1={M1} M1/N^2={Fr(M1,n*n)}={float(Fr(M1,n*n)):.6f}")
