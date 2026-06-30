"""Test canonical shortest-tier choices for the witness SDR.

The ordinary tier gate proves only that some minimum-length matching extends.
This diagnostic asks whether a canonical "rare exit first" matching works:

  1. Minimum-length bad edges F0 are matched into minimum-lambda exits E0.
  2. The matching lexicographically maximizes preservation of exits useful to
     longer bad edges, implemented as a min-cost perfect matching on F0 with
     cost (deg_F1(exit), exit-id).  Thus exits with smaller longer-tier degree
     are consumed first.
  3. The remaining exits must be matchable using F1.

This is a proof-scouting gate only.
"""

import argparse
from collections import Counter

from _codex_length_tier_matching_gate import (
    adj_from_edges,
    best_seed_moat_mask,
    h_blowup,
    max_matching,
    residuals,
    scan_graph_allmax,
    stage1_extends,
)
from _csmspec import build_K2
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_signature_gate import terminal_shadow_details

import subprocess


def min_cost_stage0(F0, E0, witnesses, deg_f1):
    """Min-cost matching of F0 into E0 by successive shortest paths."""
    F0 = tuple(F0)
    E0 = tuple(E0)
    rank = {e: i for i, e in enumerate(sorted(E0))}
    n_left = len(F0)
    n_right = len(E0)
    source = n_left + n_right
    sink = source + 1
    graph = [[] for _ in range(sink + 1)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n_left):
        add_edge(source, i, 1, 0)
    for j, e in enumerate(E0):
        add_edge(n_left + j, sink, 1, 0)
    for i, f in enumerate(F0):
        for j, e in enumerate(E0):
            if f in witnesses[e]:
                add_edge(i, n_left + j, 1, deg_f1[e] * 1000 + rank[e])

    flow = 0
    while flow < n_left:
        dist = [None] * len(graph)
        parent = [None] * len(graph)
        dist[source] = 0
        changed = True
        while changed:
            changed = False
            for u, edges in enumerate(graph):
                if dist[u] is None:
                    continue
                for ei, (v, cap, cost, _rev) in enumerate(edges):
                    if cap <= 0:
                        continue
                    nd = dist[u] + cost
                    if dist[v] is None or nd < dist[v]:
                        dist[v] = nd
                        parent[v] = (u, ei)
                        changed = True
        if dist[sink] is None:
            return None
        v = sink
        while v != source:
            u, ei = parent[v]
            edge = graph[u][ei]
            rev = edge[3]
            edge[1] -= 1
            graph[v][rev][1] += 1
            v = u
        flow += 1

    out = {}
    for i, f in enumerate(F0):
        for v, cap, _cost, _rev in graph[i]:
            if n_left <= v < n_left + n_right and cap == 0:
                out[f] = E0[v - n_left]
                break
    return out if len(out) == n_left else None


def canonical_gate(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    min_len = min(ell[f] for f in F_edges)
    min_lam = min(lamb[e] for e in E_edges)
    F0 = tuple(f for f in F_edges if ell[f] == min_len)
    E0 = tuple(e for e in E_edges if lamb[e] == min_lam)
    F1 = tuple(f for f in F_edges if ell[f] > min_len)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}

    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return False, "stage0", dict(F0=len(F0), E0=len(E0))
    ok, e_rem_size, matched = stage1_extends(E_edges, F1, witnesses, set(m0.values()))
    if not ok:
        return False, "stage1", dict(
            F0=len(F0),
            E0=len(E0),
            F1=len(F1),
            E_rem=e_rem_size,
            matched=matched,
            used=tuple(sorted(m0.values())),
            degs=tuple(sorted((e, deg_f1[e]) for e in E0)),
        )
    return True, "ok", dict(F0=len(F0), E0=len(E0), F1=len(F1), E_rem=e_rem_size)


def scan_cut(name, n, adj, side, acc, first, max_add):
    if not Bconn(n, adj, side):
        return first
    st = struct_for_side(n, adj, side)
    if st is None:
        return first
    R = residuals(n, adj, side)
    if R is None:
        return first
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            acc["no_switch"] += 1
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            acc["bad_terminal"] += 1
            continue
        ok, status, info = canonical_gate(st, det)
        acc["tested"] += 1
        acc["status"][status] += 1
        acc["info"][tuple(sorted((k, repr(v)) for k, v in info.items()))] += 1
        if not ok and first is None:
            first = dict(name=name, n=n, side="".join(map(str, side)), v=v, R=str(rv), S=tuple(i for i in range(n) if (mask >> i) & 1), status=status, info=info)
    return first


def scan_allmax(name, n, edges, acc, first, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        first = scan_cut(name, n, adj, side, acc, first, max_add)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    args = parser.parse_args()

    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0, "status": Counter(), "info": Counter()}
    first = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            first = scan_allmax("cen%d" % nn, n, edges, acc, first, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        first = scan_allmax("H2-allmax", n, edges, acc, first, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        first = scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, first, args.max_add)

    print("tested:", acc["tested"], "no_switch:", acc["no_switch"], "bad_terminal:", acc["bad_terminal"])
    print("status:", dict(acc["status"]))
    print("info:")
    for k, v in sorted(acc["info"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(v, dict(k))
    print("first:", first or "")
    print("VERDICT:", "PASS" if first is None else "FAIL")


if __name__ == "__main__":
    main()
