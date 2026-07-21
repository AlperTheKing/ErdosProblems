#!/usr/bin/env python3
"""
xengine_band8.py -- tie the band-8 polytope statistics to ACTUAL stretched
Littlewood-Richardson coefficients with two INDEPENDENT exact LR counters.

For random band triples (|nu| = W in [61,90]) with c > 0 it checks, for n = 1,2,3,

    L(n) from the hive polytope   ==   c(n nu; n lam, n mu) from engine A
                                  ==   c(n nu; n lam, n mu) from engine B

where A = engine/lr_hive.exe (hive lattice-point counter) and
      B = engine/engineB_lrrule.py (Littlewood-Richardson tableau rule).

It then re-interpolates P from L(0..3) and prints 6a1 and V, so the negativity
verdict itself is re-derived from LR coefficients alone, with no polytope code
in the loop.  Any disagreement is printed verbatim.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(R4)
sys.path.insert(0, R4)
import hive4  # noqa: E402

ENGA = os.path.join(ROOT, "engine", "lr_hive.exe")
ENGB = os.path.join(ROOT, "engine", "engineB_lrrule.py")
CAP = "100000000"


def _run(args, timeout):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    return r.stdout.strip().splitlines()[-1].strip() if r.stdout.strip() else "EMPTY"


def engA(lam, mu, nu, timeout=300):
    return _run([ENGA, ",".join(map(str, lam)), ",".join(map(str, mu)), ",".join(map(str, nu)), CAP], timeout)


def engB(lam, mu, nu, timeout=300):
    return _run([sys.executable, ENGB, ",".join(map(str, lam)), ",".join(map(str, mu)),
                 ",".join(map(str, nu)), CAP], timeout)


def rand_partition4(S, rng):
    x = sorted(rng.randint(0, S) for _ in range(3))
    return sorted([x[0], x[1] - x[0], x[2] - x[1], S - x[2]], reverse=True)


def check(lam, mu, nu, nmax=3, timeout=300):
    ref = hive4.analyze(lam, mu, nu)
    rec = {"lam": lam, "mu": mu, "nu": nu, "L_polytope": ref["L"][:nmax + 1],
           "V": str(ref["volume_normalized"]), "hstar": ref["hstar"],
           "poly": [str(x) for x in ref["poly"]], "interp_verified": ref["verified"]}
    la, lb, agree = [], [], True
    for n in range(1, nmax + 1):
        sl = [n * x for x in lam]
        sm = [n * x for x in mu]
        sn = [n * x for x in nu]
        a = engA(sl, sm, sn, timeout)
        b = engB(sl, sm, sn, timeout)
        la.append(a)
        lb.append(b)
        want = str(ref["L"][n])
        if a != want or b != want:
            agree = False
    rec["engineA"] = la
    rec["engineB"] = lb
    rec["agree"] = agree
    if agree:
        L = [1] + [int(x) for x in la]
        P = hive4.interpolate(L)
        rec["6a1_from_LR"] = str(6 * P[1])
        rec["V_from_LR"] = str(L[3] - 3 * L[2] + 3 * L[1] - 1)
        rec["neg_from_LR"] = bool(min(hive4.trim(P)) < 0)
    return rec


def main(ntest=12, seed=88, nmax=3):
    rng = random.Random(seed)
    out = []
    tested = 0
    while tested < ntest:
        W = rng.randint(61, 90)
        nu = rand_partition4(W, rng)
        A = rng.randint(0, W)
        lam = rand_partition4(A, rng)
        mu = rand_partition4(W - A, rng)
        if any(lam[i] > nu[i] for i in range(4)) or any(mu[i] > nu[i] for i in range(4)):
            continue
        r = hive4.analyze(lam, mu, nu)
        if r["c"] == 0 or r["c"] > 4000:
            continue                      # keep n=3 counts affordable for A and B
        tested += 1
        rec = check(lam, mu, nu, nmax)
        out.append(rec)
        print(json.dumps(rec))
        sys.stdout.flush()
    bad = [r for r in out if not r["agree"]]
    res = {"tested": tested, "n_disagree": len(bad), "verdict": "PASS" if not bad else "FAIL",
           "records": out}
    with open(os.path.join(HERE, "xengine_band8.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({"tested": tested, "n_disagree": len(bad), "verdict": res["verdict"]}))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 12,
                  int(sys.argv[2]) if len(sys.argv) > 2 else 88))
