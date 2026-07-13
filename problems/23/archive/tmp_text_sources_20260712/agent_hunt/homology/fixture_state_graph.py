#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 2: exact reconstruction + state-graph/liveness census of the two
Codex t=5 falsifier circuits (#298 and #264, 18-vtx rooted supports, graph6 from R49/R50).

Reconstruction rule (matches tmp/fanout/r51_independent_t5_verifier/independent_t5_cnf.py):
  support graph F* = the graph6 graph (bipartite, 24 edges);
  atoms = same-shore pairs at F*-distance EXACTLY 4 (d2-composition minus d2);
  complete row DB per atom = ALL 4-paths in F* between its endpoints;
  full graph G = F* (blue) + atoms (bad).

Census layers per genuine one-middle detour (row -> row', in-DB, same atom):
  L0: genuine detour (DB member, differs at exactly one interior position).
  L1: L0 + entering vertex lies in an ACTIVE component (off-support blue component,
      within selected vertices, containing both endpoints of some bad edge) [r39 semantics].
  L2: L1 + entering vertex owns off-diagonal collision excess (some co-occurrence pair
      count n(v,w) >= 2, w != v).
  L3: L2 + entering vertex has the t=5 equality profile at this state: deg_B = deg_M = 5,
      exactly one latent v-edge, r(v) = 5, and all star pairs {x0,y_i} covered by selected
      rows avoiding v.
Also: squares (4-cycles) census in F*; for each square, whether BOTH transposed side atoms
exist (the period-4 balanced-rotor core demand); corner owner-eligibility (deg_B=deg_M=5).
Directed-cycle analysis on the multi-row sub-product if feasible.
"""
import sys
from itertools import combinations, product
from collections import defaultdict

T = 5

def g6_decode(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for byte in data[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    edges = set()
    i = 0
    for col in range(1, n):
        for row in range(col):
            if bits[i]:
                edges.add(frozenset((row, col)))
            i += 1
    return n, edges

def bipartition(n, edges):
    adj = defaultdict(set)
    for e in edges:
        u, w = tuple(e)
        adj[u].add(w); adj[w].add(u)
    color = {}
    for s in range(n):
        if s in color or not adj[s]:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in color:
                    color[w] = 1 - color[u]
                    stack.append(w)
                elif color[w] == color[u]:
                    return None, adj
    return color, adj

def all_4paths(adj, s, t):
    out = []
    for w1 in adj[s]:
        for z in adj[w1]:
            if z in (s, t) or z == w1:
                continue
            for w2 in adj[z]:
                if w2 in (s, w1, z):
                    continue
                if t in adj[w2] and t not in (s, w1, z, w2):
                    out.append((s, w1, z, w2, t))
    return sorted(set(out))

def analyze(tag, g6):
    print(f"\n================ fixture {tag} ================")
    n, edges = g6_decode(g6)
    color, adj = bipartition(n, edges)
    assert color is not None, "not bipartite"
    shoreL = sorted(u for u in range(n) if color.get(u, 0) == 0)
    shoreR = sorted(u for u in range(n) if color.get(u, 0) == 1)
    print(f"n={n} |E|={len(edges)} shores {len(shoreL)}+{len(shoreR)}")
    assert len(edges) == 24

    # distances within F*
    import collections
    def bfs(u):
        d = {u: 0}
        q = collections.deque([u])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b not in d:
                    d[b] = d[a] + 1
                    q.append(b)
        return d
    dist = {u: bfs(u) for u in range(n)}
    atoms = []
    for shore in (shoreL, shoreR):
        for u, w in combinations(shore, 2):
            if dist[u].get(w) == 4:
                atoms.append((u, w))
    print(f"atoms (same-shore d4 pairs): {len(atoms)}")
    rows = {a: all_4paths(adj, a[0], a[1]) for a in atoms}
    fam_sizes = sorted(len(r) for r in rows.values())
    print(f"family sizes: {fam_sizes}")
    union = set()
    for rr in rows.values():
        for r in rr:
            for i in range(4):
                union.add(frozenset((r[i], r[i+1])))
    print(f"union of rows = F*: {union == edges}")
    # inclusion-minimality: every support edge is critical for some atom
    crit = True
    for e in edges:
        if not any(all(any(frozenset((r[i], r[i+1])) == e for i in range(4)) for r in rr)
                   for rr in rows.values()):
            crit = False
            break
    print(f"inclusion-minimal (every edge carried by some atom's every row): {crit}")
    # triangle-freeness of G = blue + bad
    bad = set(map(frozenset, atoms))
    G = edges | bad
    Gadj = defaultdict(set)
    for e in G:
        u, w = tuple(e)
        Gadj[u].add(w); Gadj[w].add(u)
    tri = sum(1 for u, w in combinations(range(n), 2)
              if w in Gadj[u] for z in Gadj[u] & Gadj[w] if z > w)
    print(f"triangles in blue+bad: {tri}")
    degB = {u: len(adj[u]) for u in range(n)}
    degM = defaultdict(int)
    for u, w in atoms:
        degM[u] += 1; degM[w] += 1
    owners5 = sorted(u for u in range(n) if degB[u] == T and degM[u] == T)
    print(f"equality-scale vertices (deg_B=deg_M=5): {owners5}")

    # rooted embedding: V,M same shore deg5, common nbrs X,Y, A~X, B~Y, AB atom, rows AXVYB & AXMYB in DB
    embeddings = []
    for Vv, Mm in combinations(range(n), 2):
        if color.get(Vv) != color.get(Mm) or degB[Vv] != T or degB[Mm] != T:
            continue
        common = adj[Vv] & adj[Mm]
        for Xx, Yy in combinations(sorted(common), 2):
            for Aa in adj[Xx] - {Vv, Mm}:
                for Bb in adj[Yy] - {Vv, Mm, Aa}:
                    key = (Aa, Bb) if Aa < Bb else (Bb, Aa)
                    if key in rows:
                        r1 = (Aa, Xx, Vv, Yy, Bb)
                        r2 = (Aa, Xx, Mm, Yy, Bb)
                        if r1 in rows[key] and r2 in rows[key]:
                            embeddings.append((Vv, Mm, Xx, Yy, Aa, Bb))
    print(f"rooted (V,M,X,Y,A,B) embeddings: {len(embeddings)}; first 5: {embeddings[:5]}")

    # squares census + two-sided (transposed) atom demand = period-4 rotor core
    squares = []
    for u, w in combinations(range(n), 2):
        if color.get(u) != color.get(w) or w in adj[u]:
            continue
        cn = sorted(adj[u] & adj[w])
        for c1, c2 in combinations(cn, 2):
            squares.append((u, c1, w, c2))  # cycle u-c1-w-c2
    cores = []
    for (u, c1, w, c2) in squares:
        # side atoms: pair on c-side entered between u,w? and pair on u-side entered between c1,c2
        sideA_ok = False
        for Aa in adj[c1] - {u, w}:
            for Bb in adj[c2] - {u, w, Aa}:
                key = (Aa, Bb) if Aa < Bb else (Bb, Aa)
                if key in rows:
                    ra = (Aa, c1, u, c2, Bb); rb = (Aa, c1, w, c2, Bb)
                    if ra in rows[key] and rb in rows[key]:
                        sideA_ok = True
        sideB_ok = False
        for Pp in adj[u] - {c1, c2}:
            for Qq in adj[w] - {c1, c2, Pp}:
                key = (Pp, Qq) if Pp < Qq else (Qq, Pp)
                if key in rows:
                    ra = (Pp, u, c1, w, Qq); rb = (Pp, u, c2, w, Qq)
                    if ra in rows[key] and rb in rows[key]:
                        sideB_ok = True
        if sideA_ok and sideB_ok:
            cores.append((u, c1, w, c2))
    print(f"squares (C4s): {len(squares)}; with ONE side atom pair covered both ways: "
          f"{sum(1 for s in squares if s not in cores)} (n/a breakdown below); FULL rotor cores "
          f"(both transposed atoms, both middles): {len(cores)} {cores[:8]}")

    # tuple space
    total = 1
    for rr in rows.values():
        total *= len(rr)
    multi = [a for a in atoms if len(rows[a]) > 1]
    print(f"tuple space size: {total}; multi-row atoms: {len(multi)} with sizes "
          f"{[len(rows[a]) for a in multi]}")
    return dict(n=n, edges=edges, adj=adj, color=color, atoms=atoms, rows=rows,
                bad=bad, degB=degB, degM=degM, total=total, multi=multi, tag=tag)

# ---------- state / transition machinery ----------
def state_data(fx, omega):
    rows = fx['rows']; atoms = fx['atoms']
    sel_rows = [rows[a][omega[i]] for i, a in enumerate(atoms)]
    m = defaultdict(int)
    r = defaultdict(int)
    noc = defaultdict(int)
    for row in sel_rows:
        for i in range(4):
            m[frozenset((row[i], row[i+1]))] += 1
        vs = set(row)
        for u in vs:
            r[u] += 1
        for u, w in combinations(sorted(vs), 2):
            noc[(u, w)] += 1
    S = {e for e, c in m.items() if c}
    selverts = {u for row in sel_rows for u in row}
    act = {e for e in fx['edges'] if e not in S and all(u in selverts for u in e)}
    # components of act
    cadj = defaultdict(set)
    for e in act:
        u, w = tuple(e)
        cadj[u].add(w); cadj[w].add(u)
    comp = {}
    for s in cadj:
        if s in comp:
            continue
        stack = [s]; comp[s] = s
        while stack:
            a = stack.pop()
            for b in cadj[a]:
                if b not in comp:
                    comp[b] = s
                    stack.append(b)
    active_comps = set()
    for e in fx['bad']:
        u, w = tuple(e)
        if u in comp and w in comp and comp[u] == comp[w]:
            active_comps.add(comp[u])
    return sel_rows, m, r, noc, S, act, comp, active_comps

def detours(fx, omega):
    """yield (atom_idx, new_row_idx, v_new, v_old, pos)"""
    rows = fx['rows']; atoms = fx['atoms']
    for i, a in enumerate(atoms):
        fam = rows[a]
        if len(fam) == 1:
            continue
        cur = fam[omega[i]]
        for j, alt in enumerate(fam):
            if j == omega[i]:
                continue
            diff = [p for p in range(5) if cur[p] != alt[p]]
            if len(diff) == 1 and diff[0] in (1, 2, 3):
                p = diff[0]
                yield (i, j, alt[p], cur[p], p)

def classify(fx, omega, verbose=False):
    sel_rows, m, r, noc, S, act, comp, active_comps = state_data(fx, omega)
    out = []
    for (i, j, vnew, vold, p) in detours(fx, omega):
        row = sel_rows[i]
        x0, y0 = row[p-1], row[p+1]
        # layer flags for the ENTERING vertex vnew
        lat_v = [e for e in fx['edges'] if vnew in e and e not in S]
        l1 = vnew in comp and comp[vnew] in active_comps
        exc = sum(max(c - 1, 0) for (u, w), c in noc.items() if vnew in (u, w))
        l2 = l1 and exc >= 1
        # equality profile at this state
        okdeg = fx['degB'][vnew] == T and fx['degM'][vnew] == T
        onelat = len(lat_v) == 1
        rt = r[vnew] == T
        cov = False
        if okdeg and onelat and rt:
            e_lat, = lat_v
            x0v = next(iter(e_lat - {vnew}))
            others = [w for w in fx['adj'][vnew] if w != x0v]
            cov = True
            for w in others:
                key = (x0v, w) if x0v < w else (w, x0v)
                found = False
                for rr in sel_rows:
                    if vnew in rr:
                        continue
                    vs = list(rr)
                    if x0v in vs and w in vs and abs(vs.index(x0v) - vs.index(w)) == 2:
                        found = True
                        break
                if not found:
                    cov = False
                    break
        l3 = l2 and okdeg and onelat and rt and cov
        out.append(dict(atom=i, alt=j, vnew=vnew, vold=vold, pos=p, l1=l1, exc=exc,
                        l2=l2, okdeg=okdeg, onelat=onelat, rt=rt, cov=cov, l3=l3))
    return out, (sel_rows, m, r, noc, S, act, comp, active_comps)

def census(fx, max_states=200000):
    atoms = fx['atoms']; rows = fx['rows']
    sizes = [len(rows[a]) for a in atoms]
    total = fx['total']
    do_all = total <= max_states
    counts = defaultdict(int)
    live_edges_L1 = []
    states_iter = None
    if do_all:
        states_iter = product(*[range(s) for s in sizes])
        nstates = total
    else:
        import random
        random.seed(23)
        states_iter = (tuple(random.randrange(s) for s in sizes) for _ in range(20000))
        nstates = 20000
    seen = 0
    for omega in states_iter:
        seen += 1
        dts, _ = classify(fx, omega)
        for d in dts:
            counts['L0'] += 1
            if d['l1']:
                counts['L1'] += 1
                live_edges_L1.append((omega, d['atom'], d['alt']))
            if d['l2']:
                counts['L2'] += 1
            if d['okdeg']:
                counts['P_deg'] += 1
            if d['okdeg'] and d['onelat']:
                counts['P_deg_onelat'] += 1
            if d['okdeg'] and d['onelat'] and d['rt']:
                counts['P_deg_onelat_rt'] += 1
            if d['okdeg'] and d['onelat'] and d['rt'] and d['cov']:
                counts['P_full_profile'] += 1
            if d['l3']:
                counts['L3'] += 1
    mode = 'EXHAUSTIVE' if do_all else f'SAMPLED {nstates}'
    print(f"[{fx['tag']}] transition census ({mode} over {seen} states): {dict(counts)}")
    # directed-cycle existence at L1: SCC over states restricted to L1 transitions
    if do_all and counts['L1'] > 0:
        idx = {}
        for omega, ai, aj in live_edges_L1:
            idx.setdefault(omega, [])
        graph = defaultdict(list)
        for omega, ai, aj in live_edges_L1:
            om2 = list(omega); om2[ai] = aj
            graph[omega].append(tuple(om2))
        # simple cycle detection: DFS color
        colorst = {}
        has_cycle = False
        for s in list(graph):
            if s in colorst:
                continue
            stack = [(s, iter(graph[s]))]
            colorst[s] = 1
            while stack:
                node, it = stack[-1]
                adv = False
                for nxt in it:
                    if colorst.get(nxt, 0) == 1:
                        has_cycle = True
                    elif nxt not in colorst:
                        colorst[nxt] = 1
                        stack.append((nxt, iter(graph.get(nxt, []))))
                        adv = True
                        break
                if not adv:
                    colorst[node] = 2
                    stack.pop()
            if has_cycle:
                break
        print(f"[{fx['tag']}] L1-live directed cycle exists: {has_cycle}")
    return counts

FIX = {
    '298': 'Q??????wE_[?EGs?D_@A?C_B???',
    '264': 'Q??????wE_Bws?s?DCD??@?@???',
}

if __name__ == '__main__':
    for tag, g6 in FIX.items():
        fx = analyze(tag, g6)
        census(fx)
