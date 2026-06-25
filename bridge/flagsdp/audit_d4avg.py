#!/usr/bin/env python3
"""D4 SKEPTIC part 4: the CHAIN (e) AVERAGING IDENTITY.
The whole closure hinges on:  for any larger graph H_n (n>9),
   g_r(H_n) = E_{S subset, |S|=9}[ g_r(H_n[S]) ].
If g_r is a linear combination of order-<=9 flag densities (as claimed), this MUST hold
EXACTLY for every g_r. I test it on random triangle-free graphs at n=10,11 for the 8 active
deficit atoms. A single exact mismatch REFUTES chain (e). Uses MY independent gr_exact via fx.
"""
import itertools, pickle, random
from fractions import Fraction as F
import flag_engine as fe
import flag_exact as fx

T = F(2, 25)

def load_pmap(prov, idx):
    pr = prov[idx]
    if pr[0] == "deficit":
        _, k, A, cls, p = pr
        return k, A, {cls[i]: F(int(p[i])) for i in range(len(cls))}
    _, k, A, pmap = pr
    return k, A, pmap

def induced_state(n, A, S):
    """Induced subgraph on sorted vertex list S, returned as (m, Asub) bitmask form."""
    S = sorted(S); m = len(S)
    pos = {v: i for i, v in enumerate(S)}
    Asub = [0]*m
    for ai, a in enumerate(S):
        for bi, b in enumerate(S):
            if ai != bi and (A[a] >> b) & 1:
                Asub[ai] |= (1 << bi)
    return (m, Asub)

def main():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    prov = d['prov']; ndix = d['ndix']; lam = [F(s) for s in d['lam']]
    active = [ndix[c] for c in range(len(ndix)) if lam[c] != 0]
    print("active deficit atoms:", active)

    random.seed(7)
    total_tests = 0; mism = 0; worst = None
    for n in (10, 11):
        pool = fe.enumerate_graphs(n, triangle_free=True)
        # sample some graphs (n=10,11 triangle-free counts are large; sample)
        sample = random.sample(pool, min(25, len(pool)))
        for (nn, A) in sample:
            # all 9-subsets
            subs = list(itertools.combinations(range(nn), 9))
            substates = [induced_state(nn, A, S) for S in subs]
            for atom in active:
                k, As, pmap = load_pmap(prov, atom)
                gfull = fx.gr_exact([(nn, A)], k, As, pmap, T)[0]
                gsubs = fx.gr_exact(substates, k, As, pmap, T)
                avg = sum(gsubs) / len(gsubs)
                total_tests += 1
                if avg != gfull:
                    mism += 1
                    diff = abs(float(avg - gfull))
                    if worst is None or diff > worst:
                        worst = diff
                        print(f"  MISMATCH n={nn} atom={atom}: g_full={float(gfull)} avg9={float(avg)} diff={diff}")
    print(f"averaging-identity tests: {total_tests}, mismatches: {mism}")
    if mism == 0:
        print("  PASS: g_r(H_n) == E_{9-subset}[g_r(H_n[S])] EXACTLY -> chain (e) averaging valid for g_r")
    else:
        print("  REFUTED: g_r is NOT a pure order-<=9 flag-density combination; chain (e) averaging INVALID")

if __name__ == "__main__":
    main()
