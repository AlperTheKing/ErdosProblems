#!/usr/bin/env python3
"""
validate_dim3.py -- SUPPLEMENTARY gate concentrated on the dim-3 stratum.

Negativity of an Ehrhart coefficient is impossible below dimension 3, so the
only stratum in which the r=4 cell can produce a KTT counterexample is
dim Q = 3.  The mandated 400-triple gate (validate_hive4.py) samples that
stratum only thinly (dim 3 is rare among uniform random triples), so this
script builds a pool of dim-3 triples ONLY and re-runs the full cross-engine
comparison on it: L(1) and the stretched values P(2), P(3), P(4) against BOTH
engine A and engine B.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive4  # noqa: E402
import validate_hive4 as V  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main(target=200, seed=20260721303):
    rng = random.Random(seed)
    pool = []
    tries = 0
    while len(pool) < target and tries < 3000000:
        tries += 1
        N = rng.randint(8, 60)
        nu = V.rand_partition_exact(N, 4, rng)
        if nu is None:
            continue
        a = rng.randint(1, N - 1)
        lam = V.rand_partition(a, 4, rng)
        mu = V.rand_partition(N - a, 4, rng)
        r = hive4.analyze(lam, mu, nu)
        if r["dim"] == 3:
            pool.append((lam, mu, nu, r))
    print("dim-3 pool: %d triples from %d samples" % (len(pool), tries))
    cs = sorted(r["c"] for _, _, _, r in pool)
    print("c range %d..%d ; V range %s..%s ; max vertex denominator %d"
          % (cs[0], cs[-1],
             hive4._fmt_frac(min(r["volume_normalized"] for _, _, _, r in pool)),
             hive4._fmt_frac(max(r["volume_normalized"] for _, _, _, r in pool)),
             max(r["max_denominator"] for _, _, _, r in pool)))

    lines, meta = [], []
    for lam, mu, nu, r in pool:
        for k in (1, 2, 3, 4):
            lines.append("%s;%s;%s;%d" % (V.ps([k * x for x in lam]),
                                          V.ps([k * x for x in mu]),
                                          V.ps([k * x for x in nu]), V.CAP))
            meta.append((lam, mu, nu, r, k))
    oa, ob = V.run_batch(lines, "dim3")
    bad = []
    for (lam, mu, nu, r, k), la, lb in zip(meta, oa, ob):
        mine = hive4.polyval(r["poly"], k)
        s = str(mine.numerator) if mine.denominator == 1 else str(mine)
        if not (s == la.strip() == lb.strip()):
            bad.append((V.ps(lam), V.ps(mu), V.ps(nu), k, s, la.strip(), lb.strip()))
    print("cross-engine agreements: %d / %d  (%d triples x n=1,2,3,4)"
          % (len(meta) - len(bad), len(meta), len(pool)))
    for x in bad[:20]:
        print("  MISMATCH %s;%s;%s n=%d hive4=%s A=%s B=%s" % x)

    internal = [r for _, _, _, r in pool
                if not (r["verified"] and r["vol_crosscheck"] and r["deg_eq_dim"])]
    print("internal audit failures (interp/volume/degree): %d" % len(internal))
    negs = [(l, m, n, r) for l, m, n, r in pool if r["neg"]]
    print("dim-3 triples with a strictly NEGATIVE coefficient: %d" % len(negs))
    hs = {}
    for _, _, _, r in pool:
        hs[tuple(r["hstar"])] = hs.get(tuple(r["hstar"]), 0) + 1
    print("h*-vector shapes seen (top 10): %s"
          % sorted(hs.items(), key=lambda kv: -kv[1])[:10])
    ok = not bad and not internal
    print("SUPPLEMENTARY DIM-3 GATE:", "PASS" if ok else "FAIL")
    with open(os.path.join(HERE, "validation_dim3.json"), "w") as f:
        json.dump({"n_triples": len(pool), "n_checks": len(meta),
                   "mismatches": bad, "internal_failures": len(internal),
                   "negatives": len(negs),
                   "hstar_shapes": {str(k): v for k, v in hs.items()},
                   "verdict": "PASS" if ok else "FAIL"}, f, indent=1, default=str)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 200))
