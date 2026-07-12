#!/usr/bin/env python3
"""VERIFY_2 script B: independent recomputation of every fixture-level number in the
AGENT-HOMOLOGY report (Claims 4, 5; Claim 2 empirical gate of R50's 3t-1; survival
matrix items). Written from scratch; only conventions mirrored where needed for
number comparability. graph6 decoding, matching, rank computations all reimplemented.

Fixtures: #298 Q??????wE_[?EGs?D_@A?C_B???  /  #264 Q??????wE_Bws?s?DCD??@?@???
Model (writeup R49/R50 + generator conventions):
  support F* = the 18-vtx 24-edge graph; atoms = same-shore pairs at F*-distance
  exactly 4; complete row family = ALL 4-paths between the pair (stored (u..w), u<w);
  circuit = 25 atoms, root (2,3), owners 0/1 bad-degree 5, bad-graph triangle-free,
  every edge in >=2 complete footprints, deletion-SDR (every 24-subset has a perfect
  matching onto the 24 edges through complete footprints), Forced=Inc exclusion.
"""
import random
from fractions import Fraction
from itertools import combinations, product
from collections import defaultdict, deque

FIX = {
    '298': 'Q??????wE_[?EGs?D_@A?C_B???',
    '264': 'Q??????wE_Bws?s?DCD??@?@???',
}
T = 5

# ---------- graph6 (independent implementation) ----------
def g6(s):
    vals = [ord(c) - 63 for c in s]
    assert all(0 <= v < 64 for v in vals)
    n = vals[0]
    bitstr = ''.join(format(v, '06b') for v in vals[1:])
    edges = set()
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bitstr[k] == '1':
                edges.add(frozenset((i, j)))
            k += 1
    return n, edges

def build_fixture(tag):
    n, edges = g6(FIX[tag])
    adj = defaultdict(set)
    for e in edges:
        u, w = tuple(e)
        adj[u].add(w); adj[w].add(u)
    # bipartition
    col = {}
    for s in range(n):
        if s in col or not adj[s]:
            continue
        col[s] = 0
        dq = deque([s])
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if w not in col:
                    col[w] = 1 - col[u]
                    dq.append(w)
                else:
                    assert col[w] != col[u], "not bipartite"
    # distances
    def bfs(u):
        d = {u: 0}
        dq = deque([u])
        while dq:
            a = dq.popleft()
            for b in adj[a]:
                if b not in d:
                    d[b] = d[a] + 1
                    dq.append(b)
        return d
    dist = {u: bfs(u) for u in range(n)}
    cand = [(u, w) for u, w in combinations(range(n), 2)
            if col.get(u) == col.get(w) and dist[u].get(w) == 4]
    # all 4-paths u->w (my own DFS)
    def paths4(u, w):
        out = []
        for p1 in adj[u]:
            if p1 == w:
                continue
            for p2 in adj[p1]:
                if p2 in (u, w, p1):
                    continue
                for p3 in adj[p2]:
                    if p3 in (u, w, p1, p2):
                        continue
                    if w in adj[p3]:
                        out.append((u, p1, p2, p3, w))
        return sorted(set(out))
    rows = {a: paths4(*a) for a in cand}
    uni = {frozenset((r[i], r[i + 1])) for rr in rows.values() for r in rr for i in range(4)}
    foot = {a: {frozenset((r[i], r[i + 1])) for r in rows[a] for i in range(4)} for a in cand}
    forced = {}
    for a in cand:
        f = None
        for r in rows[a]:
            es = {frozenset((r[i], r[i + 1])) for i in range(4)}
            f = es if f is None else f & es
        forced[a] = f
    return dict(tag=tag, n=n, edges=edges, adj=adj, col=col, cand=cand, rows=rows,
                foot=foot, forced=forced, union=uni)

# ---------- bipartite matching ----------
def match_size(footlist, edge_index):
    matchR = {}
    def aug(i, seen):
        for e in footlist[i]:
            ei = edge_index[e]
            if ei in seen:
                continue
            seen.add(ei)
            if ei not in matchR or aug(matchR[ei], seen):
                matchR[ei] = i
                return True
        return False
    sz = 0
    for i in range(len(footlist)):
        if aug(i, set()):
            sz += 1
    return sz

# ---------- circuit search (my own) ----------
def find_circuits(fx, excl_owners=(0, 1), cap=100):
    cand = fx['cand']
    edge_list = sorted(tuple(sorted(e)) for e in fx['edges'])
    eidx = {frozenset(e): i for i, e in enumerate(edge_list)}
    usable = []
    for a in cand:
        bad = False
        for o in excl_owners:
            if o not in a and all(o in r for r in fx['rows'][a]):
                bad = True
        if not bad:
            usable.append(a)
    root = (2, 3)
    if root not in usable:
        return [], len(usable)
    rest = [a for a in usable if a != root]
    res = []
    K = len(rest)
    degM = defaultdict(int)
    badadj = defaultdict(set)
    ecnt = [0] * 24
    chosen = [root]
    degM[2] += 1; degM[3] += 1
    badadj[2].add(3); badadj[3].add(2)
    for e in fx['foot'][root]:
        ecnt[eidx[e]] += 1

    def full_check():
        if degM[0] != 5 or degM[1] != 5:
            return False
        if any(c < 2 for c in ecnt):
            return False
        fl = [fx['foot'][a] for a in chosen]
        if match_size(fl, eidx) != 24:
            return False
        for k in range(25):
            if match_size(fl[:k] + fl[k + 1:], eidx) != 24:
                return False
        return True

    def rec(start, left):
        if len(res) >= cap:
            return
        if left == 0:
            if full_check():
                res.append(sorted(chosen))
            return
        if K - start < left or degM[0] > 5 or degM[1] > 5:
            return
        for i in range(start, K):
            if len(res) >= cap:
                return
            a = rest[i]
            u, w = a
            if badadj[u] & badadj[w]:
                continue
            chosen.append(a)
            degM[u] += 1; degM[w] += 1
            badadj[u].add(w); badadj[w].add(u)
            for e in fx['foot'][a]:
                ecnt[eidx[e]] += 1
            rec(i + 1, left - 1)
            chosen.pop()
            degM[u] -= 1; degM[w] -= 1
            badadj[u].discard(w); badadj[w].discard(u)
            for e in fx['foot'][a]:
                ecnt[eidx[e]] -= 1
    rec(0, 24)
    return res, len(usable)

# ---------- swap squares + ranks ----------
def swap_squares(fx, circ, positions):
    sqs = set()
    for a in circ:
        fam = fx['rows'][a]
        for r1, r2 in combinations(fam, 2):
            diff = [p for p in range(5) if r1[p] != r2[p]]
            if len(diff) == 1 and diff[0] in positions:
                p = diff[0]
                mid = tuple(sorted((r1[p], r2[p])))
                fl = tuple(sorted((r1[p - 1], r1[p + 1])))
                sqs.add((fl[0], mid[0], fl[1], mid[1]))
    return sorted(sqs)

def all_swap_cells(fx):
    """every same-shore pair with >=2 common nbrs, one cell per flank pair (their
    all_squares convention: both diagonals generate cells)."""
    out = []
    for u, w in combinations(range(fx['n']), 2):
        if fx['col'].get(u) != fx['col'].get(w):
            continue
        cn = sorted(fx['adj'][u] & fx['adj'][w])
        for c1, c2 in combinations(cn, 2):
            out.append((c1, u, c2, w))
    return out

def boundary_rows(fx, sqs):
    edge_list = sorted(tuple(sorted(e)) for e in fx['edges'])
    eidx = {e: i for i, e in enumerate(edge_list)}
    rows = []
    for (c1, u, c2, w) in sqs:
        v = [0] * len(edge_list)
        v[eidx[tuple(sorted((c1, u)))]] += 1
        v[eidx[tuple(sorted((u, c2)))]] += 1
        v[eidx[tuple(sorted((c2, w)))]] -= 1
        v[eidx[tuple(sorted((w, c1)))]] -= 1
        rows.append(v)
    return rows

def rankQ(mat):
    m = [[Fraction(x) for x in r] for r in mat]
    if not m:
        return 0
    rows, cols = len(m), len(m[0])
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        m[r] = [x / m[r][c] for x in m[r]]
        for i in range(rows):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
        if r == rows:
            break
    return r

def rankF2(mat):
    vs = []
    for r in mat:
        x = 0
        for i, val in enumerate(r):
            if val % 2:
                x |= 1 << i
        vs.append(x)
    r = 0
    for c in range(max((len(row) for row in mat), default=0)):
        piv = next((i for i in range(r, len(vs)) if (vs[i] >> c) & 1), None)
        if piv is None:
            continue
        vs[r], vs[piv] = vs[piv], vs[r]
        for i in range(len(vs)):
            if i != r and (vs[i] >> c) & 1:
                vs[i] ^= vs[r]
        r += 1
    return r

# ---------- pinned edges / owner arcs ----------
def pinned(fx, circ):
    pin = set()
    for a in circ:
        pin |= fx['forced'][a]
    return pin

def owner_arcs(fx, circ, positions=(1, 2, 3)):
    dM = defaultdict(int)
    for u, w in circ:
        dM[u] += 1; dM[w] += 1
    OWN = {u for u in range(fx['n']) if len(fx['adj'][u]) == T and dM[u] == T}
    out = []
    for a in circ:
        fam = fx['rows'][a]
        for i, r1 in enumerate(fam):
            for j, r2 in enumerate(fam):
                if i == j:
                    continue
                diff = [p for p in range(5) if r1[p] != r2[p]]
                if len(diff) == 1 and diff[0] in positions:
                    p = diff[0]
                    if r1[p] in OWN and r2[p] in OWN:
                        out.append((a, i, j, r1[p], r2[p], r1[p - 1], r1[p + 1], p))
    return out, OWN

# ---------- rotor cores + blockade ----------
def rotor_cores(fx, chosen):
    cores = []
    for u, w in combinations(range(fx['n']), 2):
        if fx['col'].get(u) != fx['col'].get(w):
            continue
        cn = sorted(fx['adj'][u] & fx['adj'][w])
        for c1, c2 in combinations(cn, 2):
            sA = []
            for a1 in fx['adj'][c1] - {u, w}:
                for b1 in fx['adj'][c2] - {u, w}:
                    if a1 == b1:
                        continue
                    key = (min(a1, b1), max(a1, b1))
                    if key in chosen and (a1, c1, u, c2, b1) in fx['rows'].get(key, []) \
                            and (a1, c1, w, c2, b1) in fx['rows'].get(key, []):
                        sA.append(key)
            sB = []
            for p1 in fx['adj'][u] - {c1, c2}:
                for q1 in fx['adj'][w] - {c1, c2}:
                    if p1 == q1:
                        continue
                    key = (min(p1, q1), max(p1, q1))
                    if key in chosen and (p1, u, c1, w, q1) in fx['rows'].get(key, []) \
                            and (p1, u, c2, w, q1) in fx['rows'].get(key, []):
                        sB.append(key)
            if sA and sB:
                cores.append(((u, c1, w, c2), sorted(set(sA)), sorted(set(sB))))
    return cores

def blockade(fx, chosen, square, core_atoms):
    e_sq = {frozenset((square[0], square[1])), frozenset((square[1], square[2])),
            frozenset((square[2], square[3])), frozenset((square[3], square[0]))}
    blocked = []
    for a in sorted(chosen):
        if a in core_atoms:
            continue
        if not any(all(frozenset((r[i], r[i + 1])) not in e_sq for i in range(4))
                   for r in fx['rows'][a]):
            blocked.append(a)
    return blocked, e_sq

# ---------- tuple sampling: profiles, R50 bound, liveness ----------
def sample_census(fx, circ, n_samples=12000, seed=101, max_exh=120000):
    atoms = sorted(circ)
    fams = [fx['rows'][a] for a in atoms]
    sizes = [len(f) for f in fams]
    total = 1
    for s in sizes:
        total *= s
    dM = defaultdict(int)
    for u, w in atoms:
        dM[u] += 1; dM[w] += 1
    owner_cands = [u for u in range(fx['n']) if len(fx['adj'][u]) == T and dM[u] == T]
    bad_set = [frozenset(a) for a in atoms]
    if total <= max_exh:
        it = product(*[range(s) for s in sizes])
        n_it = total
        mode = f'EXHAUSTIVE({total})'
    else:
        rng = random.Random(seed)
        it = (tuple(rng.randrange(s) for s in sizes) for _ in range(n_samples))
        n_it = n_samples
        mode = f'SAMPLED({n_samples} of {total})'
    stats = defaultdict(int)
    r50_viol = []
    live_examples = []
    for om in it:
        sel = [fams[i][om[i]] for i in range(len(atoms))]
        S = set()
        rcount = defaultdict(int)
        for r in sel:
            for i in range(4):
                S.add(frozenset((r[i], r[i + 1])))
            for u in set(r):
                rcount[u] += 1
        selverts = {u for r in sel for u in r}
        # active graph (intrinsic: F* edges off S with selected endpoints)
        act = [e for e in fx['edges'] if e not in S and all(u in selverts for u in e)]
        cadj = defaultdict(set)
        for e in act:
            u, w = tuple(e)
            cadj[u].add(w); cadj[w].add(u)
        comp = {}
        for s0 in cadj:
            if s0 in comp:
                continue
            comp[s0] = s0
            dq = deque([s0])
            while dq:
                u = dq.popleft()
                for w in cadj[u]:
                    if w not in comp:
                        comp[w] = s0
                        dq.append(w)
        active_comps = {comp[u] for e in bad_set for u, w in [tuple(e)]
                        if u in comp and w in comp and comp[u] == comp[w]}
        # profiles at owner candidates
        for v in owner_cands:
            if rcount[v] != T:
                continue
            lat = [e for e in fx['edges'] if v in e and e not in S]
            if len(lat) != 1:
                continue
            x0 = next(iter(lat[0] - {v}))
            star = [w for w in fx['adj'][v] if w != x0]
            # lean coverage: co-occurrence in a selected row
            cov_lean = all(any(x0 in r and w in r for r in sel) for w in star)
            # strict coverage: v-avoiding row with x0,w at position distance 2
            def cov2(w):
                for r in sel:
                    if v in r:
                        continue
                    if x0 in r and w in r and abs(r.index(x0) - r.index(w)) == 2:
                        return True
                return False
            cov_strict = all(cov2(w) for w in star)
            if cov_lean:
                stats['profile_lean'] += 1
            if cov_strict:
                stats['profile_strict'] += 1
            if cov_lean or cov_strict:
                # R50 empirical gate: |S| >= 3t-1 = 14, |L| <= t(t-3) = 10
                nS = len(S)
                nL = 24 - nS
                if nS < 3 * T - 1 or nL > T * (T - 3):
                    r50_viol.append((om, v, nS, nL))
                stats['profile_any'] += 1
                # owner active component size (claim 1 consistency)
                ce = sum(1 for e in act if v in comp and comp.get(tuple(e)[0]) == comp.get(v))
                if v in comp and comp[v] in active_comps:
                    stats['profile_live'] += 1  # would be a live capture (expect 0)
        # liveness on genuine detours (single-position row exchange)
        for i, a in enumerate(atoms):
            fam = fams[i]
            if len(fam) == 1:
                continue
            cur = fam[om[i]]
            for j, alt in enumerate(fam):
                if j == om[i]:
                    continue
                diff = [p for p in range(5) if cur[p] != alt[p]]
                if len(diff) == 1 and diff[0] in (1, 2, 3):
                    stats['L0'] += 1
                    vnew = alt[diff[0]]
                    if vnew in comp and comp[vnew] in active_comps:
                        stats['L1'] += 1
                        if len(live_examples) < 3:
                            live_examples.append((om, a, j))
    return mode, dict(stats), r50_viol, live_examples

# ---------- 18-vtx near-candidate triangle count ----------
def near_candidate_triangles():
    # L = {v,m,a,b0..b4}, R = {x0..x4,y0..y4}
    # blue: v,m -> all x_i; a -> x0..x3; a -> y_j; b_j -> y_j
    # atoms: vb_j, mb_j, b_ib_j, x4y_j
    V, M, A = 'v', 'm', 'a'
    B = [f'b{i}' for i in range(5)]
    X = [f'x{i}' for i in range(5)]
    Y = [f'y{i}' for i in range(5)]
    atoms = set()
    for b in B:
        atoms.add(frozenset((V, b)))
        atoms.add(frozenset((M, b)))
    for b1, b2 in combinations(B, 2):
        atoms.add(frozenset((b1, b2)))
    for y in Y:
        atoms.add(frozenset((X[4], y)))
    assert len(atoms) == 25
    aadj = defaultdict(set)
    for e in atoms:
        u, w = tuple(e)
        aadj[u].add(w); aadj[w].add(u)
    verts = sorted(aadj)
    tri = 0
    for u, w in combinations(verts, 2):
        if w in aadj[u]:
            tri += len([z for z in aadj[u] & aadj[w] if z > max(u, w)])
    return tri

if __name__ == '__main__':
    print(f"18-vtx near-candidate atom-graph triangles: {near_candidate_triangles()} (report: 30)")
    for tag in ('298', '264'):
        fx = build_fixture(tag)
        nL = sum(1 for u in range(fx['n']) if fx['col'].get(u) == 0)
        print(f"\n########## fixture {tag} ##########")
        print(f"n={fx['n']} |E|={len(fx['edges'])} shores {nL}+{fx['n']-nL} "
              f"candidates={len(fx['cand'])} union==edges: {fx['union'] == fx['edges']} "
              f"cycle_rank={len(fx['edges']) - fx['n'] + 1}")
        # blue+bad triangles over ALL candidates
        Gadj = defaultdict(set)
        for e in fx['edges'] | {frozenset(a) for a in fx['cand']}:
            u, w = tuple(e)
            Gadj[u].add(w); Gadj[w].add(u)
        tri = sum(1 for u, w in combinations(range(fx['n']), 2) if w in Gadj[u]
                  for z in Gadj[u] & Gadj[w] if z > w)
        print(f"triangles in blue+ALL-candidate-bad: {tri}")
        strict, n_us_strict = find_circuits(fx, (0, 1), cap=100)
        print(f"STRICT circuits (Forced=Inc excl owners 0,1; usable {n_us_strict}): {len(strict)}")
        circuits = strict
        if not strict:
            relaxed, n_us_rel = find_circuits(fx, (0,), cap=100)
            print(f"RELAXED circuits (excl owner 0 only; usable {n_us_rel}): {len(relaxed)}")
            circuits = relaxed
        all_cells = all_swap_cells(fx)
        for si, circ in enumerate(circuits):
            print(f"--- circuit#{si} ---")
            pin = pinned(fx, circ)
            print(f" pinned edges: {len(pin)}/24 -> {sorted(tuple(sorted(e)) for e in pin)}")
            arcs, OWN = owner_arcs(fx, circ)
            dead = free = 0
            forced_tgt = defaultdict(int)
            for (a, i, j, m, v, x, y, p) in arcs:
                evx, evy = frozenset((v, x)), frozenset((v, y))
                px, py = evx in pin, evy in pin
                if px and py:
                    dead += 1
                elif px or py:
                    forced_tgt[tuple(sorted(evy if px else evx))] += 1
                else:
                    free += 1
            print(f" owners(degB=degM=5)={sorted(OWN)}; owner-swap arcs={len(arcs)}: "
                  f"dead={dead} forced={sum(forced_tgt.values())} free={free} "
                  f"forced-targets={dict(sorted(forced_tgt.items()))}")
            # squares: their convention (pos 1,2,3) and Lean-strict middle-only
            for label, pos in (('pos123', (1, 2, 3)), ('middle-only', (2,))):
                sq = swap_squares(fx, circ, pos)
                mat = boundary_rows(fx, sq)
                rq = rankQ(mat)
                r2 = rankF2(mat)
                evenF2 = all(sum(row[k] for row in mat) % 2 == 0
                             for k in range(24)) if mat else True
                print(f" swap squares [{label}]: n={len(sq)} rankQ={rq} kerQ={len(sq)-rq} "
                      f"rankF2={r2} kerF2={len(sq)-r2} edges-covered-evenly-mod2={evenF2}")
            cores = rotor_cores(fx, set(circ))
            print(f" rotor-core squares: {len(cores)}")
            for (sq, sA, sB) in cores:
                for AB in sA:
                    for PQ in sB:
                        blk, e_sq = blockade(fx, set(circ), sq, {AB, PQ})
                        rowsused = {a: [(r, sorted(tuple(sorted((r[i], r[i+1])))
                                        for i in range(4) if frozenset((r[i], r[i+1])) in e_sq))
                                        for r in fx['rows'][a]] for a in blk}
                        print(f"   sq={sq} AB={AB} PQ={PQ} blocked={blk} "
                              f"rows/edges={rowsused}")
            # capture feasibility per arc (graph level)
            dMc = defaultdict(int)
            badnb = defaultdict(set)
            for u, w in circ:
                dMc[u] += 1; dMc[w] += 1
                badnb[u].add(w); badnb[w].add(u)
            n_feas = 0
            for (a, i, j, m, v, x, y, p) in arcs:
                feas = False
                for nb in (x, y):
                    seen = {v, nb}
                    dq = deque([nb])
                    dist = {nb: 0}
                    while dq:
                        u0 = dq.popleft()
                        for w0 in fx['adj'][u0]:
                            if w0 == v or w0 in dist:
                                continue
                            dist[w0] = dist[u0] + 1
                            dq.append(w0)
                    if any(b in dist and dist[b] >= 3 for b in badnb[v]):
                        feas = True
                    if any(v not in (c, d) and c in dist and d in dist for (c, d) in circ):
                        feas = True
                if feas:
                    n_feas += 1
            common01 = sorted(badnb[0] & badnb[1])
            print(f" arcs graph-level capture-feasible: {n_feas}/{len(arcs)}; "
                  f"owners 0,1 common bad nbrs: {common01}")
            # sampled census: profiles + R50 gate + liveness
            mode, stats, r50v, lex = sample_census(fx, circ)
            print(f" census {mode}: {stats}")
            print(f" R50 gate |S|>=14 & |L|<=10 on every profile state: "
                  f"violations={len(r50v)} {r50v[:3]}")
            if lex:
                print(f" LIVE EXAMPLES (unexpected): {lex}")
