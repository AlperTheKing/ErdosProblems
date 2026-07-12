"""S2: exact budget-vs-increment arithmetic at the extremal family C5[t].
F1 (vertex deletion): budget (2N-1)/25 vs actual increment beta(G)-beta(G-v).
F2 (pentagon deletion): budget (2N-5)/5 = (N^2-(N-5)^2)/25 vs actual increment for a
   transversal induced C5. Claim: EXACT match (2t-1) at balanced C5[t].
Also: edge-pair deletion budget (4N-4)/25 vs increment (F1').
All brute-force exact.
"""
import numpy as np
from fractions import Fraction
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\tmp\agent_reform\extremal_induction")
from S1_sanity import maxcut_exact, beta, c5_blowup, is_triangle_free

def induced_subgraph(n, edges, keep):
    keep = sorted(keep)
    pos = {v: i for i, v in enumerate(keep)}
    E2 = [(pos[i], pos[j]) for (i, j) in edges if i in pos and j in pos]
    return len(keep), E2

ok = True
print("=== F1: vertex deletion at C5[t] (delete one vertex of class V1) ===")
for t in range(2, 5):
    n, E = c5_blowup([t] * 5)
    bG = beta(n, E)
    n2, E2 = induced_subgraph(n, E, [v for v in range(n) if v != 0])
    bH = beta(n2, E2)
    inc = bG - bH
    budget = Fraction(2 * n - 1, 25)
    print(f" t={t} N={n}: beta(G)={bG} beta(G-v)={bH} increment={inc} budget=(2N-1)/25={budget} "
          f"deficit={Fraction(inc)-budget} FAILS={Fraction(inc)>budget}")
    ok &= (inc == t) and (Fraction(inc) > budget)  # documented failure F1

print("=== F2: transversal induced C5 deletion at C5[t] ===")
for t in range(2, 5):
    n, E = c5_blowup([t] * 5)
    # transversal: first vertex of each class
    trans = [sum([t] * c) for c in range(5)]  # offsets 0, t, 2t, 3t, 4t
    bG = beta(n, E)
    keep = [v for v in range(n) if v not in set(trans)]
    n2, E2 = induced_subgraph(n, E, keep)
    bH = beta(n2, E2)
    inc = bG - bH
    budget = Fraction(2 * n - 5, 5)
    print(f" t={t} N={n}: beta(G)={bG} beta(G-P)={bH} increment={inc} budget=(2N-5)/5={budget} "
          f"EXACT_MATCH={Fraction(inc)==budget}")
    ok &= (inc == 2 * t - 1) and (Fraction(inc) == budget)

print("=== F1': adjacent-pair deletion at C5[t] ===")
for t in range(2, 5):
    n, E = c5_blowup([t] * 5)
    bG = beta(n, E)
    # u=class1 vtx 0, v=class2 vtx t (adjacent)
    keep = [v for v in range(n) if v not in (0, t)]
    n2, E2 = induced_subgraph(n, E, keep)
    bH = beta(n2, E2)
    inc = bG - bH
    budget = Fraction(4 * n - 4, 25)
    print(f" t={t} N={n}: increment={inc} budget=(4N-4)/25={budget} FAILS={Fraction(inc)>budget}")
    ok &= Fraction(inc) > budget  # documented failure

print("S2 ALL OK (failure points F1, F1' confirmed; F2 budget exact-match confirmed)" if ok else "S2 UNEXPECTED")
sys.exit(0 if ok else 1)
