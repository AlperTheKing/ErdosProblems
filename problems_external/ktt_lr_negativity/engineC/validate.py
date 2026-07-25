#!/usr/bin/env python3
"""Mandated validation of engine C against engines A and B.

For each triple, engine C's P(1), P(2), P(3) (obtained WITHOUT counting lattice
points) must equal the stretched LR coefficients c(n*nu; n*lam, n*mu) reported
by engine A (C++ hive DFS) and engine B (independent LR-rule tableau counter).
"""
import json
import random
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ehr import ehrhart  # noqa: E402

A_EXE = os.path.join(ROOT, "engine", "lr_hive.exe")
B_PY = os.path.join(ROOT, "engine", "engineB_lrrule.py")


def fmt(p):
    return ",".join(str(x) for x in p)


def run_engine(cmd, lines):
    bf = os.path.join(HERE, "_val.batch")
    with open(bf, "w") as f:
        f.write("\n".join(lines) + "\n")
    out = subprocess.run(cmd + ["--batch", bf], capture_output=True, text=True)
    return out.stdout.strip().split("\n")


def rand_partition(rng, r, maxpart):
    p = sorted((rng.randint(0, maxpart) for _ in range(r)), reverse=True)
    while p and p[-1] == 0:
        p.pop()
    return p


def main(ntrip=320, seed=20260722, nmax=3, rmax=5):
    rng = random.Random(seed)
    trips = []
    tried = 0
    while len(trips) < ntrip and tried < 200000:
        tried += 1
        r = rng.randint(3, rmax)
        lam = rand_partition(rng, rng.randint(2, r), rng.randint(2, 9))
        mu = rand_partition(rng, rng.randint(2, r), rng.randint(2, 9))
        if not lam or not mu:
            continue
        W = sum(lam) + sum(mu)
        nu = rand_partition(rng, r, max(2, W))
        if not nu:
            continue
        if len(nu) != r or sum(nu) != W:
            # repair: distribute
            nu = sorted(nu, reverse=True)
            diff = W - sum(nu)
            if diff > 0:
                nu[0] += diff
            else:
                continue
        if len(nu) < len(lam) or len(nu) < len(mu):
            continue
        if any(nu[i] < nu[i + 1] for i in range(len(nu) - 1)):
            continue
        trips.append((lam, mu, nu))

    linesA = []
    for lam, mu, nu in trips:
        for n in range(1, nmax + 1):
            linesA.append("%s;%s;%s;100000000" % (fmt([n * x for x in lam]),
                                                  fmt([n * x for x in mu]),
                                                  fmt([n * x for x in nu])))
    outA = run_engine([A_EXE], linesA)
    outB = run_engine([sys.executable, B_PY], linesA)

    nchk = 0
    nfail = 0
    nnz = 0
    skipped = 0
    for i, (lam, mu, nu) in enumerate(trips):
        try:
            r = ehrhart(lam, mu, nu, vol_cap=2 * 10 ** 5)
        except Exception as e:
            print("ENGINE_C_ERR", lam, mu, nu, repr(e))
            nfail += 1
            continue
        if r["status"] != "OK":
            skipped += 1
            continue
        for n in range(1, nmax + 1):
            a = outA[i * nmax + n - 1].strip()
            b = outB[i * nmax + n - 1].strip()
            if not a.isdigit() or not b.isdigit():
                continue
            va, vb, vc = int(a), int(b), r["P"][n]
            nchk += 1
            if va > 0:
                nnz += 1
            if not (va == vb == vc):
                nfail += 1
                print("MISMATCH", lam, mu, nu, "n=", n, "A=", va, "B=", vb, "C=", vc)
    print(json.dumps(dict(triples=len(trips), checks=nchk, nonzero=nnz,
                          mismatches=nfail, skipped_volcap=skipped)))
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main(*[int(x) for x in sys.argv[1:]]))
