import random, itertools
from harness import *

def tri_free_add_ok(adj,u,v):
    return len(adj[u]&adj[v])==0  # no common neighbor => no triangle when adding u-v

def local_search(N, target_e, iters=4000, seed=0, init_edges=None):
    random.seed(seed)
    adj=[set() for _ in range(N)]
    edges=set()
    if init_edges:
        for u,v in init_edges:
            a,b=min(u,v),max(u,v)
            edges.add((a,b)); adj[a].add(b); adj[b].add(a)
    # grow to target_e by random triangle-free additions
    allpairs=[(i,j) for i in range(N) for j in range(i+1,N)]
    def try_add():
        random.shuffle(allpairs)
        for u,v in allpairs:
            if (u,v) in edges: continue
            if tri_free_add_ok(adj,u,v):
                edges.add((u,v)); adj[u].add(v); adj[v].add(u); return True
        return False
    while len(edges)<target_e:
        if not try_add(): break
    # current beta
    def cur_beta():
        return evalone(N,list(edges))[0]
    best_b=cur_beta(); best_edges=set(edges)
    # swap moves: remove a random edge, add a random triangle-free non-edge, accept if beta>=
    T=2.0
    for it in range(iters):
        if len(edges)==0: break
        re=random.choice(list(edges))
        edges.discard(re); adj[re[0]].discard(re[1]); adj[re[1]].discard(re[0])
        # find an addable edge
        random.shuffle(allpairs); added=None
        for u,v in allpairs:
            if (u,v) in edges: continue
            if (u,v)==re: continue
            if tri_free_add_ok(adj,u,v):
                added=(u,v); break
        if added is None:
            # revert
            edges.add(re); adj[re[0]].add(re[1]); adj[re[1]].add(re[0]); continue
        edges.add(added); adj[added[0]].add(added[1]); adj[added[1]].add(added[0])
        b=evalone(N,list(edges))[0]
        T*=0.999
        if b>=best_b - (1 if random.random()<0.1 else 0):
            if b>best_b:
                best_b=b; best_edges=set(edges)
        else:
            # revert
            edges.discard(added); adj[added[0]].discard(added[1]); adj[added[1]].discard(added[0])
            edges.add(re); adj[re[0]].add(re[1]); adj[re[1]].add(re[0])
    return best_b, best_edges

# Run for N=20 target e=60 (density 0.30), several seeds, init from C5[4] truncated
for N,te in [(20,60),(20,56),(25,90),(15,33)]:
    best_overall=(-1,None)
    for seed in range(6):
        b,E=local_search(N,te,iters=1500,seed=seed)
        if b>best_overall[0]:
            best_overall=(b,E)
    b,E=best_overall
    bb,ee,mc,d,tf=evalone(N,list(E))
    print(f"LS N={N} te={te}: beta={bb} e={ee} dens={d:.4f} tf={tf} band={in_band(N,ee)} N^2/25={N*N/25:.1f} ratio={bb/(N*N/25):.3f}")
