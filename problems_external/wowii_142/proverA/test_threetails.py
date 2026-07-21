#!/usr/bin/env python3
"""Test the three-tail counting claim on the residual set (and hard set).

Claim TT: for hard-branch graphs not closed by T1/T2/CT/TAIL, there exist a
shortest cycle K, a diametral pair (b,w), and an f-realizer x with

    h_K(x) + h_K(b) + h_K(w) >= m := f + 1 - floor(g/3).

Also record the per-part maxima to see which inequality binds, plus the
component-compat margins d(x,b) - h(x) - h(b) etc. for the pruning analysis.
Exact integers only.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
for p in (PE / "wowii_141" / "oracle", PE / "wowii_144" / "oracle",
          PE / "wowii_144" / "wave2"):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import bits_list  # noqa: E402


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


def main():
    res = json.loads((ROOT / "residual.json").read_text())["residual"]
    print(f"{len(res)} residual graphs")
    viol = []
    margin_hist = Counter()
    compat_bad = Counter()
    for r in res:
        g6s = r["g6"]
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
        m = f + 1 - g // 3
        Bv = bits_list(periph)
        pairs = [(b, w) for i, b in enumerate(Bv) for w in Bv[i + 1:]
                 if dist[b][w] == D]
        X = [v for v in range(n) if dist_to_mask(dist[v], periph) == f]
        best = -1
        best_detail = None
        for K in shortest_cycles(G, g)[:250]:
            km = 0
            for v in K:
                km |= 1 << v
            h = [dist_to_mask(dist[v], km) for v in range(n)]
            for (b, w) in pairs:
                for x in X:
                    tot = h[x] + h[b] + h[w]
                    if tot > best:
                        best = tot
                        best_detail = {
                            "hx": h[x], "hb": h[b], "hw": h[w],
                            "d_xb": dist[x][b], "d_xw": dist[x][w],
                            "compat_bw": dist[b][w] - h[b] - h[w],
                            "compat_xb": dist[x][b] - h[x] - h[b],
                            "compat_xw": dist[x][w] - h[x] - h[w],
                        }
        margin = best - m
        margin_hist[margin] += 1
        if margin < 0:
            viol.append({"g6": g6s, "n": n, "g": g, "D": D, "f": f,
                         "m": m, "best3": best, "detail": best_detail})
        else:
            d = best_detail
            bad = tuple(k for k in ("compat_bw", "compat_xb", "compat_xw")
                        if d[k] < 0)
            compat_bad[bad] += 1
    print("TT margin hist (best3 - m):", dict(sorted(margin_hist.items())))
    print("violations:", len(viol))
    for v in viol[:20]:
        print("  ", v)
    print("compat<0 patterns at the maximizing triple:",
          dict(compat_bad))
    (ROOT / "threetails_results.json").write_text(json.dumps({
        "margin_hist": {str(k): v for k, v in sorted(margin_hist.items())},
        "violations": viol,
        "compat_bad": {str(k): v for k, v in compat_bad.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
