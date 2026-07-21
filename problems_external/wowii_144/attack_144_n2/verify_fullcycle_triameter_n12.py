#!/usr/bin/env python3
"""Exact unrestricted audit of the W144 full-cycle rooted metric lemma."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
W144 = ROOT / "problems_external" / "wowii_144"
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
from verify_ordinary_triameter_n14 import atts, jmetric

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"
OUT = HERE / "fullcycle_triameter_n7_12.json"


def rooted_depths(adj, K, H, z):
    hv = list(bits(H))
    loc = {v: i for i, v in enumerate(hv)}
    rho = len(hv)
    ja = [0] * (rho + 1)
    legal_cycle = sum(1 << v for v in K) & ~(1 << z)
    for v in hv:
        i = loc[v]
        for w in bits(adj[v] & H):
            ja[i] |= 1 << loc[w]
        if adj[v] & legal_cycle:
            ja[i] |= 1 << rho
            ja[rho] |= 1 << i
    d = [10**9] * len(ja)
    d[rho] = 0
    queue = [rho]
    for u in queue:
        for v in bits(ja[u]):
            if d[v] == 10**9:
                d[v] = d[u] + 1
                queue.append(v)
    return {hv[i]: d[i] for i in range(rho)}


def audit_graph(g6, result):
    n, adj = parse_graph6(g6)
    g = girth(n, adj)
    if g < 7 or g > n:
        return "outside"
    dist = all_pairs_dist(n, adj)
    r = min(eccentricities(n, dist))
    lam = 2 * r + 1 - g
    cycles, capped = shortest_cycle_vertex_sets(n, adj, g, 20000)
    if capped:
        raise RuntimeError(f"shortest-cycle cap hit on {g6}")
    for K in cycles:
        km = sum(1 << v for v in K)
        for H in components_outside(adj, ((1 << n) - 1) & ~km):
            A = atts(adj, K, H)
            for z in K:
                if not (set(A) - {z}):
                    continue
                E = [
                    sigma
                    for sigma in K
                    if max(dist[sigma][y] for y in bits(H)) >= r + 1
                ]
                P, pair = jmetric(adj, K, H, z)
                slack = P - len(E) - lam
                result["tests"] += 1
                if slack < result["min_slack"]:
                    result["min_slack"] = slack
                    result["min_record"] = dict(
                        graph6=g6,
                        n=n,
                        g=g,
                        r=r,
                        K=K,
                        H=list(bits(H)),
                        attachments=A,
                        z=z,
                        E_full=E,
                        lambda_=lam,
                        rooted_triameter=P,
                        maximizing_pair=pair,
                        p=rooted_depths(adj, K, H, z),
                        slack=slack,
                    )
                if slack < 0 and len(result["failures"]) < 100:
                    result["failures"].append(result["min_record"].copy())
    return "eligible"


def main():
    started = time.time()
    result = dict(
        test="W144 full-cycle rooted metric lemma, all legal records n=7..12",
        definition="|E_full| + (2r+1-g) <= P_z(H)",
        per_n={},
        tests=0,
        min_slack=10**9,
        min_record=None,
        failures=[],
    )
    for n in range(7, 13):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            capture_output=True,
            text=True,
            check=True,
        )
        counts = dict(generated=0, outside=0, eligible=0)
        for g6 in proc.stdout.split():
            counts["generated"] += 1
            counts[audit_graph(g6, result)] += 1
        result["per_n"][str(n)] = counts
        print(n, counts, result["tests"], result["min_slack"], flush=True)
    result["elapsed_sec"] = round(time.time() - started, 2)
    raw = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest().upper()
    OUT.with_suffix(".json.sha256").write_text(f"{sha}  {OUT.name}\n")
    print("tests", result["tests"], "min_slack", result["min_slack"])
    print("failures", len(result["failures"]))
    print("sha256", sha)


if __name__ == "__main__":
    main()
