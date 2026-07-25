"""audit_G9_setfalsifier.py -- explicit exact falsifiers for the G9 claims

  (E) "arbitrary-set deletion is defeated by the same witness / has ceiling 4/25"
  (D-interpretation) "deleting an independent set can never beat the single-vertex
      version, for any graph, at any N"

Both claims are about the DELETION MECHANISM, i.e. about
      drop(S) := bip(G) - bip(G-S)   vs   budget(s) := (N^2-(N-s)^2)/25 ,
because the induction step is  bip(G) = bip(G-S) + drop(S) <= (N-s)^2/25 + budget(s)
                                     = N^2/25 .
G9 only ever bounds drop(S) by the GREEDY re-insertion cost  cost(S) >= drop(S);
the two differ by a factor > 2 on the very witness used.

Exact integers / Fractions only.
"""
from fractions import Fraction
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G9_core import (C5, blowup_bip_exact, build_blowup, bip_exhaustive,
                           delete_set, triangle_free)

print("W_t = C5[7t,2t,7t,7t,2t],  N = 25t,  delta = 4t = 4N/25,  bip = 14t^2")
print()
hdr = "%-4s %-22s %-5s %-7s %-9s %-6s %-12s %-6s"
print(hdr % ("t", "S (parts)", "|S|", "bip(G)", "bip(G-S)", "drop", "budget", "FIRES?"))
rows = [
    ("P2 u P3",      lambda t: [0, 0, 7 * t, 7 * t, 0]),
    ("P0 u P2 (independent)", lambda t: [7 * t, 0, 7 * t, 0, 0]),
    ("P0 u P3 (independent)", lambda t: [7 * t, 0, 0, 7 * t, 0]),
    ("5t from P0,P2,P3",     lambda t: [5 * t, 0, 5 * t, 5 * t, 0]),
]
for t in (1, 2, 3, 5, 10):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    b = blowup_bip_exact(5, C5, a)
    for name, f in rows:
        s = f(t)
        ssz = sum(s)
        rest = [a[i] - s[i] for i in range(5)]
        b2 = blowup_bip_exact(5, C5, rest)
        bud = Fraction(2 * N * ssz - ssz * ssz, 25)
        print(hdr % (t, name, ssz, b, b2, b - b2, str(bud), b - b2 <= bud))
    print()

print("--- independence check of A = P0 u P2 in W_1 (explicit 25-vertex graph) ---")
n, M, off, part = build_blowup(5, C5, [7, 2, 7, 7, 2])
A = [v for v in range(n) if part[v] in (0, 2)]
indep = all(M[u][v] == 0 for u in A for v in A if u != v)
n2, M2 = delete_set(n, M, A)
b_full = 14                      # verified elsewhere by 2^24 enumeration
b_rest = bip_exhaustive(n2, M2)
print("  |A|=%d  A independent = %s   bip(W_1 - A) = %d (explicit, N'=%d)"
      % (len(A), indep, b_rest, n2))
print("  drop = %d ;  budget = %s ;  single-vertex budget (2N-1)/25 = %s"
      % (b_full - b_rest, Fraction(2 * 25 * 14 - 196, 25), Fraction(49, 25)))
print("  min_v single-vertex drop on W_1 = 2 > 49/25 -> single-vertex does NOT fire,")
print("  but independent-set deletion at A DOES fire: %d <= %s"
      % (b_full - b_rest, Fraction(2 * 25 * 14 - 196, 25)))
assert indep
assert b_full - b_rest <= Fraction(2 * 25 * 14 - 196, 25)

print()
print("--- sanity: on C5[n] the true set-deletion mechanism never fires strictly ---")
for nn in range(1, 7):
    a = [nn] * 5
    N = 5 * nn
    b = blowup_bip_exact(5, C5, a)
    strict = []
    from itertools import product
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        drop = b - blowup_bip_exact(5, C5, rest)
        bud = Fraction(2 * N * ssz - ssz * ssz, 25)
        if drop < bud:
            strict.append((s, drop, bud))
    eq = 0
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        drop = b - blowup_bip_exact(5, C5, rest)
        bud = Fraction(2 * N * ssz - ssz * ssz, 25)
        if drop == bud:
            eq += 1
    print("  C5[%d]: #S with drop < budget = %d ; #S with drop == budget = %d"
          % (nn, len(strict), eq))
