import prove_cert as pc, flag_engine as fe
def popcount(x): return bin(x).count("1")
def wl_inv(n, A, rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[]
        for v in range(n):
            nb=tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))
            newc.append((col[v],nb))
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}
        col=[uniq[c] for c in newc]
    edgepairs=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)), edgepairs)
C=pc.load(9); states9=C["states"]
inv={}
coll=0
for i,(n,A) in enumerate(states9):
    k=wl_inv(n,A)
    if k in inv: coll+=1
    inv.setdefault(k,[]).append(i)
print(f"T_9: {len(states9)} states, {len(inv)} distinct WL-invariants, collisions={coll}")
print("WL injective on T_9:", len(inv)==len(states9))
