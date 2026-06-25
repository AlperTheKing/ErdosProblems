import itertools
from h2_redteam import min5drop, beta_sub

N=15
def adj_from(edges):
    adj=[set() for _ in range(N)]
    for (u,v) in edges:
        adj[u].add(v); adj[v].add(u)
    return adj

def maxcut_color(edges):
    # return an optimal coloring (bitmask) and maxcut value, brute
    best=-1; bestc=0
    for c in range(1<<N):
        cut=0
        for (u,v) in edges:
            if ((c>>u)^(c>>v))&1: cut+=1
        if cut>best: best=cut; bestc=c
    return bestc,best

# For C5[3], test: take optimal cut, then for each candidate 5-set T, compute the
# "reinsertion recovery" = max edges of T recoverable when G-T keeps its induced opt cut.
# This is a LOWER bound on MaxCut(G) hence drop <= e(T,V) - recovery.
def c5b3():
    E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(3):
            for b in range(3):
                E.append((i*3+a,j*3+b))
    return sorted(set(tuple(sorted(e)) for e in E))

# Hypothesis check: is min5drop over triangle-free /15 ALWAYS <=5? Test extremal-ish
# by checking many graphs is done elsewhere. Here verify the transversal recovers exactly.
E=c5b3()
adj=adj_from(E)
# A C5-transversal: one vtx per part, e.g 0,3,6,9,12
T=[0,3,6,9,12]
es=[tuple(sorted(e)) for e in E]
bG=beta_sub(set(range(N)),es)
bGT=beta_sub(set(range(N))-set(T),es)
eTV=sum(len(adj[v]) for v in T)  # no internal edges in transversal (independent? check)
internal=sum(1 for i in range(5) for j in range(i+1,5) if T[j] in adj[T[i]])
print("transversal T=",T,"e(T,V)=",eTV,"internal edges in T=",internal,
      "drop=",bG-bGT,"beta(G)=",bG,"beta(G-T)=",bGT)
# Each transversal vertex has degree 4 in C5[3] (2 parts x ... no: part i connects to parts i-1,i+1, each size3 =>deg 6)
print("degrees in T:",[len(adj[v]) for v in T])
