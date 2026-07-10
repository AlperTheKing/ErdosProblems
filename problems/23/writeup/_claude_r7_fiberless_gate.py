#!/usr/bin/env python3
"""CLAUDE exact gate (2026-07-10) for R7's 12-row fiberless footprint + 662-vtx realization
(WALL_ATTACK_R7_GPTPRO56.md). All exact integer/Fraction arithmetic."""
from fractions import Fraction as Fr
from itertools import combinations, product
from collections import defaultdict, deque

E11 = [(0,2),(1,3),(1,6),(2,5),(2,10),(4,5),(4,6),(4,8),(4,9),(5,7),(7,11)]
ATOMS = [((3,8),[1,2,6,7]),((6,11),[6,5,9,10]),((9,10),[8,5,3,4]),((3,9),[1,2,6,8]),
         ((6,10),[6,5,3,4]),((1,7),[2,6,5,9]),((8,11),[7,5,9,10]),((1,2),[2,6,5,3]),
         ((0,11),[0,3,9,10]),((0,9),[0,3,5,8]),((3,5),[1,2,6,5]),((8,10),[7,5,3,4])]
fails = []
# tree + bipartition + geodesic-path checks
adjT = defaultdict(set)
for a,b in E11: adjT[a].add(b); adjT[b].add(a)
seen = {0}; q = deque([0])
while q:
    x = q.popleft()
    for y in adjT[x]:
        if y not in seen: seen.add(y); q.append(y)
if not (len(E11)==11 and len(seen)==12): fails.append("not a spanning tree")
S0 = {1,2,4,7}
if any((a in S0)==(b in S0) for a,b in E11): fails.append("support edge same-side")
if any((u in S0)!=(v in S0) for (u,v),_ in ATOMS): fails.append("bad edge crossing")
for (u,v),sup in ATOMS:
    es = [E11[i] for i in sup]
    deg = defaultdict(int)
    for a,b in es: deg[a]+=1; deg[b]+=1
    ends = sorted(x for x in deg if deg[x]==1)
    if not (len(sup)==4 and ends==sorted((u,v)) and all(d<=2 for d in deg.values())): fails.append(f"support-path {(u,v)}")
# multiplicities, private, pair-unions, connectivity
mult = [sum(1 for _,s in ATOMS if i in s) for i in range(11)]
if mult != [2,3,5,6,3,9,7,3,3,4,3]: fails.append(f"mults {mult}")
if min(mult) < 2: fails.append("private edge")
if any(len(set(a)|set(b))<5 for (_,a),(_,b) in combinations(ATOMS,2)): fails.append("pair union")
# Hall table (max #supports contained in X, by |X|) + minimality
best = defaultdict(int)
for mask in range(1<<11):
    X = {i for i in range(11) if (mask>>i)&1}
    r = sum(1 for _,s in ATOMS if set(s)<=X)
    k = len(X)
    if r > best[k]: best[k] = r
tab = [best[k] for k in range(12)]
if tab != [0,0,0,0,1,2,3,5,7,8,10,12]: fails.append(f"Hall table {tab}")
minim = all(len(T) <= len(set().union(*(set(ATOMS[i][1]) for i in T)))
            for r in range(1,12) for T in combinations(range(12),r))
if not minim: fails.append("proper subfamily violates Hall")
# NO exact-one fiber (exhaustive 2^11)
fiber_exists = any(all(sum(1 for i in s if (mask>>i)&1)==1 for _,s in ATOMS) for mask in range(1<<11))
if fiber_exists: fails.append("FIBER EXISTS")
# the integer combination: A1+A2-2*A3-A4-A8+A9+2*A10 => 4*x5 = 1
coef = [0]*11; rhs = 0
for idx,c in [(1,1),(2,1),(3,-2),(4,-1),(8,-1),(9,1),(10,2)]:
    rhs += c
    for i in ATOMS[idx][1]: coef[i] += c
if not (rhs==1 and coef[5]==4 and all(coef[i]==0 for i in range(11) if i!=5)): fails.append(f"combination {coef} rhs={rhs}")
# x = 1/4 fractional feasibility
if any(sum(Fr(1,4) for _ in s) != 1 for _,s in ATOMS): fails.append("fractional 1/4")
# ---- 662-vtx realization ----
rels = [(1,4),(2,4),(7,4),(0,5),(3,5),(6,5),(8,5),(9,5),(10,5),(11,5)]
def internal(r,k,t): return 12 + 5*(13*r+k) + (t-1)
edges = set(tuple(sorted(e)) for e in E11) | set(tuple(sorted(e)) for e,_ in ATOMS)
for r,(a,b) in enumerate(rels):
    for k in range(13):
        ch = [a]+[internal(r,k,t) for t in range(1,6)]+[b]
        for i in range(6): edges.add(tuple(sorted((ch[i],ch[i+1]))))
edges = sorted(edges); N = 12 + 10*13*5
if not (N==662 and len(edges)==803): fails.append(f"realization counts N={N} E={len(edges)}")
side = {v: (0 if v in S0 else 1) for v in range(12)}
for r,(a,b) in enumerate(rels):
    s = side[a]
    if side[a]!=side[b]: fails.append(f"lock rel {a},{b} not same-side")
    for k in range(13):
        for t in range(1,6): side[internal(r,k,t)] = s ^ (t&1)
adj = defaultdict(set)
for a,b in edges: adj[a].add(b); adj[b].add(a)
if any(len(adj[a]&adj[b])>0 for a,b in edges): fails.append("TRIANGLE")
bad_disp = [(a,b) for a,b in edges if side[a]==side[b]]
if sorted(bad_disp) != sorted(tuple(sorted(e)) for e,_ in ATOMS): fails.append(f"displayed bad={len(bad_disp)}")
def pmb(sa,sb):
    best,unq = 99,0
    for bits in product([0,1],repeat=5):
        seq=[sa]+list(bits)+[sb]; bn=sum(1 for i in range(6) if seq[i]==seq[i+1])
        if bn<best: best,unq=bn,1
        elif bn==best: unq+=1
    return best,unq
mbs,uqs = pmb(0,0); mbo,_ = pmb(0,1)
if not (mbs==0 and uqs==1 and mbo>=1): fails.append("lock DP")
core = [tuple(sorted(e)) for e in E11] + [tuple(sorted(e)) for e,_ in ATOMS]
for s1,s2 in product([0,1],[0,1]):
    cs = {v:(s1 if v in S0 else s2) for v in range(12)}
    cb = sum(1 for a,b in core if cs[a]==cs[b])
    exp = 12 if s1!=s2 else 23
    if cb!=exp: fails.append(f"core case {s1}{s2}:{cb}!={exp}")
blue = [(a,b) for a,b in edges if side[a]!=side[b]]
badj = defaultdict(set)
for a,b in blue: badj[a].add(b); badj[b].add(a)
for (u,v),sup in ATOMS:
    dist={u:0}; cnt={u:1}; q=deque([u])
    while q:
        x=q.popleft()
        for y in badj[x]:
            if y not in dist: dist[y]=dist[x]+1; cnt[y]=cnt[x]; q.append(y)
            elif dist[y]==dist[x]+1: cnt[y]+=cnt[x]
    if dist.get(v)!=4 or cnt[v]!=1: fails.append(f"geo {(u,v)} d={dist.get(v)} c={cnt.get(v)}")
# crossing step: V0 = support verts of A0={3,1,6,4,8}; atom A3=3-9 geodesic 3-1-6-4-9 forced via (4,9)
X0 = {3,1,6,4,8}
F = set(tuple(sorted(E11[i])) for i in range(11))
e49 = (4,9)
if not (e49 in F and (4 in X0) and (9 not in X0)): fails.append("crossing edge")
def ports(X):
    return {(min(a,b),max(a,b),(a if a in X else b)) for a,b in blue if ((a in X)^(b in X)) and (min(a,b),max(a,b)) not in F}
PV,PW = ports(X0), ports(X0|{9})
new9 = [p for p in PW-PV if p[2]==9]
def sk(p): return {("door",(p[0],p[1])),("vs",p[2])}
cross = len(new9)==13 and all(all(not(sk(pn)&sk(po)) for po in PV) for pn in new9)
if not cross: fails.append(f"crossing sinks new9={len(new9)}")
# endpoint-half arithmetic: lock endpoint edges = 2 per path = 260; at vertex 4: paths with endpoint 4 = rels (1,4),(2,4),(7,4) => 3*13=39
lockend = 10*13*2
at4 = sum(13 for a,b in rels if 4 in (a,b))
bal = 25*11 + (lockend)*25 - 25*12
if not (lockend==260 and at4==39 and (260-39)==221 and bal==6475): fails.append(f"endpoint-half {lockend},{at4},{bal}")
print(f"footprint: tree+bipartition+12 support-paths OK; mults={mult}; Hall table={tab}; minimal={minim}")
print(f"NO exact-one fiber (2^11 exhaustive): {not fiber_exists}; combination 4*x5={coef[5]} rhs={rhs}; x=1/4 feasible")
print(f"realization: N={N} E={len(edges)} tri-free, displayed bad=12, lock DP OK, core 12v23, all 12 geodesics unique")
print(f"crossing: 13 new ports at 9, sinks disjoint from all old = {cross}; doors 260/39/221, balance +{bal}")
print(f"VERDICT: {'R7 FIBERLESS CE FULLY VERIFIED' if not fails else 'FAILS: ' + '; '.join(fails[:8])}")
