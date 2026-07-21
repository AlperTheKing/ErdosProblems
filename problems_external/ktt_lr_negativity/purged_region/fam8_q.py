#!/usr/bin/env python3
"""fam8_q.py -- fast roll-up of the FAMILY-8 d=4 census keyed on the exact
negativity margins (h*-only; no Fraction parsing).

At d = 4 the exact monomial coefficients are
  12*[n^1] = 25 + 3h1 -  h2 +  h3 - 3h4
  24*[n^2] = 35 + 11h1 - h2 -  h3 + 11h4
  12*[n^3] =  5 + 3h1 +  h2 -  h3 - 3h4
so negativity <=> one of the margins m1, m2, m3 is < 0.
"""
import json
import sys
from collections import defaultdict

files = sys.argv[1:]
bestQ = []      # (m, triple, h, |nu|)
per_n_m1 = defaultdict(lambda: 10 ** 9)
per_n_V = defaultdict(int)
bestV = (0, None)
bestV1z = (0, None)
bestV1le2 = (0, None)
best_m1 = (10 ** 9, None)
best_m2 = (10 ** 9, None)
best_m3 = (10 ** 9, None)
best_ratio = (0.0, None)
d4 = 0
tot = 0
neg = 0
top1 = []

for fn in files:
    for line in open(fn, encoding="utf-8"):
        tot += 1
        r = json.loads(line)
        if r.get("status") != "OK" or r.get("d") != 4:
            if r.get("neg"):
                neg += 1
                print("NEG(non-d4)", line.strip()[:400])
            continue
        d4 += 1
        h = r["hstar"]
        t = (r["lam"], r["mu"], r["nu"])
        N = sum(r["nu"])
        V = sum(h)
        m1 = 25 + 3 * h[1] - h[2] + h[3] - 3 * h[4]
        m2 = 35 + 11 * h[1] - h[2] - h[3] + 11 * h[4]
        m3 = 5 + 3 * h[1] + h[2] - h[3] - 3 * h[4]
        if min(m1, m2, m3) < 0:
            neg += 1
            print("NEG", json.dumps(r))
        per_n_m1[N] = min(per_n_m1[N], m1)
        per_n_V[N] = max(per_n_V[N], V)
        if V > bestV[0]:
            bestV = (V, (t, h))
        if h[1] == 0 and V > bestV1z[0]:
            bestV1z = (V, (t, h))
        if h[1] <= 2 and V > bestV1le2[0]:
            bestV1le2 = (V, (t, h))
        if m1 < best_m1[0]:
            best_m1 = (m1, (t, h))
        if m2 < best_m2[0]:
            best_m2 = (m2, (t, h))
        if m3 < best_m3[0]:
            best_m3 = (m3, (t, h))
        if h[1] > 0:
            rr = h[2] / h[1]
            if rr > best_ratio[0]:
                best_ratio = (rr, (t, h))
        top1.append((m1, t, h))

top1.sort(key=lambda x: x[0])
print("scanned=%d  d4=%d  NEG=%d" % (tot, d4, neg))
print("bestV(d=4)   :", bestV)
print("bestV h1=0   :", bestV1z)
print("bestV h1<=2  :", bestV1le2)
print("min m1 (<0?) :", best_m1)
print("min m2 (<0?) :", best_m2)
print("min m3 (<0?) :", best_m3)
print("max h2/h1    :", best_ratio)
print("m1 / maxV by |nu|:")
for N in sorted(per_n_m1):
    print("   |nu|=%2d  min_m1=%3d  maxV=%3d" % (N, per_n_m1[N], per_n_V[N]))
print("top 15 by m1:")
seen = set()
k = 0
for m, t, h in top1:
    key = tuple(h)
    if key in seen:
        continue
    seen.add(key)
    print("   m1=%3d h*=%s V=%d  %s" % (m, h, sum(h), t))
    k += 1
    if k >= 15:
        break
