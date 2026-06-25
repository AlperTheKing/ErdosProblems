import prove_cert as pc, flag_engine as fe
def popcount(x): return bin(x).count("1")
def wl2(n,A,rounds=6):
    full=(1<<n)-1
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[]
        for v in range(n):
            nb=tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))
            nn=tuple(sorted(col[u] for u in range(n) if u!=v and not ((A[v]>>u)&1)))
            newc.append((col[v],nb,nn))
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}; col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    nep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if not((A[u]>>v)&1)))
    return (tuple(sorted(col)),ep,nep)
C=pc.load(9); states=C["states"]
inv={}; coll=0
for i,(n,A) in enumerate(states):
    k=wl2(n,A)
    if k in inv: coll+=1
    inv.setdefault(k,[]).append(i)
print(f"T_9: {len(states)} states, {len(inv)} distinct invariants, collisions={coll}, INJECTIVE={len(inv)==len(states)}")
