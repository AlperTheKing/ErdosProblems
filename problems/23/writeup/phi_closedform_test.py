#!/usr/bin/env python3
"""Test NATURAL closed-form potentials phi for GPI dual-optimality (ratio R = sum_f ell(f) m_phi(f)/sum_v phi = tau*).
Candidates: uniform; geodesic-betweenness (count of shortest bad-cycles through v); bad-endpoint indicator;
B-degree; apex-indicator (vertices that are endpoints of >=2 bad edges, i.e. pencil hubs). Any phi reaching tau*
is a CLOSED-FORM dual certificate ansatz -- the object Step-2 needs. Exact-test on the witnesses."""
import numpy as np
from scipy.optimize import linprog
from census_GPI import dec, maxcut_all, gmin, geos, blow

def setup(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj));
    if r is None: return None
    side,G,M,ell=r
    geo={f:geos(adj,side,f[0],f[1]) for f in M}
    return adj,side,G,M,ell,geo

def tau_star(n,M,ell,geo):
    cols=[]; ec={}
    for ei,f in enumerate(M):
        ec[ei]=[]
        for P in geo[f]: ec[ei].append(len(cols)); cols.append((ei,set(P),ell[f]))
    nx=len(cols); c=np.zeros(nx+1); c[-1]=1
    Aeq=[]; beq=[]
    for ei in range(len(M)):
        row=np.zeros(nx+1)
        for j in ec[ei]: row[j]=1
        Aeq.append(row); beq.append(1)
    Aub=[]; bub=[]
    for v in range(n):
        row=np.zeros(nx+1)
        for j,(ei,vs,h) in enumerate(cols):
            if v in vs: row[j]=h
        row[-1]=-1; Aub.append(row); bub.append(0)
    res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=[(0,None)]*nx+[(0,None)],method='highs')
    return res.fun

def ratio(M,ell,geo,phi):
    sp=sum(phi.values())
    if sp<1e-12: return 0.0
    lhs=sum(ell[f]*min(sum(phi[v] for v in P) for P in geo[f]) for f in M)
    return lhs/sp

def run(n,E,name):
    s=setup(n,E)
    if s is None: print(f"  {name}: no gmin"); return
    adj,side,G,M,ell,geo=s
    tau=tau_star(n,M,ell,geo)
    Bdeg={v:sum(1 for w in adj[v] if side[w]!=side[v]) for v in range(n)}
    badcount={v:0 for v in range(n)}
    for u,v in M: badcount[u]+=1; badcount[v]+=1
    # geodesic-betweenness: number of shortest bad-cycles (over all bad edges) through v
    betw={v:0 for v in range(n)}
    for f in M:
        for P in geo[f]:
            for v in P: betw[v]+=1
    cands={
        "uniform":      {v:1.0 for v in range(n)},
        "betweenness":  betw,
        "badendpt":     {v:(1.0 if badcount[v]>0 else 0.0) for v in range(n)},
        "apex(>=2bad)": {v:(1.0 if badcount[v]>=2 else 0.0) for v in range(n)},
        "Bdeg":         {v:float(Bdeg[v]) for v in range(n)},
        "badcount":     {v:float(badcount[v]) for v in range(n)},
    }
    print(f"  {name}: N={n} Gamma={G} tau*={tau:.3f}")
    for cn,phi in cands.items():
        R=ratio(M,ell,geo,phi)
        print(f"     phi={cn:14} R={R:.4f}  dual-opt(R==tau*)? {abs(R-tau)<1e-4}")

print("=== natural closed-form potential phi: GPI dual-optimality (R==tau*) test ===")
for q in (2,3): run(*blow(q), f"C5[{q}]")
run(*dec("G?\x60F\x60w"), "n8")
run(*dec("J?BD@g]Qvo?"), "N11a")
run(*dec("J?AAD@ON@[?"), "N11b")
run(*dec("J?AAD@WM_{?"), "N11c")
print("\nAny phi with R==tau* on ALL witnesses = a closed-form dual certificate ansatz for the GPI (hand to Step-2).")
