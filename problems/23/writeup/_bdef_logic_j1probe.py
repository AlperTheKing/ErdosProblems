"""TARGETED J1 probe: the lever claims a LEAK-FREE K_QQ-component is K-closed in V (hence equals a full
K-component, so the boundary-deficit lemma APPLIES to it). Exercise this: enumerate leak-free K_QQ-comps
over the census (O nonempty), and exact-check K-closedness for EACH. Report count + any violation.
Distinguish leak-free-but-not-saturated (still must be K-closed) from critical (leak-free+saturated)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_logic import build_K, qq_components, full_components


def probe(Nmax, Nmin=5, stride=1):
    n_leakfree = 0           # leak-free K_QQ-comps with O nonempty
    n_leakfree_notKclosed = 0  # J1 GAP
    n_leakfree_notsat = 0    # leak-free but not saturated (deficit>0); still must be K-closed
    n_leakfree_eqfull = 0    # leak-free comp that equals some full K-comp
    examples = []
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
            if not O:
                continue  # only the O-nonempty regime where the chain is invoked
            Q = set(v for v in range(n) if T[v] <= N)
            fullset = set(tuple(c) for c in full_components(K, n))
            for C in qq_components(K, n, Q):
                Cs = set(C)
                leakfree = all(sum(K[v][o] for o in O) == 0 for v in C)
                if not leakfree:
                    continue
                n_leakfree += 1
                sat = all(T[v] == N for v in C)
                if not sat:
                    n_leakfree_notsat += 1
                kclosed = all(K[v][w] == 0 for v in C for w in range(n) if w not in Cs)
                eqfull = tuple(sorted(C)) in fullset
                if eqfull:
                    n_leakfree_eqfull += 1
                if not kclosed:
                    n_leakfree_notKclosed += 1
                    if len(examples) < 8:
                        examples.append(('J1GAP', g6, tuple(C), sorted(O)))
                elif len(examples) < 8:
                    examples.append(('ok', g6, tuple(C), 'sat' if sat else 'unsat', 'eqfull' if eqfull else 'NOTfull'))
    print(f"N={Nmin}..{Nmax} (O nonempty only):")
    print(f"  leak-free K_QQ-comps: {n_leakfree}")
    print(f"    not-saturated (deficit>0) among them: {n_leakfree_notsat}")
    print(f"    that EQUAL a full K-comp (K-closed witness): {n_leakfree_eqfull}")
    print(f"    NOT K-closed (J1 GAP): {n_leakfree_notKclosed}   <-- must be 0")
    print(f"  examples: {examples}")


if __name__ == "__main__":
    print("=== TARGETED J1 PROBE (leak-free K_QQ-comp => K-closed => full K-comp) ===")
    probe(11, 5, 1)
