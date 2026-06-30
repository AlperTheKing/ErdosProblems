"""Inspect the actual crossM/bdyB length structure of L_max-bundle switches at
each R<0 site, to find the TRUE surplus invariant (the conjectured
'crossM all L_max, bdyB all strictly shorter' is FALSE -- see _psi_surplus_gate).

We print, per site, the multiset of crossM lengths and bdyB lambdas, and test
candidate weaker invariants:
  (W1) Psi = sum crossM^2 - sum bdyB_lambda^2 > 0   (already known)
  (W2) every bdyB lambda <= L_max, AND multiset of crossM lengths
       majorizes / dominates the multiset of bdyB lambdas after pairing
  (W3) the LONGEST crossing bad edge length (= L_max) strictly exceeds the
       LONGEST boundary lambda  (peak surplus)
  (W4) |crossM| relation to |bdyB|

Run: python _psi_surplus_inspect.py
"""
import subprocess
from fractions import Fraction as F
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi, edge


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def lmax_bundle_masks(cyc, ell, v):
    lengths = set()
    for f, paths in cyc.items():
        for Q in paths:
            if v in Q:
                lengths.add(ell[f]); break
    if not lengths:
        return None, []
    Lmax = max(lengths)
    masks = set()
    for rev in (False, True):
        pref = 0; suff = 0; hit = False
        for f, paths0 in cyc.items():
            if ell[f] != Lmax:
                continue
            for Q0 in paths0:
                Q = list(reversed(Q0)) if rev else list(Q0)
                if v not in Q:
                    continue
                hit = True
                i = Q.index(v)
                for x in Q[:i+1]:
                    pref |= 1 << x
                for x in Q[i:]:
                    suff |= 1 << x
        if hit:
            masks.add(pref); masks.add(suff)
    return Lmax, list(masks)


def decompose(n, adj, side, st, mask):
    M, ell, _T, _mu, cyc = st
    bdy_b = set(); cross_m = []
    for u in range(n):
        inu = (mask >> u) & 1
        for w in adj[u]:
            if w <= u: continue
            if inu == ((mask >> w) & 1): continue
            if side[u] == side[w]: cross_m.append(edge(u, w))
            else: bdy_b.add(edge(u, w))
    psi = terminal_shadow_psi(n, adj, side, st, mask)
    if psi is None:
        return None
    witnesses = {e: [] for e in bdy_b}
    for f in cross_m:
        u, w = f
        tau = u if ((mask >> u) & 1) else w
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            bits = [(mask >> x) & 1 for x in path]
            r = 0
            while r+1 < len(bits) and bits[r+1] == 1:
                r += 1
            witnesses[edge(path[r], path[r+1])].append(f)
    crossL = sorted((ell[f] for f in cross_m), reverse=True)
    bdyLam = sorted((min(ell[f] for f in ws) for ws in witnesses.values() if ws), reverse=True)
    return crossL, bdyLam, psi


def collect(name, n, adj, side, rows):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, _T, _mu, cyc = st
    if not M:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    gamma0 = sum(ell[f]*ell[f] for f in M)
    for v, r in enumerate(R):
        if r >= 0:
            continue
        Lmax, masks = lmax_bundle_masks(cyc, ell, v)
        if Lmax is None:
            continue
        for mask in masks:
            if not ((mask >> v) & 1) or mask == 0 or mask == (1 << n)-1:
                continue
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            if not Bconn(n, adj, flip_side(side, mask)):
                continue
            dd = decompose(n, adj, side, st, mask)
            if dd is None:
                continue
            crossL, bdyLam, psi = dd
            if psi <= 0:
                continue
            g2 = gamma_of(n, adj, flip_side(side, mask))
            if g2 is None or gamma0 - g2 != psi:
                continue
            rows.append((name, n, v, Lmax, tuple(crossL), tuple(bdyLam), psi))
            break


def main():
    rows = []
    for n in range(9, 11):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            adj = adj_from_edges(nn, edges)
            for side in maxcut_all(nn, adj):
                collect(g6, nn, adj, side, rows)
    # Hblowups
    hN, hE = dec("H?AFBo]")
    base = [int(c) for c in "111110000"]
    for t in (2, 3):
        EE = []
        for (u, w) in hE:
            for a in range(t):
                for b in range(t):
                    EE.append((u*t+a, w*t+b))
        nn = hN*t; s = [base[v//t] for v in range(nn)]
        adj = adj_from_edges(nn, EE)
        collect("Hblow_t%d" % t, nn, adj, s, rows)

    print("total decomposed sites:", len(rows))
    # test invariants
    w2_fail = w3_fail = peak_eq = pairdom_fail = 0
    examples = []
    for (name, n, v, Lmax, crossL, bdyLam, psi) in rows:
        # W3: max crossing length strictly > max boundary lambda
        maxcross = max(crossL) if crossL else 0
        maxbdy = max(bdyLam) if bdyLam else 0
        if not (maxcross > maxbdy):
            w3_fail += 1
            if len(examples) < 12:
                examples.append(("W3", name, n, v, Lmax, crossL, bdyLam, str(psi)))
        if maxcross == maxbdy:
            peak_eq += 1
        # W2 paired domination: sort both desc, pad bdy with zeros, require crossL[i] >= bdyLam[i]
        cl = list(crossL); bl = list(bdyLam) + [0]*(len(crossL)-len(bdyLam)) if len(bdyLam) <= len(crossL) else list(bdyLam)
        # pad the shorter
        m = max(len(crossL), len(bdyLam))
        clp = list(crossL) + [0]*(m-len(crossL))
        blp = list(bdyLam) + [0]*(m-len(bdyLam))
        if not all(clp[i] >= blp[i] for i in range(m)):
            pairdom_fail += 1
            if len(examples) < 12:
                examples.append(("PAIRDOM", name, n, v, Lmax, crossL, bdyLam, str(psi)))
    print("W3 (max crossing > max boundary lambda) failures:", w3_fail)
    print("sites with max crossing == max boundary (peak tie):", peak_eq)
    print("paired-domination (sorted desc crossL[i]>=bdyLam[i]) failures:", pairdom_fail)
    # length composition stats
    print("\nsample decompositions (name,n,v,Lmax, crossL_desc, bdyLam_desc, psi):")
    seen = set()
    for row in rows:
        key = (row[3], row[4], row[5])
        if key in seen:
            continue
        seen.add(key)
        print("  ", row)
    print("\nexamples of invariant failures:")
    for e in examples:
        print("  ", e)


if __name__ == "__main__":
    main()
