"""
ADVERSARIAL REFEREE ATTACK on Strategy-2 Module 3.

Claimed load-bearing sub-claim (Module 3), for ARBITRARY ell:
   (Q)  m^3 * R2  <=  (N^2/25)^2,   R2 = sum_{uv in M} (d_ell(u,v)/sum ell)^2.

Cauchy: rho = sum_M (d/sum) <= sqrt(m R2). If (Q) holds, rho <= N^2/(25 m).

ATTACK: (Q) and the Cauchy chain are claimed to give rho <= N^2/(25m) for EVERY ell.
But MT25 only needs sum_M d <= max(1,N^2/(25m))*sum ell. The strategy ROUTES through
the per-ell quadratic (Q). Test whether (Q) holds for arbitrary (non-optimal) ell,
and whether the *combined* claim "rho_via_Cauchy <= N^2/(25m) for every ell" is what
is actually needed -- or whether (Q) is just MT25-for-this-ell re-stated.
"""
import math, heapq, itertools, random
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
from laminar_recursion import adjset, maxcut, rho_mcf
from crossing_defect import dell_all

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

def test_Q_arbitrary(N, A, name, n_random=30000):
    M, adjB, Be = setup(N, A)
    if not M:
        print(f"{name}: no M"); return
    m=len(M)
    target=(N*N/25.0)**2
    worst_Q=0.0; worst_sumMd=0.0; worst_lin_ratio=0.0
    cands=[{e:1.0 for e in Be}]
    random.seed(1)
    for _ in range(n_random):
        cands.append({e:random.random() for e in Be})
    for he in Be:
        d={e:0.001 for e in Be}; d[he]=1.0; cands.append(d)
    for ell in cands:
        s=sum(ell.values())
        if s<=0: continue
        D=dell_all(N, adjB, ell)
        R2=sum((D[u][v]/s)**2 for (u,v) in M)
        sumMd=sum(D[u][v]/s for (u,v) in M)
        if m**3*R2>worst_Q: worst_Q=m**3*R2
        # the ACTUAL MT25 LHS ratio for this ell:
        lin_ratio = sumMd  # = sum_M d / sum ell  (this must be <= max(1,N^2/25m))
        if lin_ratio>worst_lin_ratio: worst_lin_ratio=lin_ratio
    bound=max(1.0, N*N/(25.0*m))
    print(f"{name}: N={N} m={m}")
    print(f"    max_ell m^3 R2 = {worst_Q:.4f}  vs (N^2/25)^2={target:.4f}  {'(Q) VIOLATION' if worst_Q>target+1e-6 else 'ok'}")
    print(f"    max_ell sum_M d/sum_ell (=true MT25 LHS) = {worst_lin_ratio:.4f}  vs bound max(1,N^2/25m)={bound:.4f}  {'MT25 VIOLATION' if worst_lin_ratio>bound+1e-6 else 'ok'}")

test_Q_arbitrary(*gpt_k23(), "K23-N13")
verts=list(itertools.combinations(range(5),2)); A=[0]*10
for i,a in enumerate(verts):
    for j,b in enumerate(verts):
        if i<j and not set(a)&set(b): A[i]|=1<<j; A[j]|=1<<i
test_Q_arbitrary(10, A, "Petersen")
print("DONE", flush=True)
