#!/usr/bin/env python3
"""Adversarial stress test of the half-plane lemma at HIGH dimension.

Generates r=6 (D=10) and r=7 (D=15) hive triples in the shape of the
empirical extremals (balanced staircase-like lam=mu, small |nu|), screens
them with the validated lpfree_screen instrument, then applies the EXACT
Routh-Hurwitz test and records the dilation-invariant sector angle.
"""
import itertools, json, os, subprocess, sys, math, random
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crit import coeffs_from_hstar
from hurwitz import routh
import numpy as np

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCREEN = os.path.join(BASE, "purged_region", "lpfree_screen.py")


def parts(n, k, mx=None):
    """partitions of n into exactly k positive parts (weakly decreasing)"""
    if mx is None:
        mx = n
    if k == 0:
        if n == 0:
            yield ()
        return
    for first in range(min(n - k + 1, mx), 0, -1):
        for rest in parts(n - first, k - 1, first):
            yield (first,) + rest


def gen(r, maxN, seed=3, cap=900):
    random.seed(seed)
    out = []
    for N in range(r * (r + 1) // 2, maxN + 1):
        nus = [p for p in parts(N, r)]
        random.shuffle(nus)
        for nu in nus[:40]:
            # lam, mu with at most r-1 parts each summing to N
            for _ in range(14):
                a = random.randint(max(1, N // 3), 2 * N // 3)
                b = N - a
                if b < 1:
                    continue
                la = [p for p in parts(a, min(r - 1, a))]
                mm = [p for p in parts(b, min(r - 1, b))]
                if not la or not mm:
                    continue
                lam = random.choice(la); mu = random.choice(mm)
                out.append((lam, mu, nu))
                if len(out) >= cap:
                    return out
    return out


def run(triples, tag):
    bf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_stress_%s.batch" % tag)
    with open(bf, "w") as f:
        for lam, mu, nu in triples:
            f.write("%s;%s;%s\n" % (",".join(map(str, lam)), ",".join(map(str, mu)),
                                    ",".join(map(str, nu))))
    p = subprocess.run([sys.executable, SCREEN, "--batch", bf],
                       capture_output=True, text=True, cwd=os.path.dirname(SCREEN))
    return p.stdout.splitlines()


def analyse(lines, tag):
    ok = bad = skip = 0
    worst = (-9, None)
    fails = []
    for ln in lines:
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get("status") != "OK" or not o.get("heldout_ok"):
            skip += 1
            continue
        h = o["hstar"]
        if len(h) < 3:
            skip += 1
            continue
        a = coeffs_from_hstar(h)
        d = len(a) - 1
        v, _ = routh([a[d - i] for i in range(d + 1)])
        if v == "STRICT":
            ok += 1
        else:
            bad += 1
            fails.append((v, o["lam"], o["mu"], o["nu"], h,
                          [str(x) for x in a]))
        rts = np.roots([float(x) for x in reversed(a)])
        if len(rts):
            mc = max(z.real / abs(z) for z in rts)
            if mc > worst[0]:
                worst = (mc, (d, h, o["lam"], o["mu"], o["nu"]))
    print("[%s] screened=%d  HURWITZ=%d  NOT-HURWITZ=%d  unusable=%d" %
          (tag, ok + bad, ok, bad, skip))
    if worst[1]:
        print("   worst sector: cos=%+.4f half-angle=%.1f deg  d=%d h*=%s (%s|%s|%s)" %
              ((worst[0], math.degrees(math.acos(-worst[0]))) + worst[1]))
    for f in fails[:10]:
        print("   NOT HURWITZ:", f)
    return fails


if __name__ == "__main__":
    r = int(sys.argv[1]); maxN = int(sys.argv[2]); cap = int(sys.argv[3])
    tr = gen(r, maxN, cap=cap)
    print("generated %d triples r=%d" % (len(tr), r))
    lines = run(tr, "r%d" % r)
    analyse(lines, "r=%d" % r)
