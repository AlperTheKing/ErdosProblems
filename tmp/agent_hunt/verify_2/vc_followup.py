#!/usr/bin/env python3
"""VERIFY_2 script C: follow-ups.
 1. All-F*-swap-cells complex (both-diagonal convention) counts + ranks for both
    fixtures (report: #298 -> 28 cells, rankQ 13, kerQ 15).
 2. Bigger profile hunt (60k samples) on the profile-bearing circuits, gating R50's
    |S| >= 3t-1 = 14 and |L| <= t(t-3) = 10 on every profile state found, and
    verifying the owner's unique latent edge is an F* edge (Claim 2's t=3 lever shape).
 3. For every profile state: owner's intrinsic active component edge count and
    capture status (Claim 1 consistency: any capture would need >= 4 edges;
    expectation on these fixtures: NO capture at all).
"""
import random
from collections import defaultdict, deque
from vb_fixtures import (build_fixture, find_circuits, all_swap_cells, boundary_rows,
                         rankQ, rankF2, T)

def followup_cells(tag):
    fx = build_fixture(tag)
    cells = all_swap_cells(fx)
    mat = boundary_rows(fx, cells)
    rq = rankQ(mat)
    r2 = rankF2(mat)
    print(f"[{tag}] ALL F*-swap-cells: n={len(cells)} rankQ={rq} kerQ={len(cells)-rq} "
          f"rankF2={r2} kerF2={len(cells)-r2}")

def profile_hunt(tag, which, n_samples=60000, seed=7):
    fx = build_fixture(tag)
    strict, _ = find_circuits(fx, (0, 1), cap=100)
    circuits = strict
    if not circuits:
        circuits, _ = find_circuits(fx, (0,), cap=100)
    circ = circuits[which]
    atoms = sorted(circ)
    fams = [fx['rows'][a] for a in atoms]
    sizes = [len(f) for f in fams]
    dM = defaultdict(int)
    for u, w in atoms:
        dM[u] += 1; dM[w] += 1
    owner_cands = [u for u in range(fx['n']) if len(fx['adj'][u]) == T and dM[u] == T]
    bad_set = [frozenset(a) for a in atoms]
    rng = random.Random(seed)
    n_prof = 0
    viol = []
    comp_hist = defaultdict(int)
    captures = 0
    for _ in range(n_samples):
        om = tuple(rng.randrange(s) for s in sizes)
        sel = [fams[i][om[i]] for i in range(len(atoms))]
        S = set()
        rcount = defaultdict(int)
        for r in sel:
            for i in range(4):
                S.add(frozenset((r[i], r[i + 1])))
            for u in set(r):
                rcount[u] += 1
        selverts = {u for r in sel for u in r}
        for v in owner_cands:
            if rcount[v] != T:
                continue
            lat = [e for e in fx['edges'] if v in e and e not in S]
            if len(lat) != 1:
                continue
            x0 = next(iter(lat[0] - {v}))
            star = [w for w in fx['adj'][v] if w != x0]
            if not all(any(x0 in r and w in r for r in sel) for w in star):
                continue
            n_prof += 1
            nS, nL = len(S), 24 - len(S)
            lat_in_F = lat[0] in fx['edges']
            if nS < 3 * T - 1 or nL > T * (T - 3) or not lat_in_F:
                viol.append((om, v, nS, nL, lat_in_F))
            # owner's intrinsic active component
            act = [e for e in fx['edges'] if e not in S and all(u in selverts for u in e)]
            cadj = defaultdict(set)
            for e in act:
                a2, b2 = tuple(e)
                cadj[a2].add(b2); cadj[b2].add(a2)
            compv = {v}
            dq = deque([v])
            while dq:
                u0 = dq.popleft()
                for w0 in cadj[u0]:
                    if w0 not in compv:
                        compv.add(w0)
                        dq.append(w0)
            ecount = sum(1 for e in act if set(e) <= compv)
            comp_hist[ecount] += 1
            if any(set(b) <= compv for b in bad_set):
                captures += 1
    print(f"[{tag} c{which}] {n_samples} samples: profile states={n_prof}; "
          f"R50/latent violations={len(viol)} {viol[:3]}; owner-component edge-count "
          f"histogram={dict(sorted(comp_hist.items()))}; captures={captures} (expect 0)")

def rotor8():
    """Independent re-derivation of the survival-matrix facts for the 8-vtx rotor:
    |latent| = 1 in every state (below Claim 1's bound of 4 => vacuity forced),
    no capture anywhere, T3=-T1/T4=-T2 inverse-pair structure, and the clock-lemma
    premise failure (inserted vertices are NOT equality-scale: dM != dB)."""
    a, b, p, q, x, y, m, v = range(8)
    blue = {frozenset(e) for e in [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y),
                                   (y, v), (v, x)]}
    bads = [frozenset((a, b)), frozenset((p, q))]
    A_m, A_v = (a, x, m, y, b), (a, x, v, y, b)
    B_x, B_y = (p, m, x, v, q), (p, m, y, v, q)
    states = {'w_mx': (A_m, B_x), 'w_my': (A_m, B_y), 'w_vy': (A_v, B_y),
              'w_vx': (A_v, B_x)}
    cyc = [('w_mx', 'w_my'), ('w_my', 'w_vy'), ('w_vy', 'w_vx'), ('w_vx', 'w_mx')]
    ok = True
    chains = []
    for s1, s2 in cyc:
        r1, r2 = states[s1], states[s2]
        d = defaultdict(int)
        for rr, sg in ((r2, 1), (r1, -1)):
            for r in rr:
                for i in range(4):
                    d[frozenset((r[i], r[i + 1]))] += sg
        chains.append({e: c for e, c in d.items() if c})
    inv = (chains[2] == {e: -c for e, c in chains[0].items()} and
           chains[3] == {e: -c for e, c in chains[1].items()})
    lat_sizes = []
    caps = 0
    for st, rows in states.items():
        sup = {frozenset((r[i], r[i + 1])) for r in rows for i in range(4)}
        sel = {u for r in rows for u in r}
        act = {e for e in blue if e not in sup and set(e) <= sel}
        lat_sizes.append(len(act))
        cv = set()
        for e in act:
            cv |= set(e)
        caps += any(set(t) <= cv for t in bads)
    # clock premise: inserted vertices equality-scale?
    dB = defaultdict(int)
    for e in blue:
        for u in e:
            dB[u] += 1
    dM = defaultdict(int)
    for e in bads:
        for u in e:
            dM[u] += 1
    ins_eq = []
    for (s1, s2) in cyc:
        r1, r2 = states[s1], states[s2]
        for old, new in zip(r1, r2):
            if old != new:
                pos = next(i for i in range(5) if old[i] != new[i])
                vin = new[pos]
                ins_eq.append(dB[vin] == dM[vin])
    print(f"[8vtx] |latent| per state={lat_sizes} (report: all 1); captures={caps} "
          f"(report: 0); T3=-T1 & T4=-T2: {inv}; inserted-vertex equality-scale "
          f"flags={ins_eq} (report: premise fails => all False)")

if __name__ == '__main__':
    for tag in ('298', '264'):
        followup_cells(tag)
    rotor8()
    profile_hunt('298', 4)
    profile_hunt('264', 2)
