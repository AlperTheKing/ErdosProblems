#!/usr/bin/env python3
"""R3 structure scan: metric-only pass over the same corpus (f, D, girth),
characterizing exactly where T1 (t >= D+1) fails to close C142:
2g + 3f > 3(D+1).  Also: does f = D ever occur (any girth)?  Exact ints."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import networkx as nx

import bridge_oracle as bo

OUT = Path(__file__).resolve().parent / "r3_scan_results.json"


def main():
    tasks = bo.build_corpus()
    per_girth_min_Dmf = {}   # girth -> min over graphs of (D - f)
    fD_examples = []
    members_by_girth = Counter()
    total = 0
    for name, g6s in tasks:
        G = nx.from_graph6_bytes(g6s.encode("ascii"))
        n, adj = bo.nx_to_bitadj(G)
        if n < 2 or not bo.graph_connected(n, adj):
            continue
        g = bo.girth(n, adj)
        if g == 0:
            continue
        dist = bo.all_pairs_dist(n, adj)
        ecc = bo.eccentricities(n, dist)
        D = max(ecc)
        periph = 0
        for v in range(n):
            if ecc[v] == D:
                periph |= 1 << v
        f = bo.ecc_set(n, dist, periph)
        total += 1
        cur = per_girth_min_Dmf.get(g)
        if cur is None or D - f < cur[0]:
            per_girth_min_Dmf[g] = (D - f, f"{name} [{g6s}] n={n} D={D} f={f}")
        if f == D:
            fD_examples.append(f"{name} [{g6s}] n={n} g={g} D={D} f={f}")
        if 2 * g + 3 * f > 3 * (D + 1):
            members_by_girth[g] += 1
    res = {
        "cyclic_graphs": total,
        "f_equals_D_count": len(fD_examples),
        "f_equals_D_examples": fD_examples[:20],
        "min_D_minus_f_by_girth": {
            str(g): {"min": v[0], "witness": v[1]}
            for g, v in sorted(per_girth_min_Dmf.items())},
        "T1_fail_members_by_girth": {
            str(a): b for a, b in sorted(members_by_girth.items())},
    }
    OUT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in
                      ("cyclic_graphs", "f_equals_D_count")}, indent=2))
    print("min D-f by girth:")
    for g, v in sorted(per_girth_min_Dmf.items()):
        print(f"  g={g}: D-f>={v[0]}  ({v[1]})")


if __name__ == "__main__":
    main()
