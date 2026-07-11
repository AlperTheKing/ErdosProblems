"""R23 gate: FOURTH pattern = outside-component attachment transfer. Exact verification on
the 89-vtx falsifier (expect: repaired to FULL matching 776/776) and the 311 corridor cage
with the FIXED lex-least row tuple (expect: owner-9 demand 636, +72,580 pattern-4 halves =
191 eligible outside vertices, global flow complete).

Pattern 4 (R23): Free ordered pair (x,y), x!=y, BOTH outside U = union of selected row
vertices; K(x), K(y) = blue components of x,y in B[V \\ U]; eligible for owner v iff
exists a in Att(K(x)), b in Att(K(y)) with n(v,a) > 0 and n(v,b) > 0 (attachment boundary
Att = blue neighbours of the component inside U). Switch set = K(x) u K(y), loss >= 0
recomputed (automatic at max cut). Capacity = the FreeHalf unit; loss magnitude never spent.
Old relation (sameOwner + commonBad + rowCompanion) kept; pattern 4 is a monotone extension.
"""
from collections import deque
import hashlib, sys

ok = True
def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: ok = False

def dinic(Nn, S, T, arcs):
    graph = [[] for _ in range(Nn)]
    def add(u,v,c):
        graph[u].append([v,c,len(graph[v])])
        graph[v].append([u,0,len(graph[u])-1])
    for (u,v,c) in arcs: add(u,v,c)
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

def run_flow(N, blue, bad, rows, label, expect_full, extra_checks=None):
    """build n-counts, demands, old+pattern4 relation, exact max-flow"""
    badj = [set() for _ in range(N)]
    for (x,y) in blue: badj[x].add(y); badj[y].add(x)
    badnb = [set() for _ in range(N)]
    for (x,y) in bad: badnb[x].add(y); badnb[y].add(x)
    n = {}
    for row in rows:
        for x in row:
            for y in row: n[(x,y)] = n.get((x,y),0)+1
    U = set(v for row in rows for v in row)
    # outside components + attachment boundaries
    compid = [-1]*N
    comps = []; atts = []
    for v in range(N):
        if v not in U and compid[v] < 0:
            cid = len(comps); comp = []; att = set()
            dq = deque([v]); compid[v] = cid
            while dq:
                u = dq.popleft(); comp.append(u)
                for t in badj[u]:
                    if t in U: att.add(t)
                    elif compid[t] < 0: compid[t] = cid; dq.append(t)
            comps.append(set(comp)); atts.append(att)
    def loss(S):
        b = sum(1 for (x,y) in blue if (x in S) != (y in S))
        m = sum(1 for (x,y) in bad  if (x in S) != (y in S))
        return b - m
    companions = {}
    for v in U:
        cs = set()
        for row in rows:
            if v in row: cs |= set(row)
        companions[v] = cs   # NOTE: includes v (diagonal co-occurrence allowed as witness)
    demand = {}
    for v in range(N):
        d = 2*sum(vv-1 for (x,y),vv in n.items() if x == v and vv >= 2)
        if d > 0: demand[v] = d
    owners = sorted(demand)
    # eligible outside vertices per owner (pattern 4, per-coordinate condition)
    elig_out = {}
    losses_ok = {}
    for v in owners:
        s = set()
        for cid in range(len(comps)):
            if any(n.get((v,a),0) > 0 for a in atts[cid]):
                s |= comps[cid]
        elig_out[v] = s
    # free-cell universe: only cells reachable by SOME owner matter
    cells = {}
    def cell_idx(key):
        if key not in cells: cells[key] = len(cells)
        return cells[key]
    arcs_om = []
    for i,v in enumerate(owners):
        # sameOwner
        for y in range(N):
            if y != v and n.get((v,y),0) == 0:
                arcs_om.append((i, cell_idx((v,y))))
        # commonBad
        for x in badnb[v]:
            for y in badnb[v]:
                if x != y and n.get((x,y),0) == 0 and loss({x,y}) >= 0:
                    arcs_om.append((i, cell_idx((x,y))))
        # rowCompanion
        cvs = sorted(companions[v] - {v})
        for x in cvs:
            for y in cvs:
                if x != y and n.get((x,y),0) == 0 and loss({x,y}) >= 0:
                    arcs_om.append((i, cell_idx((x,y))))
        # pattern 4: outside pairs, per-coordinate eligibility; loss(K(x) u K(y)) computed
        eo = sorted(elig_out[v])
        # loss check per component-pair via cache (loss of union of two comps)
        lcache = {}
        for x in eo:
            for y in eo:
                if x != y:
                    key = (compid[x], compid[y])
                    if key not in lcache:
                        lcache[key] = loss(comps[compid[x]] | comps[compid[y]]) >= 0
                    if lcache[key]:
                        arcs_om.append((i, cell_idx((x,y))))
    # flow network
    nC = len(cells)
    Nn = 2 + len(owners) + nC
    S, T = 0, 1
    arcs = [(S, 2+i, demand[v]) for i,v in enumerate(owners)]
    arcs += [(2+i, 2+len(owners)+j, 2) for (i,j) in set(arcs_om)]
    arcs += [(2+len(owners)+j, T, 2) for j in range(nC)]
    total = sum(demand.values())
    mf = dinic(Nn, S, T, arcs)
    print("  [%s] owners=%d cells=%d demand=%d maxflow=%d" % (label, len(owners), nC, total, mf))
    chk("[%s] FULL matching (flow = demand = %d)" % (label, total), mf == total if expect_full else mf < total)
    if extra_checks: extra_checks(n, demand, comps, atts, elig_out, loss, compid)
    return n, demand, comps, atts, elig_out

# ================= 89-vtx =================
print("========== 89-vtx double-star (R22 falsifier) ==========")
r, cL, cR = 0, 1, 2
L = [3,4,5,6]; R = [7,8,9,10,11]; a89 = 12
q = [0,0,0,4,6,4,5,5,3,3,3,5]
blue = set(); bad = []
def be(x,y): blue.add((min(x,y),max(x,y)))
be(r,cL); be(r,cR)
for l in L: be(cL,l)
for rr in R: be(cR,rr)
for l in L:
    for rr in R: bad.append((l,rr))
nxt = 13
for v in range(12):
    for k in range(q[v]):
        x, y = nxt, nxt+1; nxt += 2
        be(v,x); be(x,y); be(y,a89)
N89 = nxt
rows89 = [(l,cL,r,cR,rr) for (l,rr) in bad]
def checks89(n, demand, comps, atts, elig_out, loss, compid):
    chk("[89] outside = ONE component of 77; Att = the 9 leaves",
        len(comps) == 1 and len(comps[0]) == 77 and atts[0] == set(L+R))
    chk("[89] loss(outside comp) = 38 (38 blue boundary, 0 bad)", loss(comps[0]) == 38)
    chk("[89] all 77 outside verts eligible for each hub; +11704 halves at W",
        all(len(elig_out[v]) == 77 for v in (r,cL,cR)) and 2*77*76 == 11704)
    chk("[89] shore W demand still 528", sum(demand[v] for v in (r,cL,cR)) == 528)
run_flow(N89, blue, bad, rows89, "89 + pattern4", True, checks89)

# ================= 311-vtx, FIXED lex-least tuple =================
print("========== 311-vtx corridor cage (fixed tuple) ==========")
blue = set(); bad = []
for i in range(26): be(i,(i+1)%26)
be(26,0)
for i in range(26): bad.append((i,(i+4)%26))
bad.append((26,3)); bad.append((26,23))
ip = [0]
for _ in range(12): ip.append((ip[-1]+9)%26)
for x,y in zip(ip,ip[1:]): be(x,y)
nxt = 27
for (x,y) in bad[:28]:
    ls = list(range(nxt,nxt+5)); nxt += 5
    ch = [x]+ls+[y]
    for u,w in zip(ch,ch[1:]): be(u,w)
v9 = 9
P0 = list(range(nxt,nxt+8));  nxt += 8
P1 = list(range(nxt,nxt+64)); nxt += 64
P3 = list(range(nxt,nxt+64)); nxt += 64
P4 = list(range(nxt,nxt+8));  nxt += 8
for x in P0:
    for y in P1: be(x,y)
for y in P1: be(y,v9)
for c in P3: be(v9,c)
for c in P3:
    for d in P4: be(c,d)
att_atoms = [(d,x) for d in P4 for x in P0]
bad += att_atoms
N311 = nxt
rows311 = [tuple((bad[k][0]+t)%26 for t in range(5)) for k in range(26)]
rows311.append((26,0,1,2,3)); rows311.append((26,0,25,24,23))
for (d,x) in att_atoms:
    rows311.append((d, P3[0], v9, P1[0], x))    # lex-least P3/P1 choices
def checks311(n, demand, comps, atts, elig_out, loss, compid):
    chk("[311] owner-9 collision demand = 636 halves", demand.get(v9) == 636)
    chk("[311] eligible outside verts for owner 9 = 191 (63 P3 + 63 P1 + 65 lock of a1..a13)",
        len(elig_out[v9]) == 191 and 2*191*190 == 72580)
run_flow(N311, blue, bad, rows311, "311 fixed-tuple + pattern4", True, checks311)

print()
print("OVERALL:", "ALL CHECKS PASS -- pattern 4 repairs 89 (full matching) and 311 fixed-tuple passes"
      if ok else "SOME CHECKS FAILED")
h = hashlib.sha256(open(__file__,'rb').read()).hexdigest()
print("gate script SHA-256:", h)
sys.exit(0 if ok else 1)
