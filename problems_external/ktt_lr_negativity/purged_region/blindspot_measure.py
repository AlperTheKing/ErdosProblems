#!/usr/bin/env python3
"""Quantify the OLD screen's blind spot, exactly.

For a set of triples with KNOWN exact d (from the mandated LP-free instrument),
re-run the old-style LP dimension oracle at K = 14, 20, 25 random objectives
(the old campaign used 14-25) and record:
  - dim_lo < d          -> the old rule "discard if c > dim_lo + 1" fires (for
                           h*_1 = 0 triples c = d+1, so dim_lo < d == discard)
  - nverts > d + 1      -> Q provably NOT a simplex, deleted by the old simplex
                           filter regardless of the oracle
Nothing here filters anything; measurement only.
"""
import json
import os
import sys
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = "E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity"
sys.path.insert(0, os.path.join(ROOT, "engine"))
from hive_poly import build            # noqa: E402
from simplex_vol import sample_vertices, rank  # noqa: E402


def _job(arg):
    idx, lam, mu, nu, d_true, tag = arg
    out = {"idx": idx, "d": d_true, "tag": tag}
    try:
        A, b, damb, interior, ok = build(lam, mu, nu)
        if not ok or damb == 0:
            out["st"] = "TRIVIAL"
            return out
        for K in (14, 20, 25, 400):
            verts, _ = sample_vertices(A, b, damb, K, 20260721 + idx)
            if verts is None:
                out["K%d" % K] = None
                continue
            v0 = verts[0]
            edge = [[verts[i][j] - v0[j] for j in range(damb)]
                    for i in range(1, len(verts))]
            out["K%d" % K] = [rank(edge, damb) if edge else 0, len(verts),
                              max(max(q.denominator for q in v) for v in verts)]
        out["st"] = "OK"
    except Exception as ex:                      # noqa: BLE001
        out["st"] = "EXC:" + repr(ex)[:120]
    return out


def main():
    jobs = []
    car = json.load(open(ROOT + "/purged_region/LADDER_CARRIERS_ALL.json",
                         encoding="utf-8"))
    for i, r in enumerate(car):
        jobs.append((i, tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]),
                     r["d"], "carrier"))
    # general population: random nonempty records with d >= 2
    pop = []
    with open(ROOT + "/purged_region/ladder_r5.jsonl", encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:                    # noqa: BLE001
                continue
            if r.get("d", 0) >= 2 and r.get("hstar"):
                pop.append(r)
    random.Random(7).shuffle(pop)
    for i, r in enumerate(pop[:1500]):
        jobs.append((100000 + i, tuple(r["lam"]), tuple(r["mu"]),
                     tuple(r["nu"]), r["d"], "pop"))
    print("jobs", len(jobs), flush=True)
    out = open(sys.argv[1], "w", encoding="utf-8")
    n = 0
    with ProcessPoolExecutor(max_workers=48) as ex:
        futs = [ex.submit(_job, j) for j in jobs]
        for f in as_completed(futs):
            out.write(json.dumps(f.result()) + "\n")
            n += 1
            if n % 250 == 0:
                print(n, flush=True)
    out.close()
    print("done", n)


if __name__ == "__main__":
    main()
