import itertools, random, sys
from h2_redteam import min5drop

N=15
ALLPAIRS=[(i,j) for i in range(N) for j in range(i+1,N)]

def adj_from_edges(edges):
    adj=[0]*N
    for (u,v) in edges:
        adj[u]|=1<<v; adj[v]|=1<<u
    return adj

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

def fit(md,bG):
    if bG<6: return -1000+bG
    if bG>9: return -500-(bG-9)
    return md*10+bG

def climb(seed, iters):
    cur=set(seed); md,bG=obj(cur); cf=fit(md,bG)
    best=set(cur); bf=cf; bmd,bbG=md,bG
    for it in range(iters):
        adj=adj_from_edges(cur)
        moves=[]
        for (u,v) in ALLPAIRS:
            if (u,v) in cur: moves.append(("rm",(u,v)))
            elif (adj[u]&adj[v])==0: moves.append(("add",(u,v)))
        random.shuffle(moves); took=False
        for mv in moves[:45]:
            c2=set(cur)
            if mv[0]=="add": c2.add(mv[1])
            else: c2.discard(mv[1])
            md2,bG2=obj(c2); f2=fit(md2,bG2)
            if f2>cf or (f2==cf and random.random()<0.25):
                cur=c2; cf=f2; took=True
                if f2>bf: best=set(cur); bf=f2; bmd,bbG=md2,bG2
                break
        if not took and moves:
            mv=random.choice(moves); c2=set(cur)
            if mv[0]=="add": c2.add(mv[1])
            else: c2.discard(mv[1])
            cur=c2; md,bG=obj(cur); cf=fit(md,bG)
    return best,bmd,bbG

random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 7)
bestmd=-1; bestbeta=-1; bestg=None; breakers=[]
trials=int(sys.argv[2]) if len(sys.argv)>2 else 50
for t in range(trials):
    seed=random_tf(random.choice([30,33,36,38,40,42,44,45]))
    g,md,bG=climb(seed,120)
    if 6<=bG<=9:
        if md>bestmd or (md==bestmd and bG>bestbeta):
            bestmd=md; bestbeta=bG; bestg=g
        if md>5:
            breakers.append((sorted(g),bG,md))
            print(f"trial {t} *** BREAK beta={bG} min5drop={md} ***", flush=True)
    if t%10==0:
        print(f"trial {t}: bestmd={bestmd} bestbeta={bestbeta}", flush=True)
print(f"FINAL bestmd={bestmd} bestbeta={bestbeta}", flush=True)
print("BESTGRAPH", sorted(bestg) if bestg else None, flush=True)
print("NUM_BREAKERS", len(breakers), flush=True)
