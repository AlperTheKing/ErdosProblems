import time, itertools
import prove_cert as pc, flag_engine as fe
def popcount(x): return bin(x).count("1")
def wl_inv(n,A,rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[(col[v],tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))) for v in range(n)]
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}; col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)),ep)
C=pc.load(9); states=C["states"]
g10=fe.enumerate_graphs(10,triangle_free=True)
# time fe.canonical(9) on 200 states
t=time.time()
for i in range(200): fe.canonical(9,states[i][1])
print(f"fe.canonical(9) x200: {time.time()-t:.2f}s -> {(time.time()-t)/200*1000:.2f}ms each")
# time wl_inv x200
t=time.time()
for i in range(200): wl_inv(9,states[i][1])
print(f"wl_inv(9) x200: {time.time()-t:.2f}s -> {(time.time()-t)/200*1000:.2f}ms each")
# time gamma on 200 dense (last) J's
full=(1<<10)-1
t=time.time()
for j in range(len(g10)-200,len(g10)):
    n,A=g10[j]
    for S in itertools.combinations(range(10),5):
        mask=0
        for v in S: mask|=1<<v
        comp=full&~mask; ok=all(popcount(A[v]&mask)==2 for v in S)
        if ok: _=all(popcount(A[v]&comp)==2 for v in range(10) if (comp>>v)&1)
print(f"gamma x200 (densest J): {time.time()-t:.2f}s -> {(time.time()-t)/200*1000:.2f}ms each, full~{(time.time()-t)/200*12172:.0f}s")
# time fe.induced x200
t=time.time()
for j in range(200):
    n,A=g10[j]
    for v in range(10): fe.induced(A,[u for u in range(10) if u!=v])
print(f"fe.induced x2000: {time.time()-t:.2f}s")
