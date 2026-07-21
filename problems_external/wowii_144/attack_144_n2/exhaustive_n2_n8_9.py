#!/usr/bin/env python3
"""Exact Candidate-N2 sweep over every connected graph of orders 8 and 9."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
W144 = HERE.parent
W141 = W144.parent / "wowii_141" / "oracle"
sys.path[:0] = [str(W141), str(W144 / "oracle_exhaustive"),
                str(W144 / "proverC"), str(W144 / "wave2")]

from invariants import (  # noqa: E402
    all_pairs_dist,
    dist_to_set,
    ecc_of_set,
    eccentricities,
    girth,
)
from run_sweep import parse_graph6, shortest_cycle_vertex_sets  # noqa: E402
from test_gpt_n2 import (  # noqa: E402
    bits,
    components_outside,
    mz_values,
)

GENG = Path("E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe")
OUT = HERE / "exhaustive_n2_n8_9_results.json"
WORKERS = 8


def check(line: str):
    n, adj = parse_graph6(line)
    g = girth(n, adj)
    if g < 5:
        return ("skip",)
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r, D = min(ecc), max(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == r)
    e = ecc_of_set(n, dist, center)
    if e == 0 or e <= D - g // 2:
        return ("nonresidual",)
    realizers = [v for v in range(n) if dist_to_set(dist, v, center) == e]
    cycles, cap = shortest_cycle_vertex_sets(n, adj, g, 5000)
    assert not cap
    for K in cycles:
        kmask = sum(1 << v for v in K)
        comps = components_outside(adj, ((1 << n) - 1) & ~kmask)
        mz = mz_values(n, adj, K)
        for x in realizers:
            h = dist_to_set(dist, x, kmask)
            if h >= e:
                return ("ok",)
            for m in (a for a in K if dist[x][a] == h):
                W = [a for a in K if dist[a][m] <= e - h - 1]
                covsum = sum(
                    sum(max(dist[s][y] for y in bits(H)) >= r + 1
                        for s in W)
                    for H in comps
                )
                for z in K:
                    if z != m and covsum <= 2 * (mz[z] - h):
                        return ("ok",)
    return ("fail", line.strip(), n, g, r, D, e, realizers,
            [list(K) for K in cycles])


def main() -> None:
    t0 = time.time()
    result = {"test": "WOWII144_Candidate_N2_exhaustive_n8_9",
              "generator": "nauty geng 2.8.9 -c", "per_n": {},
              "failures": []}
    with Pool(WORKERS) as pool:
        for n in (8, 9):
            proc = subprocess.run([str(GENG), "-c", "-q", str(n)],
                                  capture_output=True, text=True, check=True)
            lines = proc.stdout.split()
            counts = {"connected": len(lines), "girth_lt_5": 0,
                      "nonresidual": 0, "residual": 0, "failures": 0}
            for rec in pool.imap_unordered(check, lines, chunksize=256):
                tag = rec[0]
                if tag == "skip":
                    counts["girth_lt_5"] += 1
                elif tag == "nonresidual":
                    counts["nonresidual"] += 1
                else:
                    counts["residual"] += 1
                    if tag == "fail":
                        counts["failures"] += 1
                        result["failures"].append(rec[1:])
            result["per_n"][str(n)] = counts
            print(n, counts, flush=True)
    result["elapsed_sec"] = round(time.time() - t0, 2)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()
    OUT.with_suffix(".json.sha256").write_text(digest + "  " + OUT.name + "\n")
    print("wrote", OUT)
    print("sha256", digest)


if __name__ == "__main__":
    main()
