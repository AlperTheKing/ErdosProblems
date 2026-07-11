"""WF-CE hunt (double-star-traffic family): decisive counterexample gate for
RealHallFailureHasScopedScoreOneRowDescent (theorem-of-record, 8224/8224 N<=12).

CONSTRUCTION (t=25, N=2714): scaled double-star traffic block with pylon-hosted
locks + an active z-path gadget grafted onto the hubs.

  hubs r,cL,cR; L=25 left leaves, R=25 right leaves; blue double star
  r-cL, r-cR, cL-L, cR-R; bad = L x R (625 atoms, unique rows l-cL-r-cR-r').
  RIGIDITY: 25 left pylons (each blue-adjacent to ALL left leaves), 25 right
  pylons; each pylon carries q=25 private lock paths pi-x-y-A to one anchor A.
  PATTERN-4 BLOCK: locks/anchor stay OUTSIDE the selected union, but their only
  attachments are the pylons; pylons are covered by selector rows that never
  co-occur with the hubs => outside-attachment eligibility of every demanded
  owner is EMPTY (no selector rows through leaves/hubs; hubs co-occur only with
  {cL,cR} u L u R).
  PYLON COVER: 12 pair-selector rows per side u-pi-w-pi'-u2 (bad (u,u2)) +
  1 single-pylon selector row per side u-v-pi-v2-u2. Pair atoms have row DB of
  size 26 (via w, or via any of the 25 same-side leaves) => the one-row
  replacement set of the cage is NON-EMPTY (600 replacements).
  ACTIVE GADGET: bad atom (s,t) with unique selected row s-m1-m2-m3-t and an
  off-support blue path s-z1-z2-z3-z4-z5-t (length 6 > 4, so it is NOT a row);
  z_i covered by private selector rows u-v-z_i-v2-u2; grafts r-z1, cL-z2,
  cR-z4 are I-edges putting all three hubs into the single active component
  {r,cL,cR,s,t,z1..z5}.

CLAIMS GATED:
 (1) N=2714, |B|=5189, |M|=657, |E|=5846; (2) triangle-free;
 (3) displayed cut = all 5189 blue crossing, 0 bad crossing;
 (4) maxcut = 5189 EXACT via verified block decomposition (locks 2+[s_pi!=s_A],
     selector blocks constant 4, gadget 2^10 table) + exhaustive symmetric core
     enumeration (leaf/pylon neighborhood identity asserted) + random-assignment
     cross-check; hence every 2-subset switch loss >= 0 and Gamma = 25*657 is
     the GLOBAL minimum over max cuts (parity + tri-free: any missing edge of
     any max cut has even blue distance >= 4, distance 2 would be a triangle);
 (5) blue connected; every bad edge at blue distance EXACTLY 4; complete
     shortest-row DB enumerated: 633 atoms unique, 24 pair atoms with 26 rows;
 (6) canonical tuple: active components = exactly one, active vertices =
     {r,cL,cR,s,t,z1..z5}, scoped obligation score = 18435
     (collision 6144 per hub + HitNeed 1 per hub);
 (7) ACTIVE-SCOPED OWNER HALL FAILS: exact Dinic max-flow on the full
     four-pattern relation (sameFirst + rowCompanion + outsideAttachment,
     capacity-1 reservations on demanded-active cells): demand 18435,
     flow 18363, DEFICIENCY 72; outside-attachment arcs for every demanded
     owner = 0 (eligibility empty);
 (8) DESCENT ENUMERATION: all 600 one-row replacements (24 pair atoms x 25
     alternative rows; every other atom's row is unique) => exact scoped-score
     delta = 0 for every replacement => NO single-row replacement strictly
     lowers the scoped obligation score.
HIT = (7) Hall fails AND (8) min delta >= 0.
"""
from collections import deque
import hashlib, itertools, random, sys

ok = True
def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: ok = False

T = 25
r, cL, cR = 0, 1, 2
L  = list(range(3, 3 + T))
R  = list(range(3 + T, 3 + 2 * T))
LP = list(range(53, 53 + T))
RP = list(range(78, 78 + T))
A  = 103
blue = set(); bad = []
def be(x, y):
    assert x != y
    e = (min(x, y), max(x, y))
    assert e not in blue
    blue.add(e)

be(r, cL); be(r, cR)
for l in L: be(cL, l)
for rr in R: be(cR, rr)
for l in L:
    for p in LP: be(l, p)
for rr in R:
    for p in RP: be(rr, p)
for l in L:
    for rr in R: bad.append((l, rr))

nxt = 104
lock_blocks = []          # (pi, x, y) with y-A
for p in LP + RP:
    for _ in range(T):
        x, y = nxt, nxt + 1; nxt += 2
        be(p, x); be(x, y); be(y, A)
        lock_blocks.append((p, x, y))
assert nxt == 2604

s, t = 2604, 2605
m1, m2, m3 = 2606, 2607, 2608
Z = [2609, 2610, 2611, 2612, 2613]         # z1..z5
for u, v in zip([s, m1, m2, m3], [m1, m2, m3, t]): be(u, v)
zchain = [s] + Z + [t]
for u, v in zip(zchain, zchain[1:]): be(u, v)
be(r, Z[0]); be(cL, Z[1]); be(cR, Z[3])    # grafts
bad.append((s, t))
gadget_int = [s, t, m1, m2, m3] + Z

nxt = 2614
zsel_blocks = []           # (u, v, z, v2, u2)
for z in Z:
    u, v, v2, u2 = nxt, nxt + 1, nxt + 2, nxt + 3; nxt += 4
    be(u, v); be(v, z); be(z, v2); be(v2, u2)
    bad.append((u, u2))
    zsel_blocks.append((u, v, z, v2, u2))
assert nxt == 2634

pair_blocks = []           # (u, pi, w, pi2, u2)
single_blocks = []         # (u, v, pi, v2, u2)
for side in (LP, RP):
    for k in range(0, T - 1, 2):
        p1, p2 = side[k], side[k + 1]
        u, w, u2 = nxt, nxt + 1, nxt + 2; nxt += 3
        be(u, p1); be(p1, w); be(w, p2); be(p2, u2)
        bad.append((u, u2))
        pair_blocks.append((u, p1, w, p2, u2))
    p = side[T - 1]
    u, v, v2, u2 = nxt, nxt + 1, nxt + 2, nxt + 3; nxt += 4
    be(u, v); be(v, p); be(p, v2); be(v2, u2)
    bad.append((u, u2))
    single_blocks.append((u, v, p, v2, u2))
N = nxt
badset = set((min(x, y), max(x, y)) for x, y in bad)
assert len(badset) == len(bad) and not (badset & blue)

chk("(1) N=2714, |B|=5189, |M|=657, |E|=5846",
    N == 2714 and len(blue) == 5189 and len(bad) == 657
    and len(blue) + len(bad) == 5846)

E_all = blue | badset
adj = [set() for _ in range(N)]
for (x, y) in E_all: adj[x].add(y); adj[y].add(x)
badj = [set() for _ in range(N)]
for (x, y) in blue: badj[x].add(y); badj[y].add(x)

chk("(2) triangle-free", not any(adj[x] & adj[y] for (x, y) in E_all))

# displayed sides
side = [0] * N
for v in (cL, cR): side[v] = 1
for p in LP + RP: side[p] = 1
for (p, x, y) in lock_blocks: side[x] = 1
side[m1] = side[m3] = 1
side[Z[0]] = side[Z[2]] = side[Z[4]] = 1
for (u, v, z, v2, u2) in zsel_blocks:
    side[u] = side[u2] = side[z]
    side[v] = side[v2] = 1 - side[z]
for (u, p1, w, p2, u2) in pair_blocks:
    side[u] = side[u2] = side[w] = 0
for (u, v, p, v2, u2) in single_blocks:
    side[u] = side[u2] = 1
chk("(3) displayed cut: all 5189 blue cross, 0 of 657 bad cross",
    all(side[x] != side[y] for (x, y) in blue)
    and all(side[x] == side[y] for (x, y) in bad))

# ---------------- (4) EXACT MAX CUT via block decomposition ----------------
# Blocks: interiors are pairwise disjoint, and every edge lies in exactly one
# bucket whose endpoints are interior+boundary of that block.  Hence
# max over sigma  =  max over core sigma of [ core(sigma) + sum block tables ].
core_vs = set([r, cL, cR, A] + L + R + LP + RP)
buckets = {}   # edge -> bucket id
def put(e, b):
    e = (min(e), max(e))
    assert e not in buckets, e
    buckets[e] = b
interior_seen = set()
def claim(vs):
    for v in vs:
        assert v not in interior_seen and v not in core_vs
        interior_seen.add(v)

for i, (p, x, y) in enumerate(lock_blocks):
    claim([x, y]); put((p, x), ("lock", i)); put((x, y), ("lock", i)); put((y, A), ("lock", i))
claim(gadget_int)
for e in ([(s, m1), (m1, m2), (m2, m3), (m3, t)]
          + list(zip(zchain, zchain[1:]))
          + [(r, Z[0]), (cL, Z[1]), (cR, Z[3]), (s, t)]):
    put(e, ("gadget", 0))
for i, (u, v, z, v2, u2) in enumerate(zsel_blocks):
    claim([u, v, v2, u2])
    for e in [(u, v), (v, z), (z, v2), (v2, u2), (u, u2)]: put(e, ("zsel", i))
for i, (u, p1, w, p2, u2) in enumerate(pair_blocks):
    claim([u, w, u2])
    for e in [(u, p1), (p1, w), (w, p2), (p2, u2), (u, u2)]: put(e, ("pair", i))
for i, (u, v, p, v2, u2) in enumerate(single_blocks):
    claim([u, v, v2, u2])
    for e in [(u, v), (v, p), (p, v2), (v2, u2), (u, u2)]: put(e, ("single", i))
core_edges = [e for e in E_all if e not in buckets]
chk("(4a) decomposition: interiors partition V\\core; buckets+core partition E",
    interior_seen | core_vs == set(range(N))
    and len(interior_seen) + len(core_vs) == N
    and all(x in core_vs and y in core_vs for (x, y) in core_edges)
    and len(buckets) + len(core_edges) == len(E_all))

# neighborhood-identity => leaf/pylon exchange symmetry inside the core graph
coreadj = [set() for _ in range(N)]
corebad = [set() for _ in range(N)]
for (x, y) in core_edges:
    if (x, y) in blue: coreadj[x].add(y); coreadj[y].add(x)
    else: corebad[x].add(y); corebad[y].add(x)
chk("(4b) symmetry: every left leaf core-adj == {cL} u LP, bads == R; right mirrored;"
    " every pylon core-adj == its side's leaves; anchor core-isolated; q=25 locks/pylon",
    all(coreadj[l] == set([cL]) | set(LP) and corebad[l] == set(R) for l in L)
    and all(coreadj[rr] == set([cR]) | set(RP) and corebad[rr] == set(L) for rr in R)
    and all(coreadj[p] == set(L) and not corebad[p] for p in LP)
    and all(coreadj[p] == set(R) and not corebad[p] for p in RP)
    and not coreadj[A] and not corebad[A]
    and all(sum(1 for (p, x, y) in lock_blocks if p == q) == T for q in LP + RP))

# block tables (exact interior maxima given boundary bits)
def block_max(edges, badedges, interior, fixed):
    best = -1
    for bits in itertools.product((0, 1), repeat=len(interior)):
        sig = dict(fixed); sig.update(zip(interior, bits))
        v = sum(1 for (x, y) in edges if sig[x] != sig[y])
        v += sum(1 for (x, y) in badedges if sig[x] != sig[y])
        if v > best: best = v
    return best

p0, x0, y0 = lock_blocks[0]
lock_tab = {}
for sp in (0, 1):
    for sa in (0, 1):
        lock_tab[(sp, sa)] = block_max([(p0, x0), (x0, y0), (y0, A)], [],
                                       [x0, y0], {p0: sp, A: sa})
chk("(4c) lock table = 2 + [s_pi != s_A]",
    lock_tab == {(0, 0): 2, (1, 1): 2, (0, 1): 3, (1, 0): 3})

u_, v_, z_, v2_, u2_ = zsel_blocks[0]
zs_const = all(block_max([(u_, v_), (v_, z_), (z_, v2_), (v2_, u2_)],
                         [(u_, u2_)], [u_, v_, v2_, u2_], {z_: sz}) == 4
               for sz in (0, 1))
u_, p1_, w_, p2_, u2_ = pair_blocks[0]
pr_const = all(block_max([(u_, p1_), (p1_, w_), (w_, p2_), (p2_, u2_)],
                         [(u_, u2_)], [u_, w_, u2_], {p1_: s1, p2_: s2}) == 4
               for s1 in (0, 1) for s2 in (0, 1))
u_, v_, p_, v2_, u2_ = single_blocks[0]
sg_const = all(block_max([(u_, v_), (v_, p_), (p_, v2_), (v2_, u2_)],
                         [(u_, u2_)], [u_, v_, v2_, u2_], {p_: sp}) == 4
               for sp in (0, 1))
chk("(4d) selector blocks constant 4 for every boundary", zs_const and pr_const and sg_const)

gadget_edges = [(s, m1), (m1, m2), (m2, m3), (m3, t)] + list(zip(zchain, zchain[1:])) \
               + [(r, Z[0]), (cL, Z[1]), (cR, Z[3])]
h_tab = {}
for hb in itertools.product((0, 1), repeat=3):
    h_tab[hb] = block_max(gadget_edges, [(s, t)], gadget_int,
                          {r: hb[0], cL: hb[1], cR: hb[2]})
chk("(4e) gadget table: h(0,1,1)=13 attained, max over boundaries <= 13",
    h_tab[(0, 1, 1)] == 13 and max(h_tab.values()) == 13)

# symmetric core enumeration: kL/kR flipped leaves, pL/pR flipped pylons
best_total = -1
LOCK_CONST = 2 * len(lock_blocks)
SEL_CONST = 4 * (len(zsel_blocks) + len(pair_blocks) + len(single_blocks))
for hr in (0, 1):
    for hcl in (0, 1):
        for hcr in (0, 1):
            for ha in (0, 1):
                const = (hr != hcl) + (hr != hcr) + h_tab[(hr, hcl, hcr)]
                bl = []
                for k in range(T + 1):
                    m = -1
                    for p in range(T + 1):
                        val = (k * (1 - hcl) + (T - k) * hcl
                               + k * p + (T - k) * (T - p)
                               + T * (p * ha + (T - p) * (1 - ha)))
                        if val > m: m = val
                    bl.append(m)
                br = []
                for k in range(T + 1):
                    m = -1
                    for p in range(T + 1):
                        val = (k * (1 - hcr) + (T - k) * hcr
                               + k * p + (T - k) * (T - p)
                               + T * (p * ha + (T - p) * (1 - ha)))
                        if val > m: m = val
                    br.append(m)
                for kl in range(T + 1):
                    for kr in range(T + 1):
                        v = (const + bl[kl] + br[kr]
                             + kl * (T - kr) + (T - kl) * kr)
                        if v > best_total: best_total = v
best_total += LOCK_CONST + SEL_CONST
disp_val = sum(1 for (x, y) in E_all if side[x] != side[y])
chk("(4f) MAXCUT = 5189 EXACT (block DP); displayed attains it",
    best_total == 5189 and disp_val == 5189)
rng = random.Random(23)
samp_ok = True
for _ in range(300):
    sig = [rng.randint(0, 1) for _ in range(N)]
    v = sum(1 for (x, y) in E_all if sig[x] != sig[y])
    if v > 5189: samp_ok = False
chk("(4g) 300 random assignments never exceed 5189", samp_ok)

# ---------------- (5) distances, row DB, connectivity ----------------
def bfs(src):
    dist = [-1] * N
    dist[src] = 0
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for w in badj[u]:
            if dist[w] < 0:
                dist[w] = dist[u] + 1; dq.append(w)
    return dist

dist_cache = {}
def dists(v):
    if v not in dist_cache: dist_cache[v] = bfs(v)
    return dist_cache[v]

def all_shortest_rows(x, y):
    dx = dists(x)
    assert dx[y] == 4
    paths = []
    def back(v, acc):
        if dx[v] == 0:
            paths.append(tuple(reversed(acc + [v]))); return
        for w in badj[v]:
            if dx[w] == dx[v] - 1: back(w, acc + [v])
    back(y, [])
    return [p for p in paths]   # oriented x -> y

conn = bfs(r)
chk("(5a) blue connected; ALL 657 bad edges at blue distance EXACTLY 4",
    all(d >= 0 for d in conn) and all(dists(x)[y] == 4 for (x, y) in bad))

DB = {}
for (x, y) in bad: DB[(x, y)] = all_shortest_rows(x, y)
pair_atoms = set((u, u2) for (u, p1, w, p2, u2) in pair_blocks)
hist = {}
for k, v in DB.items(): hist[len(v)] = hist.get(len(v), 0) + 1
chk("(5b) row DB: 633 atoms unique; the 24 pylon-pair atoms have exactly 26 rows",
    hist == {1: 633, 26: 24}
    and all(len(DB[a]) == 26 for a in pair_atoms))
chk("(5c) Gamma = 25*657 = 16425 = GLOBAL min over max cuts (all ell=5; parity+tri-free)",
    sum((dists(x)[y] + 1) ** 2 for (x, y) in bad) == 25 * 657)

# canonical selection: unique rows; pair atoms take the via-w row
rows = []
row_of = {}
for (x, y) in bad:
    if (x, y) in pair_atoms:
        pick = [p for p in DB[(x, y)] if p[2] not in set(L) | set(R)]
        assert len(pick) == 1
        rows.append(pick[0])
    else:
        rows.append(DB[(x, y)][0])
    row_of[(x, y)] = rows[-1]
chk("(6a) tuple = 657 rows; pair atoms canonical via-w; total tuple count 26^24",
    len(rows) == 657 and all(row_of[a][2] not in set(L) | set(R) for a in pair_atoms))

# ---------------- scoped frame (exact Codex semantics) ----------------
def edge(x, y): return (x, y) if x < y else (y, x)

def scoped_parts(rows):
    counts = {}
    row_count = [0] * N
    support = set()
    for row in rows:
        for x in row:
            row_count[x] += 1
            for y in row:
                counts[(x, y)] = counts.get((x, y), 0) + 1
        support.update(edge(x, y) for x, y in zip(row, row[1:]))
    selected = set(x for row in rows for x in row)
    active = set(e for e in blue
                 if e[0] in selected and e[1] in selected and e not in support)
    parent = {v: v for v in selected}
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]; v = parent[v]
        return v
    for x, y in active:
        rx, ry = find(x), find(y)
        if rx != ry: parent[max(rx, ry)] = min(rx, ry)
    roots = set(find(x) for (x, y) in bad
                if x in selected and y in selected and find(x) == find(y))
    act_vs = set(v for v in selected if find(v) in roots)
    dem_act = set(e for e in active if find(e[0]) in roots)
    deg = {}
    for x, y in dem_act:
        deg[x] = deg.get(x, 0) + 1; deg[y] = deg.get(y, 0) + 1
    collision = {v: 2 * sum(m - 1 for (a, b), m in counts.items()
                            if a == v and m >= 2) for v in act_vs}
    hitneed = {v: max(0, deg.get(v, 0) - max(0, N - 5 * row_count[v]))
               for v in act_vs}
    return counts, row_count, support, selected, active, act_vs, dem_act, \
           collision, hitneed

(counts, row_count, support, selected, active_edges, act_vs, dem_act,
 collision, hitneed) = scoped_parts(rows)
score0 = sum(collision.values()) + sum(hitneed.values())
exp_act = set([r, cL, cR, s, t] + Z)
chk("(6b) active vertices == {r,cL,cR,s,t,z1..z5}; demanded active edges = 9;"
    " |U|=213; I-edges total = 1259",
    act_vs == exp_act and len(dem_act) == 9 and len(selected) == 213
    and len(active_edges) == 1259)
chk("(6c) scoped obligation score = 18435 (collision 6144 x3 hubs, HitNeed 1 x3)",
    score0 == 18435
    and all(collision[h] == 6144 and hitneed[h] == 1 for h in (r, cL, cR))
    and all(collision[v] == 0 and hitneed[v] == 0 for v in exp_act - {r, cL, cR}))

# ---------------- (7) exact active-scoped four-pattern owner flow ----------
degB = [len(badj[v]) for v in range(N)]
degM = [0] * N
for (x, y) in bad: degM[x] += 1; degM[y] += 1
def loss_pair(x, y):
    b = degB[x] + degB[y] - 2 * (edge(x, y) in blue)
    m = degM[x] + degM[y] - 2 * (edge(x, y) in badset)
    return b - m

demand = {v: collision[v] + hitneed[v] for v in act_vs
          if collision[v] + hitneed[v] > 0}
owners = sorted(demand)
chk("(7a) demanded owners = the 3 hubs, each demand 6145",
    owners == [r, cL, cR] and all(demand[h] == 6145 for h in owners))

# outside components + attachment eligibility
compid = [-1] * N
comps = []; atts = []
for root in range(N):
    if root in selected or compid[root] >= 0: continue
    cid = len(comps); comp = set(); att = set()
    compid[root] = cid; dq = deque([root])
    while dq:
        u = dq.popleft(); comp.add(u)
        for w in badj[u]:
            if w in selected: att.add(w)
            elif compid[w] < 0: compid[w] = cid; dq.append(w)
    comps.append(comp); atts.append(att)
elig = {v: set() for v in owners}
for v in owners:
    for cid in range(len(comps)):
        if any(counts.get((v, a2), 0) > 0 for a2 in atts[cid]):
            elig[v] |= comps[cid]
chk("(7b) outside = ONE component (2501 = locks+anchor), Att = the 50 pylons;"
    " eligibility EMPTY for all demanded owners => pattern 4 contributes 0",
    len(comps) == 1 and len(comps[0]) == 2501 and atts[0] == set(LP + RP)
    and all(not elig[v] for v in owners))

cell_id = {}; cell_cap = {}
def get_cell(x, y):
    key = (x, y)
    if key not in cell_id:
        cell_id[key] = len(cell_id)
        cell_cap[key] = 1 if edge(x, y) in dem_act else 2
    return cell_id[key]
arcs_oc = set()
for i, v in enumerate(owners):
    for y in range(N):
        if y != v and counts.get((v, y), 0) == 0:
            arcs_oc.add((i, get_cell(v, y)))
    comp_vs = [x for x in range(N) if x != v and counts.get((v, x), 0) > 0]
    for x in comp_vs:
        for y in comp_vs:
            if x != y and counts.get((x, y), 0) == 0 and loss_pair(x, y) >= 0:
                arcs_oc.add((i, get_cell(x, y)))
    # pattern 4: eligibility empty (asserted) -> no arcs

Nn = 2 + len(owners) + len(cell_id)
S, Tk = 0, 1
graph = [[] for _ in range(Nn)]
def add(u, v, c):
    graph[u].append([v, c, len(graph[v])])
    graph[v].append([u, 0, len(graph[u]) - 1])
for i, v in enumerate(owners): add(S, 2 + i, demand[v])
inv = {j: key for key, j in cell_id.items()}
for (i, j) in arcs_oc: add(2 + i, 2 + len(owners) + j, cell_cap[inv[j]])
for j in range(len(cell_id)): add(2 + len(owners) + j, Tk, cell_cap[inv[j]])
def dinic():
    flow = 0
    while True:
        lev = [-1] * Nn; lev[S] = 0; dq = deque([S])
        while dq:
            u = dq.popleft()
            for e in graph[u]:
                if e[1] > 0 and lev[e[0]] < 0:
                    lev[e[0]] = lev[u] + 1; dq.append(e[0])
        if lev[Tk] < 0: return flow
        it = [0] * Nn
        def dfs(u, f):
            if u == Tk: return f
            while it[u] < len(graph[u]):
                e = graph[u][it[u]]
                if e[1] > 0 and lev[e[0]] == lev[u] + 1:
                    d = dfs(e[0], min(f, e[1]))
                    if d > 0:
                        e[1] -= d; graph[e[0]][e[2]][1] += d; return d
                it[u] += 1
            return 0
        while True:
            f = dfs(S, 1 << 30)
            if f == 0: break
            flow += f
sys.setrecursionlimit(40000)
total = sum(demand.values())
mf = dinic()
chk("(7c) ACTIVE-SCOPED OWNER HALL FAILS: demand 18435, maxflow 18363, DEFICIENCY 72",
    total == 18435 and mf == 18363 and total - mf == 72)

# ---------------- (8) exhaustive one-row descent enumeration ----------------
def scoped_score(rws):
    p = scoped_parts(rws)
    return sum(p[7].values()) + sum(p[8].values())

deltas = []
n_repl = 0
min_delta = None
for ai, (x, y) in enumerate(bad):
    alts = [q for q in DB[(x, y)] if q != row_of[(x, y)]]
    for q in alts:
        n_repl += 1
        rws = list(rows); rws[ai] = q
        d = scoped_score(rws) - score0
        deltas.append(d)
        if min_delta is None or d < min_delta: min_delta = d
chk("(8a) replacement set NON-EMPTY: exactly 600 one-row replacements (24 x 25)",
    n_repl == 600)
chk("(8b) NO single-row replacement strictly lowers the scoped score:"
    " every delta == 0 (min delta = %s)" % str(min_delta),
    n_repl > 0 and min_delta is not None and min_delta >= 0
    and all(d == 0 for d in deltas))

print()
if ok:
    print("VERDICT: DECISIVE COUNTEREXAMPLE VERIFIED -- canonical cage N=2714"
          " (tri-free, exact maxcut 5189, connected blue, all 657 bad edges at"
          " distance 4, Gamma-min automatic, complete row DB): active-scoped"
          " owner Hall FAILS (deficiency 72) and ALL 600 one-row replacements"
          " have scoped-score delta 0 >= 0 =>"
          " RealHallFailureHasScopedScoreOneRowDescent is FALSE.")
else:
    print("VERDICT: GATE FAILED -- no counterexample claimed.")
h = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
print("gate script SHA-256:", h)
sys.exit(0 if ok else 1)
