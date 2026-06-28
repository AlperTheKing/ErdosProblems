"""Does the bridge construction have a GAMMA-MIN connected max cut with O EMPTY?
If yes, NO-Q-ONLY/C-alltie is vacuous (no violation). If the island Q-only comp coexists with O on
EVERY gamma-min cut, that's a refutation. Enumerate max cuts by combining island (2^5) x myc cuts
restricted to those achieving myc internal max (23), pick bridge cut. For each, compute Gamma, O,
and whether island is Q-only bad-carrying coexisting with O. Report gamma-min cut's O."""
from fractions import Fraction as F
from collections import deque
from itertools import product
from _bdef_construct import mycielski, union_disjoint, add_edges, Cn
from _h import bdist_restr

isl_n, isl_E = 5, Cn(5)
myc_n, myc_E = mycielski(7, Cn(7))
n, E = union_disjoint((isl_n,isl_E),(myc_n,myc_E)); n,E=add_edges((n,E),[(0,5)])
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
edges=sorted(set((min(a,b),max(a,b)) for a,b in E))
myc_edges=[(u,v) for u,v in edges if u>=5 and v>=5]
isl_edges=[(u,v) for u,v in edges if u<5 and v<5]

def Bconn(side):
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v);q.append(v)
    return len(seen)==n

def struct(side):
    if not Bconn(side): return None
    M=[(u,v) for u,v in edges if side[u]==side[v]]
    # geodesic loads
    T=[F(0)]*n; G=0; cyc={}
    for (u,v) in M:
        # all shortest B-paths u->v
        dist={u:0};pred={u:[]};layer=[u]
        while layer:
            nxt=[]
            for x in layer:
                for y in adj[x]:
                    if side[x]!=side[y]:
                        if y not in dist: dist[y]=dist[x]+1;pred[y]=[x];nxt.append(y)
                        elif dist[y]==dist[x]+1: pred[y].append(x)
            layer=nxt
        if v not in dist: return None
        P=[]
        def rec(z,acc):
            if z==u: P.append([u]+acc[::-1]);return
            for p in pred[z]: rec(p,acc+[z])
        rec(v,[]);
        ell=len(P[0]); G+=ell*ell; sh=F(ell,len(P)); cyc[(u,v)]=P
        for path in P:
            for w in path: T[w]+=sh
    O=[v for v in range(n) if T[v]>n]
    return G,T,O,M,cyc

# myc cuts achieving internal max 23: enumerate 2^15 is 32768, feasible
best_myc=23
myc_max_cuts=[]
for bits in product([0,1],repeat=15):
    s={5+i:bits[i] for i in range(15)}
    c=sum(1 for u,v in myc_edges if s[u]!=s[v])
    if c==best_myc: myc_max_cuts.append(s)
print("num myc max cuts:",len(myc_max_cuts))

results=[]
for ibits in product([0,1],repeat=5):
    isl_s={i:ibits[i] for i in range(5)}
    if sum(1 for u,v in isl_edges if isl_s[u]!=isl_s[v])!=4: continue  # island must be at internal max (one bad edge)
    for ms in myc_max_cuts:
        side=[0]*n
        for i in range(5): side[i]=isl_s[i]
        for i in range(5,20): side[i]=ms[i]
        # bridge (0,5) must be cut for total max 28
        if side[0]==side[5]: continue
        st=struct(side)
        if st is None: continue
        G,T,O,M,cyc=st
        results.append((G,tuple(side),tuple(O)))

if not results:
    print("no connected max cuts found"); raise SystemExit
gm=min(G for G,_,_ in results)
gmin_cuts=[r for r in results if r[0]==gm]
print(f"Gamma_min over all (island-maxcut x myc-maxcut, bridge-cut) connected max cuts = {gm}")
print(f"num gamma-min cuts = {len(gmin_cuts)}")
Oempty=[r for r in gmin_cuts if len(r[2])==0]
print(f"gamma-min cuts with O EMPTY = {len(Oempty)} / {len(gmin_cuts)}")
# show O of a few gamma-min cuts
from collections import Counter
oc=Counter(r[2] for r in gmin_cuts)
for o,cnt in oc.most_common(8):
    print(f"   O={list(o)} count={cnt}")
