import random, itertools
from harness import *

def build_random_trifree(N, target_e, seed):
    random.seed(seed)
    adj=[set() for _ in range(N)]
    edges=set()
    allpairs=[(i,j) for i in range(N) for j in range(i+1,N)]
    random.shuffle(allpairs)
    for u,v in allpairs:
        if len(edges)>=target_e: break
        if not (adj[u]&adj[v]):
            edges.add((u,v)); adj[u].add(v); adj[v].add(u)
    return edges, adj

def beta_of(N,edges): return evalone(N,list(edges))[0]

def local_search(N, target_e, seed=0, rounds=120, cands_per_round=40):
    edges,adj=build_random_trifree(N,target_e,seed)
    if len(edges)<target_e:
        return None
    cur_b=beta_of(N,edges)
    allpairs=[(i,j) for i in range(N) for j in range(i+1,N)]
    for rd in range(rounds):
        # generate a batch of candidate swaps (remove e_r, add e_a triangle-free)
        moves=[]; graphs=[]
        elist=list(edges)
        for _ in range(cands_per_round):
            re=random.choice(elist)
            adj[re[0]].discard(re[1]); adj[re[1]].discard(re[0])
            random.shuffle(allpairs); added=None
            for u,v in allpairs:
                if (u,v) in edges or (u,v)==re: continue
                if not (adj[u]&adj[v]): added=(u,v); break
            adj[re[0]].add(re[1]); adj[re[1]].add(re[0])
            if added is None: continue
            ne=set(edges); ne.discard(re); ne.add(added)
            moves.append((re,added)); graphs.append((N,list(ne)))
        if not graphs: continue
        res=evalmany(graphs)
        # pick best improving move
        bi=-1; bb=cur_b
        for i,(b,e,mc,d,tf) in enumerate(res):
            if b>bb: bb=b; bi=i
        if bi>=0:
            re,added=moves[bi]
            edges.discard(re); edges.add(added)
            adj[re[0]].discard(re[1]); adj[re[1]].discard(re[0])
            adj[added[0]].add(added[1]); adj[added[1]].add(added[0])
            cur_b=bb
    return cur_b, edges

import sys
if __name__=="__main__":
    N=int(sys.argv[1]); te=int(sys.argv[2]); nseed=int(sys.argv[3]) if len(sys.argv)>3 else 8
    best=(-1,None)
    for s in range(nseed):
        r=local_search(N,te,seed=s,rounds=100,cands_per_round=30)
        if r and r[0]>best[0]: best=r
    b,E=best
    bb,ee,mc,d,tf=evalone(N,list(E))
    print(f"LS-best N={N} te={te}: beta={bb} e={ee} dens={d:.4f} tf={tf} band={in_band(N,ee)} N^2/25={N*N/25:.2f} ratio={bb/(N*N/25):.3f}")
    print("EDGES",sorted(E))
