#!/usr/bin/env python3
"""Cross-check gapscan.exe against hive4.py (and, on a sample, against the two
independent LR counters engine A / engine B) on random gap vectors."""
import random
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from hive4 import analyze, trim
from gap_moduli import triple_from_gaps

EXE = "./gapscan.exe"
ENGA = "../engine/lr_hive.exe"
ENGB = "../engine/engineB_lrrule.py"


def run_one(g):
    out = subprocess.run([EXE, "--one"] + [str(x) for x in g], capture_output=True, text=True).stdout.strip()
    d = dict(kv.split("=") for kv in out.split())
    d["six_a1"] = d.pop("6a1")
    return {k: int(v) for k, v in d.items()}


def main():
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    rnd = random.Random(20260721)
    checked = 0
    bad = 0
    lr_checked = 0
    for _ in range(N * 4):
        if checked >= N:
            break
        g = [rnd.randint(0, G) for _ in range(9)]
        t = triple_from_gaps(tuple(g[:3]), tuple(g[3:6]), tuple(g[6:]))
        r = run_one(g)
        if t is None:
            if r["valid"] != 0:
                print("VALIDITY MISMATCH", g)
                bad += 1
            continue
        lam, mu, nu = t
        res = analyze(lam, mu, nu)
        L = res["L"]
        if L[1] == 0:  # Q empty: P == 0, excluded by design on both sides
            if r["valid"] != 0:
                print("EMPTY MISMATCH", g, lam, mu, nu, r)
                bad += 1
            continue
        exp6a1 = -11 + 18 * L[1] - 9 * L[2] + 2 * L[3]
        expV = L[3] - 3 * L[2] + 3 * L[1] - 1
        py_a1 = trim(res["poly"])
        py_a1 = py_a1[1] if len(py_a1) > 1 else Fraction(0)
        problems = []
        if r["valid"] != 1:
            problems.append("valid")
        else:
            if (r["L1"], r["L2"], r["L3"]) != (L[1], L[2], L[3]):
                problems.append("L(%s vs %s)" % ((r["L1"], r["L2"], r["L3"]), tuple(L[1:4])))
            if r["six_a1"] != exp6a1:
                problems.append("6a1")
            if r["V"] != expV:
                problems.append("V")
            if Fraction(r["six_a1"], 6) != py_a1:
                problems.append("a1 vs interpolated poly")
            if not res["verified"]:
                problems.append("hive4 interpolation not verified at L(4),L(5)")
            if res["dim"] == 3 and Fraction(expV) != res["volume_normalized"]:
                problems.append("V vs triangulated volume")
        checked += 1
        if problems:
            bad += 1
            if bad < 10:
                print("MISMATCH", g, lam, mu, nu, problems)
        # independent LR engines on a subsample (L(1) and L(2))
        if checked % 25 == 0:
            for n in (1, 2):
                args = [",".join(str(n * x) for x in p) for p in (lam, mu, nu)]
                a = subprocess.run([ENGA] + args + ["1000000"], capture_output=True, text=True).stdout.strip()
                b = subprocess.run([sys.executable, ENGB] + args + ["1000000"], capture_output=True, text=True).stdout.strip()
                want = str(L[n])
                lr_checked += 1
                if a.split()[-1] != want or b.split()[-1] != want:
                    bad += 1
                    print("LR ENGINE MISMATCH", lam, mu, nu, "n=", n, "hive4=", want, "A=", a, "B=", b)
    print("checked %d gap vectors, %d LR-engine cross-checks, %d mismatches" % (checked, lr_checked, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
