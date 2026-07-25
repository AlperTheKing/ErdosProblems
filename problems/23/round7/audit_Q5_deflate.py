"""Deflation probes: is any of Q5.md's positive content already trivial?

D1  Is max_x psi(V8) <= 1/25 obtainable from the TRIVIAL route (a homomorphism to
    C5)?   If phi: G -> C5 is a homomorphism then psi(G,x) <= psi(C5, phi_* x) <= 1/25
    for every x, with no Guenin and no idealness.  Exhaustive over all 5^8 maps.
D2  Is the C5[2] statement vacuous?  psi is invariant under twin-collapsing
    (accepted base 4), and C5[2] collapses to C5, so psi(C5[2],x) <= 1/25 needs no
    minor theory at all.  Checked exactly on random weights.
D3  Same question for And(4)/And(5): no homomorphism to C5 either (so the OPEN cases
    really are open, i.e. Q5.md's boundary is where it says it is).
"""
from fractions import Fraction as F
from itertools import product
import random
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import E_of, psi, C5n, andrasfai, circulant, emass

FAIL = []


def chk(name, got, want=True):
    good = (got == want)
    if not good:
        FAIL.append((name, got, want))
    print(f"  {'OK  ' if good else 'FAIL'} {name}: {got}" + ("" if good else f" (want {want})"))


def hom_to_C5(n, A):
    """Exhaustive search for a homomorphism G -> C5 (5^n maps, n small)."""
    C5adj = [[(abs(i - j) % 5 in (1, 4)) for j in range(5)] for i in range(5)]
    E = E_of(n, A)
    for f in product(range(5), repeat=n):
        if all(C5adj[f[u]][f[v]] for (u, v) in E):
            return f
    return None


print("=== D1  homomorphism V8 -> C5 ? ===")
n, A = circulant(8, [1, 4])
h = hom_to_C5(n, A)
chk("V8 has NO homomorphism to C5 (so the trivial route does not close it)", h is None)
print(f"      (searched all 5^8 = {5**8} maps)")

print("=== D3  homomorphism And(4)/And(5) -> C5 ? ===")
for k in (4, 5):
    n, A = andrasfai(k)
    if n <= 12:
        h = hom_to_C5(n, A)
        chk(f"And({k}) has NO homomorphism to C5", h is None)
    else:
        print(f"      And({k}): 5^{n} too large; circular chromatic number "
              f"(3k-1)/k = {3*k-1}/{k} > 5/2 already rules it out")

print("=== D2  is the C5[2] idealness statement vacuous? (twin-collapse) ===")
n2, A2 = C5n(2)
n1, A1 = C5n(1)
rnd = random.Random(7)
agree = 0
for t in range(200):
    raw = [rnd.randint(0, 9) for _ in range(10)]
    if sum(raw) == 0:
        continue
    s = sum(raw)
    x = [F(r, s) for r in raw]
    y = [x[2 * p] + x[2 * p + 1] for p in range(5)]
    a = psi(n2, A2, x)
    b = psi(n1, A1, y)
    if a != b:
        FAIL.append(("twin collapse", x, a, b))
        break
    agree += 1
chk(f"psi(C5[2],x) == psi(C5, collapsed x) on {agree} random exact weightings", agree == 200)
print("      => psi(C5[2],x) <= 1/25 for every x is IMMEDIATE from accepted base 4 +")
print("         psi(C5,y) = min_i y_i y_{i+1} <= 1/25 (AM-GM).  Q5.md's headline 5")
print("         ('the extremal family is inside the class') is therefore correct but")
print("         adds nothing: no minor theory is needed for C5[n].")

print("\nFAILURES:", len(FAIL))
for f in FAIL:
    print("   ", f)
