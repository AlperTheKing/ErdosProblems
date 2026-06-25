#!/usr/bin/env python3
# (R3') avenue-C refutation hunt (2026-06-12).
# Conjecture (R3'): K connected, 3-colourable, Delta<=6, total deficiency 6,
# three prescribed deficient vertices z1,z2,z3 NOT a triangle, every proper
# 3-colouring rainbow on {z1,z2,z3}  =>  some FULL (deg-6) vertex v is FROZEN
# (no proper 3-colouring of K-v with <=2 of each colour on N(v)).
#
# Construction: diamond gadget {A,B,U,T} + path edges U-V, V-W, T-W.
#   Diamond forces psi(U)=psi(T); edge T-W then forces psi(U)!=psi(W);
#   edges U-V, V-W force the rest => {U,V,W} rainbow in EVERY colouring.
#   All six gadget vertices carry deficiency 1 (Sum b = 6), so z1,z2,z3=U,V,W
#   are deficient and NO gadget vertex is full.  Pads: A:2,B:2,U:2,T:2,V:3,W:3
#   = 14 edges into 14 distinct capacity-1 bulk vertices (7 vertex-disjoint
#   bulk edges deleted), chosen pairwise FAR APART in the bulk.
# Bulk options:
#   pg : PG(2,5) incidence graph (62 vertices, girth 6, diameter 3)   [control]
#   gq : W(5)=GQ(5,5) incidence graph (312 vertices, girth 8, diam 4) [main]
# Pad side-parity rule guarantees an explicit colouring phi0 =
#   (bulk 2-colouring) + gadget colouring (A,B,U,T,V,W)=(1,2,3,3,1,2):
#   pads of A,V -> side-2 vertices; pads of B,W -> side-1; U,T anywhere.
#
# Checks (CP-SAT, witnesses re-verified by independent script r3c_verify.py):
#   (1) validity: Delta<=6, Sum(6-deg)=6, connected, deficient exactly gadget;
#   (2) K 3-colourable (also phi0 verified directly);
#   (3) rainbow-rigidity: model + (x_U == x_W) INFEASIBLE  (U~V,V~W edges
#       handle the other two pairs);  independent UNSAT check via pysat;
#   (4) frozen census over ALL full vertices: v frozen iff
#       "3-colour K-v with <=2 of each colour on N(v)" INFEASIBLE.
#       Every unfrozen vertex gets an explicit witness written to disk.
import sys, json, random, itertools
from collections import deque
from ortools.sat.python import cp_model

# ---------------------------------------------------------------- geometries
def projective_points(d, q):
    """Canonical reps (first nonzero coord = 1) of PG(d-1,q), as tuples."""
    pts = []
    for v in itertools.product(range(q), repeat=d):
        if all(c == 0 for c in v):
            continue
        # canonical: first nonzero coordinate == 1
        for c in v:
            if c != 0:
                lead = c
                break
        if lead == 1:
            pts.append(v)
    return pts

def build_pg25():
    """PG(2,5) point-line incidence graph: points 0..30, lines 31..61."""
    q = 5
    pts = projective_points(3, q)
    assert len(pts) == 31
    idx = {p: i for i, p in enumerate(pts)}
    edges = []
    for li, L in enumerate(pts):          # lines = same canonical triples (duality)
        for pi, P in enumerate(pts):
            if sum(a * b for a, b in zip(P, L)) % q == 0:
                edges.append((pi, 31 + li))
    return 62, edges, set(range(31))      # n, edges, side-1 vertex set

def build_gq55():
    """W(5) = GQ(5,5) incidence graph: 156 points + 156 t.i. lines, girth 8."""
    q = 5
    pts = projective_points(4, q)
    assert len(pts) == 156
    idx = {p: i for i, p in enumerate(pts)}
    def symp(x, y):
        return (x[0]*y[1] - x[1]*y[0] + x[2]*y[3] - x[3]*y[2]) % q
    # totally isotropic projective lines = 2-spaces spanned by p,r with symp=0
    lines = {}
    for i, p in enumerate(pts):
        for j in range(i + 1, len(pts)):
            r = pts[j]
            if symp(p, r) != 0:
                continue
            # the 6 projective points of span{p,r}
            members = set()
            for a in range(q):
                v = tuple((a * p[k] + r[k]) % q for k in range(4))
                # canonicalize
                for c in v:
                    if c != 0:
                        lead = c
                        break
                inv = pow(lead, q - 2, q)
                members.add(tuple((inv * c) % q for c in v))
            members.add(p)
            key = tuple(sorted(idx[m] for m in members))
            assert len(key) == 6
            lines[key] = True
    lines = sorted(lines.keys())
    assert len(lines) == 156, f"expected 156 t.i. lines, got {len(lines)}"
    edges = []
    for li, key in enumerate(lines):
        for pi in key:
            edges.append((pi, 156 + li))
    return 312, edges, set(range(156))

# ---------------------------------------------------------------- graph utils
def mkadj(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    return adj

def connected(n, adj, vs=None):
    vs = set(range(n)) if vs is None else set(vs)
    start = next(iter(vs))
    seen = {start}; dq = deque([start])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y in vs and y not in seen:
                seen.add(y); dq.append(y)
    return len(seen) == len(vs)

def girth(n, adj):
    best = 10**9
    for s in range(n):
        dist = {s: 0}; par = {s: -1}; dq = deque([s])
        while dq:
            x = dq.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; par[y] = x; dq.append(y)
                elif par[x] != y:
                    best = min(best, dist[x] + dist[y] + 1)
        if best == 3:
            break
    return best

def bfs_dist(n, adj, srcs):
    dist = [-1] * n
    dq = deque()
    for s in srcs:
        dist[s] = 0; dq.append(s)
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1; dq.append(y)
    return dist

# ---------------------------------------------------------------- instance
def build_instance(bulk, seed, spread_min=5, prof='p2'):
    rng = random.Random(seed)
    if bulk == 'pg':
        nb, bedges, side1 = build_pg25()
    else:
        nb, bedges, side1 = build_gq55()
    adj = mkadj(nb, bedges)
    g = girth(nb, adj)
    ndel = 7 if prof == 'p2' else 10      # f3 profile: 17 pads + 3 bulk stubs
    # --- choose ndel deleted bulk edges, endpoints pairwise far apart
    edges_set = set(map(tuple, map(sorted, bedges)))
    del_edges = []
    forbidden_near = set()
    order = sorted(edges_set); rng.shuffle(order)
    for (a, b) in order:
        if len(del_edges) == ndel:
            break
        if a in forbidden_near or b in forbidden_near:
            continue
        # tentative delete, check bulk stays connected
        adj[a].discard(b); adj[b].discard(a)
        if not connected(nb, adj):
            adj[a].add(b); adj[b].add(a)
            continue
        del_edges.append((a, b))
        d = bfs_dist(nb, adj, [a, b])
        for v in range(nb):
            if 0 <= d[v] < spread_min:
                forbidden_near.add(v)
    if len(del_edges) != ndel:
        raise RuntimeError(f"could not place {ndel} spread deleted edges")
    slots1 = [v for e in del_edges for v in e if v in side1]      # side-1 capacity
    slots2 = [v for e in del_edges for v in e if v not in side1]  # side-2 capacity
    assert len(slots1) == ndel and len(slots2) == ndel
    rng.shuffle(slots1); rng.shuffle(slots2)
    # --- gadget vertices
    A, B, U, T, V, W = nb, nb + 1, nb + 2, nb + 3, nb + 4, nb + 5
    n = nb + 6
    gedges = [(A, B), (A, U), (B, U), (A, T), (B, T), (U, V), (V, W), (T, W)]
    # pad side rule for phi0=(side1->1, side2->2, A=1,B=2,U=3,T=3,V=1,W=2):
    #   A(col1): pads -> side2 ; B(col2) -> side1 ; V(col1) -> side2 ;
    #   W(col2) -> side1 ; U,T (col3) -> anywhere.
    pads = []
    if prof == 'p2':   # all six gadget vertices deficient (b=1 each); 14 pads
        for gv, k, pool in ((A, 2, slots2), (V, 3, slots2),
                            (B, 2, slots1), (W, 3, slots1)):
            for _ in range(k):
                pads.append((gv, pool.pop()))
        left = slots1 + slots2
        assert len(left) == 4
        pads.append((U, left[0])); pads.append((U, left[1]))
        pads.append((T, left[2])); pads.append((T, left[3]))
        stub_bulk = []
    else:              # 'f3': A,B,T full; 17 pads; 3 leftover bulk stubs
        for gv, k, pool in ((A, 3, slots2), (V, 3, slots2),
                            (B, 3, slots1), (W, 3, slots1)):
            for _ in range(k):
                pads.append((gv, pool.pop()))
        left = slots1 + slots2          # 8 remaining capacity slots
        rng.shuffle(left)
        for gv, k in ((U, 2), (T, 3)):
            for _ in range(k):
                pads.append((gv, left.pop()))
        stub_bulk = left                # 3 leftover capacity-1 = bulk stubs
        assert len(stub_bulk) == 3
    all_edges = []
    for a in range(nb):
        for b in adj[a]:
            if a < b:
                all_edges.append((a, b))
    all_edges += gedges + pads
    fadj = mkadj(n, all_edges)
    expected_deficient = sorted([U, V, W] + ([A, B, T] if prof == 'p2' else stub_bulk))
    inst = dict(bulk=bulk, seed=seed, n=n, nb=nb, girth_bulk=g, prof=prof,
                edges=sorted(map(tuple, map(sorted, all_edges))),
                gadget=dict(A=A, B=B, U=U, T=T, V=V, W=W),
                z=[U, V, W], del_edges=del_edges, pads=pads,
                deficient=expected_deficient,
                side1=sorted(side1))
    return inst, fadj

def validate(inst, adj):
    n = inst['n']
    deg = [len(adj[v]) for v in range(n)]
    assert max(deg) <= 6, "Delta > 6"
    defic = sum(6 - d for d in deg)
    assert defic == 6, f"deficiency {defic} != 6"
    dV = sorted(v for v in range(n) if deg[v] < 6)
    gd = inst['gadget']
    assert dV == inst['deficient'], f"deficient set {dV} != expected"
    assert connected(n, adj)
    U, W = gd['U'], gd['W']
    assert W not in adj[U], "z1,z3 must be non-adjacent (non-triangle)"
    # phi0 explicit colouring check
    side1 = set(inst['side1'])
    phi0 = {}
    for v in range(inst['nb']):
        phi0[v] = 1 if v in side1 else 2
    phi0[gd['A']] = 1; phi0[gd['B']] = 2; phi0[gd['U']] = 3
    phi0[gd['T']] = 3; phi0[gd['V']] = 1; phi0[gd['W']] = 2
    for a, b in inst['edges']:
        assert phi0[a] != phi0[b], f"phi0 conflict on edge {(a,b)}"
    return phi0

# ---------------------------------------------------------------- CP-SAT
def base_model(n, edges, exclude=None):
    m = cp_model.CpModel()
    x = [m.new_int_var(0, 2, f"x{v}") for v in range(n)]
    for a, b in edges:
        if exclude is not None and (a == exclude or b == exclude):
            continue
        m.add(x[a] != x[b])
    return m, x

def solve(m, workers=16):
    s = cp_model.CpSolver()
    s.parameters.num_search_workers = workers
    return s, s.solve(m)

def check_rigidity(inst):
    n, edges = inst['n'], inst['edges']
    gd = inst['gadget']
    m, x = base_model(n, edges)
    s, r = solve(m)
    assert r == cp_model.FEASIBLE or r == cp_model.OPTIMAL, "K not 3-colourable!"
    m2, x2 = base_model(n, edges)
    m2.add(x2[gd['U']] == x2[gd['W']])
    s2, r2 = solve(m2)
    return r2 == cp_model.INFEASIBLE

def frozen_check(inst, adj, v):
    """Returns (frozen?, witness or None)."""
    n, edges = inst['n'], inst['edges']
    m, x = base_model(n, edges, exclude=v)
    for c in range(3):
        bs = []
        for y in adj[v]:
            b = m.new_bool_var(f"b{y}_{c}")
            m.add(x[y] == c).only_enforce_if(b)
            m.add(x[y] != c).only_enforce_if(b.Not())
            bs.append(b)
        m.add(sum(bs) <= 2)
    s, r = solve(m, workers=8)
    if r == cp_model.INFEASIBLE:
        return True, None
    assert r in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    wit = [int(s.value(x[u])) for u in range(n)]
    wit[v] = -1
    return False, wit

# ---------------------------------------------------------------- main
def main():
    bulk = sys.argv[1] if len(sys.argv) > 1 else 'gq'
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    spread = int(sys.argv[3]) if len(sys.argv) > 3 else (5 if bulk == 'gq' else 2)
    prof = sys.argv[4] if len(sys.argv) > 4 else 'p2'
    inst, adj = build_instance(bulk, seed, spread, prof)
    phi0 = validate(inst, adj)
    print(f"[{bulk} seed={seed}] n={inst['n']} bulk_girth={inst['girth_bulk']} "
          f"valid: Delta<=6, Sum b=6 (all on gadget), connected, phi0 OK", flush=True)
    rig = check_rigidity(inst)
    print(f"[{bulk} seed={seed}] rainbow-rigid (CP-SAT merge UW infeasible): {rig}", flush=True)
    if not rig:
        print("NOT rainbow-rigid — instance useless"); return
    fulls = [v for v in range(inst['n']) if len(adj[v]) == 6]
    print(f"[{bulk} seed={seed}] full vertices: {len(fulls)}; frozen census ...", flush=True)
    frozen, witnesses = [], {}
    for i, v in enumerate(fulls):
        fr, wit = frozen_check(inst, adj, v)
        if fr:
            frozen.append(v)
        else:
            witnesses[v] = wit
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(fulls)} done, frozen so far: {len(frozen)}", flush=True)
    print(f"[{bulk} seed={seed}] FROZEN COUNT = {len(frozen)} of {len(fulls)} "
          f"{'-> (R3prime) REFUTED by this instance' if not frozen else f'frozen at {frozen}'}",
          flush=True)
    out = dict(inst=inst, frozen=frozen, witnesses=witnesses, rigid=bool(rig))
    fn = (f"E:/Projects/ErdosProblems/problems/944/experiments/sixreg/r3c/"
          f"inst_{bulk}_s{seed}{'' if prof == 'p2' else '_' + prof}.json")
    with open(fn, "w") as f:
        json.dump(out, f)
    print(f"written {fn}", flush=True)

if __name__ == "__main__":
    main()
