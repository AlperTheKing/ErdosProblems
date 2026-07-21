#!/usr/bin/env python3
"""
band11_lranchor.py -- anchor the band-11 polytope engine to the two INDEPENDENT
exact Littlewood-Richardson counters (engine A = lr_hive.exe, engine B =
engineB_lrrule.py) on the band-11 record triples.

For each gap vector given on the command line (9 ints per triple, or a built-in
record list), lift to partitions and check
    P(n) = c(n nu; n lam, n mu)   for n = 1..NMAX
with hive4.py (polytope route), engine A and engine B (representation-theory
route).  Any disagreement is printed, never smoothed over.
"""
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import hive4  # noqa: E402
from band11_xcheck import gaps_to_parts  # noqa: E402

A_EXE = os.path.join(ENG, "lr_hive.exe")
B_PY = os.path.join(ENG, "engineB_lrrule.py")


def fmt(p):
    return ",".join(str(x) for x in p if x > 0) or "0"


def engA(lam, mu, nu, cap=10 ** 9):
    r = subprocess.run([A_EXE, fmt(lam), fmt(mu), fmt(nu), str(cap)],
                       capture_output=True, text=True)
    return r.stdout.strip()


def engB(lam, mu, nu, cap=10 ** 9):
    r = subprocess.run([sys.executable, B_PY, fmt(lam), fmt(mu), fmt(nu), str(cap)],
                       capture_output=True, text=True)
    return r.stdout.strip()


def check(g, nmax=4):
    p = gaps_to_parts(g[:3], g[3:6], g[6:])
    if p is None:
        print("gaps %s not realisable" % g)
        return True
    lam, mu, nu = p
    res = hive4.analyze(lam, mu, nu)
    P = res["poly"]
    print("gaps=%s lam=%s mu=%s nu=%s  dim=%d c=%s V=%s h*=%s P=[%s]"
          % (g, lam, mu, nu, res["dim"], res["c"],
             hive4._fmt_frac(res["volume_normalized"]), res["hstar"],
             hive4._pstr(P)))
    ok = True
    for n in range(1, nmax + 1):
        want = hive4.polyval(P, n)
        a = engA([n * x for x in lam], [n * x for x in mu], [n * x for x in nu])
        b = engB([n * x for x in lam], [n * x for x in mu], [n * x for x in nu])
        agree = (a == b == str(want))
        ok &= agree
        print("   n=%d  P(n)=%s  engineA=%s  engineB=%s  %s"
              % (n, want, a, b, "OK" if agree else "*** MISMATCH ***"))
    return ok


def main(argv):
    nmax = 4
    gs = []
    if argv and argv[0] == "--nmax":
        nmax = int(argv[1]); argv = argv[2:]
    if argv:
        vals = [int(x) for x in argv]
        for i in range(0, len(vals), 9):
            gs.append(vals[i:i + 9])
    else:
        gs = [[6, 1, 1, 1, 2, 6, 1, 1, 1],
              [2, 2, 2, 2, 2, 2, 2, 2, 2],
              [3, 3, 3, 3, 3, 3, 3, 3, 3]]
    allok = True
    for g in gs:
        allok &= check(g, nmax)
        print()
    print("ANCHOR:", "PASS" if allok else "FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
