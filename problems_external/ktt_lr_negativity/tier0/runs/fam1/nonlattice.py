#!/usr/bin/env python
"""EXACT non-lattice certifier (measurement only, never a filter).

For each triple, sample vertices of Q with random objectives (floats SEARCH),
then re-solve each tight system over Fractions and verify feasibility exactly
(Fractions DECIDE).  A certified vertex with a non-integer coordinate is an
exact proof that Q is NOT a lattice polytope.  Absence of one is inconclusive.

usage: nonlattice.py IN.jsonl OUT.jsonl NSAMPLE K SEED [filter]
filter: "all" | "margin0d4"  (h*_1==0 and d>=4)
"""
import sys, os, json, random
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from hive_poly import build                      # noqa: E402
from simplex_vol import sample_vertices          # noqa: E402


def main():
    inp, outp = sys.argv[1], sys.argv[2]
    nsample, K, seed = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    filt = sys.argv[6] if len(sys.argv) > 6 else "all"

    pool = []
    for fn in inp.split(","):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("status") != "OK":
                continue
            if filt == "margin0d4":
                if not (r["d"] >= 4 and r["hstar_1"] == 0):
                    continue
            elif filt == "d2":
                if r["d"] < 2:
                    continue
            pool.append((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]),
                         r["d"], r["hstar_1"], r["hstar_d"], tuple(r["hstar"])))
    pool = sorted(set(pool))
    rng = random.Random(seed)
    if nsample and len(pool) > nsample:
        pool = sorted(rng.sample(pool, nsample))
    if len(sys.argv) > 8:
        sh, nsh = int(sys.argv[7]), int(sys.argv[8])
        pool = [x for i, x in enumerate(pool) if i % nsh == sh]
    sys.stderr.write("pool %d\n" % len(pool))

    nnl = 0
    with open(outp, "w") as f:
        for (lam, mu, nu, d, h1, hd, hs) in pool:
            rec = {"lam": list(lam), "mu": list(mu), "nu": list(nu),
                   "d": d, "hstar_1": h1, "hstar_d": hd, "hstar": list(hs)}
            try:
                A, b, damb, interior, ok = build(lam, mu, nu)
                verts, tights = sample_vertices(A, b, damb, K, seed)
                if verts is None:
                    rec["vertex_status"] = "NO_VERTEX_FOUND"
                else:
                    frac = [v for v in verts if any(x.denominator != 1 for x in v)]
                    rec["nverts_found"] = len(verts)
                    rec["nfrac_verts"] = len(frac)
                    rec["NON_LATTICE_CERTIFIED"] = len(frac) > 0
                    rec["denoms"] = sorted(set(x.denominator for v in verts for x in v))
                    if frac:
                        nnl += 1
                        rec["example_frac_vertex"] = [str(x) for x in frac[0]]
                    rec["vertex_status"] = "OK"
            except Exception as e:                      # noqa: BLE001
                rec["vertex_status"] = "ERR:%s" % e
            f.write(json.dumps(rec) + "\n")
    sys.stderr.write("non-lattice certified: %d\n" % nnl)


if __name__ == "__main__":
    main()
