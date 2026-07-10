#!/usr/bin/env python3
"""CLAUDE exact gate (2026-07-10) for the R5 359-vertex root-crossing candidate (WALL_ATTACK_R5_GPTPRO56.md
S3-4). Verifies: construction counts; triangle-freeness; the max-cut lock argument (displayed bad=9; length-6
lock path parity DP; violated relation costs >=10; equality cases 9 vs 17; uniqueness incl internal
alternation); blue BFS ell=5 + geodesic uniqueness for all 9 rows; the ten footprint facts; the V0+L1R0
crossing step; door/vertexSlack sink disjointness. All exact integer arithmetic."""
from itertools import product, combinations
from collections import deque, defaultdict

L = [0, 1, 2]; C = 3; R = [4, 5, 6]; U, V = 7, 8
names = {0:"L0",1:"L1",2:"L2",3:"C",4:"R0",5:"R1",6:"R2",7:"U",8:"V"}
rels = [(0,3),(1,3),(2,3),(4,3),(5,3),(6,3),(7,8)]
def internal(r,k,t): return 9 + 5*(10*r+k) + (t-1)
N = 9 + 7*10*5
support = [(l,U) for l in L] + [(U,C),(C,V)] + [(V,r) for r in R]
bad = [(l,r) for l in L for r in R]
edges = set(tuple(sorted(e)) for e in support + bad)
for ri,(a,b) in enumerate(rels):
    for k in range(10):
        chain = [a] + [internal(ri,k,t) for t in range(1,6)] + [b]
        for i in range(6): edges.add(tuple(sorted((chain[i],chain[i+1]))))
edges = sorted(edges)
side = {v: 0 for v in range(9)}; side[U] = 1; side[V] = 1
for ri,(a,b) in enumerate(rels):
    s = side[a]
    assert side[a] == side[b]
    for k in range(10):
        for t in range(1,6): side[internal(ri,k,t)] = s ^ (t & 1)
fails = []
# construction counts
if not (N == 359 and len(edges) == 437): fails.append(f"counts N={N} E={len(edges)}")
# triangle-free
adj = defaultdict(set)
for a,b in edges: adj[a].add(b); adj[b].add(a)
tri = any(len(adj[a] & adj[b]) > 0 for a,b in edges)
if tri: fails.append("TRIANGLE")
# displayed bad count
bad_disp = [(a,b) for a,b in edges if side[a] == side[b]]
if sorted(bad_disp) != sorted(tuple(sorted(e)) for e in bad): fails.append(f"displayed bad={len(bad_disp)}")
# lock path DP: min bad over 2^5 internals, endpoints same/opposite
def path_min_bad(sa, sb):
    best, uniq = 99, 0
    for bits in product([0,1],repeat=5):
        seq = [sa]+list(bits)+[sb]
        badn = sum(1 for i in range(6) if seq[i]==seq[i+1])
        if badn < best: best, uniq = badn, 1
        elif badn == best: uniq += 1
    return best, uniq
mb_same, uq_same = path_min_bad(0,0); mb_opp, _ = path_min_bad(0,1)
if not (mb_same == 0 and uq_same == 1 and mb_opp >= 1): fails.append(f"lock DP {mb_same},{uq_same},{mb_opp}")
# max-cut argument: violated relation => >=10*1 > 9; relations satisfied => core cases
# groups: g1 = {L0,L1,L2,C,R0,R1,R2} equal; g2 = {U,V} equal. enumerate 4 cases:
core_edges = [tuple(sorted(e)) for e in support + bad]
for s1, s2 in product([0,1],[0,1]):
    cs = {**{v: s1 for v in [0,1,2,3,4,5,6]}, U: s2, V: s2}
    cb = sum(1 for a,b in core_edges if cs[a]==cs[b])
    expect = 9 if s1 != s2 else 17
    if cb != expect: fails.append(f"case {s1}{s2}: {cb}!={expect}")
# => min bad = 9, achieved only s1!=s2 with unique 0-bad lock internals => displayed cut + complement UNIQUE max cuts. QED structure.
# blue graph BFS: ell=5, unique geodesics
blue = [(a,b) for a,b in edges if side[a] != side[b]]
badj = defaultdict(set)
for a,b in blue: badj[a].add(b); badj[b].add(a)
geo_ok = True
for l in L:
    dist = {l:0}; cnt = {l:1}; par = defaultdict(list); q = deque([l])
    while q:
        x = q.popleft()
        for y in badj[x]:
            if y not in dist: dist[y]=dist[x]+1; cnt[y]=cnt[x]; par[y]=[x]; q.append(y)
            elif dist[y]==dist[x]+1: cnt[y]+=cnt[x]; par[y].append(x)
    for r in R:
        if dist.get(r) != 4 or cnt[r] != 1: geo_ok = False; fails.append(f"geo {names[l]}-{names[r]}: d={dist.get(r)} cnt={cnt.get(r)}")
        else:
            p = [r]
            while p[-1] != l: p.append(par[p[-1]][0])
            if [names[v] for v in p] != [names[r],"V","C","U",names[l]]: fails.append(f"geopath {names[l]}{names[r]}")
# footprint facts
sup = {(l,r): {tuple(sorted((l,U))),tuple(sorted((U,C))),tuple(sorted((C,V))),tuple(sorted((V,r)))} for l in L for r in R}
Esh = set().union(*sup.values())
if not (len(sup)==9 and len(Esh)==8): fails.append("S/Eshort")
mult = defaultdict(int)
for s in sup.values():
    for e in s: mult[e]+=1
if min(mult.values()) < 2: fails.append("private edge")
pu_ok = all(len(sup[a]|sup[b])>=5 for a,b in combinations(sup,2))
if not pu_ok: fails.append("pair union")
# minimality: every proper subset T: |T| <= |Eshort(T)|
minim = True
atoms = list(sup)
for rmask in range(1, 2**9-1):
    T = [atoms[i] for i in range(9) if (rmask>>i)&1]
    ET = set().union(*(sup[t] for t in T))
    if len(T) > len(ET): minim = False; break
if not minim: fails.append("not minimal (proper violator)")
# crossing step: restriction = 9 core; F = 8 support edges; core blue edges all in F?
F = Esh
core_blue = [e for e in blue if e[0] < 9 and e[1] < 9]
if sorted(core_blue) != sorted(F): fails.append("core blue != F")
X0 = {0, U, C, V, 4}  # V0 = {L0,U,C,V,R0}; QComp singletons => shore verts = X0
# atom L1R0 unique geodesic uses L1-U in F crossing X0 (L1 out, U in) => forced
e_cross = tuple(sorted((1,U)))
forced = (e_cross in F) and (1 not in X0) and (U in X0)
if not forced: fails.append("forced step")
# ports: off-support blue boundary; W adds L1
def ports(X):
    return {(min(a,b),max(a,b),(a if a in X else b)) for a,b in blue if ((a in X) ^ (b in X)) and tuple(sorted((a,b))) not in F}
PV, PW = ports(X0), ports(X0 | {1})
new = PW - PV
L1new = [p for p in new if p[2] == 1]
def sinks(p):  # door(edge) + vertexSlack(inside)
    return {("door",(p[0],p[1])), ("vs",p[2])}
cross_confirmed = len(L1new) == 10 and all(all(not (sinks(pn) & sinks(po)) for po in PV) for pn in L1new)
if not cross_confirmed: fails.append(f"crossing sinks (L1new={len(L1new)})")
print(f"N={N} E={len(edges)} tri-free={not tri} displayed_bad={len(bad_disp)} lockDP=({mb_same},{uq_same},{mb_opp})")
print(f"rows: all 9 ell=5 unique-geodesic={geo_ok}; |S|=9>|Eshort|=8; no-private; pair-unions>=5; minimal={minim}")
print(f"crossing step: forced={forced}; new L1 ports={len(L1new)}; door/vertexSlack sinks disjoint from ALL old ports={cross_confirmed}")
print(f"VERDICT: {'CANDIDATE VERIFIED - real-graph root crossing REAL under door/vertexSlack incidence' if not fails else 'FAILS: ' + '; '.join(fails[:6])}")
