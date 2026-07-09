#!/usr/bin/env python3
"""CLAUDE exact gate (2026-07-09) for WALL_ATTACK_R2 claims (all Fraction-exact):
(F1) closure-minimality falsifier instance; (F2) add-only patch falsifier;
(I1) supermodularity of Def; (I2) overlap identity Def(P1|P2)=Def(P1)+Def(P2)+Cap(N1&N2) [disjoint ports];
(I3) disjoint-neighborhood additivity; (C) minimal deficient sets have connected legal incidence graph
(one legal component) — random instances, exhaustive subset scan."""
from fractions import Fraction as F
from itertools import combinations
import random

def legalNbr(P, legal, nS):
    return frozenset(s for s in range(nS) if any((p, s) in legal for p in P))

def cap_of(T, cap):
    return sum((cap[s] for s in T), F(0))

def Def(P, L, legal, cap, nS):
    return sum((L[p] for p in P), F(0)) - cap_of(legalNbr(P, legal, nS), cap)

fails = []

# (F1) the closure-minimality falsifier
L = {0: F(1), 1: F(0)}; cap = {0: F(0), 1: F(100)}; legal = {(0, 0), (1, 1)}
d_p1 = Def({0}, L, legal, cap, 2); d_empty = Def(set(), L, legal, cap, 2)
d_closed = Def({0, 1}, L, legal, cap, 2); d_p2 = Def({1}, L, legal, cap, 2)
ok_f1 = (d_p1 == F(1) and d_p1 > 0 and d_empty <= 0 and d_closed == F(-99) and d_closed <= 0
         and d_p2 == F(-100) and d_closed == d_p1 + d_p2)  # additivity on disjoint nbrs
print(f"F1 closure-minimality falsifier: Def(p1)={d_p1} min-def OK, Def(closure)={d_closed}<=0, "
      f"only ONE deficient block -> claim VERIFIED: {ok_f1}")
if not ok_f1: fails.append("F1")

# (F2) add-only patch falsifier
theta = {"Y": F(1), "X": F(0)}; use = {("Y", "f"): F(1), ("X", "f"): F(1)}
coeff = sum(theta[c] * use[(c, "f")] for c in theta)
eps = F(1, 1000); ok_f2 = (coeff == 1 and coeff + eps * use[("X", "f")] > 1)
print(f"F2 add-only patch falsifier: saturated coeff={coeff}, +eps -> {coeff + eps} > 1: {ok_f2}")
if not ok_f2: fails.append("F2")

# (I1)-(I3) + (C) random exact instances
rng = random.Random(20260709)
n_ident = n_conn = n_minimal = 0
for trial in range(400):
    nP, nS = rng.randint(1, 6), rng.randint(1, 6)
    legal = {(p, s) for p in range(nP) for s in range(nS) if rng.random() < 0.45}
    L = {p: F(rng.randint(0, 40), rng.randint(1, 4)) for p in range(nP)}
    cap = {s: F(rng.randint(0, 40), rng.randint(1, 4)) for s in range(nS)}
    ports = list(range(nP))
    subsets = [set(c) for r in range(nP + 1) for c in combinations(ports, r)]
    # I1 supermodularity + I2/I3 on random pairs
    for _ in range(60):
        P = set(rng.sample(ports, rng.randint(0, nP))); Qs = set(rng.sample(ports, rng.randint(0, nP)))
        dP, dQ = Def(P, L, legal, cap, nS), Def(Qs, L, legal, cap, nS)
        dU, dI = Def(P | Qs, L, legal, cap, nS), Def(P & Qs, L, legal, cap, nS)
        if not (dP + dQ <= dU + dI):
            fails.append(f"I1 trial{trial} P={P} Q={Qs}"); break
        n_ident += 1
        if P & Qs == set():
            inter_cap = cap_of(legalNbr(P, legal, nS) & legalNbr(Qs, legal, nS), cap)
            if dU != dP + dQ + inter_cap:
                fails.append(f"I2 trial{trial}"); break
            if not (legalNbr(P, legal, nS) & legalNbr(Qs, legal, nS)) and dU != dP + dQ:
                fails.append(f"I3 trial{trial}"); break
    # (C) every inclusion-minimal deficient set has ONE legal component
    for P in subsets:
        if not P or not (Def(P, L, legal, cap, nS) > 0):
            continue
        if any(Def(set(Ps), L, legal, cap, nS) > 0 for r in range(len(P)) for Ps in combinations(P, r)):
            continue  # not inclusion-minimal
        n_minimal += 1
        # legal-incidence components within (P, N(P))
        comps = []
        todo = set(P)
        while todo:
            x = todo.pop(); blockP, blockS = {x}, set()
            grew = True
            while grew:
                grew = False
                for (p, s) in legal:
                    if p in blockP and s not in blockS and s in legalNbr(P, legal, nS):
                        blockS.add(s); grew = True
                    if s in blockS and p in P and p not in blockP:
                        blockP.add(p); grew = True
            todo -= blockP; comps.append(blockP)
        if len(comps) != 1:
            fails.append(f"C trial{trial} P={P} comps={len(comps)}")
        else:
            n_conn += 1

print(f"identity checks: {n_ident} supermodularity+overlap OK; minimal deficient sets found: {n_minimal}, "
      f"one-component: {n_conn}")
print(f"VERDICT: {'ALL PASS' if not fails else 'FAILS: ' + '; '.join(fails[:5])}")
