# generate graph list for the C++ exhaustive scanner (window-filtered TF graphs)
import random
from itertools import combinations

out = []

def emit(name, n, edges):
    E = sorted(set((min(u,v),max(u,v)) for u,v in edges))
    adj = [0]*n
    for u,v in E:
        adj[u] |= 1<<v; adj[v] |= 1<<u
    for u,v in E:
        assert adj[u]&adj[v]==0, ("triangle", name)
    deg = [bin(a).count("1") for a in adj]
    delta = min(deg)
    win = 25*delta > 4*n-2
    if not win:
        return False
    out.append((name, n, E))
    return True

def circ_edges(n, D):
    return [(i,(i+d)%n) for i in range(n) for d in D]

def circ_tf(n, D):
    S = set()
    for d in D: S.add(d%n); S.add((-d)%n)
    return all((a+b)%n not in S for a in S for b in S)

# --- cross-check graphs (validate C++ against python-verified numbers) ---
emit("XCHK_C13(1,5)", 13, circ_edges(13,[1,5]))
emit("XCHK_Petersen", 10, [(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+[(5,7),(7,9),(9,6),(6,8),(8,5)])
hunt12 = [[0,1],[0,2],[1,7],[2,9],[3,9],[3,11],[4,7],[4,8],[5,7],[5,10],[6,10],[6,11],[7,9],[8,10],[9,10]]
emit("XCHK_hunt12", 12, [tuple(e) for e in hunt12])

# --- full circulant sweep 15..26, all D sizes, window+TF ---
ncirc = 0
for n in range(15, 27):
    half = n//2
    # need 25*delta > 4n-2 ; delta = 2|D| - (1 if n/2 in D else 0)
    for k in range(2, half+1):
        for D in combinations(range(1, half+1), k):
            delta = 2*k - (1 if (n%2==0 and half in D) else 0)
            if 25*delta <= 4*n-2:  # window fail (deltas only grow with k, but sizes vary; cheap filter)
                continue
            if not circ_tf(n, D):
                continue
            if emit("C%d%s" % (n, str(tuple(D)).replace(" ","")), n, circ_edges(n, D)):
                ncirc += 1

# --- blow-ups (named threat tests), all-cut exact ---
def blowup(nb, Eb, sizes):
    ofs=[]; t=0
    for s in sizes: ofs.append(t); t+=s
    return t, [(ofs[u]+i, ofs[v]+j) for (u,v) in Eb for i in range(sizes[u]) for j in range(sizes[v])]

pet = [(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+[(5,7),(7,9),(9,6),(6,8),(8,5)]
gro = [(i,(i+1)%5) for i in range(5)]
for j in range(5): gro += [(5+j,(j-1)%5),(5+j,(j+1)%5),(5+j,10)]
c5 = [(i,(i+1)%5) for i in range(5)]
c13_15 = sorted(set((min(u,v),max(u,v)) for u,v in circ_edges(13,[1,5])))

n2,E2 = blowup(10, pet, (2,)*10);  emit("Petersen[2]", n2, E2)
n2,E2 = blowup(11, gro, (2,)*11);  emit("Groetzsch[2]", n2, E2)
n2,E2 = blowup(13, c13_15, (2,)*13); emit("C13(1,5)[2]", n2, E2)
n2,E2 = blowup(5, c5, (5,)*5);     emit("C5[5]", n2, E2)
n2,E2 = blowup(5, c5, (4,4,4,4,5)); emit("C5[4,4,4,4,5]", n2, E2)
n2,E2 = blowup(11, circ_edges(11,[1,4]), (2,)*11); emit("Andrasfai4[2]", n2, E2)

# --- random maximal TF, larger n than report (16..22) ---
def rand_maximal_tf(n, seed):
    rnd = random.Random(seed)
    adj=[0]*n; E=[]
    pairs = list(combinations(range(n),2))
    changed=True
    while changed:
        changed=False
        rnd.shuffle(pairs)
        for (u,v) in pairs:
            if not (adj[u]>>v)&1 and adj[u]&adj[v]==0:
                adj[u]|=1<<v; adj[v]|=1<<u; E.append((u,v)); changed=True
    return E

nrand = 0
for n in (16, 18, 20, 22):
    for s in range(8):
        E = rand_maximal_tf(n, 777*n+s)
        if emit("randTF(n=%d,s=%d)" % (n,s), n, E):
            nrand += 1

with open("graphs.txt","w") as f:
    f.write("%d\n" % len(out))
    for name,n,E in out:
        f.write("%s %d %d\n" % (name.replace(" ",""), n, len(E)))
        f.write(" ".join("%d,%d"%(u,v) for u,v in E) + "\n")
print("graphs: total=%d circulants(win,TF,15..26)=%d rand=%d" % (len(out), ncirc, nrand))
bysize = {}
for name,n,E in out: bysize[n] = bysize.get(n,0)+1
print("by N:", sorted(bysize.items()))
