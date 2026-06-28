"""Check the constant-load component induction bridge.

Candidate lemma:
  If a positive K/omega component C has T constant on C, then the global
  gamma-min cut restricted to G[C] is a full gamma-min connected maxcut of
  G[C] (not merely boundary-frozen gamma-min).

This would kill a dangerous GCD-cond1 component by induction: a proper
component with T=N on |C|<N vertices has Gamma_C=N|C|>|C|^2.
"""
import subprocess
from fractions import Fraction as F

from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free


def build_adj(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def cutsize(n, adj, side):
    return sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    bad = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    gamma = 0
    for u, v in bad:
        d = bdist_restr(adj, side, u, v)
        if d < 0:
            return None
        gamma += (d + 1) ** 2
    return gamma


def induced_graph(adj, cset):
    clist = sorted(cset)
    idx = {v: i for i, v in enumerate(clist)}
    edges = [(idx[u], idx[v]) for u in clist for v in adj[u] if v in cset and v > u]
    return len(clist), edges, clist


def full_gamma_min(m, edges):
    adj = build_adj(m, edges)
    cuts = maxcut_all(m, adj)
    max_size = max(cutsize(m, adj, side) for side in cuts)
    best = None
    for side in cuts:
        if cutsize(m, adj, side) != max_size:
            continue
        g = gamma_of(m, adj, side)
        if g is None:
            continue
        best = g if best is None or g < best else best
    return max_size, best


def analyze_graph(name, n, E, all_gamma=False):
    adj = build_adj(n, E)
    cuts = maxcut_all(n, adj)
    cand = []
    for side in cuts:
        if not Bconn(n, adj, side):
            continue
        g = gamma_of(n, adj, side)
        if g is not None:
            cand.append((side, g))
    if not cand:
        return dict(total=0, bad=0, first=None)
    gm = min(g for _, g in cand)
    sides = [s for s, g in cand if all_gamma or g == gm]
    total = 0
    bad = 0
    first = None
    for side in sides:
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        comps, _ = kcomponents(n, cyc)
        for comp in comps.values():
            cset = {v for v in comp if T[v] > 0}
            if not cset or cset == set(range(n)):
                continue
            vals = {T[v] for v in cset}
            if len(vals) != 1:
                continue
            total += 1
            m, edges, clist = induced_graph(adj, cset)
            adjc = build_adj(m, edges)
            induced_side = [side[v] for v in clist]
            induced_size = cutsize(m, adjc, induced_side)
            induced_gamma = gamma_of(m, adjc, induced_side)
            full_size, full_gamma = full_gamma_min(m, edges)
            ok = induced_size == full_size and induced_gamma == full_gamma
            if not ok:
                bad += 1
                if first is None:
                    first = dict(
                        graph=name,
                        C=sorted(cset),
                        T=str(next(iter(vals))),
                        induced_size=induced_size,
                        full_size=full_size,
                        induced_gamma=induced_gamma,
                        full_gamma=full_gamma,
                    )
    return dict(total=total, bad=bad, first=first)


def analyze_given_side(name, n, E, side):
    """Same constant-load component check for a supplied cut side."""
    adj = build_adj(n, E)
    st = struct_for_side(n, adj, side)
    if st is None:
        return dict(total=0, bad=0, first=None)
    M, ell, T, mu, cyc = st
    comps, _ = kcomponents(n, cyc)
    total = 0
    bad = 0
    first = None
    for comp in comps.values():
        cset = {v for v in comp if T[v] > 0}
        if not cset or cset == set(range(n)):
            continue
        vals = {T[v] for v in cset}
        if len(vals) != 1:
            continue
        total += 1
        m, edges, clist = induced_graph(adj, cset)
        adjc = build_adj(m, edges)
        induced_side = [side[v] for v in clist]
        induced_size = cutsize(m, adjc, induced_side)
        induced_gamma = gamma_of(m, adjc, induced_side)
        full_size, full_gamma = full_gamma_min(m, edges)
        ok = induced_size == full_size and induced_gamma == full_gamma
        if not ok:
            bad += 1
            if first is None:
                first = dict(
                    graph=name,
                    C=sorted(cset),
                    T=str(next(iter(vals))),
                    induced_size=induced_size,
                    full_size=full_size,
                    induced_gamma=induced_gamma,
                    full_gamma=full_gamma,
                )
    return dict(total=total, bad=bad, first=first)


if __name__ == "__main__":
    print("=== constant-load component bridge ===", flush=True)
    for nn in range(7, 11):
        total = bad = 0
        first = None
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            r = analyze_graph(g6, n, E)
            total += r["total"]
            bad += r["bad"]
            first = first or r["first"]
        print(f"census N={nn}: const-load proper comps={total} bad={bad} first={first}", flush=True)

    print("--- glued island battery ---", flush=True)
    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, E = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    E = E + [(i, iN + j)]
                if n > 22 or not is_triangle_free(n, E):
                    continue
                r = analyze_graph(f"isl{iN}+gad{gN}+{br}", n, E)
                if r["total"] or r["bad"]:
                    print(f"isl{iN}+gad{gN}+{br}: {r}", flush=True)
