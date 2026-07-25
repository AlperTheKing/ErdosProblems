"""AUDIT G12: settle EXACTLY the 1459 residue graphs on N = 8..11 for which no
`bip` pairwise edge-disjoint odd cycles exist (so the cheap integral certificate
nu_int = bip fails).  For each we decide bip vs nu* in exact rational arithmetic.

Acceptance path: a float LP is used ONLY to propose a support; the value is then
recomputed by an exact rational simplex restricted to that support, giving an
exactly verified feasible packing (nu* >= value).  If that fails to reach bip the
graph goes through the full exact LP over ALL odd cycles, which produces an
exactly verified dual cover, i.e. an exact upper bound on nu*.
"""
from fractions import Fraction as Fr
import sys
import numpy as np
from scipy.optimize import linprog
import audit_G12_core as A


def settle(g6s):
    n, E = A.g6(g6s)
    m = len(E)
    b = A.bip(n, E)
    odd = [es for _, es in A.simple_cycles(n, E, only_odd=True)]
    M = np.zeros((m, len(odd)))
    for j, c in enumerate(odd):
        for e in c:
            M[e, j] = 1.0
    r = linprog(c=-np.ones(len(odd)), A_ub=M, b_ub=np.ones(m), bounds=(0, None),
                method="highs")
    sup = [j for j in range(len(odd)) if r.x[j] > 1e-9]
    cols = [odd[j] for j in sup]
    res = A.nu_star_certified(n, E, columns=cols, dual_check_cycles=odd)
    if res["lower"] == b:                     # exact packing of value bip
        return ("NOGAP", b, Fr(b), g6s)
    full = A.nu_star_certified(n, E)           # exact over all odd cycles
    assert full["value"] is not None
    if full["value"] < b:
        return ("GAP", b, full["value"], g6s)
    return ("NOGAP", b, full["value"], g6s)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "audit_G12_residue.txt"
    gs = []
    for ln in open(src):
        if ln.startswith("RESIDUE"):
            gs.append(ln.split()[1])
    print(f"{len(gs)} residue graphs to settle exactly", flush=True)
    gaps = []
    for i, s in enumerate(gs):
        v = settle(s)
        if v[0] == "GAP":
            gaps.append(v)
            print("EXACT GAP", v, flush=True)
        if (i + 1) % 200 == 0:
            print(f"   ... {i+1}/{len(gs)} done, gaps so far {len(gaps)}", flush=True)
    print(f"RESULT: {len(gs)} residue graphs settled exactly; "
          f"integrality-gap witnesses found = {len(gaps)}")
    for g in gaps:
        print("   ", g)


if __name__ == "__main__":
    main()
