import itertools, random
from h2_redteam import min5drop

N=15
ALLPAIRS=[(i,j) for i in range(N) for j in range(i+1,N)]

def adj_from_edges(edges):
    adj=[0]*N
    for (u,v) in edges:
        adj[u]|=1<<v; adj[v]|=1<<u
    return adj

def tf(edges):
    adj=adj_from_edges(edges)
    for (u,v) in edges:
        if adj[u]&adj[v]:
            return False
    return True

def tf_add_ok(adj, u, v):
    # adding edge u-v keeps triangle-free iff u,v share no neighbor
    return (adj[u]&adj[v])==0

def score(edges):
    # objective: maximize min5drop, but only meaningful if beta>=6 and beta<=9.
    md,S,bG = min5drop(N, edges)
    if bG<6: return (-100+bG, bG, md)   # push beta up
    if bG>9: return (-50, bG, md)       # band is 6..9 for n=3
    return (md, bG, md)  # want md big

def random_tf_graph(target_m=45):
    edges=set()
    adj=[0]*N
    order=ALLPAIRS[:]
    random.shuffle(order)
    for (u,v) in order:
        if len(edges)>=target_m: break
        if (adj[u]&adj[v])==0:
            edges.add((u,v)); adj[u]|=1<<v; adj[v]|=1<<u
    return edges

def neighbors_moves(edges):
    adj=adj_from_edges(edges)
    moves=[]
    # add an edge
    for (u,v) in ALLPAIRS:
        if (u,v) not in edges and (adj[u]&adj[v])==0:
            moves.append(("add",(u,v)))
    # remove an edge
    for e in edges:
        moves.append(("rm",e))
    # swap: remove one, add another
    return moves

def apply(edges, mv):
    e2=set(edges)
    if mv[0]=="add": e2.add(mv[1])
    else: e2.discard(mv[1])
    return e2

def hillclimb(seed_edges, iters=400):
    cur=set(tuple(sorted(e)) for e in seed_edges)
    cs=score(cur)
    best=cur; bs=cs
    for it in range(iters):
        moves=neighbors_moves(cur)
        random.shuffle(moves)
        improved=False
        # sample a subset of moves for speed
        for mv in moves[:60]:
            cand=apply(cur,mv)
            sc=score(cand)
            if sc>cs:
                cur=cand; cs=sc; improved=True
                if cs>bs: best=cur; bs=cs
                break
        if not improved:
            # random restart kick
            mv=random.choice(moves)
            cur=apply(cur,mv); cs=score(cur)
    return best,bs

if __name__=="__main__":
    random.seed(12345)
    overall_best=None; obs=None
    found=[]
    for trial in range(40):
        seed=random_tf_graph(random.choice([35,40,42,44,45]))
        b,bs=hillclimb(seed, iters=120)
        md,bG,_=bs
        if bG>=6 and bG<=9:
            if obs is None or bs>obs:
                obs=bs; overall_best=b
            if md>5:
                found.append((sorted(b),bG,md))
                print(f"trial {trial}: BREAK beta={bG} min5drop={md}")
        if trial%10==0:
            print(f" trial {trial} best so far: {obs}")
    print("=== best overall ===", obs)
    if overall_best is not None:
        print("edges:", sorted(overall_best))
    print("breakers found:", len(found))
    for e,bG,md in found[:5]:
        print("BREAKER beta",bG,"md",md, e)
