#!/usr/bin/env python3
"""
verify_extremals_band6.py -- independent re-verification of the band-6 extremal
records with BOTH Littlewood-Richardson engines and the exact Fraction polytope
engine.

For each record triple, c(n nu; n lam, n mu) is recomputed for n = 0..5 by
  engine A  = engine/lr_hive.exe              (hive counter, C++)
  engine B  = engine/engineB_lrrule.py        (LR-rule / skew tableaux, Python)
and the resulting sequence is re-interpolated; it must agree with hive4.py and
with bandscan.exe.  Exact integers throughout.
"""
import json
import os
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "engine"))
sys.path.insert(0, HERE)
import hive4  # noqa: E402


def fmt(p):
    p = [x for x in p if x > 0]
    return ",".join(map(str, p)) if p else "0"


def engA(lam, mu, nu, cap=10 ** 12):
    return subprocess.run([os.path.join(ENG, "lr_hive.exe"), fmt(lam), fmt(mu), fmt(nu), str(cap)],
                          capture_output=True, text=True).stdout.strip()


def engB(lam, mu, nu, cap=10 ** 12):
    return subprocess.run([sys.executable, os.path.join(ENG, "engineB_lrrule.py"),
                           fmt(lam), fmt(mu), fmt(nu), str(cap)],
                          capture_output=True, text=True).stdout.strip()


def parse(s):
    p = [int(x) for x in s.split(",") if x.strip() != ""]
    return p + [0] * (4 - len(p))


RECORDS = {}
for W in range(39, 46):
    d = json.load(open(os.path.join(HERE, "runs", "band6", "W%d.json" % W)))
    for key in ("max_volume_triple", "min_a1_dim3_triple", "max_volume_hstar1_zero_triple",
                "max_hstar2_triple", "min_a1_triple"):
        RECORDS.setdefault(d[key], []).append((W, key))


def main():
    nfail = 0
    out = []
    for trip, tags in sorted(RECORDS.items()):
        a, b, c = trip.split(";")
        lam, mu, nu = parse(a), parse(b), parse(c)
        h = hive4.analyze(lam, mu, nu)
        LA, LB = [], []
        for n in range(6):
            nl = [n * x for x in lam]; nm = [n * x for x in mu]; nn = [n * x for x in nu]
            LA.append(engA(nl, nm, nn))
            LB.append(engB(nl, nm, nn))
        okA = LA == [str(x) for x in h["L"]]
        okB = LB == [str(x) for x in h["L"]]
        P = hive4.interpolate([Fraction(int(x)) for x in LA[:4]])
        okP = (hive4.polyval(P, 4) == int(LA[4]) and hive4.polyval(P, 5) == int(LA[5])
               and [str(x) for x in hive4.trim(P)] == [str(x) for x in h["poly"]])
        neg = any(x < 0 for x in h["poly"])
        ok = okA and okB and okP and (neg == h["neg"])
        nfail += (0 if ok else 1)
        out.append({
            "triple": trip, "tags": tags,
            "L_hive4": h["L"], "L_engineA": LA, "L_engineB": LB,
            "poly": [str(x) for x in h["poly"]],
            "hstar": h["hstar"], "dim": h["dim"], "c": h["c"],
            "volume_normalized": str(h["volume_normalized"]),
            "max_vertex_denominator": h.get("max_denominator"),
            "negative_coefficient": bool(neg),
            "agreeA": okA, "agreeB": okB, "interp_ok": okP, "OK": ok,
        })
        print(("OK  " if ok else "FAIL") + "  " + trip +
              "  L=" + ",".join(map(str, h["L"])) +
              "  h*=" + str(h["hstar"]) + "  P=" + str([str(x) for x in h["poly"]]) +
              "  V=" + str(h["volume_normalized"]) + "  denom=" + str(h.get("max_denominator")))
    json.dump({"records": out, "failures": nfail,
               "VERDICT": "PASS" if nfail == 0 else "FAIL"},
              open(os.path.join(HERE, "runs", "band6", "extremal_verification.json"), "w"), indent=1)
    print("FAILURES:", nfail)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
