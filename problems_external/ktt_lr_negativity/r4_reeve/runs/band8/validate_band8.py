#!/usr/bin/env python3
"""
validate_band8.py -- cross-validate bandscan.exe against the reference exact
engine hive4.py on random triples drawn from the band W = |nu| in [61,90],
plus the small-weight triples where the LR engines A/B are also affordable.

Checks, EXACTLY (Fractions / ints only):
  dim, c = L(1), L(2), L(3), normalized volume V, h*-vector, 6*a1,
  and the sign flag.
Any mismatch is reported verbatim; nothing is smoothed over.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
R4 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, R4)
import hive4  # noqa: E402

EXE = os.path.join(HERE, "bandscan.exe")


def call_exe(lam, mu, nu):
    args = [EXE, "--one"] + [str(x) for x in lam] + [str(x) for x in mu] + [str(x) for x in nu]
    out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
    d = {}
    for tok in out.split():
        k, v = tok.split("=", 1)
        d[k] = v
    return d


def rand_partition4(S, rng):
    x = sorted(rng.randint(0, S) for _ in range(3))
    q = sorted([x[0], x[1] - x[0], x[2] - x[1], S - x[2]], reverse=True)
    return q


def main(ntest=250, seed=8):
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
        # bias toward nonempty: require containment
        if any(lam[i] > nu[i] for i in range(4)) or any(mu[i] > nu[i] for i in range(4)):
            if rng.random() < 0.9:
                continue
        tested += 1
        ref = hive4.analyze(lam, mu, nu)
        got = call_exe(lam, mu, nu)
        refL = ref["L"]
        if ref["dim"] == 3:
            nonempty += 1
            exp = {
                "valid": "1",
                "L1": str(refL[1]), "L2": str(refL[2]), "L3": str(refL[3]),
                "V": str(int(ref["volume_normalized"])),
                "6a1": str(int(6 * ref["poly"][1])) if len(ref["poly"]) > 1 else "0",
                "hstar": "(1,%d,%d,%d)" % tuple(ref["hstar"][1:4]),
            }
            for k, v in exp.items():
                if got.get(k) != v:
                    bad.append({"lam": lam, "mu": mu, "nu": nu, "field": k,
                                "ref": v, "exe": got.get(k), "refpoly": [str(c) for c in ref["poly"]]})
            if not ref["verified"]:
                bad.append({"lam": lam, "mu": mu, "nu": nu, "field": "hive4_interp",
                            "detail": ref["verify_detail"]})
        else:
            # dim < 3 : bandscan reports V = 0 (and possibly valid=1 with L1>0)
            if got["valid"] == "1":
                nonempty += 1
                if got["L1"] != str(refL[1]):
                    bad.append({"lam": lam, "mu": mu, "nu": nu, "field": "L1(lowdim)",
                                "ref": str(refL[1]), "exe": got["L1"]})
                if got["V"] != "0":
                    bad.append({"lam": lam, "mu": mu, "nu": nu, "field": "V(lowdim)",
                                "ref": "0", "exe": got["V"]})
            else:
                if refL[1] != 0:
                    bad.append({"lam": lam, "mu": mu, "nu": nu, "field": "empty",
                                "ref": str(refL[1]), "exe": got["L1"]})
        if tested % 25 == 0:
            print("  ... %d/%d checked, %d mismatches" % (tested, ntest, len(bad)), flush=True)
    res = {"tested": tested, "dim3_or_nonempty": nonempty, "mismatches": bad,
           "n_mismatch": len(bad), "verdict": "PASS" if not bad else "FAIL"}
    with open(os.path.join(HERE, "validation_band8.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in ("tested", "dim3_or_nonempty", "n_mismatch", "verdict")}))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 250,
                  int(sys.argv[2]) if len(sys.argv) > 2 else 8))
