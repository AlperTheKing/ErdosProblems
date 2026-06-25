import time,sys,itertools
import prove_cert as pc, flag_engine as fe
def popcount(x): return bin(x).count("1")
def wl_inv(n,A,rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[(col[v],tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))) for v in range(n)]
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}
        col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)),ep)
t=time.time(); C=pc.load(9); states9=C["states"]; print(f"load {time.time()-t:.1f}s",file=sys.stderr)
t=time.time()
buckets={}
for i,(n,A) in enumerate(states9):
    w=wl_inv(n,A); buckets.setdefault(w,[]).append((fe.canonical(9,A),i))
print(f"bucket build (1897 wl+canon) {time.time()-t:.1f}s",file=sys.stderr)
t=time.time(); g10=fe.enumerate_graphs(10,triangle_free=True); print(f"T10 enum {time.time()-t:.1f}s n={len(g10)}",file=sys.stderr)
single={w:l[0][1] for w,l in buckets.items() if len(l)==1}; multi={w:l for w,l in buckets.items() if len(l)>1}
def match9(A9):
    w=wl_inv(9,A9)
    if w in single: return single[w]
    ck=fe.canonical(9,A9)
    for (k,idx) in multi[w]:
        if k==ck: return idx
    return -1
t=time.time()
for j in range(300):
    n,A=g10[j]
    for v in range(10):
        verts=[u for u in range(10) if u!=v]; m,B=fe.induced(A,verts); match9(B)
dt=time.time()-t; print(f"D 300J {dt:.1f}s -> full ~{dt/300*len(g10):.0f}s",file=sys.stderr)
t=time.time(); full=(1<<10)-1
for j in range(300):
    n,A=g10[j]
    for S in itertools.combinations(range(10),5):
        mask=0
        for v in S: mask|=1<<v
        comp=full&~mask; ok=all(popcount(A[v]&mask)==2 for v in S)
dt=time.time()-t; print(f"gamma 300J {dt:.1f}s -> full ~{dt/300*len(g10):.0f}s",file=sys.stderr)
