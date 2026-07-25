#!/usr/bin/env python3
"""fam10_vsweep.py -- FRACTIONAL-VERTEX sweep (family 10), MEASUREMENT stage.

For every triple in a pool: build Q(lam,mu,nu) exactly, sample exactly-certified
vertices (each re-solved over Fractions and verified against EVERY rhombus
inequality), and report

    nverts       # distinct exact vertices found (rigorous LOWER bound)
    nfrac        # of those, how many have some coordinate with denominator >= 2
    fracratio    nfrac / nverts
    maxden       max vertex denominator (>= 2 certifies Q is NOT a lattice polytope)
    dim_lo       affine rank of the certified vertices (rigorous LOWER bound on dim Q)
    dim_hi       D - rank(rows tight at every sampled vertex) (heuristic UPPER bound)

No verdict rests on this stage: it only ORDERS the pool for the exact tier-0
screen.  Nothing is discarded on dimension or simplex grounds.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, HERE)

from hive_poly import build                       # noqa: E402
from simplex_vol import sample_vertices, rank     # noqa: E402


def measure(lam, mu, nu, K, seed):
    A, b, D, interior, ok = build(lam, mu, nu)
    out = {"D": D}
    if not ok:
        out["vstatus"] = "INFEASIBLE_BOUNDARY"
        return out
    if D == 0:
        out.update(vstatus="TRIVIAL", nverts=1, nfrac=0, fracratio=0.0,
                   maxden=1, dim_lo=0, dim_hi=0)
        return out
    verts, tight = sample_vertices(A, b, D, K, seed)
    if verts is None:
        out["vstatus"] = "LP_FAIL"
        return out
    v0 = verts[0]
    edge = [[v[j] - v0[j] for j in range(D)] for v in verts[1:]]
    dim_lo = rank(edge, D) if edge else 0
    alltight = None
    for v in verts:
        s = tight[tuple(v)]
        alltight = s if alltight is None else (alltight & s)
    if alltight:
        E = [[A[i][j] for j in range(D)] for i in sorted(alltight)]
        dim_hi = D - rank(E, D)
    else:
        dim_hi = D
    nfrac = sum(1 for v in verts if any(q.denominator > 1 for q in v))
    maxden = max(max(q.denominator for q in v) for v in verts)
    out.update(vstatus="OK", nverts=len(verts), nfrac=nfrac,
               fracratio=nfrac / len(verts), maxden=maxden,
               dim_lo=int(dim_lo), dim_hi=int(dim_hi),
               n_impl_eq=(0 if not alltight else int(D - dim_hi)))
    if maxden > 1:
        for v in verts:
            if any(q.denominator > 1 for q in v):
                out["frac_vertex"] = [str(q) for q in v]
                break
    return out


def _job(arg):
    idx, lam, mu, nu, c, K, seed = arg
    rec = {"idx": idx, "lam": list(lam), "mu": list(mu), "nu": list(nu), "c": c}
    try:
        rec.update(measure(lam, mu, nu, K, seed))
    except Exception as ex:                        # noqa: BLE001
        rec["vstatus"] = "EXC:" + repr(ex)[:140]
    return rec


def main(argv):
    src, dst = argv[1], argv[2]
    K = int(argv[3]) if len(argv) > 3 else 200
    workers = int(argv[4]) if len(argv) > 4 else 56
    jobs = []
    for i, line in enumerate(open(src, encoding="utf-8")):
        r = json.loads(line)
        jobs.append((r.get("idx", i), tuple(r["lam"]), tuple(r["mu"]),
                     tuple(r["nu"]), r.get("c"), K, 20260722 + 7 * i))
    n = 0
    with open(dst, "w", encoding="utf-8") as f:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_job, j) for j in jobs]
            for fut in as_completed(futs):
                f.write(json.dumps(fut.result()) + "\n")
                n += 1
                if n % 500 == 0:
                    f.flush()
                    print("%d/%d" % (n, len(jobs)), flush=True)
    print("wrote %d" % n, flush=True)


if __name__ == "__main__":
    main(sys.argv)
