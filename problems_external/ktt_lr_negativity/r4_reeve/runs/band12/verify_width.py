#!/usr/bin/env python3
"""Independent re-derivation of the band-12 'width lemma' from hive4.build_hive4.

For each of the six directions d in {e1,e2,e3,e2-e1,e3-e1,e3-e2} the 18-row
constraint matrix contains rows with normal +d and with normal -d.  The slab
width in direction d is  w(d) = min{rhs : normal = +d} + min{rhs : normal = -d}.
Q nonempty  ==>  w(d) >= 0 for every d;  dim Q = 3  ==>  w(d) > 0 for every d.

Claimed identities (to be checked, not assumed):
  w(e1)    = min(l1-l2, n1-n2)
  w(e2)    = min(m1-m2, l3-l4)
  w(e3)    = min(m3-m4, n3-n4)
  w(e2-e1) = l2-l3
  w(e3-e1) = n2-n3
  w(e3-e2) = m2-m3
"""
import itertools, random, sys
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve")
from hive4 import build_hive4, analyze

DIRS = {
    "e1": (1, 0, 0), "e2": (0, 1, 0), "e3": (0, 0, 1),
    "e2-e1": (-1, 1, 0), "e3-e1": (-1, 0, 1), "e3-e2": (0, -1, 1),
}

def widths(A, b):
    best = {}
    for row, rhs in zip(A, b):
        t = tuple(row)
        if t not in best or rhs < best[t]:
            best[t] = rhs
    out = {}
    for name, d in DIRS.items():
        nd = tuple(-x for x in d)
        if d not in best or nd not in best:
            out[name] = None
        else:
            out[name] = best[d] + best[nd]
    return out

def claimed(lam, mu, nu):
    l = list(lam) + [0] * 4; m = list(mu) + [0] * 4; n = list(nu) + [0] * 4
    return {
        "e1": min(l[0] - l[1], n[0] - n[1]),
        "e2": min(m[0] - m[1], l[2] - l[3]),
        "e3": min(m[2] - m[3], n[2] - n[3]),
        "e2-e1": l[1] - l[2],
        "e3-e1": n[1] - n[2],
        "e3-e2": m[1] - m[2],
    }

def parts(W, maxlen=4):
    """all partitions of W with at most maxlen parts"""
    def rec(rem, mx, k):
        if k == 0:
            if rem == 0:
                yield []
            return
        if rem == 0:
            yield []
            return
        for first in range(min(rem, mx), 0, -1):
            for tail in rec(rem - first, first, k - 1):
                yield [first] + tail
    return list(rec(W, W, maxlen))

def main():
    random.seed(12)
    mism = 0; tested = 0
    # exhaustive small weights
    trips = []
    for W in range(1, 15):
        P = parts(W)
        for a in range(1, W):
            for lam in parts(a):
                for mu in parts(W - a):
                    for nu in P:
                        trips.append((lam, mu, nu))
    # plus random big ones
    for _ in range(4000):
        W = random.randint(15, 400)
        a = random.randint(1, W - 1)
        lam = random.choice(parts(a)) if a <= 24 else sorted(
            [random.randint(0, a) for _ in range(4)], reverse=True)
        if a > 24:
            s = sum(lam)
            if s == 0: continue
        mu = None
        b = W - a
        mu = random.choice(parts(b)) if b <= 24 else sorted(
            [random.randint(0, b) for _ in range(4)], reverse=True)
        nu = random.choice(parts(W)) if W <= 24 else sorted(
            [random.randint(0, W) for _ in range(4)], reverse=True)
        if sum(lam) + sum(mu) != sum(nu):
            continue
        trips.append((lam, mu, nu))

    dim3_nonstrict = []
    dim3_count = 0
    for lam, mu, nu in trips:
        H = build_hive4(lam, mu, nu)
        if not H["A"]:
            continue
        tested += 1
        w = widths(H["A"], H["b"])
        c = claimed(H["lam"], H["mu"], H["nu"])
        if w != c:
            mism += 1
            if mism <= 5:
                print("MISMATCH", lam, mu, nu, w, c)
    print("width identity: tested=%d mismatches=%d" % (tested, mism))

    # dim3 => strict, on the exhaustive W<=14 part, via the real engine
    n3 = 0; bad = 0; seen = set()
    for lam, mu, nu in trips[:200000]:
        key = (tuple(lam), tuple(mu), tuple(nu))
        if key in seen: continue
        seen.add(key)
        r = analyze(lam, mu, nu)
        if r["dim"] == 3:
            n3 += 1
            for p in (r["lam"], r["mu"], r["nu"]):
                q = list(p) + [0] * 4
                if not (q[0] > q[1] > q[2] > q[3] >= 0):
                    bad += 1
                    print("DIM3 NON-STRICT", lam, mu, nu)
                    break
    print("engine dim3 check: dim3=%d nonstrict=%d (over %d distinct triples)" % (n3, bad, len(seen)))

main()
