#!/usr/bin/env python3
"""
validate_gapscan.py -- end-to-end gate on the band-8 gap-class scanner.

For a random band triple (lam, mu, nu), |nu| = W in [61,90]:
  * compute its 9 gaps  a_i = lam_i - lam_{i+1}, b_i, c_i
  * feed ONLY the gaps to band8_gapscan2.exe --one, which rebuilds a (different)
    representative triple of the class and evaluates it with the fast routine
  * compare L(1), L(2), L(3), V, 6a1, h* against hive4.py's exact Fraction
    analysis of the ORIGINAL triple.

This simultaneously tests
  (i)  the moduli reduction  (statistics depend only on the gaps),
  (ii) the fast lattice-count rewrite,
  (iii) the region/representative bookkeeping.
Any mismatch is printed verbatim.  No floating point is used in any comparison.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, R4)
import hive4  # noqa: E402

EXE = os.path.join(HERE, "band8_gapscan2.exe")


def gaps(p):
    return [p[0] - p[1], p[1] - p[2], p[2] - p[3]]


def call_one(a, b, c):
    args = [EXE, "--one"] + [str(x) for x in a + b + c]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    d = {}
    for line in out.splitlines():
        for tok in line.split():
            if "=" in tok and not tok.startswith("lam") and not tok.startswith("mu") and not tok.startswith("nu"):
                k, v = tok.split("=", 1)
                d[k] = v
        if line.startswith("lam="):
            d["repr"] = line.strip()
    return d, out


def rand_partition4(S, rng):
    x = sorted(rng.randint(0, S) for _ in range(3))
    return sorted([x[0], x[1] - x[0], x[2] - x[1], S - x[2]], reverse=True)


def main(ntest=200, seed=8008):
    rng = random.Random(seed)
    bad = []
    tested = 0
    nonempty = 0
    while tested < ntest:
        W = rng.randint(61, 90)
        nu = rand_partition4(W, rng)
        A = rng.randint(0, W)
        lam = rand_partition4(A, rng)
        mu = rand_partition4(W - A, rng)
        if any(lam[i] > nu[i] for i in range(4)) or any(mu[i] > nu[i] for i in range(4)):
            if rng.random() < 0.85:
                continue                      # bias toward c > 0
        tested += 1
        a, b, c = gaps(lam), gaps(mu), gaps(nu)
        got, raw = call_one(a, b, c)
        ref = hive4.analyze(lam, mu, nu)
        L = ref["L"]
        six_a1 = -11 + 18 * L[1] - 9 * L[2] + 2 * L[3] if L[1] else None
        V = int(ref["volume_normalized"])
        exp_valid = 1 if L[1] > 0 else 0
        rec = {"lam": lam, "mu": mu, "nu": nu, "gaps": [a, b, c], "exe": got,
               "hive4_L": L[:4], "hive4_V": V, "hive4_hstar": ref["hstar"]}
        ok = True
        if int(got.get("valid", -1)) != exp_valid:
            ok = False
        if exp_valid:
            nonempty += 1
            exeL = [int(x) for x in got["L"].strip("()").split(",")]
            if exeL != L[1:4]:
                ok = False
            if int(got["6a1"]) != six_a1:
                ok = False
            if int(got["V"]) != V:
                ok = False
            # h* is only comparable when dim Q = 3 (hive4 returns the dim+1
            # truncated h*-vector; the scanner always prints the dim-3 formula)
            if ref["dim"] == 3:
                hs = [int(x) for x in got["h*"].strip("()").split(",")]
                if hs != list(ref["hstar"]):
                    ok = False
            # the interpolated P must reproduce the directly enumerated L(4),L(5)
            if not ref["verified"]:
                ok = False
                rec["interp_fail"] = True
            # and 6*a1 from the exact Fraction polynomial must agree
            if len(ref["poly"]) > 1 and 6 * ref["poly"][1] != six_a1:
                ok = False
                rec["poly_a1"] = str(ref["poly"][1])
        if not ok:
            rec["raw"] = raw
            bad.append(rec)
            print("MISMATCH", json.dumps(rec, default=str))
    out = {"tested": tested, "nonempty": nonempty, "n_mismatch": len(bad),
           "mismatches": bad[:5], "verdict": "PASS" if not bad else "FAIL"}
    with open(os.path.join(HERE, "validation_gapscan.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("tested", "nonempty", "n_mismatch", "verdict")}))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 200,
                  int(sys.argv[2]) if len(sys.argv) > 2 else 8008))
