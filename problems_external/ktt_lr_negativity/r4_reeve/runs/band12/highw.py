#!/usr/bin/env python3
"""Independent high-weight spot check: random band-12 triples with W >= 61.
lam, mu are random partitions with <=4 parts; nu is a random partition of
W = |lam|+|mu| with <=4 parts, accepted only if it contains both lam and mu.
Confirms dim Q <= 2 (as predicted by the width lemma) and no negative coefficient.
"""
import sys, random
from multiprocessing import Pool
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve")
from hive4 import analyze, trim

def deg(p):
    q = [x for x in p if x > 0]
    if not q: return True
    for i in range(len(q) - 1):
        if q[i] == q[i + 1]: return True
    return all(x == 1 for x in q[1:])

def rand_part(rng, maxpart):
    return tuple(sorted([rng.randint(0, maxpart) for _ in range(4)], reverse=True))

def rand_part_of(rng, W):
    """random partition of W with at most 4 parts (composition then sort)"""
    cuts = sorted(rng.randint(0, W) for _ in range(3))
    comp = [cuts[0], cuts[1] - cuts[0], cuts[2] - cuts[1], W - cuts[2]]
    return tuple(sorted(comp, reverse=True))

def job(seed):
    rng = random.Random(seed)
    dh = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
    negs = []; n = 0; vfail = 0; tries = 0
    while n < 500 and tries < 400000:
        tries += 1
        mx = rng.choice([20, 40, 80, 150])
        lam = rand_part(rng, mx)
        mu = rand_part(rng, mx)
        W = sum(lam) + sum(mu)
        if W < 61 or W > 900: continue
        if not (deg(lam) or deg(mu)):
            # keep band-12 core heavy but also allow deg(nu) only
            if rng.random() < 0.5: continue
        nu = rand_part_of(rng, W)
        if any(lam[i] > nu[i] for i in range(4)): continue
        if any(mu[i] > nu[i] for i in range(4)): continue
        if not (deg(lam) or deg(mu) or deg(nu)): continue
        res = analyze(list(lam), list(mu), list(nu))
        n += 1
        dh[res["dim"]] += 1
        if not res.get("verified", True): vfail += 1
        P = trim(res["poly"])
        if min(P) < 0: negs.append((lam, mu, nu, [str(x) for x in P]))
    return dh, negs, n, vfail, tries

if __name__ == "__main__":
    with Pool(40) as p:
        rs = p.map(job, range(40))
    DH = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}; N = 0; NEG = []; VF = 0; T = 0
    for dh, negs, n, vf, tr in rs:
        for k in DH: DH[k] += dh[k]
        N += n; NEG += negs; VF += vf; T += tr
    print("high-W band-12 sample: n=%d (from %d draws) dim hist %s negatives %d verify_failures %d"
          % (N, T, DH, len(NEG), VF))
    for x in NEG[:10]: print("NEG", x)
