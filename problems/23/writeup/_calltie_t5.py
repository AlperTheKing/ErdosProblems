"""Measure maxT_C - |C| (excess) on LARGE instances: Mycielskians, blowups, the N=22/23 witnesses.
This tells us whether the intrinsic 'excess' is bounded or grows with N.
If excess can exceed 5, the simple vertex-budget (need >=6 outside) does NOT close.
Exact Fraction."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _calltie_glue import components_from_info

def mycielski(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def report(name, nn, EE):
    info=loads(nn,EE)
    if info is None:
        print(f"{name}: loads None"); return
    T=info['T']; N=info['n']
    O=set(v for v in range(N) if T[v]>N)
    comps=components_from_info(info)
    loaded=[C for C in comps if sum(T[v] for v in C)>0]
    rows=[]
    for C in loaded:
        mx=max(T[v] for v in C); sz=len(C); gc=sum(T[v] for v in C)
        meetsO=bool(C & O)
        rows.append((float(mx-sz), sz, float(mx), float(gc), meetsO))
    rows.sort(reverse=True)
    print(f"{name} N={N}: |O|={len(O)} #loaded-Kcomp={len(loaded)} "
          f"max(excess maxT-|C|)={rows[0][0]:+.2f} "
          f"[topcomp sz={rows[0][1]} maxT={rows[0][2]} GammaC={rows[0][3]} meetsO={rows[0][4]}]")

if __name__=="__main__":
    print("=== excess maxT_C-|C| on LARGE instances ===")
    # Mycielskian chain from C5
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    n1,E1=mycielski(*C5)
    n2,E2=mycielski(n1,E1)
    report("Grotzsch", n1,E1)
    report("MycGrotzsch", n2,E2)
    # C5 blowups
    for t in [2,3,4]:
        nn=5*t; E=[]
        for i in range(5):
            for a in range(t):
                for b in range(t): E.append((i*t+a,((i+1)%5)*t+b))
        report(f"C5[{t}]", nn, E)
    # named blowups
    for g6,t in [("J???E?pNu\\?",2),("G?bF`w",3),("I?BD@g]Qo",2)]:
        try:
            nn,EE=blow(t) if False else (None,None)
        except: pass
    # the N=22 witness
    for g6 in ["J???E?pNu\\?"]:
        n,E=dec(g6); report(g6,n,E)
