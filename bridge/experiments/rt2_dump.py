import itertools, json
def conn_set(N,gens):
    S=set()
    for g in gens: S.add(g%N); S.add((-g)%N)
    S.discard(0); return S
def circ_edges(N,gens):
    S=conn_set(N,gens); E=set()
    for v in range(N):
        for s in S: w=(v+s)%N; E.add((min(v,w),max(v,w)))
    return sorted(E)
def c5n(n):
    e=set()
    for p in range(5):
        q=(p+1)%5
        for j in range(n):
            for k in range(n): a,b=p*n+j,q*n+k; e.add((min(a,b),max(a,b)))
    return sorted(e)

dumps={}
dumps["Cay(Z15,{1,4,6})"]=circ_edges(15,(1,4,6))
dumps["Cay(Z15,{2,3,7})"]=circ_edges(15,(2,3,7))
dumps["Cay(Z15,{1,4})"]=circ_edges(15,(1,4))
dumps["Cay(Z15,{2,7})"]=circ_edges(15,(2,7))
dumps["Cay(Z20,{1,4,9})"]=circ_edges(20,(1,4,9))
dumps["Cay(Z20,{1,6,9})"]=circ_edges(20,(1,6,9))
dumps["Cay(Z20,{3,8})"]=circ_edges(20,(3,8))
# Dodecahedron
dode=[(0,1),(0,4),(0,5),(1,2),(1,6),(2,3),(2,7),(3,4),(3,8),(4,9),(5,10),(5,14),(6,10),(6,11),(7,11),(7,12),(8,12),(8,13),(9,13),(9,14),(10,15),(11,16),(12,17),(13,18),(14,19),(15,16),(15,19),(16,17),(17,18),(18,19)]
dumps["Dodecahedron"]=dode
# Desargues GP(10,3)
des=[(i,(i+1)%10) for i in range(10)]+[(10+i,10+(i+3)%10) for i in range(10)]+[(i,10+i) for i in range(10)]
des=sorted((min(a,b),max(a,b)) for a,b in des)
dumps["Desargues GP(10,3)"]=des

for name, edges in dumps.items():
    print(f"{name}: n_edges={len(edges)}")
    print("  ", edges)
json.dump({k:[list(e) for e in v] for k,v in dumps.items()}, open("rt2_edgelists.json","w"))
print("written rt2_edgelists.json")
