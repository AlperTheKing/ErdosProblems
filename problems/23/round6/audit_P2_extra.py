"""AUDIT part 2: the claims of P2 sections 3, 7(a), 7(d), 9 -- attacked directly."""
import sys, os, functools, math
print = functools.partial(print, flush=True)
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_P2_core import Measure, gamma_measure

TARGET = F(1, 25)

print("=" * 100)
print("1. P2 section 7(d): the three-cluster witnesses, reproduced from the construction")
print("   three_cluster(n,eps): atoms at j/3 + i*eps, i=1..n, j=0,1,2, equal weights")
print("=" * 100)
for n, den, claim in ((15, 100000, F(21868, 421875)), (25, 400000, F(33329, 625000))):
    M = 3 * den
    pos = sorted(j * den + 3 * i for j in range(3) for i in range(1, n + 1))
    mu = Measure(M, pos, [1] * (3 * n))
    A, minm = mu.A(), mu.min_m_supp()
    gs = set(mu.gn)
    crit = min(A, minm)
    ab = mu.arcbound()
    print(f"  n={n}/cluster (N={3*n}), eps=1/{den}:  W={mu.W()}  far-regular={len(gs)==1}")
    print(f"      A={A}={float(A):.9f}   min_b m(b)={minm}={float(minm):.9f}")
    print(f"      CRIT=min(A,all bound_k)={crit}={float(crit):.9f}   P2 claim={claim}={float(claim):.9f}"
          f"   {'MATCH' if crit == claim else '*** MISMATCH ***'}")
    print(f"      ARCBOUND={ab}={float(ab):.9f}   (1/36={1/36:.9f})   item-7 falsifier={mu.is_item7_falsifier()}")
    hh = mu.min_over_arcs_of_length(F(1, 2), F(1, 2))
    print(f"      min over free-offset 1/3-arcs (= m(b), b free on the circle) = {mu.m_free()}"
          f"={float(mu.m_free()):.9f}")
    print(f"      min over arcs of length EXACTLY 1/2 = {hh}={float(hh):.9f}"
          f"   <-- P2 sect.9 says this family is 'blind by construction'")

print()
print("=" * 100)
print("2. P2 section 7(a): is 'best CRIT = 0.0429749' for n=4 attainable at all?")
print("   Exact 4-atom classification (only 2K_2 survives; every other shape has some m(b)=0).")
print("=" * 100)
# every 4-atom triangle-free circle graph, realised explicitly
shapes = {
    "2K_2   (0,3e,1/3+2e,2/3+e)": (1800, [0, 9, 606, 1203], [1, 1, 1, 1]),
    "K_{1,3} (0 far from 3 pts in (1/3,2/3))": (900, [0, 310, 400, 590], [1, 1, 1, 1]),
    "P_4": (900, [0, 302, 320, 610], [1, 1, 1, 1]),
    "P_3+K_1": (900, [0, 10, 400, 500], [1, 1, 1, 1]),
    "K_2+2K_1": (900, [0, 10, 20, 400], [1, 1, 1, 1]),
}
for nm, (M, pos, w) in shapes.items():
    mu = Measure(M, pos, w)
    deg = [sum(1 for j in range(4) if mu.adj[i][j]) for i in range(4)]
    print(f"  {nm:42s} edges={mu.edges} deg={deg} min_b m(b)={mu.min_m_supp()}"
          f"  CRIT<=min(A,min m)={min(mu.A(), mu.min_m_supp())}")
print("  => on 4 atoms only 2K_2 can have min_b m(b) > 0.")
print("  2K_2 with weights (a,b) and (c,d):  m = {ab, ab, cd, cd},  A < (ab+cd)/3  (edges are")
print("  strictly longer than 1/3).  max of min((ab+cd)/3, min(ab,cd)) s.t. a+b+c+d=1 is at")
print("  a=b=q, c=d=p=sqrt2*q  ->  CRIT < (3-2sqrt2)/4 = %.9f  for EVERY 4-atom measure."
      % ((3 - 2 * math.sqrt(2)) / 4))
print("  P2 section 7(a) reports  best CRIT(n=4) = 0.0429749 > 0.0428932  ==> NOT a CRIT value.")
print()
print("  Reason: P2_search.crit_float truncates the hierarchy at k<=10 (KLEV) and is float.")
print("  Explicit demonstration -- 2K_2 with x=(q,p,q,p), p/q swept, eps=1/6000000:")
M = 18000000
best_tr, best_true = (None, -1), (None, -1)
for num, dwt in [(29, 41), (3, 4), (7, 10), (169, 239), (5, 7), (12, 17), (17, 24), (41, 58)]:
    q, p = num, dwt                      # integer weights (q,p,q,p)
    mu = Measure(M, [0, 9, 6000006, 12000003], [q, p, q, p])
    trunc = min([mu.A()] + [mu.bound_k(k) for k in range(11)])
    true = min(mu.A(), mu.min_m_supp())
    if trunc > best_tr[1]:
        best_tr = ((q, p), trunc)
    if true > best_true[1]:
        best_true = ((q, p), true)
    print(f"    (q,p)=({q:3d},{p:3d}) p/q={p/q:.5f}  truncated CRIT(k<=10)={float(trunc):.7f}"
          f"   TRUE CRIT={float(true):.7f}   {'TRUNCATION INFLATES' if trunc > true else ''}")
print(f"    best truncated = {float(best_tr[1]):.7f} at {best_tr[0]}   "
      f"best true = {float(best_true[1]):.7f} at {best_true[0]}    "
      f"(3-2sqrt2)/4 = {(3-2*math.sqrt(2))/4:.7f}")

print()
print("=" * 100)
print("3. P2 section 3: 'every neighbourhood cut N(b) is above 1/25' -- true only for b in supp")
print("=" * 100)
tests = {
    "4-atom 2K_2 (eps=1/600)": (1800, [0, 9, 606, 1203], [1, 1, 1, 1]),
}
mu = Measure(1800, [0, 9, 606, 1203], [1, 1, 1, 1])
print(f"  4-atom witness: min over b in SUPP of m(b) = {mu.min_m_supp()} = {float(mu.min_m_supp()):.6f} > 1/25")
print(f"                  min over b in the WHOLE CIRCLE of m(b) = {mu.m_free()} "
      f"(b=4/1800 gives the cut {{606,1203}}, both sides independent)")
w14 = gamma_measure(14, [1 if i in (0, 3, 4, 7, 8, 9, 12, 13) else 0 for i in range(14)])
print(f"  Wagner/Gamma_14: min over supp = {w14.min_m_supp()}, min over the whole circle = {w14.m_free()}"
      f"  ({'free b does NOT save it' if w14.m_free() > TARGET else 'free b saves it'})")

print()
print("=" * 100)
print("4. MANDATORY REGRESSION of the two 'repair' families P2 section 9 proposes/rejects")
print("   rule A: min over arcs of length exactly 1/2      rule B: min over ALL 1/3-arcs (b free)")
print("=" * 100)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round5'))
from claude_witness_regression import WITNESSES
badA, badB = [], []
for name, m, w, why in WITNESSES:
    mu = gamma_measure(m, w)
    ra = mu.min_over_arcs_of_length(F(1, 2), F(1, 2))
    rb = mu.m_free()
    fa = "" if (ra is not None and ra <= TARGET) else " *** EXCEEDS 1/25 ***"
    fb = "" if rb <= TARGET else " *** EXCEEDS 1/25 ***"
    if fa:
        badA.append(name)
    if fb:
        badB.append(name)
    print(f"  {name:26s} half-arc-min={str(ra):>8s}={float(ra):.6f}{fa:28s} "
          f"free-1/3-arc-min={str(rb):>8s}={float(rb):.6f}{fb}")
print(f"  rule A (half-arc minimum): {'PASSES' if not badA else 'REFUTED by ' + ', '.join(badA)}")
print(f"  rule B (free 1/3-arc min): {'PASSES' if not badB else 'REFUTED by ' + ', '.join(badB)}")
