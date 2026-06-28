"""Iterated Mycielskian stress: C5 -> Grotzsch(N=11) -> Myc(Grotzsch)(N=23). Full cert exact.
Mycielskians are triangle-free, high chromatic, NOT blow-ups -- distinct structural family."""
from fractions import Fraction as F
from _h import loads
from _audit_stress import full_test, report

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    C5n=5; C5E=[(i,(i+1)%5) for i in range(5)]
    chain=[("C5",C5n,C5E)]
    n1,E1=mycielski(C5n,C5E); chain.append(("Grotzsch=Myc(C5) N=11",n1,E1))
    n2,E2=mycielski(n1,E1); chain.append(("Myc(Grotzsch) N=23",n2,E2))
    for name,nn,EE in chain:
        info=loads(nn,EE)
        if info is None: print(f"  {name}: loads=None (no valid B-connected maxcut?)",flush=True); continue
        res=full_test(info)
        if res['status']=='noO': print(f"  {name} N={nn}: noO (no overload) -> Perron rho<=maxT<=N trivially",flush=True)
        elif res['status']=='ok': print(f"  {name} N={nn}: ok |O|={len(res['O'])} minrow={float(res['minrow']):+.4f} mink2={float(res['mink2']):+.4f}",flush=True)
        else: print("  "+report(name,nn,res),flush=True)
