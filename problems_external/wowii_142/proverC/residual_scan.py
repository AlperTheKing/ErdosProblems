#!/usr/bin/env python3
"""Prover-C residual scan (WOWII 142 hard branch, g >= 4).

Applies ONLY bounds with rigorous proofs in hand and reports survivors:

  b1 (T1)      : t >= D + 1
  b3 (Lemma A) : t >= g - 1 + max_K H(K), H(K) = max_v d(v,K)
                 [g >= 4; single K-geodesic tail; foot has <= 1 neighbor in K
                  for g >= 5, antipodal pair killed by z at g = 4]
  b4 (P-tail)  : g >= 5: t >= D + 1 + max_P max_x d(x,P) over diametral
                 geodesics P (foot has <= 1 neighbor in P);
                 g = 4 : t >= D + max(1, max_P max_x d(x,P)) [reroute trick]

Target: N = f + ceil(2g/3).  Survivor := max(b1,b3,b4) < N.
g = 3 skipped (closed by T4 + T1), f = 0 skipped (skeleton branch).
Exact integer arithmetic only.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent          # .../wowii_142/proverC
sys.path.insert(0, str(ROOT.parent / "bridge_oracle"))

import bridge_oracle as bo  # noqa: E402  (pulls in invariants etc.)
from invariants import dist_to_set  # noqa: E402

OUT = ROOT / "residual_scan_results.json"
CYC_CAP = 250    # capping under-reports b3 -> conservative (extra survivors)
GEOD_CAP = 500   # same for b4


def eval_one(task):
    name, g6s = task
    try:
        G = nx.from_graph6_bytes(g6s.encode("ascii"))
        n, adj = bo.nx_to_bitadj(G)
        if n < 2 or not bo.graph_connected(n, adj):
            return None
        g = bo.girth(n, adj)
        if g == 0 or g == 3:
            return None
        dist = bo.all_pairs_dist(n, adj)
        ecc = bo.eccentricities(n, dist)
        D = max(ecc)
        periph = 0
        for v in range(n):
            if ecc[v] == D:
                periph |= 1 << v
        f = bo.ecc_set(n, dist, periph)
        if f == 0:
            return None
        target = f + (2 * g + 2) // 3          # f + ceil(2g/3)
        b1 = D + 1
        # ---- b3: max_K H(K)
        Ks = bo.shortest_cycles(G, g)
        kcap = len(Ks) > CYC_CAP
        if kcap:
            Ks = Ks[:CYC_CAP]
        bestH = 0
        for K in Ks:
            km = 0
            for v in K:
                km |= 1 << v
            H = max(dist_to_set(dist, v, km) for v in range(n))
            if H > bestH:
                bestH = H
        b3 = g - 1 + bestH
        # ---- b4: max_P h(P)
        cap = bo.GEOD_CAP_SMALL if n <= bo.EXACT_N else GEOD_CAP
        gsets, gcapped = bo.diametral_geodesic_sets(n, adj, dist, D, cap)
        hmax = 0
        for pm in gsets:
            h = max(dist_to_set(dist, v, pm) for v in range(n))
            if h > hmax:
                hmax = h
        b4 = D + 1 + hmax if g >= 5 else D + max(1, hmax)
        best = max(b1, b3, b4)
        rec = {"name": name, "g6": g6s, "n": n, "g": g, "D": D, "f": f,
               "H": bestH, "hP": hmax, "target": target, "best": best,
               "deficit": target - best, "kcap": kcap, "gcapped": gcapped}
        return rec
    except Exception as exc:
        return {"name": name, "g6": g6s, "error": repr(exc)}


def main():
    tasks = bo.build_corpus()
    print(f"corpus: {len(tasks)}", flush=True)
    survivors = []
    errors = []
    count = 0
    stats = Counter()
    margin_hist = Counter()
    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one, tasks, chunksize=32):
            if rec is None:
                continue
            if "error" in rec:
                errors.append(rec)
                continue
            count += 1
            margin_hist[min(rec["best"] - rec["target"], 10)] += 1
            if rec["deficit"] > 0:
                survivors.append(rec)
                stats[(rec["g"], rec["D"], rec["f"])] += 1
    survivors.sort(key=lambda r: (-r["deficit"], r["n"]))
    res = {
        "evaluated": count,
        "survivors": len(survivors),
        "errors": errors[:10],
        "margin_hist": {str(k): v for k, v in sorted(margin_hist.items())},
        "survivor_class_counts":
            [{"g": k[0], "D": k[1], "f": k[2], "count": v}
             for k, v in sorted(stats.items())],
        "survivor_records": survivors[:400],
    }
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(f"evaluated {count} (g>=4, f>=1); survivors {len(survivors)}; "
          f"errors {len(errors)}")
    for rec in survivors[:60]:
        print(f"  n={rec['n']} g={rec['g']} D={rec['D']} f={rec['f']} "
              f"H={rec['H']} hP={rec['hP']} target={rec['target']} "
              f"best={rec['best']} def={rec['deficit']} [{rec['g6']}] "
              f"{rec['name']}")


if __name__ == "__main__":
    main()
