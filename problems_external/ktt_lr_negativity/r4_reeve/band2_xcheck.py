#!/usr/bin/env python3
"""
band2_xcheck.py -- independent cross-validation of the hive4 engine ON THE
BAND-2 STRATUM ITSELF (W = |nu| in [15,20]).

For a deterministic pseudo-random sample of band triples (all of them dim-3,
the only stratum where an Ehrhart negativity can live), recompute the stretched
LR counts c(n*nu; n*lam, n*mu) for n = 1,2,3 with BOTH external exact engines
(A = lr_hive.exe, B = engineB_lrrule.py) and compare against the polytope
engine's Ehrhart polynomial P(n).  Any mismatch is a hard failure and is
reported, never smoothed over.
"""

import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4          # noqa: E402
import band2_census as B  # noqa: E402

ENG = os.path.join(os.path.dirname(HERE), "engine")
EXE_A = os.path.join(ENG, "lr_hive.exe")
EXE_B = os.path.join(ENG, "engineB_lrrule.py")


def pstr(p):
    p = [x for x in p if x > 0]
    return ",".join(str(x) for x in p) if p else "0"


def engA(lam, mu, nu):
    o = subprocess.run([EXE_A, pstr(lam), pstr(mu), pstr(nu)],
                       capture_output=True, text=True)
    return o.stdout.strip()


def engB(lam, mu, nu):
    o = subprocess.run([sys.executable, EXE_B, pstr(lam), pstr(mu), pstr(nu)],
                       capture_output=True, text=True)
    return o.stdout.strip()


def main(nsample=40, wmin=15, wmax=20, seed=20260721):
    rng = random.Random(seed)
    pool = []
    t0 = time.time()
    # collect dim-3 band triples
    while len(pool) < nsample * 40 and time.time() - t0 < 120:
        W = rng.randint(wmin, wmax)
        nus = B.P4(W)
        a = rng.randint(0, W)
        lams = B.P4(a)
        mus = B.P4(W - a)
        lam = rng.choice(lams)
        mu = rng.choice(mus)
        nu = rng.choice(nus)
        r = hive4.analyze(list(lam), list(mu), list(nu))
        if r["dim"] == 3:
            pool.append((lam, mu, nu, r))
    rng.shuffle(pool)
    sample = pool[:nsample]
    checks = 0
    fails = []
    recs = []
    for lam, mu, nu, r in sample:
        row = {"lam": list(lam), "mu": list(mu), "nu": list(nu),
               "poly": [hive4._fmt_frac(c) for c in r["poly"]],
               "hstar": list(r["hstar"]), "V": str(r["volume_normalized"]),
               "n": {}}
        for n in (1, 2, 3):
            Pn = hive4.polyval(r["poly"], n)
            l = [x * n for x in lam]
            m = [x * n for x in mu]
            v = [x * n for x in nu]
            a = engA(l, m, v)
            b = engB(l, m, v)
            row["n"][n] = {"P": str(Pn), "A": a, "B": b}
            checks += 1
            if not (a == b == str(Pn) == str(int(Pn))):
                fails.append((lam, mu, nu, n, str(Pn), a, b))
        recs.append(row)
    out = {"sampled_dim3_triples": len(sample), "checks": checks,
           "failures": len(fails), "failure_list": fails,
           "band": "W in [%d,%d]" % (wmin, wmax), "seed": seed,
           "records": recs}
    d = os.path.join(HERE, "runs", "band2")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "xcheck.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("dim-3 band triples sampled: %d ; cross-engine checks: %d ; FAILURES: %d"
          % (len(sample), checks, len(fails)))
    for f_ in fails[:20]:
        print("FAIL", f_)
    return 0 if not fails else 1


if __name__ == "__main__":
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    sys.exit(main(ns))
