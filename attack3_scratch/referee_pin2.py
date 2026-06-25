"""Reproduce the (Q)-violating sparse ell exactly (one heavy edge, rest tiny)."""
import math, sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
sys.path.insert(0, r'E:\Projects\ErdosProblems\attack3_scratch')
from laminar_recursion import adjset, maxcut
from crossing_defect import dell_all

def setup(N, A):
    adj = adjset(N, A); edges=[(u,v) for u in range(N) for v in adj[u] if v>u]
    mc, side = maxcut(N, adj)
    M=[(min(u,v),max(u,v)) for (u,v) in edges if side[u]==side[v]]
    adjB=[set() for _ in range(N)]; Be=[]
    for (u,v) in edges:
        if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u); Be.append((min(u,v),max(u,v)))
    return M, adjB, Be, side

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
M,adjB,Be,side=setup(N,A)
m=len(M); target=(N*N/25.0)**2
print(f"K23 N={N} m={m}  M={M}  target (N^2/25)^2={target:.4f}")
best=0; beste=None; besteps=None
for eps in [1e-2,1e-3,1e-4,1e-6,0.0]:
    for he in Be:
        ell={e:eps for e in Be}; ell[he]=1.0
        s=sum(ell.values()); D=dell_all(N,adjB,ell)
        # guard: with eps=0 some pairs unreachable -> inf; skip inf
        vals=[D[u][v] for (u,v) in M]
        if any(math.isinf(v) for v in vals): continue
        R2=sum((D[u][v]/s)**2 for (u,v) in M)
        val=m**3*R2
        if val>best: best=val; beste=he; besteps=eps
print(f"  worst sparse: heavy edge={beste} eps={besteps}  m^3 R2={best:.4f}  -> (Q) {'VIOLATED' if best>target+1e-9 else 'ok'}  ratio={best/target:.3f}")
# detail at that ell
ell={e:besteps for e in Be}; ell[beste]=1.0
s=sum(ell.values()); D=dell_all(N,adjB,ell)
print(f"  stretches/sum: {sorted(round(D[u][v]/s,4) for (u,v) in M)}")
print(f"  sum_M d/sum (MT25 LHS) = {sum(D[u][v]/s for (u,v) in M):.4f}  bound={max(1.0,N*N/(25.0*m)):.4f}")
print(f"  As eps->0: a single demand routes only across the one heavy edge -> stretch ~1, others ~0")
print("DONE", flush=True)
