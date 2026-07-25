#!/usr/bin/env python
"""fam5 generator: SHORT-vs-LONG shapes.

lam has 2 or 3 nonzero parts; mu and nu have 5..7 parts; all weights <= WMAX.
nu is produced from sorted(lam)+mu componentwise (a partition, |nu| correct)
by random DOWNWARD unit moves (row i -> row j>i), which preserves |nu| and
keeps nu dominated by lam+mu (a necessary condition for c != 0).
We additionally enforce nu_i >= max(lam_i, mu_i) (necessary: lam,mu subset nu).
"""
import random, sys, json, argparse


def rand_partition(nparts, wmax, rng, strict=False, minpart=1):
    vals = sorted((rng.randint(minpart, wmax) for _ in range(nparts)), reverse=True)
    if strict:
        # make strictly decreasing where possible
        for i in range(1, nparts):
            if vals[i] >= vals[i - 1]:
                vals[i] = max(minpart, vals[i - 1] - 1)
        vals = sorted(vals, reverse=True)
    return vals


def gen(rng, r, lam_parts, wmax, nmoves_max):
    lam = rand_partition(lam_parts, wmax, rng)
    mu = rand_partition(r, wmax, rng, minpart=0)
    if mu[0] == 0:
        return None
    lam_pad = lam + [0] * (r - len(lam))
    nu = [lam_pad[i] + mu[i] for i in range(r)]
    lo = [max(lam_pad[i], mu[i]) for i in range(r)]
    k = rng.randint(0, nmoves_max)
    for _ in range(k):
        cands = []
        for i in range(r):
            for j in range(i + 1, r):
                nu2 = list(nu)
                nu2[i] -= 1
                nu2[j] += 1
                if nu2[i] < lo[i] or nu2[j] < lo[j]:
                    continue
                if any(nu2[t] < nu2[t + 1] for t in range(r - 1)):
                    continue
                if nu2[i] < 0 or nu2[r - 1] < 0:
                    continue
                cands.append(nu2)
        if not cands:
            break
        nu = rng.choice(cands)
    if sum(nu) != sum(lam) + sum(mu):
        return None
    if any(nu[t] < nu[t + 1] for t in range(r - 1)):
        return None
    return lam, [x for x in mu if x > 0], nu


def fmt(p):
    return ",".join(str(x) for x in p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--wmax", type=int, default=20)
    ap.add_argument("--numax", type=int, default=80)
    ap.add_argument("--rs", default="5,6,7")
    ap.add_argument("--lamparts", default="2,3")
    ap.add_argument("--moves", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rs = [int(x) for x in a.rs.split(",")]
    lps = [int(x) for x in a.lamparts.split(",")]
    seen = set()
    out = []
    tries = 0
    while len(out) < a.n and tries < a.n * 200:
        tries += 1
        r = rng.choice(rs)
        lp = rng.choice(lps)
        g = gen(rng, r, lp, a.wmax, a.moves)
        if g is None:
            continue
        lam, mu, nu = g
        while nu and nu[-1] == 0:
            nu.pop()
        if sum(nu) > a.numax:
            continue
        if not (5 <= len(nu) <= 7):
            continue
        if len(mu) < 4:
            continue
        key = (tuple(lam), tuple(mu), tuple(nu))
        if key in seen:
            continue
        seen.add(key)
        out.append("%s;%s;%s" % (fmt(lam), fmt(mu), fmt(nu)))
    with open(a.out, "w") as f:
        f.write("\n".join(out) + "\n")
    sys.stderr.write("wrote %d (tries %d)\n" % (len(out), tries))


if __name__ == "__main__":
    main()
