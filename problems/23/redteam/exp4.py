import random, itertools
from harness import *

results=[]
def record(name,N,edges):
    b,e,mc,d,tf=evalone(N,edges)
    results.append((round(b/(N*N/25),3), name,N,e,b,mc,round(d,4),tf,in_band(N,e)))

# Idea: take C5[n] but make each part NOT independent across "diagonal"? No - must stay triangle-free.
# Idea: C5 blow-up where we add a perfect matching INSIDE the standard 5-cycle structure won't help.
# Better idea: "balanced blow-up of a denser triangle-free graph than C5".
# The densest triangle-free graphs maximizing beta per edge... Let's test all small graphs?

# Construction: Cayley graph on Z_n with connection set S (S=-S, 0 not in S), triangle-free iff
# no a,b,c in S with a+b=c... actually triangle-free iff S has no solution s1+s2 in S (s1,s2 in S).
# Build circulant triangle-free graphs at band density.
def circulant(n, S):
    edges=set()
    for i in range(n):
        for s in S:
            j=(i+s)%n
            a,b=min(i,j),max(i,j)
            edges.add((a,b))
    return n, list(edges)

def circ_trifree(n,S):
    # check triangle-free
    N,e=circulant(n,S)
    adj=[set() for _ in range(N)]
    for u,v in e: adj[u].add(v); adj[v].add(u)
    for u,v in e:
        if adj[u]&adj[v]: return None
    return N,e

# search circulants N=20,25 for band density max beta
for n in [20,25,15,18,22,24]:
    half=n//2
    bestloc=None
    # connection set = subset of 1..half
    base=list(range(1,half+1))
    for r in range(2, min(6,half)+1):
        for S in itertools.combinations(base, r):
            # symmetric set automatically (circulant uses +/-s)
            chk=circ_trifree(n, list(S))
            if chk is None: continue
            N,e=chk
            if not in_band(N,len(e)): continue
            b,ee,mc,d,tf=evalone(N,e)
            if bestloc is None or b>bestloc[0]:
                bestloc=(b,S,e)
    if bestloc:
        b,S,e=bestloc
        record(f"circulant n={n} S={S}", n, e)

for r in sorted(results,reverse=True):
    print(r)
