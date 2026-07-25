"""P1.md section 9 claims that the candidate

    (Q)  mu NOT pentagonal  ==>  Atilde := A_{sigma=mu} <= 1/25

is refuted by a q=26 witness with Atilde = 0.0814.  That witness is NOT non-pentagonal: it is
pentagonal with two EMPTY blocks (verified in the audit), which P1_pentagon.py cannot see
because it enumerates only 5 DISTINCT cut points.  So (Q) is untested.

Since P1.md's own (P)+(Q) split would CLOSE the arc-cut conjecture, (Q) is re-searched here
with the corrected pentagonality test: hill-climb Atilde over genuinely non-pentagonal
supports, exact acceptance.
"""
import functools, random
from fractions import Fraction as F
from itertools import combinations
print = functools.partial(print, flush=True)
from audit_P1_engine import M, TARGET

rng = random.Random(2026)


def A_mu_exact(mu):
    n = mu.n
    s = [(mu.x[i] + mu.x[(i + 1) % n]) / 2 for i in range(n)]
    tot = F(0)
    for (i, j) in mu.E:
        Dp = sum(s[t] for t in range(i, j))
        D = min(Dp, 1 - Dp)
        tot += mu.x[i] * mu.x[j] * (1 - 2 * D)
    return tot


def A_mu_float(x, E, n):
    s = [(x[i] + x[(i + 1) % n]) / 2 for i in range(n)]
    pre = [0.0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + s[i]
    tot = 0.0
    for (i, j) in E:
        Dp = pre[j] - pre[i]
        D = min(Dp, 1 - Dp)
        tot += x[i] * x[j] * (1 - 2 * D)
    return tot


best = (0.0, None)
tested = 0
for q in (8, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 24, 26):
    for size in range(5, min(q, 11) + 1):
        for _ in range(30):
            S = sorted(rng.sample(range(q), size))
            mu0 = M(q, [(k, 1) for k in S])
            if not mu0.E or mu0.pentagon() is not None:
                continue                       # corrected test: skip pentagonal supports
            tested += 1
            n = mu0.n
            E = mu0.E
            x = [rng.random() + 0.4 for _ in range(n)]
            t = sum(x)
            x = [v / t for v in x]
            cur = A_mu_float(x, E, n)
            step = 0.08
            for it in range(1500):
                i, j = rng.sample(range(n), 2)
                d = step * rng.random() * min(x[i], 0.5)
                y = list(x)
                y[i] -= d
                y[j] += d
                v = A_mu_float(y, E, n)
                if v > cur:
                    x, cur = y, v
                if it % 300 == 299:
                    step *= 0.6
            if cur > best[0]:
                keep = [k for k in range(n) if x[k] > 1e-9]
                mu = M(q, [(mu0.k[k], F(int(round(x[k] * 10 ** 9)), 10 ** 9)) for k in keep])
                if mu.pentagon() is not None:
                    continue                   # degenerated onto a pentagonal sub-support
                at = A_mu_exact(mu)
                best = (float(at), (q, [mu.k[i] for i in range(mu.n)], at, mu.arcbound()))
                print(f"   new max Atilde={float(at):.6f} q={q} sup={[mu.k[i] for i in range(mu.n)]}"
                      f"  ARCBOUND={float(mu.arcbound()):.6f}  pentagonal=False"
                      f"  {'*** EXCEEDS 1/25 ***' if at > TARGET else ''}")
print()
print(f"non-pentagonal supports hill-climbed: {tested}")
print(f"max exact Atilde on a genuinely NON-pentagonal measure: {best[0]:.6f}   (1/25 = 0.04)")
print(f"   verdict on (Q): {'REFUTED' if best[0] > 0.04 else 'SURVIVES this search'}")
if best[1]:
    q, sup, at, arc = best[1]
    print(f"   argmax: q={q} sup={sup} Atilde={at} ARCBOUND={arc}")
