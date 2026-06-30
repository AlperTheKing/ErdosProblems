"""Probe the barrier-closure proof of terminal witness Hall.

For a selected Lmax terminal-shadow switch S and a subset Y of crossing bad
edges, let Gamma(Y) be the boundary exits witnessed by Y.  The hoped-for proof:

  1. U = union of terminal prefixes of rows of f in Y.
  2. Close U across B-edges not in Gamma(Y), but never enter the far endpoints
     of the selected crossing bad edges Y.
  3. Then delta_B(U_closed) subset Gamma(Y) and Y subset delta_M(U_closed).

Max-cut gives |Gamma(Y)| >= |Y|, i.e. Hall on the left side.
"""

import argparse
import itertools
import random
import subprocess
from collections import Counter

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_switch_signature_gate import bundle_candidates, edge, terminal_shadow_details


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


def boundary_sets(n, adj, side, mask):
    bdy_b = set()
    bdy_m = set()
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            if side[u] == side[v]:
                bdy_m.add(edge(u, v))
            else:
                bdy_b.add(edge(u, v))
    return bdy_b, bdy_m


def exits_and_prefix_mask(st, switch_mask, Y):
    """Return (Gamma(Y), prefix union mask) for terminal rows of Y."""
    _M, _ell, _T, _mu, cyc = st
    exits = set()
    mask = 0
    for f in Y:
        u, v = f
        tau = u if ((switch_mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            bits = [(switch_mask >> x) & 1 for x in path]
            if bits[0] != 1:
                raise AssertionError("row not oriented from inside endpoint")
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                raise AssertionError("not terminal-prefix row")
            exits.add(edge(path[r], path[r + 1]))
            for x in path[: r + 1]:
                mask |= 1 << x
    return exits, mask


def far_endpoint_barriers(switch_mask, Y):
    out = set()
    for u, v in Y:
        out.add(v if ((switch_mask >> u) & 1) else u)
    return out


def close_over_nonexit_B(n, adj, side, mask, allowed_exits, barriers):
    changed = True
    out = mask
    while changed:
        changed = False
        for u in range(n):
            if not ((out >> u) & 1):
                continue
            for v in adj[u]:
                if (out >> v) & 1:
                    continue
                if v in barriers:
                    continue
                if side[u] == side[v]:
                    continue
                if edge(u, v) in allowed_exits:
                    continue
                out |= 1 << v
                changed = True
    return out


def best_lmax_switch(n, adj, side, st, v):
    _M, ell, _T, _mu, cyc = st
    Lmax = max((ell[f] for f, paths in cyc.items() for p in paths if v in p), default=None)
    best = None
    for L, rev, sign, mask, hits in bundle_candidates(ell, cyc, v):
        if L != Lmax:
            continue
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        if not Bconn(n, adj, flip_side(side, mask)):
            continue
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None or det["psi"] <= 0:
            continue
        cand = (mask.bit_count(), -det["psi"], L, rev, sign, mask, hits, det)
        if best is None or cand < best:
            best = cand
    return best


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def subset_iter(items, max_all, rng, random_subsets):
    m = len(items)
    if m <= max_all:
        for r in range(1, m + 1):
            for comb in itertools.combinations(items, r):
                yield tuple(comb)
    else:
        seen = set()
        # Always include singleton, full set, and threshold-like prefixes.
        for x in items:
            seen.add((x,))
        seen.add(tuple(items))
        for _ in range(random_subsets):
            sub = tuple(x for x in items if rng.random() < 0.5)
            if sub:
                seen.add(sub)
        for sub in seen:
            yield sub


def scan_cut(name, n, adj, side, acc, max_all, random_subsets, rng):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        acc["neg"] += 1
        best = best_lmax_switch(n, adj, side, st, v)
        if best is None:
            acc["no_switch"] += 1
            continue
        _size, _negpsi, L, _rev, sign, switch_mask, _hits, det = best
        cross = list(det["cross_m"])
        for Y_tuple in subset_iter(cross, max_all, rng, random_subsets):
            Y = set(Y_tuple)
            acc["subsets"] += 1
            exits, raw = exits_and_prefix_mask(st, switch_mask, Y)
            barriers = far_endpoint_barriers(switch_mask, Y)
            closed = close_over_nonexit_B(n, adj, side, raw, exits, barriers)
            bdy_b, bdy_m = boundary_sets(n, adj, side, closed)
            if not bdy_b <= exits:
                acc["fail_boundary"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        "boundary",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        len(cross),
                        len(Y),
                        sorted(Y),
                        sorted(bdy_b - exits),
                        sorted(exits),
                        mask_tuple(n, closed),
                    )
            if not Y <= bdy_m:
                acc["fail_cross"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (
                        "cross",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        len(cross),
                        len(Y),
                        sorted(Y - bdy_m),
                        sorted(exits),
                        mask_tuple(n, closed),
                    )
            if len(exits) < len(Y):
                acc["hall_fail"] += 1
                if acc["first_hall_fail"] is None:
                    acc["first_hall_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        len(cross),
                        len(Y),
                        len(exits),
                        sorted(Y),
                        sorted(exits),
                    )


def scan_graph(name, n, edges, acc, max_all, random_subsets, rng):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_all, random_subsets, rng)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=4)
    parser.add_argument("--random", type=int, default=80)
    parser.add_argument("--max-all", type=int, default=12)
    parser.add_argument("--random-subsets", type=int, default=300)
    args = parser.parse_args()

    rng = random.Random(2112)
    acc = dict(
        neg=0,
        no_switch=0,
        subsets=0,
        fail_boundary=0,
        fail_cross=0,
        hall_fail=0,
        first_fail=None,
        first_hall_fail=None,
    )

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc, args.max_all, args.random_subsets, rng)
        print("N=%d neg=%d subsets=%d fail=%d" % (n, acc["neg"], acc["subsets"], acc["fail_boundary"] + acc["fail_cross"]), flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc, args.max_all, args.random_subsets, rng)
        print("H%d neg=%d subsets=%d fail=%d" % (t, acc["neg"], acc["subsets"], acc["fail_boundary"] + acc["fail_cross"]), flush=True)

    if args.random:
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
            scan_graph("rand%d" % made, n, edges, acc, args.max_all, args.random_subsets, rng)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("neg:", acc["neg"], "no_switch:", acc["no_switch"])
    print("subsets:", acc["subsets"])
    print("boundary closure failures:", acc["fail_boundary"])
    print("cross preservation failures:", acc["fail_cross"])
    print("Hall count failures:", acc["hall_fail"], acc["first_hall_fail"] or "")
    print("first closure fail:", acc["first_fail"] or "")


if __name__ == "__main__":
    main()
