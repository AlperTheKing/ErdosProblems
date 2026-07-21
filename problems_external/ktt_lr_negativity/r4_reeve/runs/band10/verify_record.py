#!/usr/bin/env python3
"""
verify_record.py -- BAND 10 record verification.

Given a gap vector (or an explicit triple), recompute with hive4.py the exact
dim / c / V / h* / Ehrhart polynomial, and cross-check c = L(1) against the two
independent LR engines:
    A : engine/lr_hive.exe          "lam" "mu" "nu" [cap]
    B : engine/engineB_lrrule.py    "lam" "mu" "nu" [cap]
Optionally also cross-check the stretched values L(n) = c(n nu; n lam, n mu)
for n = 0..NMAX against both engines and re-interpolate the polynomial.

usage: verify_record.py --gaps a1 a2 a3 b1 b2 b3 c1 c2 c3 [--nmax N] [--cap C]
       verify_record.py --triple "l1,l2,l3,l4" "m..." "n..." [--nmax N]
"""
import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # .../r4_reeve
BASE = os.path.dirname(ROOT)                           # .../ktt_lr_negativity
sys.path.insert(0, ROOT)
import hive4  # noqa: E402

ENG_A = os.path.join(BASE, "engine", "lr_hive.exe")
ENG_B = os.path.join(BASE, "engine", "engineB_lrrule.py")


def gaps_to_triple(g):
    Aw = 3 * g[2] + 2 * g[1] + g[0]
    Bw = 3 * g[5] + 2 * g[4] + g[3]
    Cw = 3 * g[8] + 2 * g[7] + g[6]
    D = Cw - Aw - Bw
    if D % 4 != 0:
        raise SystemExit("gap vector not realisable (4 does not divide D=%d)" % D)
    k = D // 4
    l4 = k if k >= 0 else 0
    n4 = 0 if k >= 0 else -k
    lam = [l4 + g[2] + g[1] + g[0], l4 + g[2] + g[1], l4 + g[2], l4]
    mu = [g[5] + g[4] + g[3], g[5] + g[4], g[5], 0]
    nu = [n4 + g[8] + g[7] + g[6], n4 + g[8] + g[7], n4 + g[8], n4]
    return lam, mu, nu


def fmt(p):
    return ",".join(str(x) for x in p)


def eng(cmd, lam, mu, nu, cap, timeout):
    try:
        r = subprocess.run(cmd + [fmt(lam), fmt(mu), fmt(nu), str(cap)],
                           capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else "EMPTY"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:  # engine missing etc.
        return "ERR:%s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaps", nargs=9, type=int)
    ap.add_argument("--triple", nargs=3)
    ap.add_argument("--nmax", type=int, default=5)
    ap.add_argument("--cap", type=int, default=10 ** 7)
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    if a.gaps:
        lam, mu, nu = gaps_to_triple(a.gaps)
    else:
        lam, mu, nu = [[int(t) for t in s.split(",")] for s in a.triple]

    r = hive4.analyze(lam, mu, nu)
    out = {
        "lam": lam, "mu": mu, "nu": nu,
        "weight": sum(nu),
        "dim": r["dim"], "n_vertices": r.get("n_vertices"),
        "c": r["c"], "V": str(r["volume_normalized"]),
        "hstar": r["hstar"], "L": r["L"],
        "poly_ascending": [hive4._fmt_frac(x) for x in r["poly"]],
        "min_coeff": hive4._fmt_frac(r["min_coeff"]),
        "NEG": r["neg"], "interp_verified_at_n=4,5": r["verified"],
        "vol_crosscheck": r.get("vol_crosscheck"),
        "vertices": r.get("vertices"),
    }
    # independent LR engines on the stretched sequence
    xa, xb = [], []
    for n in range(0, a.nmax + 1):
        L = [n * x for x in lam]
        M = [n * x for x in mu]
        N = [n * x for x in nu]
        if n == 0:
            xa.append("1"); xb.append("1"); continue
        xa.append(eng([ENG_A], L, M, N, a.cap, a.timeout))
        xb.append(eng([sys.executable, ENG_B], L, M, N, a.cap, a.timeout))
    out["engineA_stretched"] = xa
    out["engineB_stretched"] = xb
    out["hive4_stretched"] = [str(x) for x in r["L"][:a.nmax + 1]]
    agree = all(xa[i] == out["hive4_stretched"][i] for i in range(len(xa)) if xa[i].isdigit())
    agreeB = all(xb[i] == out["hive4_stretched"][i] for i in range(len(xb)) if xb[i].isdigit())
    out["engineA_agrees_where_computed"] = agree
    out["engineB_agrees_where_computed"] = agreeB
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
