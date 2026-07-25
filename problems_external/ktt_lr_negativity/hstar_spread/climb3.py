#!/usr/bin/env python3
"""Adversarial hill-climb at d=3: maximise  h*_2 / (h*_1 + h*_3).
KTT-SD (simplex domination) at d=3 says this ratio is <= 2.
KTT itself only needs  h*_2 <= 11 + 2(h*_1 + h*_3).
Any observation > 2 falsifies KTT-SD (but not KTT)."""
import json, os, random, subprocess, sys
from fractions import Fraction as F

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCREEN = os.path.join(BASE, "purged_region", "lpfree_screen.py")
HERE = os.path.dirname(os.path.abspath(__file__))


def screen(batch):
    bf = os.path.join(HERE, "_climb.batch")
    with open(bf, "w") as f:
        for lam, mu, nu in batch:
            f.write("%s;%s;%s\n" % (",".join(map(str, lam)), ",".join(map(str, mu)),
                                    ",".join(map(str, nu))))
    p = subprocess.run([sys.executable, SCREEN, "--batch", bf],
                       capture_output=True, text=True, cwd=os.path.dirname(SCREEN))
    out = []
    for l in p.stdout.splitlines():
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("status") != "OK" or not o.get("heldout_ok"):
            continue
        h = o["hstar"]
        if len(h) != 4:
            continue
        den = h[1] + h[3]
        if den == 0:
            continue
        out.append((F(h[2], den), (tuple(o["lam"]), tuple(o["mu"]), tuple(o["nu"])), h))
    return out


def perturb(t, rng, amp):
    lam, mu, nu = [list(x) for x in t]
    for v in (lam, mu, nu):
        for i in range(len(v)):
            if rng.random() < 0.5:
                v[i] += rng.randint(-amp, amp)
    nu = sorted([x for x in nu if x > 0], reverse=True)
    lam = sorted([x for x in lam if x > 0], reverse=True)
    mu = sorted([x for x in mu if x > 0], reverse=True)
    if not (lam and mu and nu):
        return None
    d = sum(nu) - sum(lam) - sum(mu)
    if d > 0:
        mu[0] += d
    elif d < 0:
        if mu[0] + d < (mu[1] if len(mu) > 1 else 1):
            return None
        mu[0] += d
    mu = sorted([x for x in mu if x > 0], reverse=True)
    if not mu or sum(lam) + sum(mu) != sum(nu):
        return None
    return (tuple(lam), tuple(mu), tuple(nu))


if __name__ == "__main__":
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    seeds = [((25, 17, 13, 1), (24, 20, 6), (40, 27, 22, 17)),
             ((13, 10, 7, 4, 1), (14, 10, 7, 4, 1), (23, 19, 15, 12, 2)),
             ((49, 41, 17), (80, 72, 51), (124, 113, 68, 5))]
    pool = list(seeds)
    best = F(0); bestt = None; besth = None
    for gen in range(int(sys.argv[2]) if len(sys.argv) > 2 else 25):
        cand = []
        for t in pool:
            for amp in (1, 2, 4, 8):
                for _ in range(12):
                    p = perturb(t, rng, amp)
                    if p:
                        cand.append(p)
        cand = list(dict.fromkeys(cand))[:600]
        res = screen(cand)
        res.sort(key=lambda x: -x[0])
        if res and res[0][0] > best:
            best, bestt, besth = res[0][0], res[0][1], res[0][2]
        pool = [r[1] for r in res[:6]] or pool
        print("gen %2d  cands=%3d  best ratio = %s = %.5f  h*=%s" %
              (gen, len(cand), best, float(best), besth), flush=True)
        if best > 2:
            print("!!! KTT-SD VIOLATED", bestt, besth)
            break
    print("FINAL best h*_2/(h*_1+h*_3) =", best, float(best), bestt, besth)
