#!/usr/bin/env python3
"""
vertex_measure.py -- MEASUREMENT ONLY (never a filter).

For a list of triples with an ALREADY-KNOWN exact Ehrhart degree d (from the
mandated LP-free instrument), sample exactly-certified vertices of the hive
polytope Q(lam,mu,nu) and report how many DISTINCT exact vertices are found.

Rigour: every vertex returned by simplex_vol.sample_vertices is re-solved and
verified over Fractions against every rhombus inequality, so the count is a
rigorous LOWER bound on the true number of vertices.  Consequently

      nverts_found > d_true + 1   ==>   Q is PROVABLY NOT a simplex.

The converse is not claimed: nverts_found <= d+1 is inconclusive (random
objectives can miss vertices).  Nothing here is used to discard any triple.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "engine"))
from hive_poly import build            # noqa: E402
from simplex_vol import sample_vertices, rank  # noqa: E402


def parse_p(s):
    return tuple(int(x) for x in str(s).replace(";", ",").split(",")
                 if x.strip() not in ("", "0"))


def _job(arg):
    idx, lam, mu, nu, d_true, K, seed = arg
    out = {"idx": idx, "lam": list(lam), "mu": list(mu), "nu": list(nu),
           "d_true": d_true}
    try:
        A, b, damb, interior, ok = build(lam, mu, nu)
        if not ok:
            out["vstatus"] = "INFEASIBLE_BOUNDARY"
            return out
        if damb == 0:
            out.update(vstatus="TRIVIAL_POINT", nverts=1, dim_lo=0, maxden=1)
            return out
        verts, _ = sample_vertices(A, b, damb, K, seed)
        if verts is None:
            out["vstatus"] = "LP_FAIL"
            return out
        v0 = verts[0]
        edge = [[verts[i][j] - v0[j] for j in range(damb)]
                for i in range(1, len(verts))]
        out["dim_lo"] = rank(edge, damb) if edge else 0
        out["nverts"] = len(verts)
        out["maxden"] = max(max(q.denominator for q in v) for v in verts)
        out["vstatus"] = ("PROVABLY_NOT_SIMPLEX" if len(verts) > d_true + 1
                          else "SIMPLEX_CONSISTENT")
    except Exception as ex:            # noqa: BLE001
        out["vstatus"] = "EXC:" + repr(ex)[:160]
    return out


def main(argv):
    src, dst = argv[1], argv[2]
    K = int(argv[3]) if len(argv) > 3 else 400
    workers = int(argv[4]) if len(argv) > 4 else 48
    jobs = []
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        jobs.append((r["idx"], tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]),
                     r["d"], K, 20260721 + r["idx"]))
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_job, j) for j in jobs]
            for fut in as_completed(futs):
                f.write(json.dumps(fut.result()) + "\n")
                f.flush()
                n += 1
                if n % 200 == 0:
                    print("%d/%d" % (n, len(jobs)), flush=True)
    print("wrote %d" % n)


if __name__ == "__main__":
    main(sys.argv)
