"""Q4: which cuts of Gamma_8 are non-dominated, which are 'arc' cuts, and which carry multiplier mass."""
import pickle, sys
import numpy as np
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts

m = int(sys.argv[1]) if len(sys.argv) > 1 else 8
n, E = gamma_graph(m)
cuts = all_cuts(n, E)
nd = nondominated_cuts(cuts)


def side(mask, v):
    return 0 if v == 0 else (mask >> (v - 1)) & 1


def as_set(mask):
    return frozenset(v for v in range(n) if side(mask, v) == 1)


def is_arc(Sset):
    """Is S (or its complement) a set of consecutive vertices on the circle Z_n?"""
    for T in (Sset, frozenset(range(n)) - Sset):
        if not T:
            return True
        k = len(T)
        for s in range(n):
            if T == frozenset((s + i) % n for i in range(k)):
                return True
    return False


print(f"Gamma_{m}: {len(nd)} non-dominated cuts")
arcs = 0
for mask, mono in nd:
    S = as_set(mask)
    a = is_arc(S)
    arcs += a
    print(f"  S={sorted(S)!s:28s} |mono|={len(mono)} mono={sorted(E[k] for k in mono)}  arc={a}")
print(f"arc cuts among non-dominated: {arcs};  non-arc: {len(nd)-arcs}")

if len(sys.argv) > 2:
    sol = pickle.load(open(sys.argv[2], "rb"))
    nu = sol['nu']
    print("\nmultiplier mass per cut (solution %s):" % sys.argv[2])
    for i, (mask, mono) in enumerate(sol['cuts']):
        S = as_set(mask)
        print(f"  S={sorted(S)!s:28s} arc={is_arc(S)}  sum nu = {nu[i].sum():10.6f}  max = {nu[i].max():10.6f}")
