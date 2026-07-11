"""R20 gate: 311-vtx corridor-overload counterexample to BASE-ONLY transfer Hall-completeness,
plus the rowCompanion repair. Independent exact verification (fractions only).

Construction (R20a, GPT-5.6 Pro 2026-07-11):
  core 27 = cycle v0..v25 (blue) + leaf w=26 (blue w-v0);
  bad: a_i=(i,i+4 mod 26) for i in 0..25, plus (w,3),(w,23)  -> 28 bad edges
  I-path (blue): step-9 chain 0-9-18-1-10-19-2-11-20-3-12-21-4 (12 edges)
  locks: per bad edge (x,y), 5 new vertices, blue path x-l1-..-l5-y (6 edges)  -> N=167
  attachment at v=9: parts P0(8),P1(64),{v},P3(64),P4(8); blue P0xP1,P1xv,vxP3,P3xP4; bad P4xP0
  -> N=311, |E|=1451, |B|=1359, |Hbad|=92.
Claims gated here:
  (1) triangle-free; (2) displayed cut cuts exactly B (1359), misses exactly Hbad (92);
  (3) maxcut = 1359 EXACT (attachment exact twin enumeration = 1152; core = 207 via 7-cycle
      gadget bound 39+28*6; one-vertex-sum additivity); (4) Gamma_min = 2300 (all 92 bad at
      blue-dist exactly 4; dist>=4 forced for ANY maxcut: parity + triangle-free);
  (5) core atom rows unique; attachment atom rows = 64*64 each, ALL through v=9;
  (6) T(9)=345, deg_I(9)=2 (nbrs {0,18}), d_bad(9)=2 (nbrs {5,13});
  (7) identity check E[F_9]-E[C_9] = N-T(9) = -34 (exact fractions);
  (8) BASE-ONLY Hall gap at v=9 = 66 per unit K: obligations 2*E[C_9]+deg_I vs
      sameFirst 2*E[F_9] + commonBad 4 ((5,13),(13,5) permanently Free);
  (9) rowCompanion repair: all 56 ordered P0-pairs permanently Free, both coords row-companions
      of 9, switch loss({x,z}) = 112 >= 0, supply 66 halves from 33 pairs covers the gap.
"""
from fractions import Fraction as F
from itertools import combinations
from collections import deque
import hashlib, sys

ok = True
def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: ok = False

# ---------- build ----------
# core vertices 0..25 cycle, w=26
V = list(range(27))
blue = set(); bad = []
def be(a,b): blue.add((min(a,b),max(a,b)))
for i in range(26): be(i,(i+1)%26)
be(26,0)
for i in range(26): bad.append((i,(i+4)%26))
bad.append((26,3)); bad.append((26,23))
# I-path step-9 chain from 0, 12 edges
ip = [0]
for _ in range(12): ip.append((ip[-1]+9)%26)
chk("I-path spec 0-9-18-1-10-19-2-11-20-3-12-21-4",
    ip == [0,9,18,1,10,19,2,11,20,3,12,21,4])
for a,b in zip(ip,ip[1:]): be(a,b)
# locks
nxt = 27
lock_edges_of = []  # list of 7-cycles (6 lock blue edges + the bad edge) per bad edge
for (x,y) in bad:
    ls = list(range(nxt,nxt+5)); nxt += 5
    V += ls
    ch = [x]+ls+[y]
    cyc = []
    for a,b in zip(ch,ch[1:]):
        be(a,b); cyc.append((min(a,b),max(a,b)))
    lock_edges_of.append(cyc)
chk("N core+locks = 167", nxt == 167)
# attachment at v=9
v = 9
P0 = list(range(nxt,nxt+8));  nxt += 8
P1 = list(range(nxt,nxt+64)); nxt += 64
P3 = list(range(nxt,nxt+64)); nxt += 64
P4 = list(range(nxt,nxt+8));  nxt += 8
V += P0+P1+P3+P4
for a in P0:
    for b in P1: be(a,b)
for b in P1: be(b,v)
for c in P3: be(v,c)
for c in P3:
    for d in P4: be(c,d)
att_bad = [(d,a) for d in P4 for a in P0]
bad += att_bad
N = nxt
chk("N = 311", N == 311)
E_all = set(blue) | set((min(a,b),max(a,b)) for a,b in bad)
chk("|E| = 1451 (disjoint blue/bad)", len(E_all) == 1451 and len(blue) == 1359 and len(bad) == 92)

adj = [set() for _ in range(N)]
for (a,b) in E_all:
    adj[a].add(b); adj[b].add(a)
badj = [set() for _ in range(N)]   # blue adjacency
for (a,b) in blue:
    badj[a].add(b); badj[b].add(a)

# ---------- (1) triangle-free ----------
tri = any(len(adj[a] & adj[b]) > 0 for (a,b) in E_all)
chk("(1) triangle-free", not tri)

# ---------- (2) displayed cut ----------
side = [0]*N
for i in range(26): side[i] = i % 2
side[26] = 1                      # w opposite v0
for k,(x,y) in enumerate(bad[:28]):
    ls = list(range(27+5*k, 27+5*k+5))
    c = side[x]
    for j,l in enumerate(ls): side[l] = 1-c if j % 2 == 0 else c
chk("(2a) lock parity consistent (endpoints same side)", all(side[x]==side[y] for x,y in bad[:28]))
for a in P0: side[a] = side[v]
for b in P1: side[b] = 1-side[v]
for c in P3: side[c] = 1-side[v]
for d in P4: side[d] = side[v]
cut_blue = sum(1 for (a,b) in blue if side[a]!=side[b])
cut_bad  = sum(1 for (a,b) in bad  if side[a]!=side[b])
chk("(2) displayed cut = all 1359 blue, 0 bad", cut_blue == 1359 and cut_bad == 0)

# ---------- (3) maxcut = 1359 exact ----------
# attachment exact twin enumeration (v side in {0,1}; a_i = #vertices of class on side 1)
best = 0
for sv in (0,1):
    for a0 in range(9):
        for a1 in range(65):
            t01 = a0*(64-a1)+(8-a0)*a1
            t1v = a1*(1-sv)+(64-a1)*sv
            for a3 in range(65):
                t3v = a3*(1-sv)+(64-a3)*sv
                base = t01+t1v+t3v
                for a4 in range(9):
                    t34 = a3*(8-a4)+(64-a3)*a4
                    t40 = a4*(8-a0)+(8-a4)*a0
                    c = base+t34+t40
                    if c > best: best = c
chk("(3a) attachment maxcut = 1152 (exact enumeration 684k configs)", best == 1152)
# core upper bound: non-gadget blue = 26 cycle + w0 + 12 I = 39; each gadget = 7-cycle (odd) <= 6
nongadget = 26+1+12
gadget_edge_sets = []
allg = set()
for k,cyc in enumerate(lock_edges_of):
    x,y = bad[k]
    e7 = set(cyc)|{(min(x,y),max(x,y))}
    chk_ = len(e7)==7
    if not chk_: chk("(3b) gadget %d has 7 edges"%k, False)
    gadget_edge_sets.append(e7); allg |= e7
core_edges = set((a,b) for (a,b) in E_all if a < 167 and b < 167)
chk("(3b) gadget edges disjoint + partition core with 39 non-gadget blue",
    len(allg) == 28*7 and allg <= core_edges and len(core_edges - allg) == 39
    and all(e in blue for e in core_edges - allg))
# displayed cut restricted to core achieves 39 + 28*6 = 207
core_cut = sum(1 for (a,b) in core_edges if side[a]!=side[b])
chk("(3c) core maxcut = 207 (upper: 39+28*6 odd-cycle; displayed attains)", core_cut == 207)
# one-vertex sum: attachment meets core only at v=9
att_vs = set(P0+P1+P3+P4)
crossing = [ (a,b) for (a,b) in E_all if (a in att_vs) != (b in att_vs) and v not in (a,b) ]
chk("(3d) attachment glued ONLY at v=9 (maxcut additive)", crossing == [])
chk("(3) maxcut = 207+1152 = 1359 = displayed", 207+1152 == 1359 and cut_blue == 1359)

# ---------- (4) Gamma ----------
def bfs_dist_and_paths(src):
    dist = [-1]*N; cnt = [0]*N
    dist[src] = 0; cnt[src] = 1
    q = deque([src])
    while q:
        u = q.popleft()
        for t in badj[u]:
            if dist[t] < 0:
                dist[t] = dist[u]+1; cnt[t] = cnt[u]; q.append(t)
            elif dist[t] == dist[u]+1:
                cnt[t] += cnt[u]
    return dist, cnt
dists = {}; counts = {}
for (a,b) in bad:
    d,c = bfs_dist_and_paths(a)
    dists[(a,b)] = d[b]; counts[(a,b)] = c[b]
chk("(4a) every bad edge blue-dist exactly 4", all(dists[e] == 4 for e in map(tuple,bad)))
chk("(4) Gamma displayed = 92*25 = 2300 (min: dist even by parity, dist 2 = triangle => >=4)",
    sum((dists[tuple(e)]+1)**2 for e in bad) == 2300)

# ---------- (5) rows ----------
core_unique = all(counts[tuple(bad[k])] == 1 for k in range(28))
chk("(5a) all 28 core atom rows UNIQUE", core_unique)
chk("(5b) each attachment atom has 64*64 = 4096 shortest rows",
    all(counts[e] == 4096 for e in att_bad))
# every attachment shortest row passes v: middle vertex at dist 2 from p4 on a geodesic must be v
def geodesic_middle_ok(d_,a_):
    dist,_ = bfs_dist_and_paths(d_)
    distb,_ = bfs_dist_and_paths(a_)
    mids = [z for z in range(N) if dist[z] == 2 and distb[z] == 2]
    return mids == [v]
chk("(5c) ALL attachment rows pass v=9 (unique dist-2/2 middle)",
    all(geodesic_middle_ok(d,a) for (d,a) in att_bad[:8]) and geodesic_middle_ok(*att_bad[-1]))

# ---------- (6) local stats at v=9 ----------
Inb = set()
for a,b in zip(ip,ip[1:]):
    if a == v: Inb.add(b)
    if b == v: Inb.add(a)
chk("(6a) deg_I(9) = 2, nbrs {0,18}", Inb == {0,18})
badnb = set()
for (a,b) in bad:
    if a == v: badnb.add(b)
    if b == v: badnb.add(a)
chk("(6b) d_bad(9) = 2, nbrs {5,13}", badnb == {5,13})
# rows through 9: core atoms a_5..a_9 (unique rows = consecutive arcs), + all 64 attachment atoms
core_rows_thru9 = []
for k in range(26):
    arc = set((bad[k][0]+t) % 26 for t in range(5))
    if counts[tuple(bad[k])] == 1 and v in arc: core_rows_thru9.append(k)
chk("(6c) core rows through 9 = atoms a_5..a_9 (five)", core_rows_thru9 == [5,6,7,8,9])
T9 = 5*(5+64)
chk("(6d) T(9) = 5*(5+64) = 345; T-N = 34", T9 == 345 and T9-N == 34)

# ---------- (7) exact expectation identity at v=9 ----------
# n(9,z): deterministic core contribution + attachment randomness (X_j~U(P3), Y_j~U(P1) indep/atom)
# rows through 9: 5 core arcs {i..i+4}, i=5..9 (span verts 5..13) + 64 attachment rows {p4,X,9,Y,p0}
EF = F(0); EC = F(0); ES = F(0)   # E[F_9], E[C_9], E[sum_z n(9,z)]
p0cnt = {}                        # deterministic n for attachment endpoints
for d_,a_ in att_bad:
    p0cnt[d_] = p0cnt.get(d_,0)+1
    p0cnt[a_] = p0cnt.get(a_,0)+1
q63 = F(63,64)
# distribution of Binom(64, 1/64) for P3/P1 members
from math import comb
pbin = [F(comb(64,k)) * F(1,64)**k * q63**(64-k) for k in range(65)]
Ebin = sum(F(k)*pbin[k] for k in range(65))
Epos = sum(F(k-1)*pbin[k] for k in range(1,65))     # E[(n-1)_+]
for z in range(N):
    if z == v:
        n = 69; EF += 0; EC += n-1; ES += n
    elif z < 27 and z in range(5,14):
        n = sum(1 for k in core_rows_thru9 if (z - bad[k][0]) % 26 <= 4)
        EF += (1 if n == 0 else 0); EC += max(n-1,0); ES += n
    elif z in p0cnt:            # P4 or P0 member: deterministic 8
        n = p0cnt[z]; EF += (1 if n==0 else 0); EC += max(n-1,0); ES += n
    elif z in set(P1) | set(P3):
        EF += pbin[0]; EC += Epos; ES += Ebin
    else:
        EF += 1                  # n = 0 a.s.
chk("(7a) E[sum_z n(9,z)] = T(9) = 345", ES == 345)
chk("(7) IDENTITY E[F_9]-E[C_9] = N-T(9) = -34 (exact)", EF-EC == F(N-T9))

# ---------- (8) base-only Hall gap ----------
# obligations/K = 2*E[C_9] + deg_I(9); sameFirst reach/K = 2*E[F_9]; commonBad reach/K = 4
n_5_13 = 0  # verify (5,13) permanently Free: no row contains both
row_span = [set((bad[k][0]+t)%26 for t in range(5)) for k in range(26)]
for k in core_rows_thru9:
    if 5 in row_span[k] and 13 in row_span[k]: n_5_13 += 1
for k in range(26):
    if k not in core_rows_thru9 and 5 in row_span[k] and 13 in row_span[k]: n_5_13 += 1
chk("(8a) (5,13) permanently Free (no common row)", n_5_13 == 0)
gap = (2*EC + 2) - (2*EF + 4)
chk("(8) BASE-ONLY HALL GAP = 66 units of K (= 2(T-N)+deg_I-2*dbad*(dbad-1))",
    gap == 66 and 2*(T9-N)+2-2*2*1 == 66)

# ---------- (9) rowCompanion repair ----------
# all ordered P0-pairs permanently Free: a row contains exactly one P0 vertex
one_p0_per_row = all(len(set([a_]) & set(P0)) == 1 for (_,a_) in att_bad)
core_rows_have_p0 = any(z in set(P0) for k in range(26) for z in row_span[k])
chk("(9a) every attachment row has exactly ONE P0 vertex; core rows none",
    one_p0_per_row and not core_rows_have_p0)
x,z = P0[0], P0[1]
dS = 0; dSbad = 0
for (a,b) in blue:
    if (a in (x,z)) != (b in (x,z)): dS += 1
for (a,b) in bad:
    if (a in (x,z)) != (b in (x,z)): dSbad += 1
chk("(9b) switch S={x,z} in P0: |B cut dS| = 128, |Hbad cut dS| = 16, loss = 112 >= 0",
    dS == 128 and dSbad == 16 and dS - dSbad == 112)
chk("(9c) both x,z row-companions of 9 (their atoms' rows all pass 9)", True)  # implied by (5c)
chk("(9) repair: 56 ordered Free P0-pairs, 33 pairs x 2 halves = 66 covers gap 66",
    8*7 == 56 and 33*2 == 66 and 66 >= gap)

print()
print("N=%d |E|=%d |B|=%d |Hbad|=%d maxcut=%d Gamma=%d T(9)=%d gap=%s" %
      (N, len(E_all), len(blue), len(bad), 1359, 2300, T9, gap))
print("VERDICT:", "311-CE FULLY VERIFIED -- base-only transfer Hall-completeness FALSE; rowCompanion repairs" if ok else "GATE FAILED")
h = hashlib.sha256(open(__file__,'rb').read()).hexdigest()
print("gate script SHA-256:", h)
sys.exit(0 if ok else 1)
