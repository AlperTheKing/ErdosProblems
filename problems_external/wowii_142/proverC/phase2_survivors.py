#!/usr/bin/env python3
"""Phase 2: analyze residual-scan survivors against the planned proof steps.

For each survivor of {T1, LemmaA, P-tail} we test, with exact integers:

  K1 (3-tail): exists shortest cycle K, deep vertex x* (d(x*,B)=f), diametral
     pair (b0,b1), and K-geodesic tails T*,T0,T1 (enumerated via shortest-path
     DAGs, capped) that are PAIRWISE CLASH-FREE (no shared vertex, no edge
     between different tails) with  g - 1 + |T*|+|T0|+|T1| >= target,
     where empty tails are allowed (vertex on K).
     Feet all have exactly 1 K-neighbor for g>=5 (checked), and a z in K
     avoiding all feet neighbors exists (g>=4 > #feet not guaranteed; checked).

  smallD: g in {5,8,11} class check: all heights <= 1 (V = K + satellites),
     f = g//3 + 1, D = g//3 + 2, and >= 2 satellites present; closure by
     M(K) >= 2 (two non-adjacent satellites or an adjacent pair component).

  g4: girth-4 residue: report detail (D, f, structure) for the g=4 endgame.

Output: phase2_results.json with per-survivor verdicts; FLAG list = survivors
closed by neither K1 numeric+clash-free choice, smallD closure, nor g4 bucket.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "bridge_oracle"))

import bridge_oracle as bo  # noqa: E402
from invariants import dist_to_set  # noqa: E402

IN = ROOT / "residual_scan_results.json"
OUT = ROOT / "phase2_results.json"
TAIL_CAP = 40      # max distinct tails enumerated per (vertex, K)
TRIPLE_CAP = 4000  # max tail-combination checks per (K, x*, b0, b1)


def bits_list(mask: int) -> list[int]:
    out = []
    while mask:
        b = mask & -mask
        mask ^= b
        out.append(b.bit_length() - 1)
    return out


def k_tails(n, adj, dist, kmask, v, cap=TAIL_CAP):
    """All K-geodesic tails from v: vertex-masks of shortest v->K paths minus
    the K-endpoint.  Returns list of (mask, foot) — foot = level-1 vertex.
    If v in K: single empty tail (mask 0, foot None)."""
    if (1 << v) & kmask:
        return [(0, None)]
    lam = dist_to_set(dist, v, kmask)
    lev = [dist_to_set(dist, u, kmask) for u in range(n)]
    tails = []
    stack = [(v, 1 << v)]
    while stack and len(tails) < cap:
        x, mask = stack.pop()
        lx = lev[x]
        if lx == 1:
            tails.append((mask, x))
            continue
        nb = adj[x]
        while nb:
            b = nb & -nb
            nb ^= b
            y = b.bit_length() - 1
            if not ((1 << y) & kmask) and lev[y] == lx - 1:
                stack.append((y, mask | b))
    return tails


def clash_free(adj, masks):
    """True if the given vertex-mask components are pairwise disjoint and
    non-adjacent."""
    for a in range(len(masks)):
        for b in range(a + 1, len(masks)):
            if masks[a] & masks[b]:
                return False
            nbh = 0
            m = masks[a]
            while m:
                bb = m & -m
                m ^= bb
                nbh |= adj[bb.bit_length() - 1]
            if nbh & masks[b]:
                return False
    return True


def try_K1(n, adj, dist, g, D, f, target, Ks, deep, dpairs):
    """Search for a clash-free triple achieving g-1+sum >= target.
    Returns (ok, detail)."""
    best = None
    for K in Ks:
        kmask = 0
        for v in K:
            kmask |= 1 << v
        for xs in deep:
            tx = k_tails(n, adj, dist, kmask, xs)
            lx = dist_to_set(dist, xs, kmask)
            for (b0, b1) in dpairs:
                l0 = dist_to_set(dist, b0, kmask)
                l1 = dist_to_set(dist, b1, kmask)
                if g - 1 + lx + l0 + l1 < target:
                    continue  # numerically insufficient regardless of clash
                t0 = k_tails(n, adj, dist, kmask, b0)
                t1 = k_tails(n, adj, dist, kmask, b1)
                checks = 0
                for (m_, f_), (m0, f0), (m1, f1) in product(tx, t0, t1):
                    checks += 1
                    if checks > TRIPLE_CAP:
                        break
                    masks = [m for m in (m_, m0, m1) if m]
                    if not clash_free(adj, masks):
                        continue
                    feet = [ft for ft in (f_, f0, f1) if ft is not None]
                    # feet K-neighbor counts (g>=5 -> must be 1)
                    fner = [bin(adj[ft] & kmask).count("1") for ft in feet]
                    if g >= 5 and any(c != 1 for c in fner):
                        return (False, {"err": "foot multi-neighbor at g>=5"})
                    # z avoiding all feet attachment vertices
                    att = 0
                    for ft in feet:
                        att |= adj[ft] & kmask
                    if kmask & ~att == 0:
                        continue
                    return (True, {"K": K, "x": xs, "b0": b0, "b1": b1,
                                   "sum": lx + l0 + l1,
                                   "bound": g - 1 + lx + l0 + l1})
    return (False, best)


def small_d_class(n, adj, dist, g, D, f, Ks):
    """Check the pinned small-D class and its closure (needs M(K) >= 2 via
    satellites)."""
    if g not in (5, 8, 11):
        return None
    if f != g // 3 + 1 or D != g // 3 + 2:
        return None
    for K in Ks:
        kmask = 0
        for v in K:
            kmask |= 1 << v
        sats = [v for v in range(n) if not ((1 << v) & kmask)]
        if any(dist_to_set(dist, v, kmask) > 1 for v in sats):
            continue  # heights > 1 -> not this K; try next
        if len(sats) >= 2:
            return {"class": "smallD", "g": g, "n_sat": len(sats),
                    "closed": True}
        return {"class": "smallD", "g": g, "n_sat": len(sats),
                "closed": False}
    return None


def eval_survivor(rec):
    g6s = rec["g6"]
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = bo.nx_to_bitadj(G)
    g = bo.girth(n, adj)
    dist = bo.all_pairs_dist(n, adj)
    ecc = bo.eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = bo.ecc_set(n, dist, periph)
    target = f + (2 * g + 2) // 3
    Ks = bo.shortest_cycles(G, g)[:60]
    deep = [v for v in range(n) if dist_to_set(dist, v, periph) == f]
    dpairs = [(u, v) for u in range(n) for v in range(u + 1, n)
              if dist[u][v] == D][:80]

    out = {"g6": g6s, "n": n, "g": g, "D": D, "f": f, "target": target,
           "name": rec.get("name", "")}
    # LArc-far sanity: any (K,P) with d(K,P)>=2?  (in-zone should be rare)
    # (skipped for speed; the K1/smallD/g4 verdicts are what matter)
    if g == 4:
        out["bucket"] = "g4"
        out["hP"] = rec.get("hP")
        # rigidity data: is every vertex within distance 1 of every diametral
        # geodesic?  f = D - 1?
        out["f_eq_D_minus_1"] = (f == D - 1)
        return out
    sd = small_d_class(n, adj, dist, g, D, f, Ks)
    if sd is not None:
        out["bucket"] = "smallD"
        out.update(sd)
        return out
    ok, detail = try_K1(n, adj, dist, g, D, f, target, Ks, deep, dpairs)
    out["bucket"] = "K1" if ok else "FLAG"
    out["K1_ok"] = ok
    if ok:
        out["K1"] = {k: detail[k] for k in ("sum", "bound")}
        out["largeD_holds"] = (D >= g + 1 - 2 * (g // 3))
    else:
        out["detail"] = detail
    return out


def main():
    res = json.loads(IN.read_text())
    survivors = res["survivor_records"]
    print(f"{len(survivors)} survivors to analyze", flush=True)
    outs = []
    buckets = Counter()
    for i, rec in enumerate(survivors):
        o = eval_survivor(rec)
        outs.append(o)
        buckets[o["bucket"]] += 1
        if o["bucket"] == "FLAG":
            print("FLAG:", json.dumps(o), flush=True)
        if (i + 1) % 40 == 0:
            print(f"  {i+1}/{len(survivors)} {dict(buckets)}", flush=True)
    OUT.write_text(json.dumps(
        {"buckets": dict(buckets), "records": outs}, indent=2) + "\n")
    print("buckets:", dict(buckets))
    # summarize g4 + smallD detail
    for o in outs:
        if o["bucket"] == "smallD" and not o.get("closed", True):
            print("smallD-UNCLOSED:", o)
    g4 = [o for o in outs if o["bucket"] == "g4"]
    print(f"g4 residue: {len(g4)}; f=D-1 in all: "
          f"{all(o['f_eq_D_minus_1'] for o in g4)}")
    k1 = [o for o in outs if o["bucket"] == "K1"]
    print(f"K1-closed: {len(k1)}; largeD holds in all: "
          f"{all(o.get('largeD_holds') for o in k1)}")


if __name__ == "__main__":
    main()
