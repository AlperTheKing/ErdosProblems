"""Terminal-shadow gate using repaired length-bundle half-switches.

The older terminal-shadow gate used the per-bad-edge half-switch family.
That family is too narrow on H?AFBo][2].  This script uses the repaired
equal-length geodesic bundle switches from _codex_k2t_lenbundle_switch_gate.
"""

import argparse
import random
import subprocess

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
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


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    _M, ell, _T, _mu, cyc = st
    R = residuals(n, adj, side)
    if R is None:
        return

    cut_has_negative = False
    for v, r in enumerate(R):
        if r >= 0:
            continue
        cut_has_negative = True
        acc["neg_vertices"] += 1
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
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
            continue

        _size, _negpsi, mask, psi = best
        acc["covered"] += 1
        acc["size_hist"][mask.bit_count()] = acc["size_hist"].get(mask.bit_count(), 0) + 1
        acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
        if len(acc["examples"]) < acc["example_limit"]:
            acc["examples"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(r),
                    tuple(i for i in range(n) if (mask >> i) & 1),
                    psi,
                )
            )
    if cut_has_negative:
        acc["bad_cuts"] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def new_acc(example_limit):
    return dict(
        bad_cuts=0,
        neg_vertices=0,
        covered=0,
        fail=0,
        first_fail=None,
        size_hist={},
        psi_hist={},
        examples=[],
        example_limit=example_limit,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
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
    print("Psi histogram:", dict(sorted(acc["psi_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)


if __name__ == "__main__":
    main()
