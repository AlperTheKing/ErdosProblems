import itertools
def conn_set(N,gens):
    S=set()
    for g in gens: S.add(g%N); S.add((-g)%N)
    S.discard(0); return S
def circ_edges(N,gens):
    S=conn_set(N,gens); E=set()
    for v in range(N):
        for s in S: w=(v+s)%N; E.add((min(v,w),max(v,w)))
    return E
def c5n(n):
    e=set()
    for p in range(5):
        q=(p+1)%5
        for j in range(n):
            for k in range(n): a,b=p*n+j,q*n+k; e.add((min(a,b),max(a,b)))
    return e
def adj(N,E):
    a=[set() for _ in range(N)]
    for u,v in E: a[u].add(v); a[v].add(u)
    return a

g1=circ_edges(15,(1,4,6))
a1=adj(15,g1)
print("conn set {1,4,6}:", sorted(conn_set(15,(1,4,6))))
# candidate parts of size 3 = independent sets that are "blobs". {0,5,10}?
def is_indep(S): return all(b not in a1[x] for x,b in itertools.combinations(S,2))
print("{0,5,10} indep:", is_indep([0,5,10]))
print("{1,6,11} indep:", is_indep([1,6,11]))
# Try mapping part_p = {p, p+5, p+10}? but C5 structure is 0-1-2-3-4. Let me test the 5 cosets of <5>? 
# Actually search: does Cay {1,4,6} == C5[3]? Use a known fact: blow-up C5[3] is circulant iff arrangement works.
# Brute isomorphism check is expensive; instead verify both have SAME max-cut beta AND same #(induced C5).
def count_induced_C5(N,E):
    a=adj(N,E); cnt=0
    for S in itertools.combinations(range(N),5):
        ind=[ (x,y) for x,y in itertools.combinations(S,2) if y in a[x]]
        if len(ind)==5:
            # check it's a single 5-cycle (each deg 2, connected)
            deg={v:0 for v in S}
            for x,y in ind: deg[x]+=1; deg[y]+=1
            if all(d==2 for d in deg.values()): cnt+=1
    return cnt
import time
t=time.time()
c1=count_induced_C5(15,g1)
c2=count_induced_C5(15,c5n(3))
print(f"induced C5 count: Cay={c1}  C5[3]={c2}  (time {time.time()-t:.1f}s)")
