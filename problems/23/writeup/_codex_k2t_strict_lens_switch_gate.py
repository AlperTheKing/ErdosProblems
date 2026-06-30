"""Probe whether strict lenses alone force terminal-shadow descent.

This is deliberately narrower than the live K2T gate.  The live theorem only
needs vertices with negative residual R[v] < 0.  This diagnostic checks the
tempting stronger simplification:

    every vertex on the short side of a strict bad-geodesic lens
    has a neutral B-connected length-bundle terminal-shadow switch with Psi>0.

If this fails, the proof target must keep the negative-residual weighting.
"""

import argparse
import random
import subprocess

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _lens_gate import strict_lenses
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


def connected(adj):
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def has_terminal_switch(n, adj, side, st, v):
    _M, ell, _T, _mu, cyc = st
    best = None
    for mask in length_bundle_half_switches(ell, cyc, v):
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        if not Bconn(n, adj, flip_side(side, mask)):
            continue
        psi = terminal_shadow_psi(n, adj, side, st, mask)
        if psi is None or psi <= 0:
            continue
        cand = (mask.bit_count(), -psi, mask, psi)
        if best is None or cand < best:
            best = cand
    return best


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, _T, _mu, cyc = st
    if not M:
        return
    pairs, short_verts = strict_lenses(M, ell, cyc)
    if not pairs:
        return

    acc["lensed_cuts"] += 1
    R = residuals(n, adj, side)
    neg = {v for v, r in enumerate(R or []) if r < 0}
    for v in sorted(short_verts):
        best = has_terminal_switch(n, adj, side, st, v)
        if best is None:
            acc["lens_vertex_fail"] += 1
            if acc["first_lens_fail"] is None:
                rv = None if R is None else str(R[v])
                acc["first_lens_fail"] = (name, n, "".join(map(str, side)), v, rv, len(pairs))
        else:
            acc["lens_vertex_covered"] += 1

    for v in sorted(neg):
        acc["neg_vertices"] += 1
        best = has_terminal_switch(n, adj, side, st, v)
        if best is None:
            acc["neg_fail"] += 1
            if acc["first_neg_fail"] is None:
                acc["first_neg_fail"] = (name, n, "".join(map(str, side)), v, str(R[v]), len(pairs))
        else:
            acc["neg_covered"] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def new_acc():
    return dict(
        lensed_cuts=0,
        lens_vertex_covered=0,
        lens_vertex_fail=0,
        first_lens_fail=None,
        neg_vertices=0,
        neg_covered=0,
        neg_fail=0,
        first_neg_fail=None,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
    args = parser.parse_args()

    acc = new_acc()
    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print(
            "census N=%d lensed_cuts=%d lens_vertices=%d/%d neg=%d/%d"
            % (
                n,
                acc["lensed_cuts"],
                acc["lens_vertex_covered"],
                acc["lens_vertex_covered"] + acc["lens_vertex_fail"],
                acc["neg_covered"],
                acc["neg_vertices"],
            ),
            flush=True,
        )

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print(
            "H?AFBo][%d] lens_vertices=%d/%d neg=%d/%d"
            % (
                t,
                acc["lens_vertex_covered"],
                acc["lens_vertex_covered"] + acc["lens_vertex_fail"],
                acc["neg_covered"],
                acc["neg_vertices"],
            ),
            flush=True,
        )

    if args.random:
        rng = random.Random(771)
        made = 0
        tries = 0
        while made < args.random and tries < 100000:
            tries += 1
            n = rng.choice([11, 12])
            p = rng.uniform(0.16, 0.32)
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
            if not edges or not is_triangle_free(n, edges):
                continue
            adj = adj_from_edges(n, edges)
            if not connected(adj):
                continue
            made += 1
            scan_graph("rand%d" % made, n, edges, acc)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("lensed cuts:", acc["lensed_cuts"])
    print("strict-lens short vertices covered:", acc["lens_vertex_covered"])
    print("strict-lens short vertices FAIL:", acc["lens_vertex_fail"], acc["first_lens_fail"] or "")
    print("negative vertices covered:", acc["neg_covered"])
    print("negative vertices FAIL:", acc["neg_fail"], acc["first_neg_fail"] or "")


if __name__ == "__main__":
    main()
