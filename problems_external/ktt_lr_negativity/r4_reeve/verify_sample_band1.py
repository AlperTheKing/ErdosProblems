#!/usr/bin/env python3
"""
verify_sample_band1.py -- cross-engine audit of the band1 census on a random
sample of the FULL band (not only the dim-3 stratum), so that the large
population of c = 0 / dim = 0 triples is independently confirmed too.

For each sampled triple the polytope engine's L(1), L(2), L(3) are compared
with c(n*nu; n*lam, n*mu) from engine A (lr_hive.exe) and engine B
(engineB_lrrule.py).  Exact integers only.
"""

import argparse
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(os.path.dirname(HERE), "engine")
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from census_band1 import P  # noqa: E402


def pstr(p):
    return ",".join(map(str, p)) if p else "0"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=20260721)
    ap.add_argument("--nmax", type=int, default=3)
    ap.add_argument("--wmin", type=int, default=4)
    ap.add_argument("--wmax", type=int, default=14)
    ap.add_argument("--cap", type=int, default=100000000)
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "band1", "sample_verify.json"))
    args = ap.parse_args(argv)

    rng = random.Random(args.seed)
    all_t = []
    for W in range(args.wmin, args.wmax + 1):
        for a in range(W + 1):
            for lam in P(a):
                for mu in P(W - a):
                    for nu in P(W):
                        all_t.append((lam, mu, nu))
    print("band size:", len(all_t))
    samp = rng.sample(all_t, min(args.n, len(all_t)))

    lines, index, refs = [], [], []
    n_zero = 0
    for lam, mu, nu in samp:
        r = hive4.analyze(list(lam), list(mu), list(nu))
        if r["c"] == 0:
            n_zero += 1
        refs.append(r["L"])
        for n in range(1, args.nmax + 1):
            lines.append("%s;%s;%s;%d" % (pstr([n * x for x in lam]),
                                          pstr([n * x for x in mu]),
                                          pstr([n * x for x in nu]), args.cap))
            index.append((len(refs) - 1, n))
    bf = os.path.join(HERE, "runs", "band1", "_sample_verify.batch")
    os.makedirs(os.path.dirname(bf), exist_ok=True)
    with open(bf, "w") as f:
        f.write("\n".join(lines) + "\n")

    outA = subprocess.run([os.path.join(ENG, "lr_hive.exe"), "--batch", bf],
                          capture_output=True, text=True, check=True).stdout.split()
    outB = subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"), "--batch", bf],
                          capture_output=True, text=True, check=True).stdout.split()
    assert len(outA) == len(lines) == len(outB)

    bad = []
    for (i, n), a, b in zip(index, outA, outB):
        ref = refs[i][n]
        if a != str(ref) or b != str(ref):
            lam, mu, nu = samp[i]
            bad.append({"lam": list(lam), "mu": list(mu), "nu": list(nu), "n": n,
                        "hive4": ref, "A": a, "B": b})
    res = {"sampled": len(samp), "of_band": len(all_t), "seed": args.seed,
           "nmax": args.nmax, "checks": 2 * len(lines),
           "sampled_c_zero": n_zero, "mismatches": bad,
           "all_agree": not bad}
    with open(args.out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}, indent=1))
    return 0 if res["all_agree"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
