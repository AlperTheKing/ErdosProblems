"""R22 gate: 89-vtx double-star counterexample to GLOBAL-MINIMIZER collision-owner Hall
(GPT-5.6 Pro, Codex-routed consult, 2026-07-11). Independent exact verification.

Construction: core r=0,cL=1,cR=2, L={3..6}, R={7..11}; blue core = double star
(r-cL, r-cR, cL-L, cR-R); bad = L x R (20, all ell=5); anchor a=12; lock loads
q=(0,0,0,4,6,4,5,5,3,3,3,5); per (v,k<=q_v): private x,y + blue v-x-y-a. N=89.
Claims gated: (1) N/E/B counts; (2) tri-free; (3) displayed cut = all 125 blue;
(4) maxcut = 125 EXACT (lock-path parity bound 3/2 + exhaustive 4096 core assignments);
(5) unique shortest rows (all 20 bad, dist 4, path count 1) => singleton row DB =>
    the tuple is trivially the unique global Score minimizer; B-connected; Gamma=500 min;
(6) activeEdges = empty; Score = 776; covered ordered pairs = 112;
(7) THE HALL GAP: exact max-flow on the full demand/source bipartite graph with
    sameOwner + commonBad + rowCompanion arcs (switch loss >= 0 recomputed per pair);
    total demand 776, max matching 774, deficiency 2; deficient shore contains hubs
    {r,cL,cR} with D(W)=528 vs Reach(W)=526.
"""
from collections import deque
import hashlib, sys

ok = True
def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: ok = False

r, cL, cR = 0, 1, 2
L = [3,4,5,6]; R = [7,8,9,10,11]
a = 12
q = [0,0,0,4,6,4,5,5,3,3,3,5]
blue = set(); bad = []
def be(x,y): blue.add((min(x,y),max(x,y)))
be(r,cL); be(r,cR)
for l in L: be(cL,l)
for rr in R: be(cR,rr)
for l in L:
    for rr in R: bad.append((l,rr))
nxt = 13
lockpairs = []   # (v, x, y)
for v in range(12):
    for k in range(q[v]):
        x, y = nxt, nxt+1; nxt += 2
        be(v,x); be(x,y); be(y,a)
        lockpairs.append((v,x,y))
N = nxt
chk("(1) N=89, |B|=125, |M|=20, |E|=145",
    N == 89 and len(blue) == 125 and len(bad) == 20 and len(blue)+len(bad) == 145)

E_all = set(blue) | set((min(x,y),max(x,y)) for x,y in bad)
adj = [set() for _ in range(N)]
for (x,y) in E_all: adj[x].add(y); adj[y].add(x)
badj = [set() for _ in range(N)]
for (x,y) in blue: badj[x].add(y); badj[y].add(x)

chk("(2) triangle-free", not any(adj[x] & adj[y] for (x,y) in E_all))

side = [0]*N
side[cL] = side[cR] = side[a] = 1
for (v,x,y) in lockpairs: side[x] = 1
chk("(3) displayed cut: 125 blue cross, 0 bad cross",
    sum(1 for (x,y) in blue if side[x]!=side[y]) == 125 and
    all(side[x]==side[y] for (x,y) in bad))

# (4) maxcut: value(sigma over 12 core verts; a fixed side 1; lock paths contribute
#     3 if sigma_v = 0 (opposite a) else 2 -- parity bound on 3-path with fixed endpoints)
core_blue = [(x,y) for (x,y) in blue if x < 12 and y < 12]
best = 0; arg = None
for mask in range(4096):
    s = [(mask >> v) & 1 for v in range(12)]
    val = sum(q[v]*(3 - s[v]) for v in range(12))
    val += sum(1 for (x,y) in core_blue if s[x] != s[y])
    val += sum(1 for (x,y) in bad if s[x] != s[y])
    if val > best: best, arg = val, mask
disp_mask = (1<<cL) | (1<<cR)
chk("(4) maxcut = 125 EXACT (4096 core assignments; lock parity bound); displayed attains",
    best == 125 and (sum(q[v]*(3-((disp_mask>>v)&1)) for v in range(12))
                     + sum(1 for (x,y) in core_blue if ((disp_mask>>x)&1)!=((disp_mask>>y)&1))
                     + 0) == 125)

def bfs(src):
    dist = [-1]*N; cnt = [0]*N
    dist[src] = 0; cnt[src] = 1
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for t in badj[u]:
            if dist[t] < 0: dist[t] = dist[u]+1; cnt[t] = cnt[u]; dq.append(t)
            elif dist[t] == dist[u]+1: cnt[t] += cnt[u]
    return dist, cnt
uni = True; g500 = 0
for (x,y) in bad:
    d,c = bfs(x)
    if d[y] != 4 or c[y] != 1: uni = False
    g500 += (d[y]+1)**2
d0,_ = bfs(r)
chk("(5) all 20 rows UNIQUE (dist 4, count 1); B connected; Gamma = 500 (min by parity+tri-free)",
    uni and all(dd >= 0 for dd in d0) and g500 == 500)

rows = [(l,cL,r,cR,rr) for (l,rr) in bad]
n = {}
for row in rows:
    for x in row:
        for y in row: n[(x,y)] = n.get((x,y),0)+1
sel_union = set(v for row in rows for v in row)
active = [(x,y) for (x,y) in blue if x in sel_union and y in sel_union
          and not any(x in row and y in row for row in rows)]
covered = sum(1 for k,v in n.items() if v > 0)
coll_units = sum(v-1 for v in n.values() if v >= 2)
chk("(6) activeEdges empty; covered = 112; collisionUnits = 388; Score = 776",
    active == [] and covered == 112 and coll_units == 388 and 2*coll_units == 776)

# (7) exact max-flow: demands (owner v, halves 2*(n(v,y)-1) summed) vs Free cells (2 halves)
def loss(S):
    b = sum(1 for (x,y) in blue if (x in S) != (y in S))
    m = sum(1 for (x,y) in bad  if (x in S) != (y in S))
    return b - m
badnb = [set() for _ in range(N)]
for (x,y) in bad: badnb[x].add(y); badnb[y].add(x)
companions = {}
for v in range(N):
    cs = set()
    for row in rows:
        if v in row: cs |= set(row)
    cs.discard(v)
    companions[v] = cs
demand = {v: 2*sum(vv-1 for (x,y),vv in n.items() if x == v and vv >= 2) for v in range(N)}
demand = {v:d for v,d in demand.items() if d > 0}
free_cells = [(x,y) for x in range(N) for y in range(N)
              if n.get((x,y),0) == 0]
# arcs: owner v -> cell (x,y)
def reach(v, x, y):
    if x == v: return True                                    # sameOwner
    if x != y and x in badnb[v] and y in badnb[v] and loss({x,y}) >= 0: return True   # commonBad
    if x != y and x in companions[v] and y in companions[v] and loss({x,y}) >= 0: return True  # rowCompanion
    return False
# Dinic max-flow: S -> owners (cap demand) -> cells (cap 2) -> T
owners = sorted(demand)
cell_id = {c:i for i,c in enumerate(free_cells)}
Nn = 2 + len(owners) + len(free_cells)
S, T = 0, 1
def oid(i): return 2 + i
def cid(i): return 2 + len(owners) + i
graph = [[] for _ in range(Nn)]
def add(u,v,c):
    graph[u].append([v,c,len(graph[v])])
    graph[v].append([u,0,len(graph[u])-1])
for i,v in enumerate(owners): add(S, oid(i), demand[v])
used_cells = set()
for i,v in enumerate(owners):
    for j,(x,y) in enumerate(free_cells):
        if reach(v,x,y):
            add(oid(i), cid(j), 2); used_cells.add(j)
for j in used_cells: add(cid(j), T, 2)
def dinic():
    flow = 0
    while True:
        lev = [-1]*Nn; lev[S] = 0; dq = deque([S])
        while dq:
            u = dq.popleft()
            for e in graph[u]:
                if e[1] > 0 and lev[e[0]] < 0: lev[e[0]] = lev[u]+1; dq.append(e[0])
        if lev[T] < 0: return flow
        it = [0]*Nn
        def dfs(u, f):
            if u == T: return f
            while it[u] < len(graph[u]):
                e = graph[u][it[u]]
                if e[1] > 0 and lev[e[0]] == lev[u]+1:
                    d = dfs(e[0], min(f, e[1]))
                    if d > 0:
                        e[1] -= d; graph[e[0]][e[2]][1] += d; return d
                it[u] += 1
            return 0
        while True:
            f = dfs(S, 1<<30)
            if f == 0: break
            flow += f
def tot(): return sum(demand.values())
mf = dinic()
chk("(7a) total demand = 776; max matching = 774; DEFICIENCY = 2", tot() == 776 and mf == 774)
# hub shore exact numbers
W = [r,cL,cR]
DW = sum(demand[v] for v in W)
reach_cells = set()
for v in W:
    for j,(x,y) in enumerate(free_cells):
        if reach(v,x,y): reach_cells.add(j)
RW = 2*len(reach_cells)
chk("(7b) shore W={r,cL,cR}: D(W)=528, |Reach(W)|=526, gap 2", DW == 528 and RW == 526)
chk("(7c) commonBad vacuous at hubs (no bad nbrs)", all(not badnb[v] for v in W))

print()
print("VERDICT:", ("89-vtx FALSIFIER FULLY VERIFIED -- global-minimizer collision-owner Hall "
      "(sameOwner+commonBad+rowCompanion) FAILS with gap 2; row DB singleton => NO exchange/prune "
      "of any size exists; conjecture UNTHREATENED (beta=20 <= 89^2/25=316.84)") if ok else "GATE FAILED")
h = hashlib.sha256(open(__file__,'rb').read()).hexdigest()
print("gate script SHA-256:", h)
sys.exit(0 if ok else 1)
