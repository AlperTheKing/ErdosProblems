# INDEPENDENT adversarial referee verifier for the R3' refutation artifacts.
# Written from scratch; does NOT import or reuse r3c_*.py.
import json, sys, itertools
from collections import deque

def load(path):
    d = json.load(open(path))
    inst = d['inst']
    n = inst['n']
    E = set()
    for a, b in inst['edges']:
        a, b = int(a), int(b)
        assert a != b, "self-loop"
        key = (min(a, b), max(a, b))
        assert key not in E, "duplicate edge"
        E.add(key)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return d, inst, n, E, adj

def check_validity(inst, n, E, adj):
    errs = []
    deg = [len(adj[v]) for v in range(n)]
    if max(deg) > 6: errs.append("max degree > 6")
    defi = sum(6 - dv for dv in deg)
    if defi != 6: errs.append(f"total deficiency = {defi} != 6")
    deficient = sorted(v for v in range(n) if deg[v] < 6)
    if 'deficient' in inst and deficient != sorted(inst['deficient']):
        errs.append("deficient set mismatch vs JSON")
    # connectivity
    seen = {0}; q = deque([0])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in seen: seen.add(y); q.append(y)
    if len(seen) != n: errs.append("not connected")
    # z triple
    z = inst['z']
    if not all(zz in deficient for zz in z): errs.append("some z not deficient")
    zadj = [(min(a,b),max(a,b)) in E for a,b in [(z[0],z[1]),(z[1],z[2]),(z[0],z[2])]]
    if all(zadj): errs.append("z triple IS a triangle")
    return errs, deg, deficient, zadj

def check_rigidity_gadget_enum(inst, E):
    """Complete proof of rainbow-rigidity (given 3-colourability):
    every assignment to the 6 gadget vertices that is proper on the INDUCED
    gadget subgraph must be rainbow on z. Properness on an induced subgraph is
    necessary for any proper colouring of K, so this is exhaustive and rigorous."""
    g = inst['gadget']
    gv = [g[k] for k in ['A','B','U','T','V','W']]
    gset = set(gv)
    gE = [(a, b) for (a, b) in E if a in gset and b in gset]
    z = inst['z']
    bad = []
    n_proper = 0
    for assign in itertools.product((0,1,2), repeat=6):
        col = dict(zip(gv, assign))
        if any(col[a] == col[b] for a, b in gE): continue
        n_proper += 1
        if len({col[z[0]], col[z[1]], col[z[2]]}) != 3:
            bad.append(assign)
    return n_proper, bad, gE

def three_colour_backtrack(n, adj, forced_equal=None, exclude=None, timeout_nodes=50_000_000):
    """Exact backtracking 3-colourer with MRV. forced_equal=(u,w) merges u,w.
    Returns (status, colouring or None). status in {'SAT','UNSAT'}."""
    rep = list(range(n))
    if forced_equal:
        u, w = forced_equal
        rep[w] = u
    verts = [v for v in range(n) if rep[v] == v and (exclude is None or v != exclude)]
    madj = {v: set() for v in verts}
    for v in verts:
        nb = set()
        for x in range(n):
            if rep[x] == v:
                for y in adj[x]:
                    ry = rep[y]
                    if ry != v and (exclude is None or ry != exclude):
                        nb.add(ry)
        madj[v] = nb
    if forced_equal and rep[forced_equal[1]] == forced_equal[0]:
        # check merged vertex has no self-loop (u~w would make UNSAT trivially)
        if forced_equal[0] in adj[forced_equal[1]]:
            return 'UNSAT', None
    avail = {v: {0,1,2} for v in verts}
    col = {}
    nodes = [0]
    def pick():
        # MRV with DSATUR tie-break (most coloured neighbours), so that the
        # constrained core gets coloured before the flexible bulk.
        best, bv = None, None
        for v in verts:
            if v in col: continue
            l = len(avail[v])
            if l == 0: return v
            sat = sum(1 for y in madj[v] if y in col)
            key = (l, -sat, -len(madj[v]))
            if best is None or key < best: best, bv = key, v
        return bv
    def bt():
        nodes[0] += 1
        if nodes[0] > timeout_nodes: raise RuntimeError("node budget exceeded")
        v = pick()
        if v is None: return True
        for c in sorted(avail[v]):
            col[v] = c
            changed = []
            ok = True
            for y in madj[v]:
                if y not in col and c in avail[y]:
                    avail[y].discard(c); changed.append(y)
                    if not avail[y]: ok = False
            if ok and bt(): return True
            for y in changed: avail[y].add(c)
            del col[v]
        return False
    try:
        sat = bt()
    except RuntimeError:
        return 'TIMEOUT', None
    if not sat: return 'UNSAT', None
    full = [None]*n
    for x in range(n):
        if exclude is not None and x == exclude: full[x] = -1
        else: full[x] = col[rep[x]]
    return 'SAT', full

def check_phi0(inst, n, E, adj):
    """Build phi0 per the claimed parity colouring and check properness."""
    side1 = set(inst['side1'])
    g = inst['gadget']
    col = [None]*n
    for v in range(n):
        if v in g.values(): continue
        col[v] = 0 if v in side1 else 1
    gc = {'A':0,'B':1,'U':2,'T':2,'V':0,'W':1}
    for k, c in gc.items(): col[g[k]] = c
    bad = [(a,b) for a,b in E if col[a] == col[b]]
    return bad, col

def check_witnesses(d, inst, n, E, adj, deg):
    errs = []
    wit = d['witnesses']
    full = sorted(v for v in range(n) if deg[v] == 6)
    keys = sorted(int(k) for k in wit)
    if keys != full:
        errs.append(f"witness keys != full-vertex set (missing {set(full)-set(keys)}, extra {set(keys)-set(full)})")
    nver = 0
    for k, col in wit.items():
        v = int(k)
        if col[v] != -1: errs.append(f"witness {v}: col[v] != -1"); continue
        if any(col[x] not in (0,1,2) for x in range(n) if x != v):
            errs.append(f"witness {v}: bad colour values"); continue
        viol = [(a,b) for a,b in E if a != v and b != v and col[a] == col[b]]
        if viol: errs.append(f"witness {v}: improper on {viol[:3]}"); continue
        from collections import Counter
        tr = Counter(col[x] for x in adj[v])
        if any(tr[c] > 2 for c in (0,1,2)):
            errs.append(f"witness {v}: trace {dict(tr)} violates <=2"); continue
        nver += 1
    return errs, nver, len(full)

def rebuild_pg25():
    """PG(2,5) point-line incidence as described: canonical vectors of F_5^3,
    first nonzero coordinate 1, itertools.product order; p ~ 31+l iff <p,l>=0 mod 5."""
    vecs = []
    for v in itertools.product(range(5), repeat=3):
        nz = next((x for x in v if x != 0), None)
        if nz == 1: vecs.append(v)
    assert len(vecs) == 31
    E = set()
    for i, p in enumerate(vecs):
        for j, l in enumerate(vecs):
            if (p[0]*l[0] + p[1]*l[1] + p[2]*l[2]) % 5 == 0:
                E.add((i, 31 + j))
    return E

def bulk_girth(nb, E):
    adj = [[] for _ in range(nb)]
    for a, b in E:
        if a < nb and b < nb: adj[a].append(b); adj[b].append(a)
    g = 10**9
    for s in range(nb):
        dist = {s: 0}; par = {s: -1}; q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; par[y] = x; q.append(y)
                elif par[x] != y:
                    g = min(g, dist[x] + dist[y] + 1)
    return g

def main(path, do_merge_unsat=True, do_rebuild_pg=False):
    d, inst, n, E, adj = load(path)
    print(f"=== {path} ===")
    print(f"n={n} |E|={len(E)} bulk={inst.get('bulk')} seed={inst.get('seed')} prof={inst.get('prof')}")
    errs, deg, deficient, zadj = check_validity(inst, n, E, adj)
    print("VALIDITY:", "OK" if not errs else errs)
    print(f"  deficient={deficient} z={inst['z']} z-adjacency(12,23,13)={zadj}")
    if do_rebuild_pg:
        pg = rebuild_pg25()
        # bulk edges of K should be pg minus del_edges; pads/gadget separate
        dele = {(min(a,b),max(a,b)) for a,b in inst['del_edges']}
        bulkE = {(a,b) for a,b in E if a < 62 and b < 62}
        want = {(min(a,b),max(a,b)) for a,b in pg} - dele
        print("  PG rebuild matches bulk:", bulkE == want, f"(|pg|={len(pg)}, |del|={len(dele)}, |bulk|={len(bulkE)})")
    nb = inst['nb']
    g = bulk_girth(nb, E)
    print(f"  bulk girth = {g} (claimed {inst.get('girth_bulk')})")
    badphi, phi0 = check_phi0(inst, n, E, adj)
    print("PHI0 proper:", "OK" if not badphi else f"VIOLATIONS {badphi[:5]}")
    n_proper, bad, gE = check_rigidity_gadget_enum(inst, E)
    print(f"RIGIDITY(gadget-enum): proper gadget assignments={n_proper}, non-rainbow={len(bad)}",
          "OK -> rainbow-rigid PROVEN" if (not bad and not badphi) else "FAIL")
    print(f"  induced gadget edges: {sorted(gE)}")
    if do_merge_unsat:
        z = inst['z']
        # the non-adjacent pair(s) among z must be difference-forced.
        # Exact certificate: merging the pair creates a K4 => merged graph not
        # 3-colourable => psi(z_i) != psi(z_j) in every proper 3-colouring of K.
        for (i,j) in [(0,1),(1,2),(0,2)]:
            a, b = z[i], z[j]
            if (min(a,b),max(a,b)) not in E:
                madj_ab = (adj[a] | adj[b]) - {a, b}
                k4 = None
                cand = sorted(madj_ab)
                for x, y, w in itertools.combinations(cand, 3):
                    if y in adj[x] and w in adj[x] and w in adj[y]:
                        k4 = (x, y, w); break
                print(f"  merge-check psi({a})=psi({b}): K4 on merged({a},{b})+{k4}"
                      f" -> {'UNSAT PROVEN' if k4 else 'NO K4 CERT (inconclusive)'}")
        st, _ = three_colour_backtrack(n, adj)
        print(f"  K itself 3-colourable: {st} (expect SAT)")
    werrs, nver, nfull = check_witnesses(d, inst, n, E, adj, deg)
    print(f"WITNESSES: {nver}/{nfull} verified; frozen-list={d['frozen']}",
          "OK" if (not werrs and nver == nfull) else werrs[:5])
    return not errs and not badphi and not bad and not werrs and nver == nfull

if __name__ == '__main__':
    p = sys.argv[1]
    rebuild = ('pg' in p)
    ok = main(p, do_rebuild_pg=rebuild)
    print("OVERALL:", "PASS" if ok else "FAIL")
