#!/usr/bin/env python3
"""CLAUDE exact gate (2026-07-09) for the WALL_ATTACK_R3 W2 counterexample: 2-quotient-component abstract
instance where full-escape closure crosses legal root blocks WITHOUT merging legal components.
Checks: closure laws (extensive/monotone/idempotent, exhaustive over 2^2 shores); exposure map; the closed-shore
inventory; Def values; MinimalClosedDeficient({pA,pB}); blockClosed FAILURE (no closed shore exposes {pA});
legal-incidence decomposition of {pA,pB} = 2 components with disjoint sink neighborhoods."""
from fractions import Fraction as F
from itertools import chain, combinations

A, B = "A", "B"; pA, pB = "pA", "pB"; sA, sB = "sA", "sB"
legal = {(pA, sA), (pB, sB)}
cap = {sA: F(1), sB: F(1)}
L = {pA: F(3), pB: F(1)}

def cl(U):
    return frozenset({A, B}) if A in U else frozenset(U)

def exposed(U):
    out = set()
    if A in U: out.add(pA)
    if B in U: out.add(pB)
    return frozenset(out)

def N(P):
    return frozenset(s for s in (sA, sB) if any((p, s) in legal for p in P))

def Def(P):
    return sum((L[p] for p in P), F(0)) - sum((cap[s] for s in N(P)), F(0))

def powerset(xs):
    return [frozenset(c) for c in chain.from_iterable(combinations(xs, r) for r in range(len(xs) + 1))]

fails = []
shores = powerset([A, B])
# closure laws
for U in shores:
    if not (U <= cl(U)): fails.append(f"extensive {set(U)}")
    if cl(cl(U)) != cl(U): fails.append(f"idempotent {set(U)}")
    for V in shores:
        if U <= V and not (cl(U) <= cl(V)): fails.append(f"monotone {set(U)},{set(V)}")
closed = [U for U in shores if cl(U) == U]
closed_exposures = sorted(sorted(exposed(U)) for U in closed)
ok_closed = closed_exposures == [[], ["pA", "pB"], ["pB"]]
if not ok_closed: fails.append(f"closed inventory {closed_exposures}")
# deficiencies
d_full, d_pB, d_empty = Def({pA, pB}), Def({pB}), Def(frozenset())
if not (d_full == F(2) and d_full > 0): fails.append(f"Def(full)={d_full}")
if not (d_pB == 0 and d_empty == 0): fails.append(f"Def(pB)={d_pB} Def(empty)={d_empty}")
# MinimalClosedDeficient({pA,pB}): every closed P' strictly inside has Def <= 0
min_ok = all(Def(exposed(U)) <= 0 for U in closed if exposed(U) < frozenset({pA, pB}))
if not min_ok: fails.append("minimal-closed-deficient")
# blockClosed failure: no closed shore exposes exactly {pA}
block_fail = all(exposed(U) != frozenset({pA}) for U in closed)
if not block_fail: fails.append("blockClosed did NOT fail")
# legal decomposition of {pA,pB}: two components, disjoint neighborhoods
comps = [({pA}, N({pA})), ({pB}, N({pB}))]
two_roots = N({pA}).isdisjoint(N({pB})) and len(comps) == 2
if not two_roots: fails.append("root decomposition")
# the crossing step {A} -> {A,B}: adds pB whose sinks are disjoint from pA's
step_cross = (cl({A}) == frozenset({A, B})) and N({pB}).isdisjoint(N({pA}))
if not step_cross: fails.append("crossing step")

print(f"closed shores: {[sorted(U) for U in sorted(closed, key=sorted)]}")
print(f"Def(full)={d_full}>0, Def(pB)={d_pB}, minimal-closed-deficient OK={min_ok}")
print(f"blockClosed FAILS (no closed shore exposes only pA): {block_fail}")
print(f"two disjoint legal roots: {two_roots}; closure step A->AB crosses without merging: {step_cross}")
print(f"VERDICT: {'CE VERIFIED - W2-as-stated FALSE at abstract level' if not fails else 'FAILS: ' + '; '.join(fails)}")
