"""Gate the length-bundle half-switch K2T bridge.

This repairs the too-narrow per-bad-edge half-switch family.

For a connected-B maximum cut and a vertex v with negative K2T residual

    R[v] = N*T[v] - (K2*T)[v] < 0,

collect, for each length L, all shortest B-geodesic rows of all bad edges of
length L that contain v.  In each orientation, form the union of prefixes up
to v and the union of suffixes from v.  The candidate bridge asks whether one
of these length-bundle half-switches is cut-neutral, keeps B connected, and
strictly decreases Gamma.
"""

import argparse
import random
import subprocess

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import (
    adj_from_edges,
    boundary_delta,
    flip_side,
    gamma_of,
    residuals,
)


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


def length_bundle_half_switches(ell, cyc, v):
    masks = set()
    for L in sorted(set(ell.values())):
        for rev in (False, True):
            hits = []
            for f, paths0 in cyc.items():
                if ell[f] != L:
                    continue
                for path0 in paths0:
                    path = list(reversed(path0)) if rev else list(path0)
                    if v in path:
                        hits.append(path)
            if not hits:
                continue

            pref = 0
            suff = 0
            for path in hits:
                i = path.index(v)
                for x in path[: i + 1]:
                    pref |= 1 << x
                for x in path[i:]:
                    suff |= 1 << x
            masks.add(pref)
            masks.add(suff)
    return masks


def covering_switch(n, adj, side, gamma0, ell, cyc, v):
    best = None
    for mask in length_bundle_half_switches(ell, cyc, v):
        if not ((mask >> v) & 1):
            continue
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        side2 = flip_side(side, mask)
        gamma2 = gamma_of(n, adj, side2)
        if gamma2 is None or gamma2 >= gamma0:
            continue
        cand = (mask.bit_count(), -(gamma0 - gamma2), mask, gamma2)
        if best is None or cand < best:
            best = cand
    return best


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    _M, ell, _T, _mu, cyc = st
    gamma0 = gamma_of(n, adj, side)
    R = residuals(n, adj, side)
    if gamma0 is None or R is None:
        return

    cut_has_neg = False
    for v, r in enumerate(R):
        if r >= 0:
            continue
        cut_has_neg = True
        acc["neg_vertices"] += 1
        best = covering_switch(n, adj, side, gamma0, ell, cyc, v)
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
            continue

        size, negdrop, mask, gamma2 = best
        drop = -negdrop
        acc["covered"] += 1
        acc["size_hist"][size] = acc["size_hist"].get(size, 0) + 1
        acc["drop_hist"][drop] = acc["drop_hist"].get(drop, 0) + 1
        if len(acc["examples"]) < acc["example_limit"]:
            acc["examples"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(r),
                    tuple(i for i in range(n) if (mask >> i) & 1),
                    gamma2,
                    drop,
                )
            )
    if cut_has_neg:
        acc["bad_cuts"] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def h_blowup(t):
    n, edges = dec("H?AFBo]")
    base_side = [int(c) for c in "111110000"]
    out_edges = []
    side = []
    for i in range(n):
        side += [base_side[i]] * t
    for u, v in edges:
        for a in range(t):
            for b in range(t):
                out_edges.append((u * t + a, v * t + b))
    return n * t, out_edges, side


def new_acc(example_limit):
    return dict(
        bad_cuts=0,
        neg_vertices=0,
        covered=0,
        fail=0,
        first_fail=None,
        size_hist={},
        drop_hist={},
        examples=[],
        example_limit=example_limit,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--random", type=int, default=0)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--examples", type=int, default=12)
    args = parser.parse_args()

    acc = new_acc(args.examples)
    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print(
            "census N=%d bad_cuts=%d neg_vertices=%d covered=%d fail=%d"
            % (n, acc["bad_cuts"], acc["neg_vertices"], acc["covered"], acc["fail"]),
            flush=True,
        )

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        adj = adj_from_edges(n, edges)
        scan_cut("H?AFBo][%d]" % t, n, adj, side, acc)
        print(
            "H?AFBo][%d] bad_cuts=%d neg_vertices=%d covered=%d fail=%d"
            % (t, acc["bad_cuts"], acc["neg_vertices"], acc["covered"], acc["fail"]),
            flush=True,
        )

    if args.random:
        rng = random.Random(123)
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
    print("bad cuts:", acc["bad_cuts"])
    print("negative vertices:", acc["neg_vertices"])
    print("covered:", acc["covered"])
    print("FAIL:", acc["fail"], acc["first_fail"] or "")
    print("switch size histogram:", dict(sorted(acc["size_hist"].items())))
    print("Gamma drop histogram:", dict(sorted(acc["drop_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)


if __name__ == "__main__":
    main()
