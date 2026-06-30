"""Gate a matching form of the length-bundle selector.

This strengthens the tail-dominance gate.  For a terminal-shadow switch S,
let crossing bad edges be C and old B-boundary exits be E.  For each boundary
exit e, witnesses[e] is the set of crossing bad edges whose shortest row exits
S through e, and lambda(e) is the minimum length among those witnesses.

For every cutoff t, the matching atom asks that the short crossing bad edges

    C_<t = {f in C : ell(f) < t}

can be matched injectively into the short exits

    E_<t = {e in E : lambda(e) < t}

using only witness incidences f -> e.  This implies the short-count inequality
for every cutoff, hence the crossing length multiset tail-dominates the
boundary witness-length multiset.
"""

import argparse
import random
import subprocess

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec, maxcut_all
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


def witness_data(n, adj, side, st, mask):
    _M, ell, _T, _mu, cyc = st
    cross = []
    boundary = []
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if ((mask >> u) & 1) == ((mask >> v) & 1):
                continue
            e = edge(u, v)
            if side[u] == side[v]:
                cross.append(e)
            else:
                boundary.append(e)

    witnesses = {e: [] for e in boundary}
    for f in cross:
        u, v = f
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
    lambdas = {e: min(ell[f] for f in fs) for e, fs in witnesses.items()}
    return cross, boundary, witnesses, lambdas, ell


def has_matching(left, right, adjmap):
    match_right = {}

    def dfs(x, seen):
        for y in adjmap.get(x, []):
            if y in seen:
                continue
            seen.add(y)
            if y not in match_right or dfs(match_right[y], seen):
                match_right[y] = x
                return True
        return False

    for x in left:
        if not dfs(x, set()):
            return False
    return True


def cutoff_matching_atom(data):
    cross, boundary, witnesses, lambdas, ell = data
    levels = sorted(set([ell[f] for f in cross] + list(lambdas.values())))
    strict = False
    for t in levels:
        left = [f for f in cross if ell[f] < t]
        right = [e for e in boundary if lambdas[e] < t]
        adjmap = {f: [e for e in right if f in witnesses[e]] for f in left}
        if not has_matching(left, right, adjmap):
            return False
        if len([f for f in cross if ell[f] >= t]) > len([e for e in boundary if lambdas[e] >= t]):
            strict = True
    return strict


def find_matching_switch(n, adj, side, st, v):
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
        data = witness_data(n, adj, side, st, mask)
        if data is None or not cutoff_matching_atom(data):
            continue
        cross, _boundary, _witnesses, lambdas, ell = data
        cand = (
            psi,
            -mask.bit_count(),
            mask,
            tuple(sorted(ell[f] for f in cross)),
            tuple(sorted(lambdas.values())),
        )
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
        best = find_matching_switch(n, adj, side, st, v)
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
            continue
        psi, _negsize, mask, cross_lengths, boundary_lengths = best
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
                    cross_lengths,
                    boundary_lengths,
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

    acc = dict(negative=0, covered=0, fail=0, first_fail=None, psi_hist={}, examples=[], example_limit=args.examples)

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print("census N=%d negative=%d covered=%d fail=%d" % (n, acc["negative"], acc["covered"], acc["fail"]), flush=True)

    from _hardy_gate import maxcut_ls

    gr_n, gr_e = mycielski(5, Cn(5))
    m2_n, m2_e = mycielski(gr_n, gr_e)
    adj = adj_from_edges(m2_n, m2_e)
    scan_cut("MycGrotzsch_N23", m2_n, adj, maxcut_ls(m2_n, adj), acc)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)

    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (2, 2, 2, 2, 2)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 13:
            scan_graph("blow%s" % (sizes,), n, edges, acc)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(isl, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    scan_graph("isl", n, edges, acc)

    if args.random:
        rng = random.Random(2468)
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
