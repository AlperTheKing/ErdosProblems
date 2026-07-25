#!/usr/bin/env python3
"""
gen_fam11.py -- family 11: LARGE-WEIGHT probe.

Generates batch files (lines "lam;mu;nu") for the tier-0 screen.
Every arm is a WEIGHT LADDER: a shape is held fixed (structurally) and the
weight |nu| is pushed up, so that the campaign statistic

    margin(t) := h*_1 - h*_d      (= B - (d+1), B = #boundary lattice pts)

can be read as a function of the weight.  margin < 0 is a JACKPOT.

Arms
  A  dilation ladder            (lam,mu,nu) -> k*(lam,mu,nu)          k=1..K
  B  top-row inflation          mu_1 += t, nu_1 += t                  t=0..T
  C  column invariance control  lam += (t^r), nu += (t^r)   (P must be IDENTICAL)
  D  staircase stretch          near-staircase nu with growing step
  E  random large-weight thin   sampled, |nu| in bands, r in {5,6,7}
  F  plateau-engineered         repeated parts / big gaps => implicit equalities
"""
import sys, os, random, json

def fmt(p):
    return ",".join(str(x) for x in p)

def valid(lam, mu, nu):
    r = len(nu)
    if len(lam) > r or len(mu) > r:
        return False
    for p in (lam, mu, nu):
        if any(x <= 0 for x in p):
            return False
        if any(p[i] < p[i + 1] for i in range(len(p) - 1)):
            return False
    if sum(lam) + sum(mu) != sum(nu):
        return False
    if lam[0] > nu[0] or mu[0] > nu[0]:
        return False
    return True

def emit(out, lam, mu, nu, tag, param):
    if not valid(lam, mu, nu):
        return 0
    out.append(("%s;%s;%s" % (fmt(lam), fmt(mu), fmt(nu)), tag, param))
    return 1

# ---------------- seeds -------------------------------------------------
# best known shapes: h*_1 = 0 (c = d+1) refuter, plus structural cousins.
SEEDS = [
    ("refuter",  [2, 2, 1], [4, 3, 2, 1], [5, 4, 3, 2, 1]),
    ("stair5",   [3, 2, 1], [4, 3, 2, 1], [5, 4, 3, 2, 1]),
    ("stair5b",  [2, 1],    [5, 4, 3, 2], [6, 4, 3, 2, 1]),
    ("stair6",   [3, 2, 1], [5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1]),
    ("stair6b",  [2, 2, 1], [6, 5, 4, 3, 1], [7, 6, 4, 3, 2, 1]),
    ("thin5",    [1, 1],    [4, 3, 2, 1],   [5, 3, 2, 1, 1]),
    ("thin6",    [1, 1, 1], [5, 4, 3, 2, 1], [6, 4, 3, 2, 1, 1]),
    ("stair7",   [3, 2, 1], [6, 5, 4, 3, 2, 1], [7, 6, 5, 4, 3, 2, 1]),
]

def arm_A(out, K=8):
    n = 0
    for name, lam, mu, nu in SEEDS:
        for k in range(1, K + 1):
            n += emit(out, [k * x for x in lam], [k * x for x in mu],
                      [k * x for x in nu], "A:dil:" + name, k)
    return n

def arm_B(out, T=60):
    n = 0
    for name, lam, mu, nu in SEEDS:
        for t in list(range(0, 21)) + list(range(25, T + 1, 5)) + [80, 120, 200, 400]:
            mu2 = [mu[0] + t] + mu[1:]
            nu2 = [nu[0] + t] + nu[1:]
            n += emit(out, lam, mu2, nu2, "B:toprow:" + name, t)
            # second axis: grow nu_1 and lam_1 together
            lam2 = [lam[0] + t] + lam[1:]
            nu3 = [nu[0] + t] + nu[1:]
            n += emit(out, lam2, mu, nu3, "B:toprowL:" + name, t)
    return n

def arm_C(out, T=40):
    """lam -> lam padded to r then +t everywhere, nu -> nu + t everywhere.
    skew shape nu/lam is translated, so P must be IDENTICAL: instrument audit
    at very large weight."""
    n = 0
    for name, lam, mu, nu in SEEDS:
        r = len(nu)
        for t in [0, 1, 2, 3, 5, 8, 13, 21, T, 100, 250]:
            lam2 = [x + t for x in (list(lam) + [0] * (r - len(lam)))]
            nu2 = [x + t for x in nu]
            lam2 = [x for x in lam2 if x > 0]
            n += emit(out, lam2, mu, nu2, "C:coladd:" + name, t)
    return n

def arm_D(out):
    """staircase stretch: nu with constant step s, lam/mu likewise."""
    n = 0
    for r in (5, 6, 7):
        for s in (1, 2, 3, 5, 8, 13, 21, 34, 55):
            for a in (1, 2, 3):
                nu = [s * (r - i) for i in range(r)]
                lam = [a * (len(nu) - 1 - i) for i in range(len(nu) - 1)]
                lam = [x for x in lam if x > 0]
                need = sum(nu) - sum(lam)
                if need <= 0:
                    continue
                # mu: greedy staircase with total = need, r parts, mu_1<=nu_1
                mu = []
                rem = need
                for i in range(r):
                    hi = min(nu[0], rem)
                    if mu:
                        hi = min(hi, mu[-1])
                    take = min(hi, (rem + (r - i) - 1) // (r - i) + (1 if i == 0 else 0))
                    take = min(take, hi)
                    if take <= 0:
                        break
                    mu.append(take)
                    rem -= take
                if rem != 0:
                    continue
                n += emit(out, lam, mu, nu, "D:stretch:r%d_a%d" % (r, a), s)
    return n

def rand_triple(rng, r, W):
    """random triple with |nu| ~ W, r parts."""
    for _ in range(200):
        cuts = sorted(rng.randint(1, W) for _ in range(r - 1))
        parts = []
        prev = 0
        for c in cuts + [W]:
            parts.append(c - prev)
            prev = c
        nu = sorted((p for p in parts if p > 0), reverse=True)
        if len(nu) != r:
            continue
        L = rng.randint(max(1, W // 4), W - max(1, W // 4))
        kl = rng.randint(2, r)
        cuts = sorted(rng.randint(1, L) for _ in range(kl - 1))
        lam = []
        prev = 0
        for c in cuts + [L]:
            lam.append(c - prev)
            prev = c
        lam = sorted((p for p in lam if p > 0), reverse=True)
        M = W - L
        km = rng.randint(2, r)
        cuts = sorted(rng.randint(1, M) for _ in range(km - 1))
        mu = []
        prev = 0
        for c in cuts + [M]:
            mu.append(c - prev)
            prev = c
        mu = sorted((p for p in mu if p > 0), reverse=True)
        if valid(lam, mu, nu):
            return lam, mu, nu
    return None

def arm_E(out, per=900, seed=110711):
    rng = random.Random(seed)
    n = 0
    for r in (5, 6, 7):
        for W in (40, 60, 90, 130, 190, 280, 400):
            for _ in range(per):
                t = rand_triple(rng, r, W)
                if t:
                    n += emit(out, t[0], t[1], t[2], "E:rand:r%d_W%d" % (r, W), W)
    return n

def arm_F(out):
    """plateau-engineered: repeated parts in lam/mu and long gaps in nu force
    implicit equalities (non-full-dimensional Q), the ONLY regime not closed
    by Theorem 1.  Weight ladder in g."""
    n = 0
    for r in (5, 6):
        for g in (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144):
            # nu with one huge part then a flat tail
            nu = [g + r] + [1] * (r - 1)
            # lam = flat block, mu = the rest
            for a in (1, 2, 3):
                lam = [a] * min(r, 3)
                need = sum(nu) - sum(lam)
                if need <= 0:
                    continue
                mu = [min(nu[0], need)]
                rem = need - mu[0]
                while rem > 0 and len(mu) < r:
                    take = min(mu[-1], rem)
                    mu.append(take)
                    rem -= take
                if rem != 0:
                    continue
                n += emit(out, lam, mu, nu, "F:spike:r%d_a%d" % (r, a), g)
            # equal-parts lam and mu (maximal plateau bait)
            for m in (2, 3, 4):
                lam = [g] * min(m, r)
                mu = [g] * min(m, r)
                nu2 = sorted([2 * g] * min(m, r) + [0] * 0, reverse=True)
                if len(nu2) < r:
                    nu2 = nu2 + []
                if sum(lam) + sum(mu) != sum(nu2):
                    continue
                n += emit(out, lam, mu, nu2, "F:equal:m%d" % m, g)
            # near-extreme: nu = sorted(lam ++ mu) minus one box moved down
            for m in (2, 3):
                lam = [g, g][:m]
                mu = [g + 1, g - 1][:m] if g > 1 else None
                if mu is None:
                    continue
                nu2 = sorted(lam + mu, reverse=True)
                if len(nu2) > r:
                    continue
                n += emit(out, lam, mu, nu2, "F:nearext:m%d" % m, g)
    return n

def main():
    outdir = os.path.dirname(os.path.abspath(__file__))
    out = []
    counts = {}
    counts["A"] = arm_A(out)
    counts["B"] = arm_B(out)
    counts["C"] = arm_C(out)
    counts["D"] = arm_D(out)
    counts["F"] = arm_F(out)
    counts["E"] = arm_E(out)
    # dedupe, keep first tag
    seen = {}
    for line, tag, param in out:
        if line not in seen:
            seen[line] = (tag, param)
    with open(os.path.join(outdir, "fam11.batch"), "w") as fh:
        for line in seen:
            fh.write(line + "\n")
    with open(os.path.join(outdir, "fam11.tags.json"), "w") as fh:
        json.dump({k: list(v) for k, v in seen.items()}, fh)
    print(json.dumps({"generated": len(out), "unique": len(seen),
                      "per_arm": counts}))

if __name__ == "__main__":
    main()
