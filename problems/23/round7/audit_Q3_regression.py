"""audit_Q3_regression.py -- protocol step 2 of the Q3 audit:
run the Q3 claims against the ten round-5 regression witnesses, exactly, and check
tightness at C5[n].

Q3's quantitative claims that can be tested pointwise:
  (B1)  psi(H,x) <= 1/25                                  (the conjecture; must hold)
  (B2)  psi(H,x) <= 1/25 - (19/425) * d(H,x)              (pass-1 b.5 empirical envelope)
  (B3)  psi(H,x) <= 1/25 - (1/5)   * d(H,x)               (pass-2 "worst local direction" ceiling)
  (B4)  Theorem Q3-1:  psi <= 1/25 - (18/625)*MISS, valid only when H is a subgraph of B_phi.

psi and d are computed here from scratch, in exact integer arithmetic, on the SUPPORT of x
(zero-weight vertices contribute 0 to every term of both functionals, cf. Q3.md a.2).
"""
from fractions import Fraction as F
from itertools import combinations, product
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round5'))
from claude_witness_regression import WITNESSES, gamma

def psi_int(k, adjm, w):
    """min over all 2^(k-1) cuts of sum of w_u w_v over monochromatic edges (integers)."""
    best = None
    for S in range(1 << (k - 1)):
        tot = 0
        for u in range(k):
            for v in range(u + 1, k):
                if adjm[u][v] and ((S >> u) & 1) == ((S >> v) & 1):
                    tot += w[u] * w[v]
        if best is None or tot < best:
            best = tot
    return best

def dist_int(k, adjm, w):
    """min over phi:V->Z5 of weighted symmetric difference to the blow-up B_phi (integers).
    phi(0)=0 by rotation invariance; brute force 5^(k-1)."""
    cons = [[1 if ((a - b) % 5) in (1, 4) else 0 for b in range(5)] for a in range(5)]
    best = None
    for tail in product(range(5), repeat=k - 1):
        phi = (0,) + tail
        tot = 0
        for u in range(k):
            for v in range(u + 1, k):
                e = 1 if adjm[u][v] else 0
                if e != cons[phi[u]][phi[v]]:
                    tot += w[u] * w[v]
        if best is None or tot < best:
            best = tot
            if best == 0:
                break
    return best

print("witness                     |supp|  Q    psi           d             B1  B2  B3")
bad1 = bad2 = bad3 = 0
for (name, m, w, why) in WITNESSES:
    adj = gamma(m)
    supp = [i for i in range(m) if w[i] != 0]
    k = len(supp)
    ww = [w[i] for i in supp]
    A = [[adj[supp[a]][supp[b]] for b in range(k)] for a in range(k)]
    Q = sum(ww)
    if k > 13:
        print("%-27s %5d  %3d   (skipped: 5^%d templates -- see engine run for unit weights)"
              % (name, k, Q, k - 1))
        continue
    p = F(psi_int(k, A, ww), Q * Q)
    d = F(dist_int(k, A, ww), Q * Q)
    b1 = p <= F(1, 25)
    b2 = p <= F(1, 25) - F(19, 425) * d
    b3 = p <= F(1, 25) - F(1, 5) * d
    bad1 += (not b1); bad2 += (not b2); bad3 += (not b3)
    print("%-27s %5d  %3d   %-13s %-13s %s  %s  %s"
          % (name, k, Q, str(p), str(d), "ok" if b1 else "VIOL", "ok" if b2 else "VIOL",
             "ok" if b3 else "VIOL"))

print()
print("violations: B1 (psi<=1/25): %d   B2 (envelope 19/425): %d   B3 (local ceiling 1/5): %d"
      % (bad1, bad2, bad3))

# tightness at C5[n]
print("\nTIGHTNESS AT C5[n] (required):")
for n in range(1, 7):
    k = 5
    A = [[(abs(i - j) % 5) in (1, 4) for j in range(5)] for i in range(5)]
    ww = [n] * 5
    Q = 5 * n
    p = F(psi_int(5, A, ww), Q * Q)
    d = F(dist_int(5, A, ww), Q * Q)
    print("   C5[%d]: psi = %s = %s   d = %s   B2 rhs = %s   B3 rhs = %s   tight: %s"
          % (n, p, "1/25" if p == F(1, 25) else "NOT 1/25", d,
             F(1, 25) - F(19, 425) * d, F(1, 25) - F(1, 5) * d,
             p == F(1, 25) - F(19, 425) * d == F(1, 25) - F(1, 5) * d))
