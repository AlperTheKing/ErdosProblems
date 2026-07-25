"""AUDIT of the remaining claims of round6/P1.md (Theorems 1-3, sections 5, 6, 9).

(a) which Andrasfai graphs And(k) = Gamma_{3k-1} are "pentagonal"?  (the chain reduces the
    conjecture to exactly this family, so this decides how much the pentagon lemma covers)
(b) the two factual claims of P1.md section 5 about R2 and W7 vs bound_0
(c) Theorem 1 stress test: random rational sigma must never go below ARCBOUND
(d) Theorem 2 constructive check: spike sigma reproduces individual arc-cut values
(e) section 6 epsilon-degeneration table
(f) does the weight floor x_i >= 1/(3n) really give "real slack" on non-pentagonal measures?
(g) mandatory regression of every rule P1 proposes against round5/claude_witness_regression.py
"""
import sys, random, functools
print = functools.partial(print, flush=True)  # noqa
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round5")

from audit_P1_engine import M, TARGET, WIT, CE, CE8, gam

print("=== (a) Andrasfai graphs And(k) = Gamma_{3k-1}, uniform measure ===")
for k in range(2, 8):
    q = 3 * k - 1
    mu = gam(q, [1] * q)
    pb = mu.pentagon()
    print(f"   And({k}) = Gamma_{q:2d}: pentagonal={'Y' if pb else 'n'}  homC5={'Y' if mu.hom_C5() else 'n'}"
          f"  ARCBOUND={float(mu.arcbound()):.6f}  A={float(mu.W - 2*mu.T):.6f}"
          f"  b0={float(mu.bound(0)):.6f}")

print()
print("=== (b) P1.md section 5 claims about the 'recorded hard cases' ===")
for tag, mu in WIT:
    if tag.startswith(("R1", "R2", "W7")):
        A = mu.W - 2 * mu.T
        print(f"   {tag}: W={mu.W}={float(mu.W):.6f}  A={float(A):.6f}  b0={mu.bound(0)}="
              f"{float(mu.bound(0)):.6f}  b1={float(mu.bound(1)):.6f}  b2={float(mu.bound(2)):.6f}")
        print(f"        b0 <= 1/25 ? {mu.bound(0) <= TARGET}   W-4W^2 <= 1/25 ? "
              f"{mu.W - 4*mu.W**2 <= TARGET}   (chain item 7: b0 settles W<=1/20 and W>=1/5)")

print()
print("=== (c) Theorem 1 stress test (random rational sigma, exact) ===")


def A_sigma(mu, s):
    assert sum(s) == 1
    tot = F(0)
    for (i, j) in mu.E:
        Dp = sum(s[t] for t in range(i, j))
        D = min(Dp, 1 - Dp)
        tot += mu.x[i] * mu.x[j] * (1 - 2 * D)
    return tot


def sigma_mu(mu):
    n = mu.n
    return [(mu.x[i] + mu.x[(i + 1) % n]) / 2 for i in range(n)]


def sigma_leb(mu):
    n, q = mu.n, mu.q
    return [F((mu.k[(i + 1) % n] - mu.k[i]) % q, q) for i in range(n)]


rng = random.Random(11)
rows = list(WIT) + [("CE V8 G20", CE), ("CE V8 G8", CE8)]
worstgap = None
viol = 0
for tag, mu in rows:
    arc = mu.arcbound()
    aL, aM = A_sigma(mu, sigma_leb(mu)), A_sigma(mu, sigma_mu(mu))
    if aL < arc or aM < arc:
        viol += 1
    best = min(aL, aM)
    for _ in range(400):
        raw = [rng.randint(0, 30) for _ in range(mu.n)]
        if sum(raw) == 0:
            continue
        s = [F(t, sum(raw)) for t in raw]
        v = A_sigma(mu, s)
        if v < arc:
            viol += 1
            print("   *** VIOLATION", tag, s, v, arc)
        best = min(best, v)
    print(f"   {tag:26s} ARC={float(arc):.6f}  A_leb={float(aL):.6f}  A_mu={float(aM):.6f}  "
          f"best random/exact sigma={float(best):.6f}  ok={best >= arc}")
print(f"   total violations of Theorem 1 over {400*len(rows)} random exact sigmas: {viol}")

print()
print("=== (d) Theorem 2: a spike sigma at a chosen arc reproduces that arc's cut value ===")
mu = CE
for mask in (0b1111, 0b11, 0b111111):
    n = mu.n
    idx = [i for i in range(n) if (mask >> i) & 1]
    if not idx or len(idx) == n:
        continue
    # cut = the cyclic interval; put sigma mass 1/2 just after its two boundary atoms
    a = max(i for i in range(n) if (mask >> i) & 1 and not ((mask >> ((i + 1) % n)) & 1))
    b = max(i for i in range(n) if not ((mask >> i) & 1) and ((mask >> ((i + 1) % n)) & 1))
    s = [F(0)] * n
    s[a] = s[b] = F(1, 2)
    val = mu.mono(mask)
    print(f"   arc atoms {[mu.k[i] for i in idx]}: cut value {val}={float(val):.6f}   "
          f"A_spike={A_sigma(mu, s)}   equal={A_sigma(mu, s) == val}")

print()
print("=== (e) section 6 epsilon-degeneration (recomputed exactly) ===")
V8 = [0, 1, 6, 7, 12, 13, 14, 19]
heavy = [0, 1, 7, 12, 14]
for eps in (F(1, 10), F(1, 100), F(1, 1000), F(1, 10 ** 6)):
    items = [(k, eps if k not in heavy else (1 - 3 * eps) / 5) for k in V8]
    m2 = M(20, items)
    pb = m2.pentagon()
    print(f"   eps={str(eps):9s} pentagonal={'Y' if pb else 'n'} homC5={'Y' if m2.hom_C5() else 'n'}"
          f"  ARCBOUND={float(m2.arcbound()):.8f}  psi={float(m2.psi()):.8f}")
m5 = M(20, [(k, 1) for k in heavy])
print(f"   eps=0     pentagonal={'Y' if m5.pentagon() else 'n'}  ARCBOUND={m5.arcbound()}")

print()
print("=== (f) is 'robustly non-pentagonal' (x_i >= 1/(3n)) really bounded away from 1/25? ===")
print("    construction: blow up the five C5-atoms of V8 into clusters of c atoms and keep the")
print("    three pentagonality-breaking atoms as singletons of weight exactly the floor 1/(3n).")
print("    (non-pentagonality is inherited from the quotient V8: a blow-up maps onto C5 only if")
print("     V8 does, and V8 does not -- verified once here)")
_v8 = M(20, [(k, 1) for k in V8])
print(f"    quotient V8: homC5={_v8.hom_C5()}  pentagonal={_v8.pentagon() is not None}")
for (Mu, c) in ((10, 2), (10, 3), (30, 6), (30, 10)):
    q = 20 * Mu
    items = []
    pos = []
    for j in V8:
        if j in heavy:
            pos.append([j * Mu + t for t in range(c)])
        else:
            pos.append([j * Mu])
    n = sum(len(p) for p in pos)
    fl = F(1, 3 * n)
    light = 3 * fl
    for j, ps in zip(V8, pos):
        for p in ps:
            items.append((p, fl if j not in heavy else (1 - light) / (5 * c)))
    mm = M(q, items)
    assert min(mm.x) >= F(1, 3 * mm.n), (Mu, c, min(mm.x), F(1, 3 * mm.n))
    pb = mm.pentagon() if mm.n <= 13 else "skipped"
    arc = mm.arcbound()
    print(f"   q={q:4d} c={c:2d} n={mm.n:3d} floor=1/{3*mm.n:3d}  "
          f"pent={pb if pb == 'skipped' else ('Y' if pb else 'n')}  "
          f"ARCBOUND={float(arc):.6f}   > 0.037150 ? {float(arc) > 0.037150}", flush=True)

print()
print("=== (g) MANDATORY REGRESSION against round5/claude_witness_regression.py ===")
import claude_witness_regression as R5


def rule_pentagon(m, adj, x):
    """P1's Theorem 3 as a rule: returns the pentagon bound if pentagonal, else +infinity."""
    mu = M(m, [(k, x[k]) for k in range(m)])
    pb = mu.pentagon()
    return pb[0] if pb else F(10 ** 9)


def rule_Amu(m, adj, x):
    mu = M(m, [(k, x[k]) for k in range(m)])
    return A_sigma(mu, sigma_mu(mu))


def rule_Aleb(m, adj, x):
    mu = M(m, [(k, x[k]) for k in range(m)])
    return A_sigma(mu, sigma_leb(mu))


def rule_minAB(m, adj, x):
    mu = M(m, [(k, x[k]) for k in range(m)])
    A = mu.W - 2 * mu.T
    nu = [mu.x[i] * mu.g[i] for i in range(mu.n)]
    best = F(0)
    for i in range(mu.n):
        v = sum(nu[j] for j in range(mu.n) if (F(mu.k[j] - mu.k[i], mu.q)) % 1 <= F(1, 3))
        best = max(best, v)
    return min(A, mu.W - best)


for nm, rule in (("pentagon lemma (Thm 3)", rule_pentagon), ("A_mu (sigma=mu)", rule_Amu),
                 ("A_leb (= A = W-2T)", rule_Aleb), ("min(A,B)", rule_minAB)):
    print(f"  RULE {nm}")
    bad = R5.check_rule(rule, nm)
