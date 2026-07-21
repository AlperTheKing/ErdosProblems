#!/usr/bin/env python3
"""fam2_analyze.py -- aggregate the FAMILY F2 records into the ladder report."""
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "runs", "fam2")


def main():
    recs = []
    for p in sorted(glob.glob(os.path.join(RUN, "tier2_*.jsonl"))):
        for ln in open(p):
            ln = ln.strip()
            if not ln:
                continue
            try:
                recs.append(json.loads(ln))
            except json.JSONDecodeError:
                pass   # truncated tail of a still-running writer
    ok = [r for r in recs if r.get("status") == "OK"]
    print("records %d  OK %d" % (len(recs), len(ok)))
    from collections import Counter
    print(Counter(r.get("status") for r in recs))

    negs = [r for r in ok if r.get("neg")]
    print("NEG records: %d" % len(negs))
    for r in negs[:20]:
        print("  " + json.dumps(r)[:400])

    bad = [r for r in ok if not r.get("hstar_nonneg")]
    print("h* NOT nonneg (anomaly): %d" % len(bad))

    def key(r):
        return (r.get("hstar_sum") or -1)

    best = max(ok, key=key)
    print("\nMAX V overall: V=%s  lam=%s mu=%s nu=%s d=%s h*=%s h1=%s"
          % (best.get("hstar_sum"), best["lam"], best["mu"], best["nu"],
             best.get("d"), best.get("hstar"), best.get("hstar_1")))

    for lim in (0, 1, 2):
        sub = [r for r in ok if r.get("hstar_1") == 0] if lim == 0 else \
              [r for r in ok if isinstance(r.get("hstar_1"), int)
               and r["hstar_1"] <= lim]
        if not sub:
            print("h*_1 <= %d : none" % lim)
            continue
        b = max(sub, key=key)
        print("h*_1 %s %d : max V=%s  lam=%s mu=%s nu=%s d=%s h*=%s"
              % ("==" if lim == 0 else "<=", lim, b.get("hstar_sum"),
                 b["lam"], b["mu"], b["nu"], b.get("d"), b.get("hstar")))

    # minimum monomial coefficient over everything
    mn = None
    mnr = None
    for r in ok:
        for c in r.get("coeffs_low_to_high", []):
            f = Fraction(c)
            if mn is None or f < mn:
                mn = f
                mnr = r
    print("\nMIN monomial coefficient over all OK records: %s   (%s %s %s)"
          % (mn, mnr["lam"], mnr["mu"], mnr["nu"]) if mn is not None else "n/a")

    # negativity-distance diagnostics (the exact criteria)
    worst_u = (-10 ** 9, None)
    best_u2 = (10 ** 9, None)
    for r in ok:
        h = r.get("hstar")
        d = r.get("d")
        if not h or d is None or d < 2:
            continue
        V = sum(h)
        if V == 0:
            continue
        mu1 = Fraction(sum(hj * (2 * j - (d + 1)) for j, hj in enumerate(h)), V)
        mu2 = Fraction(sum(hj * (2 * j - (d + 1)) ** 2
                           for j, hj in enumerate(h)), V)
        if mu1 > worst_u[0]:
            worst_u = (mu1, r)
        ratio = mu2 / Fraction(d + 1, 3)
        if ratio < best_u2[0]:
            best_u2 = (ratio, r)
    print("\nmax <u> (need > 0 for [n^{d-1}] < 0): %s   %s %s %s d=%s h*=%s"
          % (worst_u[0], worst_u[1]["lam"], worst_u[1]["mu"], worst_u[1]["nu"],
             worst_u[1]["d"], worst_u[1]["hstar"]))
    print("min <u^2>/((d+1)/3) (need < 1 for [n^{d-2}] < 0): %s   %s %s %s "
          "d=%s h*=%s"
          % (best_u2[0], best_u2[1]["lam"], best_u2[1]["mu"],
             best_u2[1]["nu"], best_u2[1]["d"], best_u2[1]["hstar"]))

    # h* support height
    hs = [(len([j for j, x in enumerate(r["hstar"]) if x], ) and
           max(j for j, x in enumerate(r["hstar"]) if x), r)
          for r in ok if r.get("hstar")]
    top = max(hs, key=lambda t: (t[0] - (t[1]["d"] or 0)))
    print("max (deg h* - d): %d   %s %s %s h*=%s d=%s"
          % (top[0] - top[1]["d"], top[1]["lam"], top[1]["mu"], top[1]["nu"],
             top[1]["hstar"], top[1]["d"]))
    return ok


if __name__ == "__main__":
    main()
