"""INDEPENDENT exact reproduction of the workflow's N=23 falsification, using MY trusted _half.analyze.
_half.analyze returns per overloaded o: (o, half_margin, low, k2m, S_o, T_o) where
  k2m = N^2(N-T[o]) + sum_q K[o,q]psi(q) = (k2)*N^2 = the k=2 Neumann truncation *N^2.
Claim under test (workflow): on Myc(Grotzsch) N=23, min k2m < 0 (so (k2) is FALSE at N=23),
while TRUE full-depth Schur row-sum stays >=0 (cert condition still holds). Also: does HALF fail too?
EXACT Fraction only."""
from fractions import Fraction as F
from _h import loads
from _half import analyze

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
    n1,E1=mycielski(C5n,C5E)        # Grotzsch N=11
    n2,E2=mycielski(n1,E1)          # Myc(Grotzsch) N=23
    for name,(nn,EE) in [("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2))]:
        info=loads(nn,EE)
        if info is None:
            print(f"{name}: loads=None"); continue
        res,N=analyze(info)
        if not res:
            print(f"{name}: |O|=0 (no overload), (k2) vacuous"); continue
        k2vals=[(r[3],r[0]) for r in res]           # (k2m, o)
        halfvals=[(r[1],r[0]) for r in res]         # (half_margin, o)
        mink2,ok2=min(k2vals); minh,oh=min(halfvals)
        n_k2bad=sum(1 for v,_ in k2vals if v<0); n_hbad=sum(1 for v,_ in halfvals if v<0)
        print(f"=== {name}: |O|={len(res)} ===")
        print(f"  (k2) [=k2m/N^2]: min margin = {float(mink2)/(N*N):+.5f} (exact {mink2}/{N*N}) @ o={ok2} | #o with (k2)<0: {n_k2bad}")
        print(f"  HALF margin   : min = {float(minh):+.4f} @ o={oh} | #o with HALF<0: {n_hbad}")
        # detail on the worst k2 vertex
        for (o,hm,low,k2m,So,To) in res:
            if k2m<0:
                print(f"    o={o}: T={float(To):.3f} S={float(So):.3f} low-regime(T+4S<=2N)={low}  (k2)*N^2={k2m}<0  HALF margin={float(hm):+.3f}")
