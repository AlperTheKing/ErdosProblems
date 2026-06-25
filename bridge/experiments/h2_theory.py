import itertools
from h2_redteam import min5drop, beta_sub, is_triangle_free

# For any triangle-free G on 15 vtx, what is the max achievable min5drop?
# Bound: removing 5 vertices of highest degree. drop = e(S,V) - (MaxCut(G)-MaxCut(G-S)).
# Since MaxCut(G) <= MaxCut(G-S) + e(S,V) trivially, drop >= 0.
# But we also have: for ANY 5-set, drop <= e(S,V) - 0... not helpful upper bound.
# Real question: is there G triangle-free /15 with min over 5-sets of drop >= 6?

# Triangle-free on 15 vtx has at most floor(15^2/4)=56 edges (Turán/Mantel), C5[3] has 45.
# To make min5drop large you want every 5-set to be "expensive" to reinsert.

# Let's compute, for the two beta=9 Cayley graphs and C5[3], the FULL distribution of 5-set drops
def cayley(conn):
    E=[]
    for v in range(15):
        for s in conn:
            E.append((v,(v+s)%15))
    return sorted(set(tuple(sorted(e)) for e in E))

def c5b3():
    E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(3):
            for b in range(3):
                E.append((i*3+a,j*3+b))
    return sorted(set(tuple(sorted(e)) for e in E))

import collections
for name,E in [("C5[3]",c5b3()),("Cay[1,4,6]",cayley([1,4,6])),("Cay[2,3,7]",cayley([2,3,7]))]:
    es=[tuple(sorted(e)) for e in E]
    bG=beta_sub(set(range(15)),es)
    dist=collections.Counter()
    allv=set(range(15))
    for S in itertools.combinations(range(15),5):
        d=bG-beta_sub(allv-set(S),es)
        dist[d]+=1
    print(name,"beta",bG,"drop dist", dict(sorted(dist.items())))
