#!/usr/bin/env python3
"""fam11_analyze.py -- aggregate every fam11 screen record (exact arithmetic)."""
import collections
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "runs", "fam11")


def tstr(t):
    return "%s | %s | %s" % tuple(",".join(map(str, p)) for p in t)


def load(paths):
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def main(argv):
    paths = argv[1:] or sorted(glob.glob(os.path.join(RUN, "*.jsonl")))
    paths = [p for p in paths if "smoke" not in os.path.basename(p)]
    n = ok = unres = 0
    best0 = (0, None)        # max V with h*_1 = 0
    best2 = (0, None)        # max V with h*_1 <= 2
    bestV = (0, None)        # max V overall
    minc = (Fraction(10 ** 9), None)
    negs = []
    MOM = [(Fraction(-10**9), None), (Fraction(10**9), None)]
    MINNL = [(Fraction(10**9), None)]
    PERD = {}
    dist0 = collections.Counter()
    distd = collections.Counter()
    ratio = collections.defaultdict(lambda: [0, 0])   # rho bin -> [n, nladder]
    for r in load(paths):
        n += 1
        if r.get("status") != "OK":
            unres += 1
            continue
        ok += 1
        h = r["hstar"]
        V = r["hstar_sum"]
        d = r["d"]
        trip = (r["lam"], r["mu"], r["nu"])
        distd[(r["r"], d)] += 1
        if h[1] == 0:
            dist0[(d, V)] += 1
            if V > best0[0]:
                best0 = (V, {"triple": tstr(trip), "hstar": h, "c": r["c"], "d": d, "coeffs": r["coeffs_low_to_high"]})
        if h[1] <= 2 and V > best2[0]:
            best2 = (V, {"triple": tstr(trip), "hstar": h, "c": r["c"], "d": d})
        if V > bestV[0]:
            bestV = (V, {"triple": tstr(trip), "hstar": h, "c": r["c"], "d": d})
        cl = r["coeffs_low_to_high"]
        for k, cs in enumerate(cl):
            cv = Fraction(cs)
            if k < len(cl) - 1 and cv < MINNL[0][0]:
                MINNL[0] = (cv, {"triple": tstr(trip), "hstar": h, "d": d,
                                 "k": k, "coeffs": cl})
            if cv < minc[0]:
                minc = (cv, {"triple": tstr(trip), "hstar": h, "d": d, "coeffs": r["coeffs_low_to_high"]})
        # exact "distance to negativity" diagnostics (THEORY1 moment form):
        #   [n^{d-1}] < 0  <=>  <u> > 0 ,  u_j = 2j-(d+1)
        #   [n^{d-2}] < 0  <=>  <u^2> < (d+1)/3
        if d >= 2:
            Vf = Fraction(V)
            m1 = Fraction(sum(h[j] * (2 * j - (d + 1)) for j in range(d + 1)), V)
            m2 = Fraction(sum(h[j] * (2 * j - (d + 1)) ** 2 for j in range(d + 1)), V)
            if m1 > MOM[0][0]:
                MOM[0] = (m1, {"triple": tstr(trip), "hstar": h, "d": d})
            gap = m2 - Fraction(d + 1, 3)
            cell = PERD.setdefault(d, [Fraction(-10**9), Fraction(10**9), 0])
            if m1 > cell[0]:
                cell[0] = m1
            if gap < cell[1]:
                cell[1] = gap
            cell[2] += 1
            if gap < MOM[1][0]:
                MOM[1] = (gap, {"triple": tstr(trip), "hstar": h, "d": d})
        if r.get("neg"):
            negs.append(r)
        a = sum(r["lam"])
        b = sum(r["mu"])
        rho = Fraction(min(a, b), max(a, b))
        key = round(float(rho), 1)
        ratio[key][0] += 1
        if h[1] == 0 and V >= 2:
            ratio[key][1] += 1

    out = {
        "files": [os.path.basename(p) for p in paths],
        "records": n, "ok": ok, "unresolved": unres,
        "best_V_hstar1_zero": {"V": best0[0], "witness": best0[1]},
        "best_V_hstar1_le2": {"V": best2[0], "witness": best2[1]},
        "best_V_any": {"V": bestV[0], "witness": bestV[1]},
        "min_coefficient": {"value": str(minc[0]), "witness": minc[1]},
        "min_nonleading_coefficient": {"value": str(MINNL[0][0]),
                                       "witness": MINNL[0][1]},
        "per_d_max_mean_u__min_2ndmoment_gap__count":
            {str(k): [str(v[0]), str(v[1]), v[2]] for k, v in sorted(PERD.items())},
        "negatives": len(negs),
        "max_mean_u_(neg_iff_>0)": {"value": str(MOM[0][0]), "witness": MOM[0][1]},
        "min_secondmoment_gap_(neg_iff_<0)": {"value": str(MOM[1][0]),
                                              "witness": MOM[1][1]},
        "hstar1_zero_by_(d,V)": {str(k): v for k, v in sorted(dist0.items())},
        "by_(r,d)": {str(k): v for k, v in sorted(distd.items())},
        "ratio_bins_min|max_weight": {str(k): v for k, v in sorted(ratio.items())},
    }
    print(json.dumps(out, indent=1))
    if negs:
        with open(os.path.join(RUN, "NEGATIVES.jsonl"), "w", encoding="utf-8") as f:
            for r in negs:
                f.write(json.dumps(r) + "\n")
        print("WROTE %d NEGATIVES" % len(negs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
