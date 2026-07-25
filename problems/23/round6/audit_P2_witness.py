"""AUDIT: re-verify every witness quoted in round6/P2.md with the independent core."""
import sys, os, functools
print = functools.partial(print, flush=True)
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_P2_core import Measure, gamma_measure

R = {}

print("=" * 100)
print("A. CALIBRATION on C5 (must give A = bound_k = ARCBOUND = psi = 1/25 exactly)")
print("=" * 100)
c5 = Measure(5, [0, 1, 2, 3, 4], [1] * 5)
r = c5.report("C5 = Gamma_5 uniform")
assert r['A'] == F(1, 25) and r['b0'] == F(1, 25) and r['arc'] == F(1, 25) and r['psi'] == F(1, 25)
assert all(c5.bound_k(k) == F(1, 25) for k in range(12))
print("    CALIBRATION OK: every route returns exactly 1/25 on C5.\n")

print("=" * 100)
print("B. P2 section 4: the FOUR-ATOM minimal falsifier, eps = 1/600  -> M = 1800")
print("=" * 100)
# positions 0, 3e, 1/3+2e, 2/3+e with e = 1/600 ; M = 1800 -> 0, 9, 606, 1203
w4 = Measure(1800, [0, 9, 606, 1203], [1, 1, 1, 1])
r = w4.report("4 atoms uniform, eps=1/600")
R['4atom'] = r
print(f"    P2 claims: W=1/8, all bound_k=1/16, A=49/1200, ARCBOUND=psi=0, graph = 2K_2")
print(f"    edges (index pairs) = {w4.edges}  -> {'2K_2' if len(w4.edges) == 2 else 'NOT 2K_2'}")
assert r['W'] == F(1, 8) and r['A'] == F(49, 1200) and r['arc'] == 0 and r['psi'] == 0
assert all(w4.bound_k(k) == F(1, 16) for k in range(30))

print("=" * 100)
print("C. P2 section 4: the OPTIMAL four-atom weighting (169,239,169,239)/816, eps=1/600000")
print("=" * 100)
M = 1800000
w4b = Measure(M, [0, 9, 600006, 1200003], [169, 239, 169, 239])
r = w4b.report("4 atoms (169,239,169,239), eps=1/600000")
R['4atom_opt'] = r
print(f"    P2 claims CRIT = 2142007159/49939200000, min_b m(b) = 28561/665856, ARCBOUND=psi=0")
print(f"    my A               = {r['A']}")
print(f"    P2 CRIT            = {F(2142007159,49939200000)}")
print(f"    my min_b m(b)      = {r['minm']}   P2: {F(28561,665856)}")
print(f"    (3-2sqrt2)/4       = 0.0428932188...   my CRIT = {float(min(r['A'], r['minm'])):.9f}")

print("=" * 100)
print("D. P2 section 5: WAGNER V8 on Gamma_14 and on Gamma_29")
print("=" * 100)
wag14 = gamma_measure(14, [1 if i in (0, 3, 4, 7, 8, 9, 12, 13) else 0 for i in range(14)])
r = wag14.report("Wagner on Gamma_14, uniform")
R['wagner14'] = r
print("    P2 claims W=3/16, T/W=11/28, A=9/224, every bound_k=3/64, ARCBOUND=psi=1/32")
deg = [sum(1 for j in range(wag14.n) if wag14.adj[i][j]) for i in range(wag14.n)]
print(f"    degrees = {deg}")
wag29 = gamma_measure(29, [1 if i in (0, 8, 9, 17, 18, 19, 27, 28) else 0 for i in range(29)])
r = wag29.report("Wagner on Gamma_29, uniform (claimed sweep maximum)")
R['wagner29'] = r
print("    P2 claims A=3/58, every bound_k=3/64, CRIT=3/64, ARCBOUND=psi=1/32")

print("=" * 100)
print("E. P2 section 6: the two hand-checked Gamma witnesses")
print("=" * 100)
g11 = gamma_measure(11, [3, 0, 1, 3, 0, 1, 3, 3, 0, 1, 3])
r = g11.report("Gamma_11 w=(3,0,1,3,0,1,3,3,0,1,3), q=18")
R['g11'] = r
print("    P2 claims A=4/99, min_b m(b)=13/324, CRIT=4/99, ARCBOUND=psi=5/162")
print(f"    inf_k bound_k >= min_b m(b) = {r['minm']} = {float(r['minm']):.7f} < A = {float(r['A']):.7f}")
g17 = gamma_measure(17, [1 if i in (0, 4, 5, 9, 10, 11, 15, 16) else 0 for i in range(17)])
r = g17.report("Gamma_17 uniform on {0,4,5,9,10,11,15,16}")
R['g17'] = r
print("    P2 claims A=3/68, every bound_k=3/64, CRIT=3/68, ARCBOUND=psi=1/32")

print("=" * 100)
print("F. Discrete stand-in for the 1/3-PERIODIC family mu_eta (P2 section 2)")
print("=" * 100)
# three clusters of c equally spaced atoms of width eta, uniform: exactly 1/3-periodic
for (c, M, step) in [(5, 3000, 1), (15, 90000, 1), (25, 750000, 1)]:
    pos = []
    for cl in range(3):
        base = cl * M // 3
        pos += [base + t * step for t in range(c)]
    pos = sorted(pos)
    mu = Measure(M, pos, [1] * (3 * c))
    A = mu.A()
    print(f"  clusters of {c} atoms, M={M}: W={mu.W()} min_b m(b)={mu.min_m_supp()}={float(mu.min_m_supp()):.7f}"
          f"  A={A}={float(A):.7f}  ARCBOUND={float(mu.arcbound()):.7f}"
          f"  falsifier={mu.is_item7_falsifier()}")
    half = mu.min_over_arcs_of_length(F(1, 2), F(1, 2))
    print(f"        1/18={1/18:.7f}  1/36={1/36:.7f}  min over free-offset 1/3-arcs = "
          f"{float(mu.m_free()):.7f}   min over length-EXACTLY-1/2 arcs = "
          f"{'n/a' if half is None else float(half)}")

print("=" * 100)
print("G. MANDATORY 9-WITNESS REGRESSION (round5/claude_witness_regression.py)")
print("=" * 100)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round5'))
from claude_witness_regression import WITNESSES, arcbound as r5_arcbound, gamma as r5_gamma
P2_CLAIM = [F(1, 49), F(1, 49), F(1, 49), F(1, 25), F(1, 54), F(3, 100), F(0), F(1, 49), F(1, 100)]
ok = True
for idx, (name, m, w, why) in enumerate(WITNESSES):
    mu = gamma_measure(m, w)
    mine = mu.arcbound()
    theirs = r5_arcbound(m, r5_gamma(m), [F(wi, sum(w)) for wi in w])
    claim = P2_CLAIM[idx]
    tag = "MATCH" if (mine == theirs == claim) else "*** MISMATCH ***"
    ok &= (mine == theirs == claim)
    print(f"  {name:26s} m={m:3d} my ARCBOUND={str(mine):>8s}  round5={str(theirs):>8s}  "
          f"P2 claim={str(claim):>8s}  {tag}")
    print(f"        A={str(mu.A()):>10s}={float(mu.A()):.6f} min_b m={float(mu.min_m_supp()):.6f} "
          f"psi={str(mu.psi()):>8s}  item7-falsifier={mu.is_item7_falsifier()}")
print(f"  REGRESSION: {'all nine reproduced' if ok else 'DISCREPANCY FOUND'}")

print("=" * 100)
print("H. ARC-CUT CONJECTURE spot check: is ARCBOUND <= 1/25 on every witness above?")
print("=" * 100)
for k, v in R.items():
    print(f"  {k:12s} ARCBOUND={str(v['arc']):>10s}={float(v['arc']):.7f}  "
          f"{'OK <= 1/25' if v['arc'] <= F(1,25) else '*** EXCEEDS 1/25 ***'}")
