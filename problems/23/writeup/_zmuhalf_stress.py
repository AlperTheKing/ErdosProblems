"""ZMU-HALF stress (per guardrail: must survive N=23 Mycielskian + blowups, exact).
ZMU-HALF: for a zero-mu B-edge uv with BOTH T(u)>0 and T(v)>0, max(T(u),T(v)) <= N/2.
Also probe the SHARPER side-bound: is max(T(u),T(v)) <= |side containing the bigger one| or <= min(|side0|,|side1|)?
And: is the bound really N/2 or |smaller side|?
Test on: Grotzsch(11), Myc(Grotzsch)(23), Myc(C7)(15), C5[t] blowups, C7[t], random triangle-free.
Exact Fraction."""
from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def blow(t):
    nn=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return nn,E

def blowC(c,t):
    nn=c*t;E=[]
    for i in range(c):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%c)*t+b))
    return nn,E

def analyze(name, n, E):
    info=loads(n,E)
    if info is None:
        print(f"  {name}: loads None (no gmin)"); return
    N=info['n']; T=info['T']; side=info['side']
    s0=sum(1 for x in side if x==0); s1=N-s0
    mu=mu_edges(info)
    worst=F(0); worst_wit=None; cases=0; viol_half=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]>0 and T[v]>0:
            cases+=1
            mx=max(T[u],T[v])
            if mx>worst: worst=mx; worst_wit=(u,v,str(T[u]),str(T[v]))
            if 2*mx>N: viol_half+=1
    print(f"  {name} (N={N}, sides {s0}/{s1}): both-pos zero-mu cases={cases} | max(max T)={float(worst)}={worst} (N/2={N/2}) | HALF-violations(2max>N)={viol_half}  wit={worst_wit}", flush=True)

if __name__=="__main__":
    print("=== ZMU-HALF stress (max(Tu,Tv)<=N/2 on both-positive zero-mu edges) ===")
    C5=(5,[(i,(i+1)%5) for i in range(5)])
    C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5)            # Grotzsch 11
    n2,E2=mycielski(n1,E1)         # Myc(Grotzsch) 23
    m1,F1=mycielski(*C7)           # Myc(C7) 15
    analyze("Grotzsch", n1,E1)
    analyze("Myc(Grotzsch) N=23", n2,E2)
    analyze("Myc(C7) N=15", m1,F1)
    for t in [2,3,4]:
        nn,EE=blow(t); analyze(f"C5[{t}]", nn,EE)
    for c in [7,9]:
        for t in [2,3]:
            nn,EE=blowC(c,t); analyze(f"C{c}[{t}]", nn,EE)
