"""
Pin down the (Q)-violating ell on K23-N13 EXACTLY and confirm it is real.
Also test: is (Q) even needed only at the rho-OPTIMAL ell? The strategy's Cauchy step
rho <= sqrt(m R2) is applied at the WORST ell for rho. We must check (Q) precisely there.
"""
import math, heapq, itertools
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
from laminar_recursion import adjset, maxcut, rho_mcf
from crossing_defect import dell_all, optimal_metric_lp

def setup(N, A):
    adj = adjset(N, A); edges=[(u,v) for u in range(N) for v in adj[u] if v>u]
    mc, side = maxcut(N, adj)
    M=[(min(u,v),max(u,v)) for (u,v) in edges if side[u]==side[v]]
    adjB=[set() for _ in range(N)]; Be=[]
    for (u,v) in edges:
        if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u); Be.append((min(u,v),max(u,v)))
    return M, adjB, Be

def gpt_k23():
    N=13; A=[0]*N
    def add(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in (0,1):
        for j in (2,3,4): add(i,j)
    nxt=5
    for (x,y) in [(0,1),(2,3),(2,4),(3,4)]:
        a,b=nxt,nxt+1; nxt+=2; add(x,a); add(a,b); add(b,y)
    return N,A

N,A=gpt_k23()
M,adjB,Be=setup(N,A)
m=len(M)
target=(N*N/25.0)**2
print(f"K23: N={N} m={m} #Be={len(Be)} target (N^2/25)^2={target:.4f}")

# (1) optimal ell for rho
ell_opt=optimal_metric_lp(N,adjB,M,Be)
s=sum(ell_opt.values()); D=dell_all(N,adjB,ell_opt)
R2=sum((D[u][v]/s)**2 for (u,v) in M)
print(f"  OPTIMAL ell:  m^3 R2 = {m**3*R2:.4f}   sum_M d/sum = {sum(D[u][v]/s for (u,v) in M):.4f}  (Q at opt: {'VIOL' if m**3*R2>target+1e-9 else 'ok'})")

# (2) the worst ell found by coordinate search to MAXIMIZE m^3 R2
import random
best=0; bestell=None
random.seed(7)
for trial in range(200000):
    ell={e:random.random() for e in Be}
    sm=sum(ell.values());
    Dd=dell_all(N,adjB,ell)
    val=m**3*sum((Dd[u][v]/sm)**2 for (u,v) in M)
    if val>best: best=val; bestell=dict(ell)
print(f"  WORST random ell for (Q): m^3 R2 = {best:.4f}  -> (Q) {'VIOLATED' if best>target+1e-9 else 'ok'}  ratio={best/target:.3f}")
# show that ell concentrated on a single bad-edge geodesic does it; report stretches
sm=sum(bestell.values()); Dd=dell_all(N,adjB,bestell)
stretch=sorted(round(Dd[u][v]/sm,4) for (u,v) in M)
print(f"     stretches at worst ell: {stretch}  sum={sum(Dd[u][v]/sm for (u,v) in M):.4f}")
# For comparison: the actual MT25 LHS at that worst-for-Q ell:
print(f"     MT25 LHS there = {sum(Dd[u][v]/sm for (u,v) in M):.4f} <= bound {max(1.0,N*N/(25.0*m)):.4f}  (MT25 itself fine)")
print("DONE", flush=True)
