import itertools
from fastbeta import min5drop_fast
from h2_redteam import is_triangle_free

def es(E): return sorted(set(tuple(sorted(e)) for e in E))
def tf(n,E):
    adj=[0]*n
    for u,v in E: adj[u]|=1<<v; adj[v]|=1<<u
    for u,v in E:
        if adj[u]&adj[v]: return False
    return True

def rep(name,n,E):
    E=es(E)
    if not tf(n,E):
        print(f"{name}: NOT triangle-free"); return None
    md,S,bG=min5drop_fast(n,E)
    thr=2*(n//5)-1
    flag="*** BREAKS ***" if md>thr else "ok"
    print(f"{name}: m={len(E)} beta={bG} min5drop={md} thr={thr} {flag}")
    return (bG,md,E)

cands={}

# Grotzsch graph (Mycielskian of C5): 11 vertices, triangle-free, chromatic 4. Pad to 15.
# vertices: 0..4 = C5 outer; 5..9 = mirror; 10 = apex.
G=[]
for i in range(5): G.append((i,(i+1)%5))   # C5
for i in range(5):
    G.append((5+i, (i+1)%5)); G.append((5+i,(i-1)%5))  # mirror to neighbors of original
for i in range(5): G.append((10,5+i))  # apex to mirrors
# pad with 4 isolated 11,12,13,14
cands["Grotzsch+4iso"]=(15,G)

# Grotzsch with the 4 pad vertices forming a C4 (still TF) attached
G2=list(G)+[(11,12),(12,13),(13,14),(14,11)]
cands["Grotzsch+C4"]=(15,G2)

# Mycielskian of C7? C7 has 7, Myc adds 7+1=15! Mycielskian(C7) = 15 vertices, triangle-free
M=[]
for i in range(7): M.append((i,(i+1)%7))  # C7 on 0..6
for i in range(7):
    # mirror i' = 7+i connects to neighbors of i in C7
    M.append((7+i,(i+1)%7)); M.append((7+i,(i-1)%7))
for i in range(7): M.append((14,7+i))  # apex 14 to all mirrors
cands["Mycielskian(C7)"]=(15,M)

# Incidence graph of small config: bipartite, beta=0 (bipartite). skip-ish but include
# Heawood graph is 14 v incidence of Fano; +1 vertex. bipartite => beta 0; not useful but list.
# Generalized Petersen GP(7,2),GP(7,3) on 14 + apex
def gp(m,k,apex_conn):
    E=[]
    for i in range(m):
        E.append((i,(i+1)%m)); E.append((i,m+i)); E.append((m+i,m+(i+k)%m))
    n=2*m
    for c in apex_conn:
        E.append((n,c))
    return n+1,E
cands["GP(7,2)+apex(0,2,4)"]=gp(7,2,[0,2,4])
cands["GP(7,3)+apex(0,3,5)"]=gp(7,3,[0,3,5])

# C5[3] minus one transversal-blocking: add a perfect matching across parts to kill transversals?
# Take C5[3] then DELETE edges to make every would-be transversal cost more. Hard; just try
# C5[3] with parts sizes 3,3,3,3,3 but rewire part-4<->part-0 as a different bipartite (C6-like)
def c5b3_twist():
    E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(3):
            for b in range(3):
                if i==4:  # twist last layer: only connect a->b if a!=b (remove diagonal)
                    if a==b: continue
                E.append((3*i+a,3*j+b))
    return 15,E
cands["C5[3]_twist_layer4"]=c5b3_twist()

# Cayley on Z15 with 4 generators that is 8-regular triangle-free? check
def cay(conn):
    E=[]
    for v in range(15):
        for s in conn: E.append((v,(v+s)%15))
    return 15,E
cands["Cay[1,2,4,7]"]=cay([1,2,4,7])
cands["Cay[1,4,6,7]"]=cay([1,4,6,7])
cands["Cay[2,3,5,7]"]=cay([2,3,5,7])

# Two disjoint C5[1.5]? Not integer. Try C5[2] (10) + C5 (5) "stacked" blow-up
def stacked():
    E=[]
    # C5[2] on 0..9 parts of size2
    for i in range(5):
        j=(i+1)%5
        for a in range(2):
            for b in range(2):
                E.append((2*i+a,2*j+b))
    # third vertex of each "part" lives in 10..14: part i third = 10+i, connect to parts i-1,i+1 fully
    for i in range(5):
        j=(i+1)%5
        # 10+i (part i) to part j (2 vtx) and to 10+j
        for b in range(2): E.append((10+i,2*j+b))
        for b in range(2): E.append((2*i+b,10+j))
        E.append((10+i,10+j))
    return 15,E
cands["C5[3]_reassembled"]=stacked()

res=[]
for name,(n,E) in cands.items():
    r=rep(name,n,E)
    if r: res.append((name,n,r))
print("\n=== any breakers? ===")
for name,n,r in res:
    if r[1]>2*(n//5)-1: print("BREAK",name,r[0],r[1])
