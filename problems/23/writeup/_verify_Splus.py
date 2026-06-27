"""EXACT-test the user's (S+): for every phi>=0, do weights x_{f,C}>=0 on the phi-MINIMIZING shortest cycles C_f(phi)
with sum_C x_{f,C}=1 exist such that for EVERY distinct nonempty superlevel set S_t(phi)={v:phi(v)>t}:
   sum_f ell(f) sum_C x_{f,C} |C cap S_t|  <=  K |S_t| ,  K=N+(N^2-Gamma)?
LP-feasibility per phi (scipy). If feasible for all tested phi on all witnesses, (S+) is numerically supported.
Also report: is (S+) feasible using the SAME weights across all levels (it must -- one routing serves all S_t)."""
import numpy as np
from scipy.optimize import linprog
from census_GPI import dec, maxcut_all, gmin, geos, blow
import random

def splus_feasible(n,E,phi):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    K=n+(n*n-G)
    # phi-min cycles per bad edge
    cols=[]; ec={}
    for ei,f in enumerate(M):
        Ps=geos(adj,side,f[0],f[1])
        masses=[sum(phi[v] for v in P) for P in Ps]
        mn=min(masses)
        Cf=[P for P,m in zip(Ps,masses) if m==mn]   # argmin (phi-minimizing)
        ec[ei]=[]
        for P in Cf: ec[ei].append(len(cols)); cols.append((ei,set(P),ell[f]))
    nx=len(cols)
    # distinct nonempty superlevel sets S = {v: phi[v] >= theta} for theta in sorted distinct positive values
    vals=sorted(set(v for v in phi if v>0))
    Ss=[]
    for theta in vals:
        S=set(u for u in range(n) if phi[u]>=theta)
        if S: Ss.append(S)
    # LP: vars x (nx). equality sum_C x=1 per edge. ineq: for each S, sum_f ell sum_{C in S-touch} x*|C cap S| <= K|S|
    Aeq=[]; beq=[]
    for ei in range(len(M)):
        row=[0.0]*nx
        for j in ec[ei]: row[j]=1.0
        Aeq.append(row); beq.append(1.0)
    Aub=[]; bub=[]
    for S in Ss:
        row=[0.0]*nx
        for j,(ei,vs,h) in enumerate(cols):
            row[j]=h*len(vs & S)
        Aub.append(row); bub.append(K*len(S))
    res=linprog(np.zeros(nx), A_ub=np.array(Aub) if Aub else None, b_ub=np.array(bub) if bub else None,
                A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=[(0,None)]*nx, method='highs')
    return res.success

def run(name,n,E,trials=300):
    rng=random.Random(99)
    infeas=0; ok=0
    for _ in range(trials):
        phi=[rng.randint(0,5) for _ in range(n)]
        if sum(phi)==0: continue
        f=splus_feasible(n,E,phi)
        if f is None: print(f"  {name}: no gmin"); return
        if f: ok+=1
        else: infeas+=1
    print(f"  {name:7}: (S+) LP-feasible in {ok}/{ok+infeas} random phi | INFEASIBLE (S+ FAILS): {infeas}")

print("=== EXACT-test (S+): phi-min-cycle routing with superlevel-set load bound feasible for all phi? ===")
for q in (2,3): run(f"C5[{q}]",*blow(q))
run("n8",*dec("G?\x60F\x60w"))
run("N11a",*dec("J?BD@g]Qvo?")); run("N11b",*dec("J?AAD@ON@[?")); run("N11c",*dec("J?AAD@WM_{?"))
print("0 infeasible everywhere => (S+) holds numerically (the user's stronger inequality is consistent).")
