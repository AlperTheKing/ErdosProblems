#!/usr/bin/env python3
"""Round 2: z-tail routes on the residual set.

dz(v) = d(v, K \ {z}) for a shortest cycle K and z in K.  A shortest
v -> (K\{z}) path minus its K-endpoint is a valid Lemma-M component for
g >= 5 (window argument; edges into z are free).  Tests on the 242 residual
graphs (and separately re-checks which ones a CT'' single z-tail closes):

  CT'' : exists K, z, v : dz(v) >= m       (single z-tail)
  TT'  : exists K, z, diametral pair (b,w), realizer x :
             dz(x) + dz(b) + dz(w) >= m    (three z-tails, shared z)

Also records compat margins for the pruning analysis and the binding cases.
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
    ct2_closed = 0
    tt_margin = Counter()
    viol = []
    girth_of_open = Counter()
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
        ct2 = 0          # best single z-tail
        tt = -1          # best three-z-tail total
        tt_det = None
        for K in shortest_cycles(G, g)[:250]:
            kv = sorted(K)
            km = 0
            for v in kv:
                km |= 1 << v
            for z in kv:
                bm = km & ~(1 << z)
                dz = [dist_to_mask(dist[v], bm) for v in range(n)]
                mx = max(dz)
                if mx > ct2:
                    ct2 = mx
                for (b, w) in pairs:
                    for x in X:
                        tot = dz[x] + dz[b] + dz[w]
                        if tot > tt:
                            tt = tot
                            tt_det = {
                                "dzx": dz[x], "dzb": dz[b], "dzw": dz[w],
                                "compat_bw": dist[b][w] - dz[b] - dz[w],
                                "compat_xb": dist[x][b] - dz[x] - dz[b],
                                "compat_xw": dist[x][w] - dz[x] - dz[w],
                            }
        if ct2 >= m:
            ct2_closed += 1
            continue
        tt_margin[tt - m] += 1
        if tt < m:
            viol.append({"g6": g6s, "n": n, "g": g, "D": D, "f": f, "m": m,
                         "ct2": ct2, "tt": tt, "detail": tt_det})
            girth_of_open[g] += 1
    print("closed by CT'' (single z-tail):", ct2_closed)
    print("TT' margin hist on the rest:", dict(sorted(tt_margin.items())))
    print("TT' violations:", len(viol), "girths:", dict(girth_of_open))
    for v in viol[:25]:
        print("  ", v)
    (ROOT / "ztails_results.json").write_text(json.dumps({
        "ct2_closed": ct2_closed,
        "tt_margin_hist": {str(k): v for k, v in sorted(tt_margin.items())},
        "violations": viol,
    }, indent=2))


if __name__ == "__main__":
    main()
