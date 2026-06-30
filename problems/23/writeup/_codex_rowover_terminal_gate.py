"""Gate the row-overload form of the K2T terminal-shadow construction.

The exact algebraic identity is

    -R[v] = sum_{f,Q contains v} (sum_{x in Q} T[x] - N*ell[f]) / |cyc[f]|.

Thus R[v] < 0 is a positive weighted average of row-overload through v.
This script tests the sharper construction target:

    if v lies on at least one positive-overload row, then v has a
    length-bundle terminal-shadow switch with Psi>0.

The identity is checked exactly using Fractions.
"""

import argparse
import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


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


def has_positive_terminal_switch(n, adj, side, st, v):
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
        cand = (psi, -mask.bit_count(), mask)
        if best is None or cand > best:
            best = cand
    return best


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    R = residuals(n, adj, side)
    if R is None:
        return

    row_average = [F(0)] * n
    positive_row = [False] * n
    positive_row_count = [0] * n
    for f, paths in cyc.items():
        L = ell[f]
        denom = F(len(paths))
        for path in paths:
            vertices = set(path)
            over = sum(T[x] for x in vertices) - F(n * L)
            for v in vertices:
                row_average[v] += over / denom
                if over > 0:
                    positive_row[v] = True
                    positive_row_count[v] += 1

    for v in range(n):
        acc["vertices"] += 1
        if row_average[v] != -R[v]:
            acc["identity_fail"] += 1
            if acc["first_identity_fail"] is None:
                acc["first_identity_fail"] = (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(row_average[v]),
                    str(-R[v]),
                )
            continue

        if positive_row[v]:
            acc["rowpos_vertices"] += 1
            best = has_positive_terminal_switch(n, adj, side, st, v)
            if best is None:
                acc["rowpos_no_switch"] += 1
                if acc["first_rowpos_no_switch"] is None:
                    acc["first_rowpos_no_switch"] = (
                        name,
                        n,
                        "".join(map(str, side)),
                        v,
                        str(R[v]),
                        positive_row_count[v],
                    )
            else:
                psi, _negsize, mask = best
                acc["covered"] += 1
                acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
                if len(acc["examples"]) < acc["example_limit"]:
                    acc["examples"].append(
                        (
                            name,
                            n,
                            "".join(map(str, side)),
                            v,
                            str(R[v]),
                            positive_row_count[v],
                            psi,
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
    parser.add_argument("--examples", type=int, default=20)
    args = parser.parse_args()

    acc = dict(
        vertices=0,
        identity_fail=0,
        first_identity_fail=None,
        rowpos_vertices=0,
        covered=0,
        rowpos_no_switch=0,
        first_rowpos_no_switch=None,
        psi_hist={},
        examples=[],
        example_limit=args.examples,
    )

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print(
            "census N=%d vertices=%d rowpos=%d covered=%d fail=%d"
            % (n, acc["vertices"], acc["rowpos_vertices"], acc["covered"], acc["rowpos_no_switch"]),
            flush=True,
        )

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print(
            "H?AFBo][%d] vertices=%d rowpos=%d covered=%d fail=%d"
            % (t, acc["vertices"], acc["rowpos_vertices"], acc["covered"], acc["rowpos_no_switch"]),
            flush=True,
        )

    if args.random:
        rng = random.Random(456)
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
    print("vertices:", acc["vertices"])
    print("identity failures:", acc["identity_fail"], acc["first_identity_fail"] or "")
    print("positive-row vertices:", acc["rowpos_vertices"])
    print("covered:", acc["covered"])
    print("rowpos no switch:", acc["rowpos_no_switch"], acc["first_rowpos_no_switch"] or "")
    print("Psi histogram:", dict(sorted(acc["psi_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)
    verdict = acc["identity_fail"] == 0 and acc["rowpos_no_switch"] == 0
    print("VERDICT:", "PASS" if verdict else "FAIL")


if __name__ == "__main__":
    main()
