#!/usr/bin/env python3
"""End-to-end cross-check of the r=4 edge-local certificate against polytopes
it has never seen.

Loads mu from q2_basis_witness_certificate.json, then generates lattice
3-polytopes {x : n_i.x <= b_i} with random integral b over the certificate's
own 15 normals, using the INDEPENDENT sampler in fixed_normal_linearity.py
(own vertex enumeration, own facet/edge extraction, own brute-force lattice
counting, own exact interpolation), and checks

        Lambda(P) . mu  ==  a_1(P)          exactly, for every sample.

A single mismatch refutes the certificate.
"""
import json
import os
import random
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(os.path.dirname(HERE), "q2_basis_witness_certificate.json")

cert = json.load(open(CERT))
src = open(os.path.join(HERE, "fixed_normal_linearity.py")).read()
src = re.sub(r"NORMALS = \[.*?\]\n",
             "NORMALS = " + repr([tuple(v) for v in cert["normals"]]) + "\n",
             src, count=1, flags=re.S)
src = src.replace("PAIRS = [(i,j) for i in range(15) for j in range(i+1,15)]",
                  "PAIRS = [tuple(p) for p in " + repr(cert["nonparallel_pairs"]) + "]")
src = src.split("random.seed(4242)")[0]
g = {}
exec(src, g)

mu = [F(x) for x in cert["mu"]]
assert len(mu) == 99
print("min mu =", min(mu), " all mu >= 0:", all(x >= 0 for x in mu))

n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 200
random.seed(999)
n = bad = 0
mins = None
while n < n_target:
    b = [random.randint(0, 5) for _ in range(15)]
    r = g["sample"](b)
    if r is None:
        continue
    n += 1
    Lam, a1 = r
    pred = sum(F(Lam[k]) * mu[k] for k in range(99))
    if pred != a1:
        bad += 1
        print("MISMATCH b=", b, "pred", pred, "true", a1)
    if mins is None or a1 < mins:
        mins = a1
print("polytopes tested:", n, " mu-prediction mismatches:", bad)
print("min a_1 =", mins, " 6*a_1 =", 6 * mins)
print("PASS" if bad == 0 else "FAIL")
