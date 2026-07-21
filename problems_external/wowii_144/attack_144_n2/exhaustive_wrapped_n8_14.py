#!/usr/bin/env python3
"""Exact wrapped-N2 sweep of all connected triangle/square-free graphs, n=8..14."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "n2base", HERE / "exhaustive_n2_n8_9.py")
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)
OUT = HERE / "exhaustive_wrapped_n2_n8_14_results.json"


def check(line: str):
    n, adj = BASE.parse_graph6(line)
    g = BASE.girth(n, adj)
    if g < 5:
        return "skip"
    dist = BASE.all_pairs_dist(n, adj)
    ecc = BASE.eccentricities(n, dist)
    r, D = min(ecc), max(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == r)
    e = BASE.ecc_of_set(n, dist, center)
    if e == 0 or e <= D - g // 2:
        return "nonresidual"
    realizers = [v for v in range(n)
                 if BASE.dist_to_set(dist, v, center) == e]
    cycles, cap = BASE.shortest_cycle_vertex_sets(n, adj, g, 5000)
    assert not cap
    for K in cycles:
        kmask = sum(1 << v for v in K)
        comps = BASE.components_outside(adj, ((1 << n) - 1) & ~kmask)
        mz = BASE.mz_values(n, adj, K)
        for x in realizers:
            h = BASE.dist_to_set(dist, x, kmask)
            if h >= e:
                return "ok"
            for m in (a for a in K if dist[x][a] == h):
                delta = e - h
                W = [a for a in K if dist[a][m] <= delta - 1]
                covsum = sum(
                    sum(max(dist[s][y] for y in BASE.bits(H)) >= r + 1
                        for s in W)
                    for H in comps)
                correction = max(0, 2 * delta - g)
                if any(z != m and covsum + correction <= 2 * (mz[z] - h)
                       for z in K):
                    return "ok"
    return "fail"


def main() -> None:
    t0 = time.time()
    result = {"test": "WOWII144_wrapped_N2_exhaustive_n8_14",
              "generator": "nauty geng 2.8.9 -c -t -f",
              "per_n": {}}
    for n in range(8, 15):
        proc = subprocess.run(
            [str(BASE.GENG), "-c", "-t", "-f", "-q", str(n)],
            capture_output=True, text=True, check=True)
        lines = proc.stdout.split()
        counts = {"generated": len(lines), "girth_lt_5": 0,
                  "nonresidual": 0, "residual": 0, "failures": 0}
        for line in lines:
            tag = check(line)
            if tag == "skip":
                counts["girth_lt_5"] += 1
            elif tag == "nonresidual":
                counts["nonresidual"] += 1
            else:
                counts["residual"] += 1
                counts["failures"] += tag == "fail"
        result["per_n"][str(n)] = counts
        print(n, counts, flush=True)
    result["elapsed_sec"] = round(time.time() - t0, 2)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()
    OUT.with_suffix(".json.sha256").write_text(digest + "  " + OUT.name + "\n")
    print("sha256", digest)


if __name__ == "__main__":
    main()
