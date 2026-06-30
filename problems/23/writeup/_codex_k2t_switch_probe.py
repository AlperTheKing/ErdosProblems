"""Codex probe for the K2T gamma-minimality bridge.

For connected-B maximum cuts (not necessarily gamma-min), compute the exact
K2T residual

    R[v] = N*T[v] - (K2*T)[v].

For every vertex with R[v] < 0, exhaustively search switches S containing v
such that:

    delta_B(S) = delta_M(S)          (cut size preserved)
    B after flipping S is connected
    Gamma(after) < Gamma(before)

This is evidence for the contrapositive bridge:
negative K2T residual => neutral Gamma-descent, so gamma-min cuts have R>=0.
"""

import argparse
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def flip_side(side, mask):
    out = side[:]
    v = 0
    while mask:
        if mask & 1:
            out[v] ^= 1
        mask >>= 1
        v += 1
    return out


def boundary_delta(n, adj, side, mask):
    dB = 0
    dM = 0
    for u in range(n):
        inu = (mask >> u) & 1
        for v in adj[u]:
            if v <= u:
                continue
            if inu == ((mask >> v) & 1):
                continue
            if side[u] == side[v]:
                dM += 1
            else:
                dB += 1
    return dB - dM


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return 0
    _M, ell, _T, _mu, _cyc = st
    return sum(ell[f] * ell[f] for f in ell)


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def best_descent_switch(n, adj, side, gamma0, v):
    best = None
    full = (1 << n) - 1
    for mask in range(1, full):
        if not ((mask >> v) & 1):
            continue
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        side2 = flip_side(side, mask)
        gamma2 = gamma_of(n, adj, side2)
        if gamma2 is None or gamma2 >= gamma0:
            continue
        size = mask.bit_count()
        drop = gamma0 - gamma2
        cand = (size, -drop, mask, gamma2)
        if best is None or cand < best:
            best = cand
    return best


def side_str(side):
    return "".join(str(x) for x in side)


def mask_tuple(n, mask):
    return tuple(v for v in range(n) if (mask >> v) & 1)


def scan_graph(name, n, edges, limit_examples, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        gamma0 = gamma_of(n, adj, side)
        if gamma0 is None or gamma0 == 0:
            continue
        R = residuals(n, adj, side)
        if R is None:
            continue
        neg = [v for v, r in enumerate(R) if r < 0]
        if not neg:
            continue
        acc["bad_cuts"] += 1
        for v in neg:
            acc["neg_vertices"] += 1
            best = best_descent_switch(n, adj, side, gamma0, v)
            if best is None:
                acc["no_switch"] += 1
                if len(acc["examples"]) < limit_examples:
                    acc["examples"].append((name, n, side_str(side), gamma0, v, str(R[v]), None))
                continue
            size, negdrop, mask, gamma2 = best
            drop = -negdrop
            acc["covered"] += 1
            acc["size_hist"][size] = acc["size_hist"].get(size, 0) + 1
            acc["drop_hist"][drop] = acc["drop_hist"].get(drop, 0) + 1
            if len(acc["examples"]) < limit_examples:
                acc["examples"].append(
                    (name, n, side_str(side), gamma0, v, str(R[v]), mask_tuple(n, mask), gamma2, drop)
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument("--examples", type=int, default=12)
    args = parser.parse_args()
    acc = dict(
        bad_cuts=0,
        neg_vertices=0,
        covered=0,
        no_switch=0,
        size_hist={},
        drop_hist={},
        examples=[],
    )
    for n in range(args.min_n, args.max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        for g6 in graphs:
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, args.examples, acc)
        print(
            "N=%d bad_cuts=%d neg_vertices=%d covered=%d no_switch=%d"
            % (n, acc["bad_cuts"], acc["neg_vertices"], acc["covered"], acc["no_switch"]),
            flush=True,
        )
    print("=" * 72)
    print("bad cuts with some R[v]<0:", acc["bad_cuts"])
    print("negative vertices:", acc["neg_vertices"])
    print("covered by neutral B-connected Gamma descent:", acc["covered"])
    print("NO-SWITCH:", acc["no_switch"])
    print("switch size histogram:", dict(sorted(acc["size_hist"].items())))
    print("Gamma drop histogram:", dict(sorted(acc["drop_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)


if __name__ == "__main__":
    main()
