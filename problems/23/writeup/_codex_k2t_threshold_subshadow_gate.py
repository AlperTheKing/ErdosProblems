"""Test the threshold-subshadow proof mechanism for length majorization.

For a selected positive-Psi length-bundle switch S and threshold t, let U_t be
the union of the terminal prefixes inside S of all crossing bad edges f with
ell[f] <= t.  The hoped-for mechanism is:

  delta_B(U_t) subset {e in delta_B(S): lambda_S(e) <= t}

Then max-cut gives |{f in delta_M(S): ell[f]<=t}| <= |{e:lambda(e)<=t}|,
which is the sorted length-majorization certificate.
"""

import argparse
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


def close_inside_switch_over_noncheap_B(n, adj, side, switch_mask, mask, cheap_boundary):
    """Close mask inside switch_mask across B-edges not in cheap_boundary."""
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
                if not ((switch_mask >> v) & 1):
                    continue
                if side[u] == side[v]:
                    continue
                if edge(u, v) in cheap_boundary:
                    continue
                out |= 1 << v
                changed = True
    return out


def close_over_noncheap_B(n, adj, side, mask, cheap_boundary):
    """Close mask across all B-edges not in cheap_boundary."""
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
                if side[u] == side[v]:
                    continue
                if edge(u, v) in cheap_boundary:
                    continue
                out |= 1 << v
                changed = True
    return out


def prefix_mask_for_short_crossing(st, switch_mask, short_cross):
    _M, _ell, _T, _mu, cyc = st
    out = 0
    for f in short_cross:
        u, v = f
        tau = u if ((switch_mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            bits = [(switch_mask >> x) & 1 for x in path]
            if bits[0] != 1:
                continue
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            for x in path[: r + 1]:
                out |= 1 << x
    return out


def best_switch(n, adj, side, st, v):
    _M, ell, _T, _mu, cyc = st
    best = None
    for L, rev, sign, mask, hits in bundle_candidates(ell, cyc, v):
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


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    _M, ell, _T, _mu, _cyc = st
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        acc["neg"] += 1
        best = best_switch(n, adj, side, st, v)
        if best is None:
            acc["no_switch"] += 1
            continue
        _size, _negpsi, L, _rev, sign, mask, _hits, det = best
        bdy_b_S = set(det["bdy_b"])
        cross_m_S = set(det["cross_m"])

        # Recompute lambda per edge for threshold sets.
        witnesses = {e: [] for e in bdy_b_S}
        for f in cross_m_S:
            u, w = f
            tau = u if ((mask >> u) & 1) else w
            for path0 in st[4][f]:
                path = list(path0)
                if path[0] != tau:
                    path = list(reversed(path))
                bits = [(mask >> x) & 1 for x in path]
                r = 0
                while r + 1 < len(bits) and bits[r + 1] == 1:
                    r += 1
                witnesses[edge(path[r], path[r + 1])].append(f)
        lambdas = {e: min(ell[f] for f in fs) for e, fs in witnesses.items()}

        for t in sorted(set(det["cross_lengths"]) | set(det["lambda_lengths"])):
            short_cross = {f for f in cross_m_S if ell[f] <= t}
            cheap_boundary = {e for e in bdy_b_S if lambdas[e] <= t}
            U = prefix_mask_for_short_crossing(st, mask, short_cross)
            U_closed = close_inside_switch_over_noncheap_B(n, adj, side, mask, U, cheap_boundary)
            U_full_closed = close_over_noncheap_B(n, adj, side, U, cheap_boundary)
            bdy_b_U, bdy_m_U = boundary_sets(n, adj, side, U)
            bdy_b_closed, bdy_m_closed = boundary_sets(n, adj, side, U_closed)
            bdy_b_full_closed, bdy_m_full_closed = boundary_sets(n, adj, side, U_full_closed)
            acc["thresholds"] += 1
            if not short_cross <= bdy_m_U:
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
                        t,
                        mask_tuple(n, U),
                        sorted(short_cross - bdy_m_U),
                    )
            if not bdy_b_U <= cheap_boundary:
                acc["fail_boundary_subset"] += 1
                extra = bdy_b_U - cheap_boundary
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
                        t,
                        mask_tuple(n, U),
                        sorted(extra),
                        sorted(cheap_boundary),
                    )
            if len(bdy_b_U) < len(short_cross):
                acc["fail_count"] += 1
                if acc["first_count_fail"] is None:
                    acc["first_count_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        len(bdy_b_U),
                        len(short_cross),
                        mask_tuple(n, U),
                    )
            if len(cheap_boundary) < len(short_cross):
                acc["fail_cheap_count"] += 1
                if acc["first_cheap_count_fail"] is None:
                    acc["first_cheap_count_fail"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        len(cheap_boundary),
                        len(short_cross),
                        sorted(cheap_boundary),
                        sorted(short_cross),
                    )
            if len(cheap_boundary) < len(bdy_b_U):
                acc["fail_cheap_dominates_bdy"] += 1
            if not short_cross <= bdy_m_closed:
                acc["fail_closed_cross"] += 1
                if acc["first_closed_fail"] is None:
                    acc["first_closed_fail"] = (
                        "closed-cross",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        mask_tuple(n, U_closed),
                        sorted(short_cross - bdy_m_closed),
                    )
            if not bdy_b_closed <= cheap_boundary:
                acc["fail_closed_boundary_subset"] += 1
                if acc["first_closed_fail"] is None:
                    acc["first_closed_fail"] = (
                        "closed-boundary",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        mask_tuple(n, U_closed),
                        sorted(bdy_b_closed - cheap_boundary),
                        sorted(cheap_boundary),
                    )
            if not short_cross <= bdy_m_full_closed:
                acc["fail_full_closed_cross"] += 1
                if acc["first_full_closed_fail"] is None:
                    acc["first_full_closed_fail"] = (
                        "full-closed-cross",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        mask_tuple(n, U_full_closed),
                        sorted(short_cross - bdy_m_full_closed),
                    )
            if not bdy_b_full_closed <= cheap_boundary:
                acc["fail_full_closed_boundary_subset"] += 1
                if acc["first_full_closed_fail"] is None:
                    acc["first_full_closed_fail"] = (
                        "full-closed-boundary",
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(rv),
                        L,
                        sign,
                        t,
                        mask_tuple(n, U_full_closed),
                        sorted(bdy_b_full_closed - cheap_boundary),
                        sorted(cheap_boundary),
                    )
            acc["extra_boundary_hist"][len(bdy_b_U - cheap_boundary)] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=80)
    args = parser.parse_args()

    acc = dict(
        neg=0,
        no_switch=0,
        thresholds=0,
        fail_cross=0,
        fail_boundary_subset=0,
        fail_count=0,
        fail_cheap_count=0,
        fail_cheap_dominates_bdy=0,
        fail_closed_cross=0,
        fail_closed_boundary_subset=0,
        fail_full_closed_cross=0,
        fail_full_closed_boundary_subset=0,
        first_fail=None,
        first_count_fail=None,
        first_cheap_count_fail=None,
        first_closed_fail=None,
        first_full_closed_fail=None,
        extra_boundary_hist=Counter(),
    )

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print("census N=%d neg=%d thresholds=%d failures=%d" % (n, acc["neg"], acc["thresholds"], acc["fail_boundary_subset"]), flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print("H?AFBo][%d] neg=%d thresholds=%d failures=%d" % (t, acc["neg"], acc["thresholds"], acc["fail_boundary_subset"]), flush=True)

    if args.random:
        rng = random.Random(774)
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
    print("neg:", acc["neg"], "no_switch:", acc["no_switch"])
    print("thresholds:", acc["thresholds"])
    print("short_cross subset delta_M(U) failures:", acc["fail_cross"])
    print("delta_B(U) subset cheap_boundary failures:", acc["fail_boundary_subset"])
    print("count failures |delta_B(U)| < |short_cross|:", acc["fail_count"], acc["first_count_fail"] or "")
    print("cheap count failures |cheap_boundary| < |short_cross|:", acc["fail_cheap_count"], acc["first_cheap_count_fail"] or "")
    print("cheap count < |delta_B(U)| failures:", acc["fail_cheap_dominates_bdy"])
    print("closed short_cross subset delta_M failures:", acc["fail_closed_cross"])
    print("closed delta_B subset cheap_boundary failures:", acc["fail_closed_boundary_subset"], acc["first_closed_fail"] or "")
    print("full-closed short_cross subset delta_M failures:", acc["fail_full_closed_cross"])
    print("full-closed delta_B subset cheap_boundary failures:", acc["fail_full_closed_boundary_subset"], acc["first_full_closed_fail"] or "")
    print("first structural fail:", acc["first_fail"] or "")
    print("extra boundary histogram:", dict(acc["extra_boundary_hist"]))


if __name__ == "__main__":
    main()
