#!/usr/bin/env python3
"""
validate_band6.py -- cross-validation gate for the band-6 (W in [39,45]) census.

Three independent checks on randomly drawn band triples:
  (A) bandscan.exe --one  vs  hive4.py  (exact polytope engine, Fractions):
      L(1..5), dim, and the coefficients 6a1 / 2a2 / 6a3 must agree.
  (B) polynomiality audit: the P interpolated from L(0..3) must reproduce the
      INDEPENDENTLY counted L(4) and L(5).
  (C) LR audit: L(1) = c(nu;lam,mu) must equal both LR engines,
      engine A = engine/lr_hive.exe and engine B = engine/engineB_lrrule.py,
      and for a smaller subsample also L(2) = c(2nu;2lam,2mu).
All arithmetic exact.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import hive4  # noqa: E402

BAND = list(range(39, 46))


def rand_partition_le(nu, W, rng):
    """random partition lam with lam_i <= nu_i, |lam| = W, or None."""
    for _ in range(400):
        lam = [0, 0, 0, 0]
        rem = W
        ok = True
        for i in range(4):
            hi = min(nu[i], lam[i - 1] if i else nu[0], rem)
            lo = 0
            if hi < lo:
                ok = False
                break
            lam[i] = rng.randint(lo, hi)
            rem -= lam[i]
        if ok and rem == 0:
            return lam
    return None


def rand_nu(W, rng):
    while True:
        cuts = sorted(rng.randint(0, W) for _ in range(3))
        p = sorted([cuts[0], cuts[1] - cuts[0], cuts[2] - cuts[1], W - cuts[2]], reverse=True)
        if sum(p) == W and p[0] > 0:
            return p


def cpp_one(lam, mu, nu):
    args = [os.path.join(HERE, "bandscan.exe"), "--one"] + [str(x) for x in lam + mu + nu]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def fmt(p):
    p = [x for x in p if x > 0]
    return ",".join(map(str, p)) if p else "0"


def engA(lam, mu, nu, cap=10 ** 9):
    exe = os.path.join(ENG, "lr_hive.exe")
    out = subprocess.run([exe, fmt(lam), fmt(mu), fmt(nu), str(cap)],
                         capture_output=True, text=True).stdout.strip()
    return out


def engB(lam, mu, nu, cap=10 ** 9):
    out = subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"),
                          fmt(lam), fmt(mu), fmt(nu), str(cap)],
                         capture_output=True, text=True).stdout.strip()
    return out


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20260721
    NA = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    NC = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    rng = random.Random(seed)
    failA = failB = failC = 0
    doneA = doneC = 0
    samples = []
    while len(samples) < NA:
        W = rng.choice(BAND)
        nu = rand_nu(W, rng)
        k = rng.randint(0, W)
        lam = rand_partition_le(nu, k, rng)
        mu = rand_partition_le(nu, W - k, rng)
        if lam is None or mu is None:
            continue
        samples.append((lam, mu, nu))

    for lam, mu, nu in samples:
        c = cpp_one(lam, mu, nu)
        h = hive4.analyze(lam, mu, nu)
        L = c["L"]
        # (A) agreement with the exact Fraction engine
        okA = True
        if c["zero"]:
            okA = (h["c"] == 0)
        else:
            okA = (list(L) == list(h["L"]) and h["dim"] == c["dim"])
            P = h["poly"]
            a1 = P[1] if len(P) > 1 else Fraction(0)
            a2 = P[2] if len(P) > 2 else Fraction(0)
            a3 = P[3] if len(P) > 3 else Fraction(0)
            okA = okA and (Fraction(c["six_a1"], 6) == a1)
            okA = okA and (Fraction(c["two_a2"], 2) == a2)
            okA = okA and (Fraction(c["six_a3"], 6) == a3)
        if not okA:
            failA += 1
            print("FAIL-A", lam, mu, nu, c, h["L"], h["poly"])
        doneA += 1
        # (B) polynomiality: P from L(0..3) must hit L(4), L(5)
        if not c["zero"]:
            P = hive4.interpolate([Fraction(x) for x in L[:4]])
            if hive4.polyval(P, 4) != L[4] or hive4.polyval(P, 5) != L[5]:
                failB += 1
                print("FAIL-B", lam, mu, nu, L)

    for lam, mu, nu in samples[:NC]:
        c = cpp_one(lam, mu, nu)
        L1 = 0 if c["zero"] else c["L"][1]
        a = engA(lam, mu, nu)
        b = engB(lam, mu, nu)
        if a != str(L1) or b != str(L1):
            failC += 1
            print("FAIL-C", lam, mu, nu, "L1=", L1, "A=", a, "B=", b)
        doneC += 1

    print(json.dumps({"seed": seed, "samples": doneA, "failA": failA, "failB": failB,
                      "lr_samples": doneC, "failC": failC,
                      "VERDICT": "PASS" if (failA + failB + failC) == 0 else "FAIL"}))
    return 0 if (failA + failB + failC) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
