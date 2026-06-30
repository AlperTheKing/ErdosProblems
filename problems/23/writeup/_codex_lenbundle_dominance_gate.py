"""Gate a dominance form of the length-bundle terminal-shadow selector.

For a switch S, let C(S) be the multiset of lengths of crossing bad edges and
let L(S) be the multiset of boundary-exit witness lengths lambda(e).  If C
strictly tail-dominates L,

    #{c in C : c >= t} >= #{l in L : l >= t} for every t,
    with strict inequality for some t,

then sum C^2 > sum L^2, hence terminal Psi(S)>0 once the terminal-shadow
conditions hold.

This script gates the sharper construction target:

    R[v] < 0 => some length-bundle switch through v is neutral,
               B-connected, terminal-shadow valid, and has strict
               tail-dominance C(S) >_tail L(S).
"""

import argparse
import random
import subprocess

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec, maxcut_all
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import odd_blowup
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import edge, terminal_shadow_psi


def connected(adj):
    if not adj:
        return True
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def length_multisets(n, adj, side, st, mask):
    _M, ell, _T, _mu, cyc = st
    cross_lengths = []
    boundary = []
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if ((mask >> u) & 1) == ((mask >> v) & 1):
                continue
            e = edge(u, v)
            if side[u] == side[v]:
                cross_lengths.append(ell[e])
            else:
                boundary.append(e)

    witnesses = {e: [] for e in boundary}
    for f in ell:
        u, v = f
        if ((mask >> u) & 1) == ((mask >> v) & 1):
            continue
        tau = u if ((mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            if path[0] != tau:
                continue
            bits = [(mask >> x) & 1 for x in path]
            if bits[0] != 1 or bits[-1] != 0:
                continue
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                continue
            exit_edge = edge(path[r], path[r + 1])
            if exit_edge in witnesses:
                witnesses[exit_edge].append(f)

    if any(not fs for fs in witnesses.values()):
        return None
    boundary_lengths = [min(ell[f] for f in fs) for fs in witnesses.values()]
    return cross_lengths, boundary_lengths


def strict_tail_dominates(left, right):
    if not left and right:
        return False
    strict = False
    for level in sorted(set(left + right)):
        lcnt = sum(1 for x in left if x >= level)
        rcnt = sum(1 for x in right if x >= level)
        if lcnt < rcnt:
            return False
        if lcnt > rcnt:
            strict = True
    return strict


def find_dominating_switch(n, adj, side, st, v):
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
        multisets = length_multisets(n, adj, side, st, mask)
        if multisets is None:
            continue
        cross, boundary = multisets
        if not strict_tail_dominates(cross, boundary):
            continue
        cand = (psi, -mask.bit_count(), mask, tuple(sorted(cross)), tuple(sorted(boundary)))
        if best is None or cand > best:
            best = cand
    return best


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return

    for v, r in enumerate(R):
        if r >= 0:
            continue
        acc["negative"] += 1
        best = find_dominating_switch(n, adj, side, st, v)
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
            continue
        psi, _negsize, mask, cross, boundary = best
        acc["covered"] += 1
        acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
        if len(acc["examples"]) < acc["example_limit"]:
            acc["examples"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(r),
                    psi,
                    cross,
                    boundary,
                    tuple(i for i in range(n) if (mask >> i) & 1),
                )
            )


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
    parser.add_argument("--examples", type=int, default=16)
    args = parser.parse_args()

    acc = dict(
        negative=0,
        covered=0,
        fail=0,
        first_fail=None,
        psi_hist={},
        examples=[],
        example_limit=args.examples,
    )

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print("census N=%d negative=%d covered=%d fail=%d" % (n, acc["negative"], acc["covered"], acc["fail"]), flush=True)

    # Mycielskian guardrail.
    gr_n, gr_e = mycielski(5, Cn(5))
    m2_n, m2_e = mycielski(gr_n, gr_e)
    adj = adj_from_edges(m2_n, m2_e)
    # Reuse deterministic local-search max cut from _hardy_gate to avoid
    # importing all of the construction gate.
    from _hardy_gate import maxcut_ls

    scan_cut("MycGrotzsch_N23", m2_n, adj, maxcut_ls(m2_n, adj), acc)
    print("after Myc23 negative=%d covered=%d fail=%d" % (acc["negative"], acc["covered"], acc["fail"]), flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print("H?AFBo][%d] negative=%d covered=%d fail=%d" % (t, acc["negative"], acc["covered"], acc["fail"]), flush=True)

    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (2, 2, 2, 2, 2)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 13:
            scan_graph("blow%s" % (sizes,), n, edges, acc)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(isl, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    scan_graph("isl", n, edges, acc)
    print("after blowups+island negative=%d covered=%d fail=%d" % (acc["negative"], acc["covered"], acc["fail"]), flush=True)

    if args.random:
        rng = random.Random(789)
        made = 0
        tries = 0
        while made < args.random and tries < 100000:
            tries += 1
            n = rng.choice([11, 12])
            p = rng.uniform(0.14, 0.32)
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
            if not edges or not is_triangle_free(n, edges):
                continue
            adj = adj_from_edges(n, edges)
            if any(not adj[v] for v in range(n)) or not connected(adj):
                continue
            made += 1
            scan_graph("rand%d" % made, n, edges, acc)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("negative:", acc["negative"])
    print("covered:", acc["covered"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("Psi histogram:", dict(sorted(acc["psi_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
