import random, itertools
from harness import *

results=[]
def record(name,N,edges):
    b,e,mc,d,tf=evalone(N,edges)
    band=in_band(N,e)
    tgt=N*N/25.0
    results.append((b/tgt, name,N,e,b,mc,round(d,4),tf,band))
    return b,e,mc,d,tf

# ---- Family A: unbalanced C5 blowups at N=20,25 ----
def c5_parts(sizes):
    offs=[0]
    for s in sizes: offs.append(offs[-1]+s)
    N=offs[5]; edges=[]
    for p in range(5):
        q=(p+1)%5
        for i in range(sizes[p]):
            for j in range(sizes[q]):
                edges.append((offs[p]+i, offs[q]+j))
    return N,edges

# enumerate part-size vectors summing to 20 and 25, keep those in band, record beta
for total in [20,25]:
    best=None
    for sizes in itertools.combinations_with_replacement(range(0,total),5):
        if sum(sizes)!=total: continue
        if 0 in sizes: continue
        N,edges=c5_parts(list(sizes))
        if N!=total: continue
        e=len(edges)
        if not in_band(N,e): continue
        b,ee,mc,d,tf=evalone(N,edges)
        if best is None or b>best[0]:
            best=(b,sizes,e,mc,d)
    if best:
        b,sizes,e,mc,d=best
        record(f"C5blowup-unbal{sizes}",total,c5_parts(list(sizes))[1])

# ---- Family B: Petersen graph (N=10, e=15, girth5 triangle-free), and blowups ----
pet=[(0,1),(1,2),(2,3),(3,4),(4,0),  # outer
     (5,7),(7,9),(9,6),(6,8),(8,5),  # inner pentagram
     (0,5),(1,6),(2,7),(3,8),(4,9)]  # spokes
record("Petersen",10,pet)

# Petersen blow-up x2 (N=20)
def blowup(N,edges,t):
    NN=N*t; ee=[]
    for u,v in edges:
        for a in range(t):
            for c in range(t):
                ee.append((u*t+a, v*t+c))
    return NN,ee
N2,e2=blowup(10,pet,2)
record("Petersen[2]",N2,e2)

# ---- Family C: Kneser/other named ----
# C7 blowups? C7 is triangle-free. blow up C7 to N=21? Actually do cycle C_k blowups.
def cycle(k):
    return [(i,(i+1)%k) for i in range(k)]
# C7 blowup x3 = N=21
N,e=blowup(7,cycle(7),3); record("C7[3]",N,e)
# C5 blowup deleted already covered.

print("done family A-C")
for r in sorted(results,reverse=True):
    print(r)
