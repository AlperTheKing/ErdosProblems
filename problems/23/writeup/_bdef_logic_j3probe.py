"""TARGETED J3 probe: does the 'proper => dB>0' link ever get EXERCISED with O nonempty?
Find census configs with O!=empty AND a proper full-K-component disjoint from O (a 'Q-only component'),
and for each verify dB>0 (so the contradiction in the chain would fire). Also confirm the converse claim
that whenever O!=empty, EVERY full-K-comp disjoint from O is proper (never =V). Exact Fraction.

Also dump, for the few extremal C=V critical components (O empty), that they are exactly T===N (Gamma=N^2),
confirming the only 'critical' components are the uniform-load extremals where the chain is NOT invoked.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_logic import build_K, full_components


def probe(Nmax, Nmin=5, stride=1):
    n_qonly_withO = 0           # proper full-K-comp disjoint from O, with O nonempty
    n_qonly_withO_dB0 = 0       # ... and dB==0  (would be the GAP)
    n_compV_critical = 0        # full comp = V that is critical (T===N), O must be empty
    n_compV_critical_Ononempty = 0  # GAP: C=V critical but O nonempty (impossible)
    examples_qonly = []
    examples_critV = []
    for nn in range(Nmin, Nmax + 1):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()[::stride]
        for g6 in outg:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            K, T, n = build_K(info)
            N = n
            O = set(v for v in range(n) if T[v] > N)
            Bset = info['Bset']
            comps = full_components(K, n)
            for C in comps:
                Cs = set(C)
                if Cs & O:
                    continue  # not disjoint from O
                isV = (len(C) == n)
                allTN = all(T[v] == N for v in C)
                dB = sum(1 for (a, b) in Bset if (a in Cs) ^ (b in Cs))
                if O and not isV:
                    n_qonly_withO += 1
                    if dB == 0:
                        n_qonly_withO_dB0 += 1
                        if len(examples_qonly) < 5:
                            examples_qonly.append((g6, tuple(C), dB, sorted(O)))
                    elif len(examples_qonly) < 5:
                        examples_qonly.append((g6, tuple(C), dB, sorted(O)))  # record a normal one too
                if isV and allTN:
                    n_compV_critical += 1
                    if O:
                        n_compV_critical_Ononempty += 1
                    if len(examples_critV) < 5:
                        examples_critV.append((g6, n, float(sum(T)), len(O)))
    print(f"N={Nmin}..{Nmax} stride{stride}:")
    print(f"  Q-only comps (proper full-K-comp disjoint from O, O NONEMPTY): {n_qonly_withO}")
    print(f"    of those with dB==0 (THE J3 GAP): {n_qonly_withO_dB0}   <-- must be 0")
    print(f"  C=V critical (T===N) comps: {n_compV_critical}; of those with O nonempty (IMPOSSIBLE): {n_compV_critical_Ononempty}  <-- must be 0")
    print(f"  example Q-only-with-O (g6,C,dB,O): {examples_qonly}")
    print(f"  example C=V-critical (g6,n,sumT,|O|): {examples_critV}")


if __name__ == "__main__":
    print("=== TARGETED J3 PROBE (does proper=>dB>0 ever get exercised w/ O nonempty?) ===")
    probe(11, 5, 1)
