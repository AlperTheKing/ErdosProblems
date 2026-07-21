#!/usr/bin/env python3
"""WOWII 142 prover-A reconnaissance.

Goal: find which hard-set graphs (T1 fails: f + ceil(2g/3) > D+1) are NOT
closed by the four elementary PROVABLE routes, and anatomize optimal
witnesses on the residual set to extract the constructive proof pattern.

Provable routes tested (g >= 4 assumed; g = 3 closes via T4 + T1):
  T1   : t >= D + 1               closes iff s := f + ceil(2g/3) - D - 1 <= 0
  T2   : t >= g - 1               closes iff m := f + 1 - floor(g/3) <= 0
  CT'  : t >= g - 1 + H_K (single deepest tail on cycle base; g>=4 ok via z)
         closes iff exists shortest cycle K: max_v d(v,K) >= m
  TAIL : t >= D + 1 + k_P (single deepest tail on geodesic base; g>=5 exact,
         g=4 with the swap trick guarantees k_P - 1)
         closes iff exists diametral geodesic P: max_v d(v,P) >= s (g>=5)
                    or >= s+1 (g=4)

All arithmetic exact integers.  Output: recon_results.json + residual.json.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent          # .../wowii_142/proverA
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
for p in (PE / "wowii_141" / "oracle", PE / "wowii_144" / "oracle",
          PE / "wowii_144" / "wave2"):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import (  # noqa: E402
    build_corpus, diametral_geodesic_sets, bits_list,
)
from lemma_e_tests import components_of_mask, edges_in_mask  # noqa: E402

EXACT_N = 14
GEOD_CAP = 500
CYC_CAP = 250
OUT = ROOT / "recon_results.json"
OUT_RES = ROOT / "residual.json"


def dist_to_mask(dist_v, mask):
    best = None
    m = mask
    while m:
        b = m & -m
        m ^= b
        d = dist_v[b.bit_length() - 1]
        if best is None or d < best:
            best = d
    return best


def eval_one(task):
    name, g6s = task
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    rec = {"name": name, "g6": g6s, "n": n}
    if n < 2 or not graph_connected(n, adj):
        rec["skip"] = "disconnected"
        return rec
    g = girth(n, adj)
    if g == 0:
        rec["skip"] = "acyclic"
        return rec
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = ecc_set(n, dist, periph)
    c23 = (2 * g + 2) // 3          # ceil(2g/3)
    f3 = g // 3                     # floor(g/3)
    s = f + c23 - D - 1
    m = f + 1 - f3
    rec.update(girth=g, D=D, f=f, s=s, m=m, r=min(ecc),
               nB=periph.bit_count())
    if g == 3:
        rec["route"] = "g3_T4"
        return rec
    if s <= 0:
        rec["route"] = "T1"
        return rec
    if m <= 0:
        rec["route"] = "T2"
        return rec
    # CT': max over shortest cycles of graph height above the cycle
    Ks = shortest_cycles(G, g)
    cyc_capped = len(Ks) > CYC_CAP
    if cyc_capped:
        Ks = Ks[:CYC_CAP]
    H_best = 0
    for K in Ks:
        km = 0
        for v in K:
            km |= 1 << v
        h = max(dist_to_mask(dist[v], km) for v in range(n))
        if h > H_best:
            H_best = h
    rec["H_best"] = H_best
    rec["cyc_capped"] = cyc_capped
    if H_best >= m:
        rec["route"] = "CT"
        return rec
    # TAIL: max over diametral geodesics of graph height above the path
    cap = 10 ** 9 if n <= EXACT_N else GEOD_CAP
    gsets, gcapped = diametral_geodesic_sets(n, adj, dist, D, cap)
    kP_best = 0
    for pm in gsets:
        k = max(dist_to_mask(dist[v], pm) for v in range(n))
        if k > kP_best:
            kP_best = k
    rec["kP_best"] = kP_best
    rec["geod_capped"] = gcapped
    need = s if g >= 5 else s + 1
    if kP_best >= need:
        rec["route"] = "TAIL"
        return rec
    rec["route"] = "RESIDUAL"
    return rec


# ---------------------------------------------------------- witness anatomy

def best_forest_for_kz(n, adj, kmask, z, comp_cap=18):
    """Exact max forest for base K, deleted vertex z: returns (size, fmask)
    or (None, None) if some component too big."""
    full = (1 << n) - 1
    outside = full & ~kmask
    base = kmask & ~(1 << z)
    total = 0
    fmask = 0
    for cm in components_of_mask(adj, outside):
        verts = bits_list(cm)
        if len(verts) > comp_cap:
            return None, None
        best, bmask = 0, 0
        for sub in range(1, 1 << len(verts)):
            sz = sub.bit_count()
            if sz <= best:
                continue
            mask = 0
            t = sub
            while t:
                b = t & -t
                t ^= b
                mask |= 1 << verts[b.bit_length() - 1]
            ne = edges_in_mask(adj, mask)
            comps = components_of_mask(adj, mask)
            if ne != sz - len(comps):
                continue
            ok = True
            for c in comps:
                tot = 0
                cc = c
                while cc:
                    b = cc & -cc
                    cc ^= b
                    tot += (adj[b.bit_length() - 1] & base).bit_count()
                if tot != 1:
                    ok = False
                    break
            if ok:
                best, bmask = sz, mask
        total += best
        fmask |= bmask
    return total, fmask


def classify_components(n, adj, dist, fmask, basemask, xset_mask, periph):
    out = []
    for c in components_of_mask(adj, fmask):
        verts = bits_list(c)
        sz = len(verts)
        ne = edges_in_mask(adj, c)
        is_path = (ne == sz - 1 and
                   max((adj[v] & c).bit_count() for v in verts) <= 2)
        attach = []
        for v in verts:
            a = adj[v] & basemask
            while a:
                b = a & -a
                a ^= b
                attach.append(b.bit_length() - 1)
        depth = max(dist_to_mask(dist[v], basemask) for v in verts)
        out.append({
            "size": sz, "path": is_path, "attach": sorted(attach),
            "depth": depth,
            "has_xstar": bool(c & xset_mask),
            "has_periph": bool(c & periph),
        })
    return out


def anatomy(task):
    """For a residual graph: best R2 witness (K, z, F) and its components."""
    name, g6s = task
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    g = girth(n, adj)
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = ecc_set(n, dist, periph)
    xset = 0
    for v in range(n):
        if dist_to_mask(dist[v], periph) == f:
            xset |= 1 << v
    m = f + 1 - g // 3
    best = (-1, None, None, None)   # (size, K, z, fmask)
    for K in shortest_cycles(G, g)[:CYC_CAP]:
        kv = sorted(K)
        km = 0
        for v in kv:
            km |= 1 << v
        for z in kv:
            tot, fm = best_forest_for_kz(n, adj, km, z)
            if tot is None:
                continue
            if tot > best[0]:
                best = (tot, kv, z, fm)
    tot, kv, z, fm = best
    rec = {"name": name, "g6": g6s, "n": n, "g": g, "D": D, "f": f,
           "m_needed": m, "M_best": tot}
    if kv is not None:
        km = 0
        for v in kv:
            km |= 1 << v
        rec["K"] = kv
        rec["z"] = z
        rec["components"] = classify_components(
            n, adj, dist, fm, km & ~(1 << z), xset, periph)
        rec["heights_B"] = sorted(
            dist_to_mask(dist[v], km) for v in bits_list(periph))
        rec["h_xstar"] = sorted(
            dist_to_mask(dist[v], km) for v in bits_list(xset))
    return rec


def main():
    t0 = time.time()
    tasks = build_corpus()
    print(f"corpus: {len(tasks)}", flush=True)
    routes = Counter()
    per_girth_residual = Counter()
    residual = []
    stats = []
    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one, tasks, chunksize=32):
            if "skip" in rec:
                continue
            routes[rec["route"]] += 1
            if rec["route"] == "RESIDUAL":
                residual.append(rec)
                per_girth_residual[rec["girth"]] += 1
            stats.append({k: rec.get(k) for k in
                          ("g6", "girth", "D", "f", "s", "m", "route")})
    print("routes:", dict(routes), flush=True)
    print("residual girth hist:", dict(per_girth_residual), flush=True)
    print(f"elapsed {time.time()-t0:.0f}s", flush=True)

    # anatomy pass on residual graphs (small ones exactly)
    small = [(r["name"], r["g6"]) for r in residual if r["n"] - r["girth"] <= 18]
    print(f"anatomy on {len(small)}/{len(residual)} residual graphs",
          flush=True)
    anat = []
    with Pool(8) as pool:
        for rec in pool.imap_unordered(anatomy, small, chunksize=4):
            anat.append(rec)

    OUT.write_text(json.dumps({
        "routes": dict(routes),
        "residual_girth_hist": {str(k): v
                                for k, v in sorted(per_girth_residual.items())},
        "n_residual": len(residual),
    }, indent=2))
    OUT_RES.write_text(json.dumps({
        "residual": residual,
        "anatomy": anat,
    }, indent=2))
    print("written", OUT, OUT_RES, flush=True)
    print(f"total {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
