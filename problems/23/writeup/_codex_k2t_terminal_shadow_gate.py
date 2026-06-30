"""Exact gate for GPT-Pro's terminal-shadow K2T switch certificate.

For vertices with negative K2T residual R[v] < 0, this searches the closed
geodesic half-switch family for a switch S that is:

  * cut-neutral,
  * connected after flipping,
  * terminal-geodesic for every crossing bad edge,
  * covering every new bad boundary edge by an old crossing geodesic,
  * safe for noncrossing old bad edges,
  * and has Psi(S) > 0.

Psi(S) is old-cut computable:

  sum_{f in dM(S)} ell[f]^2 - sum_{e in dB(S)} lambda_S(e)^2,

where lambda_S(e) is the cheapest crossing bad edge whose old shortest
geodesic exits S through e. The gates imply Gamma(after) <= Gamma(before)-Psi.
"""

import argparse
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_halfswitch_gate import closed_half_switches
from _codex_k2t_switch_probe import (
    adj_from_edges,
    boundary_delta,
    flip_side,
    residuals,
)


def edge(u, v):
    return (u, v) if u < v else (v, u)


def terminal_shadow_psi(n, adj, side, st, mask):
    M, ell, _T, _mu, cyc = st
    bdy_b = set()
    cross_m = []
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            if side[u] == side[v]:
                cross_m.append(edge(u, v))
            else:
                bdy_b.add(edge(u, v))

    witnesses = {e: [] for e in bdy_b}
    for f in cross_m:
        u, v = f
        tau = u if ((mask >> u) & 1) else v
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            if path[0] != tau:
                return None
            bits = [(mask >> x) & 1 for x in path]
            if bits[0] != 1 or bits[-1] != 0:
                return None
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                return None
            if r > len(path) - 2:
                return None
            exit_edge = edge(path[r], path[r + 1])
            if exit_edge not in witnesses:
                return None
            witnesses[exit_edge].append(f)

    if any(not ws for ws in witnesses.values()):
        return None

    for h in M:
        if h in cross_m:
            continue
        safe = False
        for path in cyc[h]:
            if all(edge(path[i], path[i + 1]) not in bdy_b for i in range(len(path) - 1)):
                safe = True
                break
        if not safe:
            return None

    psi = sum(ell[f] * ell[f] for f in cross_m)
    for ws in witnesses.values():
        lam = min(ell[f] for f in ws)
        psi -= lam * lam
    return psi


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        _M, _ell, _T, _mu, cyc = st
        R = residuals(n, adj, side)
        if R is None:
            continue
        cut_has_negative = False
        for v, r in enumerate(R):
            if r >= 0:
                continue
            cut_has_negative = True
            acc["neg_vertices"] += 1
            ok = False
            best = None
            for mask in closed_half_switches(cyc, v):
                if boundary_delta(n, adj, side, mask) != 0:
                    continue
                if not Bconn(n, adj, flip_side(side, mask)):
                    continue
                psi = terminal_shadow_psi(n, adj, side, st, mask)
                if psi is None or psi <= 0:
                    continue
                cand = (mask.bit_count(), psi, mask)
                if best is None or cand < best:
                    best = cand
                ok = True
            if ok:
                acc["covered"] += 1
                size, psi, mask = best
                acc["size_hist"][size] = acc["size_hist"].get(size, 0) + 1
                acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
                if len(acc["examples"]) < acc["example_limit"]:
                    acc["examples"].append(
                        (name, n, "".join(map(str, side)), v, str(r), tuple(i for i in range(n) if (mask >> i) & 1), psi)
                    )
            else:
                acc["fail"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
        if cut_has_negative:
            acc["bad_cuts"] += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    acc = dict(
        bad_cuts=0,
        neg_vertices=0,
        covered=0,
        fail=0,
        first_fail=None,
        size_hist={},
        psi_hist={},
        examples=[],
        example_limit=args.examples,
    )
    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print(
            "census N=%d bad_cuts=%d neg_vertices=%d covered=%d fail=%d"
            % (n, acc["bad_cuts"], acc["neg_vertices"], acc["covered"], acc["fail"]),
            flush=True,
        )

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
