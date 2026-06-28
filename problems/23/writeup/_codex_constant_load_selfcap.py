"""Exact diagnostics for the constant-load component self-cap lemma.

Candidate lemma:
  Let C be a proper positive K/omega component in a gamma-min connected-B
  max cut. If T is constant on C, say T(v)=lambda for every v in C, then
  lambda <= |C|.

This is the narrow consequence needed for GCD-cond1: a dangerous ungrounded
Q-component would have T(v)=N on a proper component, contradicting lambda<=|C|.
"""
import subprocess

from _h import dec, GENG
from _codex_constant_load_component import (
    analyze_given_side,
    build_adj,
    gamma_of,
)
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free


def connected_gamma_min_sides(n, adj, all_gamma=False):
    from _h import maxcut_all, Bconn

    cand = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        g = gamma_of(n, adj, side)
        if g is not None:
            cand.append((side, g))
    if not cand:
        return []
    gm = min(g for _, g in cand)
    return [side for side, g in cand if all_gamma or g == gm]


def check_side(name, n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return dict(total=0, bad=0, first=None)
    _M, _ell, T, _mu, cyc = st
    comps, _ = kcomponents(n, cyc)
    total = 0
    bad = 0
    first = None
    for comp in comps.values():
        cset = {v for v in comp if T[v] > 0}
        if not cset or len(cset) == n:
            continue
        vals = {T[v] for v in cset}
        if len(vals) != 1:
            continue
        total += 1
        lam = next(iter(vals))
        ok = lam <= len(cset)
        if not ok:
            bad += 1
            if first is None:
                first = dict(graph=name, C=sorted(cset), size=len(cset), lambda_=str(lam))
    return dict(total=total, bad=bad, first=first)


def check_graph(name, n, edges, all_gamma=False):
    adj = build_adj(n, edges)
    total = bad = 0
    first = None
    for side in connected_gamma_min_sides(n, adj, all_gamma=all_gamma):
        r = check_side(name, n, adj, side)
        total += r["total"]
        bad += r["bad"]
        first = first or r["first"]
    return dict(total=total, bad=bad, first=first)


def run_census(nmin=7, nmax=10):
    for nn in range(nmin, nmax + 1):
        total = bad = 0
        first = None
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            r = check_graph(g6, n, edges)
            total += r["total"]
            bad += r["bad"]
            first = first or r["first"]
        print(f"census N={nn}: const-load comps={total} selfcap_bad={bad} first={first}", flush=True)


def run_glued():
    print("--- glued island battery ---", flush=True)
    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, edges = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    edges = edges + [(i, iN + j)]
                if n > 22 or not is_triangle_free(n, edges):
                    continue
                r = check_graph(f"isl{iN}+gad{gN}+{br}", n, edges)
                if r["total"] or r["bad"]:
                    print(f"glued {iN}+{gN}+{br}: {r}", flush=True)


def run_named():
    print("--- named / blow-up spot checks ---", flush=True)
    names = [
        "G?bF`w",
        "I?BD@g]Qo",
        "I?ABCc]}?",
        "J??CE?{{?]?",
        "J???E?pNu\\?",
    ]
    for g6 in names:
        try:
            n, edges = dec(g6)
        except Exception as exc:
            print(f"skip {g6}: {exc}", flush=True)
            continue
        print(f"named {g6}: {check_graph(g6, n, edges)}", flush=True)


if __name__ == "__main__":
    print("=== constant-load component selfcap: lambda <= |C| ===", flush=True)
    run_census(7, 10)
    run_glued()
    run_named()
