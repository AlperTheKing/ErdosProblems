#!/usr/bin/env python3
"""
verify_dim3_band1.py -- independent re-verification of the dim-3 stratum of
band1 against the two cross-calibrated LR engines.

For every dim-3 triple found by collect_dim3_band1.py we recompute the STRETCHED
Littlewood-Richardson numbers  c(n*nu; n*lam, n*mu)  for n = 1..NMAX with
  engine A : engine/lr_hive.exe   (C++ hive counter)
  engine B : engine/engineB_lrrule.py  (LR-rule counter)
and compare, entry by entry, with the polytope engine's L(n); then we
re-interpolate P from the ENGINE values and check it equals the polytope
engine's P.  Any disagreement is reported, never smoothed over.

Only exact integers / Fractions are used.
"""

import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(os.path.dirname(HERE), "engine")
sys.path.insert(0, HERE)
from hive4 import interpolate, trim, polyval  # noqa: E402
from census_band1 import _fmt  # noqa: E402


def pstr(p):
    return ",".join(map(str, p)) if p else "0"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--recs", default=os.path.join(HERE, "runs", "band1", "dim3_band1.json"))
    ap.add_argument("--nmax", type=int, default=5)
    ap.add_argument("--cap", type=int, default=100000000)
    ap.add_argument("--out", default=os.path.join(HERE, "runs", "band1", "dim3_verify.json"))
    args = ap.parse_args(argv)

    recs = json.load(open(args.recs))
    print("dim-3 records:", len(recs))

    lines = []
    index = []
    for i, r in enumerate(recs):
        for n in range(1, args.nmax + 1):
            lam = [n * x for x in r["lam"]]
            mu = [n * x for x in r["mu"]]
            nu = [n * x for x in r["nu"]]
            lines.append("%s;%s;%s;%d" % (pstr(lam), pstr(mu), pstr(nu), args.cap))
            index.append((i, n))
    bfile = os.path.join(HERE, "runs", "band1", "_dim3_verify.batch")
    with open(bfile, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("batch lines:", len(lines))

    outA = subprocess.run([os.path.join(ENG, "lr_hive.exe"), "--batch", bfile],
                          capture_output=True, text=True, check=True).stdout.split()
    print("engine A returned", len(outA))
    outB = subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"), "--batch", bfile],
                          capture_output=True, text=True, check=True).stdout.split()
    print("engine B returned", len(outB))
    assert len(outA) == len(lines) and len(outB) == len(lines), "engine output length mismatch"

    mismatches = []
    polyfail = []
    negcheck = []
    for (i, n), a, b in zip(index, outA, outB):
        r = recs[i]
        ref = r["L"][n]
        if a != str(ref) or b != str(ref):
            mismatches.append({"lam": r["lam"], "mu": r["mu"], "nu": r["nu"], "n": n,
                               "hive4_L": ref, "engineA": a, "engineB": b})
    # rebuild P from ENGINE values (using L(0)=1 and engine L(1..3)), compare
    byrec = {}
    for (i, n), a in zip(index, outA):
        byrec.setdefault(i, {})[n] = int(a)
    for i, r in enumerate(recs):
        Le = [1] + [byrec[i][n] for n in range(1, args.nmax + 1)]
        Pe = trim(interpolate([Fraction(x) for x in Le[:4]]))
        Ps = [Fraction(x) for x in r["poly"]]
        ok45 = all(polyval(Pe, n) == Le[n] for n in (4, 5) if n <= args.nmax)
        if [_fmt(x) for x in Pe] != r["poly"] or not ok45:
            polyfail.append({"lam": r["lam"], "mu": r["mu"], "nu": r["nu"],
                             "engineP": [_fmt(x) for x in Pe], "hive4P": r["poly"],
                             "engineL": Le, "held_out_ok": ok45})
        if min(Pe) < 0:
            negcheck.append({"lam": r["lam"], "mu": r["mu"], "nu": r["nu"],
                             "P": [_fmt(x) for x in Pe], "L": Le})

    res = {
        "n_dim3": len(recs), "nmax": args.nmax,
        "checks": len(lines) * 2,
        "mismatches": mismatches,
        "poly_rebuild_failures": polyfail,
        "engine_confirmed_negative": negcheck,
        "all_agree": not mismatches and not polyfail,
    }
    with open(args.out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()}, indent=1))
    return 0 if res["all_agree"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
