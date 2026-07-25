#!/usr/bin/env python3
"""
Do REAL r=4 hive polytopes actually use the three NON-ALCOVED normals as
genuine facets, and is the sub-configuration of their actual facet normals
non-unimodular?  (If every real hive used only alcoved normals, the F4 hint
would survive.)
"""
import sys, itertools, random
from fractions import Fraction
from collections import Counter
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems_external\ktt_lr_negativity\r4_reeve")
sys.path.insert(0, ".")
import hive4
from unimodularity import det

ODD = {(1,-1,-1), (-1,1,-1), (-1,-1,1)}

def primitive(v):
    from math import gcd
    g = 0
    for x in v: g = gcd(g, abs(x))
    return tuple(x//g for x in v) if g else v

random.seed(11)
stats = Counter()
examples = {}
tot = 0
for trial in range(4000):
    L = 14
    lam = sorted((random.randint(0,L) for _ in range(4)), reverse=True)
    mu  = sorted((random.randint(0,L) for _ in range(4)), reverse=True)
    s = sum(lam)+sum(mu)
    nu  = sorted((random.randint(0,2*L) for _ in range(4)), reverse=True)
    d = s - sum(nu)
    nu[0] += d
    if nu[0] < nu[1]: continue
    H = hive4.build_hive4(lam, mu, nu)
    if not H["ok"]: continue
    V = hive4.vertices(H["A"], H["b"])
    if len(V) < 4 or hive4._affine_rank(V) < 3: continue
    tot += 1
    F = hive4.facets(H["A"], H["b"], V)
    normals = sorted({primitive(tuple(row)) for row, S in F})
    nodd = sum(1 for n in normals if n in ODD)
    stats["hives"] += 1
    if nodd: stats["with_odd_facet"] += 1
    # unimodularity of the ACTUAL facet-normal configuration of this hive
    mins = {abs(det([normals[i] for i in S])) for S in itertools.combinations(range(len(normals)),3)}
    mins.discard(0)
    if len(mins) > 1:
        stats["nonunimodular_actual"] += 1
        if "nonunimod" not in examples:
            examples["nonunimod"] = (lam, mu, nu, normals, sorted(mins))
    if nodd and "odd" not in examples:
        examples["odd"] = (lam, mu, nu, normals)

print("full-dim r=4 hives sampled:", tot)
print(dict(stats))
for k, v in examples.items():
    print("\nEXAMPLE", k)
    print("  lam,mu,nu =", v[0], v[1], v[2])
    print("  actual facet normals:", v[3])
    if len(v) > 4: print("  |3x3 minors| =", v[4])
