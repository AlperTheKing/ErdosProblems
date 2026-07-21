#!/usr/bin/env python3
"""
xval_engines_band5.py -- independent-engine gate.

Takes dim-3 band triples, and for each checks the STRETCHED Littlewood-Richardson
counts c(n nu; n lam, n mu) for n = 1,2 (and n=3 for the smaller ones) against BOTH
independent exact LR engines:
    A  engine/lr_hive.exe
    B  engine/engineB_lrrule.py
and against the polytope engine's L(n).  Disagreement is fatal.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.normpath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
from xval_band5 import parts_le4, contained  # noqa: E402


def s(p):
    t = [x for x in p if x > 0]
    return ",".join(map(str, t)) if t else "0"


def scale(p, n):
    return [x * n for x in p if x > 0] or [0]


def main(ntrip=40, nmax=3, seed=424242, wlo=33, whi=38, cap=2000000):
    rng = random.Random(seed)
    cache = {}

    def P(n):
        if n not in cache:
            cache[n] = parts_le4(n)
        return cache[n]

    pool = []
    while len(pool) < 200000:
        W = rng.randint(wlo, whi)
        nu = rng.choice(P(W))
        a = rng.randint(0, W)
        lam = rng.choice(P(a))
        mu = rng.choice(P(W - a))
        if contained(lam, nu) and contained(mu, nu):
            pool.append((lam, mu, nu))
    bf = os.path.join(HERE, "_xval_eng_pool.txt")
    with open(bf, "w") as f:
        for lam, mu, nu in pool:
            f.write("%s;%s;%s\n" % (s(lam), s(mu), s(nu)))
    out = subprocess.run([os.path.join(HERE, "census_band5.exe"), "--check", bf],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    d3 = [(t, l) for t, l in zip(pool, out) if " dim=3 " in l]
    rng.shuffle(d3)
    d3 = d3[:ntrip]

    jobs = []
    for (lam, mu, nu), line in d3:
        L = [int(x) for x in dict(tok.split("=", 1) for tok in line.split("|", 1)[1].split()
                                  if "=" in tok)["L"].split(",")]
        for n in range(1, nmax + 1):
            jobs.append((lam, mu, nu, n, L[n]))

    batch = os.path.join(HERE, "_xval_eng.batch")
    with open(batch, "w") as f:
        for lam, mu, nu, n, _ in jobs:
            f.write("%s;%s;%s;%d\n" % (s(scale(lam, n)), s(scale(mu, n)), s(scale(nu, n)), cap))

    ra = subprocess.run([os.path.join(ENG, "lr_hive.exe"), "--batch", batch],
                        capture_output=True, text=True, check=True).stdout.split()
    rb = subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"), "--batch", batch],
                        capture_output=True, text=True, check=True).stdout.split()
    assert len(ra) == len(jobs) and len(rb) == len(jobs), (len(ra), len(rb), len(jobs))

    bad = []
    for (lam, mu, nu, n, Ln), a, b in zip(jobs, ra, rb):
        if a != str(Ln) or b != str(Ln):
            bad.append((list(lam), list(mu), list(nu), n, Ln, a, b))
    print("dim-3 triples gated : %d   (n = 1..%d, %d stretched counts)" % (len(d3), nmax, len(jobs)))
    print("engine A/B vs polytope L(n) mismatches: %d" % len(bad))
    for x in bad[:20]:
        print("   ", x)
    with open(os.path.join(HERE, "runs", "band5", "xval_engines_report.json"), "w") as f:
        json.dump({"triples": len(d3), "checks": len(jobs), "mismatches": len(bad),
                   "seed": seed, "detail": bad[:50]}, f, indent=1)
    print("XVAL-ENGINES:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    sys.exit(main(k))
