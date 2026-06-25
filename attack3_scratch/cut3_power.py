from beta import *
from cut3 import cut3, neighbors
from search_small import gen
import sys

def best_cut3(adj,n):
    # min over all nonedges of the cut3 bound; if no nonedge return e
    best=None
    for u in range(n):
        for v in range(u+1,n):
            if not (adj[u]>>v)&1:
                bd=cut3(adj,n,u,v)['bound']
                if best is None or bd<best: best=bd
    if best is None:
        return num_edges(adj,n)
    return best

def conj_cap(N):
    # best balanced C5 blowup value on N vertices
    import itertools
    best=-1
    for a in range(N+1):
      for b in range(N+1-a):
        for c in range(N+1-a-b):
          for d in range(N+1-a-b-c):
            e=N-a-b-c-d
            ms=[a,b,c,d,e]
            v=min(ms[i]*ms[(i+1)%5] for i in range(5))
            if v>best:best=v
    return best

if __name__=="__main__":
    N=int(sys.argv[1])
    cap=conj_cap(N)
    # for each graph, compare beta, cut3-bound to cap
    n_graphs=0; cut3_exceeds_cap=0; cut3_loose=0; maxbeta=-1
    worst_gap=-10  # max(cut3_bound - cap)
    for adj,n in gen(N):
        n_graphs+=1
        b=beta(adj,n)
        if b>maxbeta:maxbeta=b
        c=best_cut3(adj,n)
        if c>cap:
            cut3_exceeds_cap+=1
            if c-cap>worst_gap: worst_gap=c-cap
    print(f"N={N}: conj_cap={cap}, maxbeta={maxbeta}, graphs={n_graphs}")
    print(f"  #graphs where min-nonedge-CUT3 bound > cap: {cut3_exceeds_cap} (worst overshoot {worst_gap})")
