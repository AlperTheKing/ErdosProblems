"""Gate a stronger, proof-shaped form of NET.

NET says, for a fixed unique geodesic P_f and every interval I on P_f,

    endpoint_tax_P(I) <= #{off-path B-components whose attachment span meets I}.

This script tests the stronger fractional containment-flow statement:
every P-contained atom interval J can be routed to an off-path B-component
whose attachment span contains J, with capacity 1 per component and atom
weight 1/|geodesics(g)|.

Containment-flow => NET, because any interval intersecting J also intersects
any containing component span.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import deque
from fractions import Fraction as F
from multiprocessing import get_context

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def maxflow_fraction(cap, source, sink):
    n = len(cap)
    residual = [row[:] for row in cap]
    value = F(0)

    while True:
        parent = [-1] * n
        parent[source] = source
        q = deque([source])
        while q and parent[sink] < 0:
            u = q.popleft()
            for v, c in enumerate(residual[u]):
                if parent[v] < 0 and c > 0:
                    parent[v] = u
                    q.append(v)
        if parent[sink] < 0:
            return value

        aug = None
        v = sink
        while v != source:
            u = parent[v]
            aug = residual[u][v] if aug is None else min(aug, residual[u][v])
            v = u

        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= aug
            residual[v][u] += aug
            v = u
        value += aug


def atoms_and_spans(n, adj, side, M, cyc, f):
    path = cyc[f][0]
    pos = {x: i for i, x in enumerate(path)}
    path_set = set(path)

    atoms = []
    for g in M:
        if g == f:
            continue
        k = len(cyc[g])
        for Q in cyc[g]:
            if set(Q) <= path_set:
                js = sorted(pos[v] for v in Q)
                atoms.append((js[0], js[-1], F(1, k), g))

    rest = [v for v in range(n) if v not in path_set]
    if not rest:
        return atoms, []

    parent = {v: v for v in rest}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u in rest:
        for w in adj[u]:
            if w not in path_set and side[u] != side[w]:
                parent[find(u)] = find(w)

    components = {}
    for v in rest:
        components.setdefault(find(v), set()).add(v)

    spans = []
    for C in components.values():
        attachments = {
            pos[x]
            for u in C
            for x in adj[u]
            if x in path_set and side[u] != side[x]
        }
        if attachments:
            spans.append((min(attachments), max(attachments), len(C)))

    return atoms, spans


def containment_flow(atoms, spans):
    A = len(atoms)
    C = len(spans)
    source = 0
    atom0 = 1
    span0 = 1 + A
    sink = 1 + A + C
    n = sink + 1
    cap = [[F(0) for _ in range(n)] for __ in range(n)]

    total = F(0)
    for i, (lo, hi, w, _g) in enumerate(atoms):
        cap[source][atom0 + i] = w
        total += w
        for j, (a, b, _size) in enumerate(spans):
            if a <= lo and hi <= b:
                cap[atom0 + i][span0 + j] = w

    for j in range(C):
        cap[span0 + j][sink] = F(1)

    return maxflow_fraction(cap, source, sink), total


def check_cut(n, adj, side, name):
    st = struct_for_side(n, adj, side)
    if st is None:
        return 0, None
    M, _ell, _T, _mu, cyc = st
    checked = 0
    for f in M:
        if len(cyc[f]) != 1:
            continue
        atoms, spans = atoms_and_spans(n, adj, side, M, cyc, f)
        if not atoms:
            continue
        checked += 1
        flow, total = containment_flow(atoms, spans)
        if flow < total:
            return checked, (name, "".join(map(str, side)), f, total, flow, atoms, spans)
    return checked, None


def graph_probe(g6):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    checked = 0
    for side in cuts:
        c, fail = check_cut(n, adj, side, g6)
        checked += c
        if fail is not None:
            return checked, fail
    return checked, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=32)
    args = ap.parse_args()

    total_checked = 0
    for nn in range(5, args.max_n + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(nn)], capture_output=True, text=True
        ).stdout.split()
        n_checked = 0
        fail = None
        if args.workers > 1:
            ctx = get_context("spawn")
            with ctx.Pool(args.workers) as pool:
                for checked, res in pool.imap_unordered(
                    graph_probe, graphs, chunksize=args.chunksize
                ):
                    n_checked += checked
                    if res is not None:
                        fail = res
                        pool.terminate()
                        break
        else:
            for g6 in graphs:
                checked, res = graph_probe(g6)
                n_checked += checked
                if res is not None:
                    fail = res
                    break
        total_checked += n_checked
        print(f"N={nn} checked_unique_rows={n_checked} fail={fail}", flush=True)
        if fail is not None:
            break
    print(f"TOTAL checked_unique_rows={total_checked}", flush=True)


if __name__ == "__main__":
    main()
