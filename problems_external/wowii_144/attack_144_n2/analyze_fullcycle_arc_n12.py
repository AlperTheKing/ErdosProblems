#!/usr/bin/env python3
"""Structural diagnostics for the exact W144 full-cycle metric frontier."""
from __future__ import annotations

import collections
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
W144 = ROOT / "problems_external" / "wowii_144"
HERE = Path(__file__).resolve().parent
sys.path[:0] = [
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(W144 / "oracle"),
    str(W144 / "oracle_exhaustive"),
    str(W144 / "proverC"),
    str(W144 / "wave2"),
    str(HERE),
]
from invariants import all_pairs_dist, eccentricities, girth
from run_sweep import parse_graph6, shortest_cycle_vertex_sets
from test_gpt_n2 import bits, components_outside
from verify_ordinary_triameter_n14 import atts

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"
OUT = HERE / "fullcycle_arc_diagnostic_n7_12.json"


def cycle_order(adj, K):
    ks = set(K)
    start = min(ks)
    first = min(v for v in ks if (adj[start] >> v) & 1)
    order = [start, first]
    while len(order) < len(K):
        prev, cur = order[-2], order[-1]
        nxt = next(v for v in ks if v != prev and (adj[cur] >> v) & 1)
        order.append(nxt)
    assert (adj[order[-1]] >> start) & 1
    return order


def jdata(adj, K, H, z):
    hv = list(bits(H))
    loc = {v: i for i, v in enumerate(hv)}
    rho = len(hv)
    ja = [0] * (rho + 1)
    legal = sum(1 << v for v in K) & ~(1 << z)
    for v in hv:
        i = loc[v]
        for w in bits(adj[v] & H):
            ja[i] |= 1 << loc[w]
        if adj[v] & legal:
            ja[i] |= 1 << rho
            ja[rho] |= 1 << i
    dd = []
    for s in range(len(ja)):
        d = [10**9] * len(ja)
        d[s] = 0
        queue = [s]
        for u in queue:
            for v in bits(ja[u]):
                if d[v] == 10**9:
                    d[v] = d[u] + 1
                    queue.append(v)
        dd.append(d)
    p = {v: dd[rho][loc[v]] for v in hv}
    perim = {(u, v): p[u] + p[v] + dd[loc[u]][loc[v]] for u in hv for v in hv}
    return p, perim


def cyclic_components(order, E):
    mark = [v in E for v in order]
    if not any(mark):
        return 0
    if all(mark):
        return 1
    return sum(mark[i] and not mark[i - 1] for i in range(len(mark)))


def main():
    stats = collections.Counter()
    examples = collections.defaultdict(list)
    for n in range(7, 13):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            capture_output=True,
            text=True,
            check=True,
        )
        for g6 in proc.stdout.split():
            N, adj = parse_graph6(g6)
            g = girth(N, adj)
            if g < 7 or g > N:
                continue
            dist = all_pairs_dist(N, adj)
            r = min(eccentricities(N, dist))
            lam = 2 * r + 1 - g
            cycles, capped = shortest_cycle_vertex_sets(N, adj, g, 20000)
            assert not capped
            for K in cycles:
                order = cycle_order(adj, K)
                km = sum(1 << v for v in K)
                for H in components_outside(adj, ((1 << N) - 1) & ~km):
                    A = atts(adj, K, H)
                    for z in K:
                        if not (set(A) - {z}):
                            continue
                        stats["records"] += 1
                        E = {
                            s
                            for s in K
                            if max(dist[s][y] for y in bits(H)) >= r + 1
                        }
                        cc = cyclic_components(order, E)
                        stats[f"E_components_{cc}"] += 1
                        if cc > 1:
                            stats["nonarc"] += 1
                            if len(examples["nonarc"]) < 10:
                                examples["nonarc"].append(dict(graph6=g6, K=order, H=list(bits(H)), z=z, E=sorted(E)))
                            continue
                        if not E or E == set(K):
                            continue
                        endpoints = [
                            v
                            for v in E
                            if any(((adj[v] >> w) & 1) and w not in E for w in K)
                        ]
                        if len(E) == 1:
                            endpoints = [next(iter(E)), next(iter(E))]
                        assert len(endpoints) == 2
                        uys = [y for y in bits(H) if dist[endpoints[0]][y] >= r + 1]
                        vys = [y for y in bits(H) if dist[endpoints[1]][y] >= r + 1]
                        p, perim = jdata(adj, K, H, z)
                        best = max(perim[u, v] for u in uys for v in vys)
                        need = len(E) + lam
                        stats["endpoint_tests"] += 1
                        stats["endpoint_min_slack"] = min(stats.get("endpoint_min_slack", 10**9), best - need)
                        if best < need:
                            stats["endpoint_failures"] += 1
                            if len(examples["endpoint_failures"]) < 20:
                                examples["endpoint_failures"].append(
                                    dict(graph6=g6, n=N, g=g, r=r, lambda_=lam, K=order,
                                         H=list(bits(H)), A=A, z=z, E=sorted(E), endpoints=endpoints,
                                         witnesses=[uys, vys], p=p, best=best, need=need)
                                )
        print(n, dict(stats), flush=True)
    OUT.write_text(json.dumps(dict(stats=stats, examples=examples), indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
