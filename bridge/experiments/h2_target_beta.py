import itertools, random
from h2_redteam import min5drop

N=15
ALLPAIRS=[(i,j) for i in range(N) for j in range(i+1,N)]

def adj_from_edges(edges):
    adj=[0]*N
    for (u,v) in edges:
        adj[u]|=1<<v; adj[v]|=1<<u
    return adj

def tf_add_ok(adj,u,v):
    return (adj[u]&adj[v])==0

def random_tf(target_m):
    edges=set(); adj=[0]*N
    order=ALLPAIRS[:]; random.shuffle(order)
    for (u,v) in order:
        if len(edges)>=target_m: break
        if (adj[u]&adj[v])==0:
            edges.add((u,v)); adj[u]|=1<<v; adj[v]|=1<<u
    return edges

def obj(edges):
    md,S,bG=min5drop(N,edges)
    return md,bG

def climb(seed, iters):
    cur=set(seed)
    md,bG=obj(cur)
    # fitness: in-band beta in [6,9], maximize md, prefer larger md strongly
    def fit(md,bG):
        if bG<6: return (-1000+bG,)
        if bG>9: return (-500-(bG-9),)
        return (md*10 - (9-bG),)  # want md high, beta near 9 mild bonus
    cf=fit(md,bG); cmd,cbG=md,bG
    best=set(cur); bmd,bbG=md,bG; bf=cf
    for it in range(iters):
        adj=adj_from_edges(cur)
        cand=None
        # try add or remove or swap
        kind=random.random()
        moves=[]
        for (u,v) in ALLPAIRS:
            if (u,v) in cur:
                moves.append(("rm",(u,v)))
            elif (adj[u]&adj[v])==0:
                moves.append(("add",(u,v)))
        random.shuffle(moves)
        took=False
        for mv in moves[:50]:
            c2=set(cur)
            if mv[0]=="add": c2.add(mv[1])
            else: c2.discard(mv[1])
            md2,bG2=obj(c2)
            f2=fit(md2,bG2)
            if f2>=cf:
                if f2>cf or random.random()<0.3:
                    cur=c2; cf=f2; cmd,cbG=md2,bG2; took=True
                    if cf>bf: best=set(cur); bf=cf; bmd,bbG=md2,bG2
                    break
        if not took:
            # kick
            mv=random.choice(moves)
            c2=set(cur)
            if mv[0]=="add": c2.add(mv[1])
            else: c2.discard(mv[1])
            cur=c2; cmd,cbG=obj(cur); cf=fit(cmd,cbG)
    return best,bmd,bbG

if __name__=="__main__":
    random.seed(99)
    best=None; bbest=(-1,-1)
    breakers=[]
    for trial in range(60):
        seed=random_tf(random.choice([30,33,36,38,40,42,44]))
        b,md,bG=climb(seed,150)
        if 6<=bG<=9 and md>(bmax:=bbest[0]):
            bbest=(md,bG); best=b
        if 6<=bG<=9 and md>5:
            breakers.append((sorted(b),bG,md))
            print(f"trial {trial} BREAK beta={bG} md={md}")
        if trial%10==0:
            print(f"trial {trial} bestmd={bbest}")
    print("BEST md/beta", bbest)
    if best: print("edges", sorted(best))
    print("num breakers", len(breakers))
    for e,bG,md in breakers[:8]:
        print("BREAKER", bG, md, e)
