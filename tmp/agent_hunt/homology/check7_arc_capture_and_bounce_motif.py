#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 7: graph-level capture feasibility per owner-swap arc +
the minimal live-2-bounce square motif, on the reconstructed #298/#264 circuits.

Facts used (proved in the session report, elementary):
  P1 (position-timeline) Along any rotor (directed cycle of live middle-swaps),
     at each touched (atom, position) the value sequence is cyclic and EVERY
     value is inserted at some transition; inserted vertices are the transition
     owners, so every value is a FULL PROFILE OWNER at its insertion state.
     Hence every rotor swap-arc has BOTH its expelled and entering vertex
     owner-eligible (deg_B = deg_M = t).
  P2 (capture lower bound, Check 6) A live owner v (latent degree 1) needs its
     latent component to contain a capture pair; the minimal shape is the
     pendant 4-path v-x-z-w-b with vb bad; ANY capture needs, inside F* - v,
     a walk from the active neighbour x to a bad neighbour b of v (incident),
     or to both endpoints of a whole bad edge (remote).  Graph-level relaxation
     (necessary): reachability in F* - v from x.

Checks per circuit:
  A For every owner-swap arc (entering v, expelled m, square (x,v,y,m)):
      - incident feasibility via x: exists bad nbr b of v (in the circuit)
        with b reachable from x in F* - v   [also record min odd distance]
      - remote feasibility via x: exists circuit atom {a,b}, v not in it,
        both endpoints reachable from x in F* - v
      - the same via y (the swap fills the v-x edge where x is the ACTIVE
        neighbour; both roles tested since either row-neighbour could be it)
      - triangle sanity: no bad nbr b of v is F*-adjacent to x (would be a
        triangle) - asserted.
  B Minimal live-2-bounce motif: squares (x,v,y,m) with both transposed rows
    present in a common atom's DB family (rotor squares), v,m owner-eligible,
    AND a common bad co-neighbour b (vb and mb both circuit atoms).  The
    minimal 2-bounce needs additionally the shared latent 3-path; we report
    the weaker graph-level count (0 already kills it).
"""
import sys
from itertools import combinations
from collections import defaultdict, deque
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_atoms_v3 import find_circuits_v3
from fixture_264_variants import find as find_variant

def reach(adj, banned, src):
    seen = {src}
    dq = deque([src])
    dist = {src: 0}
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if w == banned or w in seen:
                continue
            seen.add(w)
            dist[w] = dist[u] + 1
            dq.append(w)
    return dist

def arcs_of(fx, circ, OWN):
    """owner-swap arcs: (atom, i, j, expelled, entered, x, y, pos)"""
    out = []
    for a in circ:
        fam = fx['rows'][a]
        for i, r1 in enumerate(fam):
            for j, r2 in enumerate(fam):
                if i == j:
                    continue
                diff = [p for p in range(5) if r1[p] != r2[p]]
                if len(diff) == 1 and diff[0] in (1, 2, 3):
                    p = diff[0]
                    if r1[p] in OWN and r2[p] in OWN:
                        out.append((a, i, j, r1[p], r2[p], r1[p-1], r1[p+1], p))
    return out

def analyze(tag):
    fx = build(tag)
    if tag == '298':
        subs = find_circuits_v3(fx, cap=1000)
    else:
        subs, _ = find_variant(fx, (0,), cap=1000)
    subs = [sorted(map(tuple, s)) for s in subs]
    print(f"\n===== {tag}: {len(subs)} circuits =====")
    adj = fx['adj']
    for si, circ in enumerate(subs):
        chosen = set(map(tuple, circ))
        dM = defaultdict(int)
        badnb = defaultdict(set)
        for u, w in circ:
            dM[u] += 1; dM[w] += 1
            badnb[u].add(w); badnb[w].add(u)
        OWN = {u for u in range(fx['n']) if len(adj[u]) == 5 and dM[u] == 5}
        A = arcs_of(fx, circ, OWN)
        n_arc = len(A)
        inc_ok = rem_ok = any_ok = 0
        details = []
        for (a, i, j, m, v, x, y, p) in A:
            feas = False
            modes = []
            for nb_role, nb in (('x', x), ('y', y)):
                dist = reach(adj, v, nb)
                # triangle sanity: bad nbr of v adjacent to nb would be triangle
                for b in badnb[v]:
                    assert b not in adj[nb] or b not in dist or dist.get(b, 99) != 1, \
                        f"triangle {v},{nb},{b}"
                inc = [b for b in badnb[v] if b in dist and dist[b] >= 3]
                # remote: whole atom inside reach
                rem = [(c, d) for (c, d) in chosen
                       if v not in (c, d) and c in dist and d in dist]
                if inc:
                    modes.append(f"{nb_role}:INC{sorted(inc)}")
                if rem:
                    modes.append(f"{nb_role}:REM{len(rem)}")
                if inc or rem:
                    feas = True
            if feas:
                any_ok += 1
            if any('INC' in mo for mo in modes):
                inc_ok += 1
            if any('REM' in mo for mo in modes):
                rem_ok += 1
            details.append(((a, m, v, x, y), modes))
        print(f" circuit#{si}: owner-swap arcs {n_arc}; graph-level capture-feasible "
              f"{any_ok} (incident {inc_ok}, remote {rem_ok})")
        for (key, modes) in details[:6]:
            print(f"    arc {key}: {modes if modes else 'STERILE (no graph-level capture)'}")
        # B: minimal 2-bounce motif
        motifs = []
        for u, w in combinations(range(fx['n']), 2):
            if fx['color'].get(u) != fx['color'].get(w) or w in adj[u]:
                continue
            cn = sorted(adj[u] & adj[w])
            for c1, c2 in combinations(cn, 2):
                # square (c1, u, c2, w): middles u,w
                if u in OWN and w in OWN:
                    commonbad = badnb[u] & badnb[w]
                    # rotor square: transposed rows in one atom's family
                    rotor = False
                    for (aa, bb) in chosen:
                        fam = fx['rows'][(aa, bb)]
                        for r1 in fam:
                            for pos in (1, 2, 3):
                                if r1[pos] == u:
                                    r2 = r1[:pos] + (w,) + r1[pos+1:]
                                    if r2 in fam and r1[pos-1] in (c1, c2) and r1[pos+1] in (c1, c2):
                                        rotor = True
                    if commonbad:
                        motifs.append(((c1, u, c2, w), sorted(commonbad), rotor))
        rotor_motifs = [mo for mo in motifs if mo[2]]
        print(f"    2-bounce motif squares (both middles eligible + common bad "
              f"co-neighbour): {len(motifs)}; of these ROTOR squares: {len(rotor_motifs)}")
        for mo in motifs[:6]:
            print(f"      square {mo[0]} common-bad {mo[1]} rotor={mo[2]}")

if __name__ == '__main__':
    for tag in ('298', '264'):
        analyze(tag)
