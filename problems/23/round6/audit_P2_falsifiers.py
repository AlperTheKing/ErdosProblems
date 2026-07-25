"""AUDIT: post-process the 1790 falsifiers found by audit_P2_sweep.exe.
Checks (all exact):
  * every one really satisfies the three item-7 hypotheses AND min_b m(b) > 1/25;
  * its true ARCBOUND and psi -- is any of them a counterexample to the ARC-CUT conjecture
    (ARCBOUND > 1/25) or to Erdos 23 (psi > 1/25)?   P2 claims max ARCBOUND = 1/32.
  * P2 section 6 'caution' example, and the V8 max_x psi point.
"""
import sys, os, functools, collections
print = functools.partial(print, flush=True)
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_P2_core import Measure, gamma_measure

TARGET = F(1, 25)
here = os.path.dirname(os.path.abspath(__file__))

rows = [l.split() for l in open(os.path.join(here, 'audit_sweep_falsifiers.txt'))]
print(f"falsifiers dumped by the audit sweep: {len(rows)}")
maxarc, maxpsi, bad = F(0), F(0), []
percell = collections.Counter()
critvals = collections.Counter()
for r in rows:
    m, q, w = int(r[0]), int(r[1]), [int(t) for t in r[2:]]
    assert sum(w) == q and len(w) == m
    mu = gamma_measure(m, w)
    assert mu.is_item7_falsifier(), f"NOT a falsifier: {m} {w}"
    ab, ps = mu.arcbound(), mu.psi()
    assert ps <= ab, "psi > ARCBOUND (impossible)"
    maxarc = max(maxarc, ab)
    maxpsi = max(maxpsi, ps)
    if ab > TARGET or ps > TARGET:
        bad.append((m, w, ab, ps))
    percell[m] += 1
    critvals[min(mu.A(), mu.min_m_supp())] += 1
print(f"  all {len(rows)} re-verified as item-7 falsifiers in exact arithmetic (hypotheses + min_b m > 1/25)")
print(f"  falsifiers per m: {dict(sorted(percell.items()))}")
print(f"  max ARCBOUND over all falsifiers = {maxarc} = {float(maxarc):.7f}   (1/32 = {1/32:.7f})")
print(f"  max psi      over all falsifiers = {maxpsi} = {float(maxpsi):.7f}")
print(f"  any with ARCBOUND > 1/25 or psi > 1/25 ?  {bad if bad else 'NONE'}")
top = sorted(critvals.items(), key=lambda kv: -kv[0])[:5]
print("  top CRIT values (exact, = min(A, min_b m(b))): "
      + ", ".join(f"{v}={float(v):.6f} x{c}" for v, c in top))

print()
print("=" * 100)
print("P2 section 6 caution example: Gamma_11 w=(3,0,1,2,2,0,1,2,1,0,2), q=14")
print("=" * 100)
mu = gamma_measure(11, [3, 0, 1, 2, 2, 0, 1, 2, 1, 0, 2])
print(f"  q={mu.Q}  A={mu.A()}={float(mu.A()):.7f}  min_b m(b)={mu.min_m_supp()}={float(mu.min_m_supp()):.7f}")
print("  bound_k, k=0..14: " + " ".join(f"{float(mu.bound_k(k)):.5f}" for k in range(15)))
b12 = mu.bound_k(12)
print(f"  bound_12 = {b12} = {float(b12):.7f}  {'<= 1/25 (closes it)' if b12 <= TARGET else '> 1/25'}"
      f"   -- P2 says 'bound_12 = 0.03971 < 1/25'")
print(f"  first k with bound_k <= 1/25: "
      f"{next((k for k in range(200) if mu.bound_k(k) <= TARGET), None)}")
print(f"  is it an item-7 falsifier? {mu.is_item7_falsifier()}  (must be False)")

print()
print("=" * 100)
print("Sanity trap check: the Wagner witness psi = 1/32 is a VALUE AT ONE x, not max_x psi.")
print("V8 has an induced C5, so max_x psi(V8) >= 1/25 -- exhibited here.")
print("=" * 100)
c5in = gamma_measure(14, [1 if i in (0, 3, 7, 8, 12) else 0 for i in range(14)])
print(f"  Gamma_14 support {{0,3,7,8,12}} (an induced C5 of the same V8), uniform weights:")
print(f"     edges={c5in.edges}  psi={c5in.psi()}={float(c5in.psi()):.7f}  "
      f"ARCBOUND={c5in.arcbound()}  => max_x psi(V8) >= 1/25 > 1/32")
