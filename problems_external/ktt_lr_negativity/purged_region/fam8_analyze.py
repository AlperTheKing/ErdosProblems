#!/usr/bin/env python3
"""fam8_analyze.py -- roll up the FAMILY-8 d=4 census."""
import glob
import json
import sys
from collections import Counter
from fractions import Fraction

files = sys.argv[1:] or glob.glob("runs/fam8/*.jsonl")

tot = 0
prof = 0
d4 = 0
unres = 0
shapes = Counter()
degs = Counter()
bestV = (0, None)
bestV1z = (0, None)
bestV1le2 = (0, None)
best_h2_at_h1z = (0, None)
best_h3 = (0, None)
maxs = (0, None)          # largest deg h* at d=4
mincoef = (Fraction(10 ** 9), None)
mincoef_all = (Fraction(10 ** 9), None, None)
neg = []
# margin for the cheapest d=4 negativity route: 12*[n^3] = 5+3h1+h2-h3-3h4
best_m3 = (10 ** 9, None)
best_m1 = (10 ** 9, None)   # 12*[n^1] = 25+3h1-h2+h3-3h4
best_m2 = (10 ** 9, None)   # 24*[n^2] = 35+11h1-h2-h3+11h4

for fn in files:
    for line in open(fn, encoding="utf-8"):
        tot += 1
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("status") != "OK":
            unres += 1
            continue
        prof += 1
        d = r.get("d")
        degs[d] += 1
        h = r.get("hstar")
        t = (r["lam"], r["mu"], r["nu"])
        cs = [Fraction(x) for x in r["coeffs_low_to_high"]]
        mc = min(cs)
        if mc < mincoef_all[0]:
            mincoef_all = (mc, t, d)
        if r.get("neg"):
            neg.append(r)
        if d != 4:
            continue
        d4 += 1
        V = sum(h)
        shapes[tuple(h)] += 1
        s = max(i for i, x in enumerate(h) if x) if V > 1 else 0
        if s > maxs[0]:
            maxs = (s, (t, h))
        if V > bestV[0]:
            bestV = (V, (t, h))
        if h[1] == 0 and V > bestV1z[0]:
            bestV1z = (V, (t, h))
        if h[1] <= 2 and V > bestV1le2[0]:
            bestV1le2 = (V, (t, h))
        if h[1] == 0 and h[2] > best_h2_at_h1z[0]:
            best_h2_at_h1z = (h[2], (t, h))
        if h[3] > best_h3[0]:
            best_h3 = (h[3], (t, h))
        if mc < mincoef[0]:
            mincoef = (mc, (t, h))
        m3 = 5 + 3 * h[1] + h[2] - h[3] - 3 * h[4]
        m1 = 25 + 3 * h[1] - h[2] + h[3] - 3 * h[4]
        m2 = 35 + 11 * h[1] - h[2] - h[3] + 11 * h[4]
        if m3 < best_m3[0]:
            best_m3 = (m3, (t, h))
        if m1 < best_m1[0]:
            best_m1 = (m1, (t, h))
        if m2 < best_m2[0]:
            best_m2 = (m2, (t, h))

print("records=%d  profiled_OK=%d  unresolved=%d  d=4: %d" % (tot, prof, unres, d4))
print("degree histogram:", dict(sorted(degs.items(), key=lambda kv: (kv[0] is None, kv[0]))))
print("bestV(d=4)      :", bestV)
print("bestV h*_1=0    :", bestV1z)
print("bestV h*_1<=2   :", bestV1le2)
print("max h*_2 @h1=0  :", best_h2_at_h1z)
print("max h*_3 (d=4)  :", best_h3)
print("max deg h* (d=4):", maxs)
print("min coeff d=4   :", mincoef)
print("min coeff ALL d :", mincoef_all)
print("margin 12*[n^3] :", best_m3, " (need < 0)")
print("margin 12*[n^1] :", best_m1, " (need < 0)")
print("margin 24*[n^2] :", best_m2, " (need < 0)")
print("NEG hits        :", len(neg))
for r in neg[:5]:
    print("  ", json.dumps(r))
print("top d=4 h* shapes:")
for s, c in shapes.most_common(25):
    print("   ", s, "V=%d" % sum(s), c)
