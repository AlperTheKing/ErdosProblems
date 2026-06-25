import prove_cert as pc, flag_engine as fe
def popcount(x): return bin(x).count("1")
def wl_inv(n,A,rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[(col[v],tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))) for v in range(n)]
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}; col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)),ep)
def walkcounts(n,A):
    # adjacency as matrix; compute A^2,A^3,A^4 row sums per vertex
    M=[[1 if (A[u]>>v)&1 else 0 for v in range(n)] for u in range(n)]
    def matmul(X,Y):
        return [[sum(X[i][k]*Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    A2=matmul(M,M); A3=matmul(A2,M); A4=matmul(A3,M)
    sig=tuple(sorted((sum(A2[v]),sum(A3[v]),sum(A4[v]),A2[v][v],A3[v][v],A4[v][v]) for v in range(n)))
    return sig
C=pc.load(9); states=C["states"]
inv={}; coll=0
for i,(n,A) in enumerate(states):
    k=(wl_inv(n,A), walkcounts(n,A))
    if k in inv: coll+=1
    inv.setdefault(k,[]).append(i)
print(f"T_9 with (WL,walkcounts): {len(inv)} distinct / {len(states)}, collisions={coll}, INJECTIVE={len(inv)==len(states)}")
