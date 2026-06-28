"""Investigate the k2_neg finding on Myc(Grotzsch) N=23.
Confirm EXACT: (a) full cert conditions (1)(2)(3) -- does TRUE E-rowsum stay >=0? (it printed +6.56)
(b) k2 truly negative? what Neumann depth k makes the truncation >=0? (the (k2)=>(3) argument needs the
SMALLEST k that always works; k=2 is refuted here.)
This does NOT break the certificate (true rowsum>=0 => cond3 holds) but BREAKS the proposed k=2 proof of cond3."""
from fractions import Fraction as F
from _h import loads
from _audit_stress import full_test, build_K
from _schur_neumann import neumann_resid

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    C5n=5; C5E=[(i,(i+1)%5) for i in range(5)]
    n1,E1=mycielski(C5n,C5E)          # Grotzsch N=11
    n2,E2=mycielski(n1,E1)            # Myc(Grotzsch) N=23
    info=loads(n2,E2)
    res=full_test(info)
    print("Myc(Grotzsch) N=23 full cert:", res['status'], "fails=",res['fails'],
          "TRUE-min-E-rowsum=",float(res['minrow']), "mink2=",float(res['mink2']))
    print("  => certificate conditions (1)(2)(3):", "STILL HOLD (E rowsum>=0)" if res['minrow']>=0 else "ACTUALLY FAIL")
    print("  => the k=2 proxy:", "FAILS (k2<0)" if res['mink2']<0 else "ok")
    # depth sweep
    K,T,N,n=build_K(info)
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    out=neumann_resid(K,T,O,Q,N,n,16)
    print("  Neumann depth sweep (min over o of r[o]+K[o,Q].g_k):")
    smallest=None
    for k in sorted(out):
        v=out[k]
        if v>=0 and smallest is None: smallest=k
        print(f"    k={k:2d}: min={float(v):+.5f}{'  <-- first >=0' if k==smallest else ''}")
    print(f"  SMALLEST Neumann depth k with truncation>=0: {smallest}")
