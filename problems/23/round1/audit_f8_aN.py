"""Independent recomputation of a(N)=max bip over triangle-free N-vertex graphs,
via the pattern reduction (Method A), in exact integer arithmetic.
Also verifies the claimed extremal witnesses and the top-table entries."""
import glob, os, sys
from fractions import Fraction
from itertools import combinations
from audit_f8_lib import g6dec, g6enc, mono_masks, psi_int, bip_exact, edges, cayleyZ, blowup, trifree

D = os.path.dirname(os.path.abspath(__file__))
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 15

PAT = {}
for fn in glob.glob(os.path.join(D, 'f8_rmtf_*.g6')):
    k = int(fn.rsplit('_', 1)[1].split('.')[0])
    if k > NMAX:
        continue
    for l in open(fn):
        l = l.strip()
        if not l:
            continue
        n, adj = g6dec(l)
        E, mn = mono_masks(n, adj)
        PAT.setdefault(n, []).append((l, E, mn))
# K_2 (the only other reduced pattern, bipartite -> Psi=0) is irrelevant to a max.
print("patterns:", {k: len(v) for k, v in sorted(PAT.items())})


def comps(N, k):
    for cut in combinations(range(1, N), k - 1):
        prev, out = 0, []
        for c in cut:
            out.append(c - prev)
            prev = c
        out.append(N - prev)
        yield out


print(f"{'N':>3} {'a(N)':>5} {'floor(N^2/25)':>14} {'a(N)/N^2':>10}   witness")
res = {}
for N in range(5, NMAX + 1):
    best, wit = 0, None
    for k, pats in sorted(PAT.items()):
        if k > N:
            continue
        for (g6, E, mn) in pats:
            for a in comps(N, k):
                v = psi_int(E, mn, a)
                if v > best:
                    best, wit = v, (g6, tuple(a))
    res[N] = best
    print(f"{N:>3} {best:>5} {N*N//25:>14} {str(Fraction(best,N*N)):>10}   {wit}")
print("a(5..15) =", [res[N] for N in range(5, NMAX + 1)])

# --- direct check of the claimed N=14 witness: C13(1,5) with one part doubled
n13, a13 = cayleyZ(13, [1, 5])
assert trifree(n13, a13)
b13, m13 = bip_exact(n13, a13)
print(f"\nC13(1,5): n=13 m={m13} bip={b13}  ratio={Fraction(b13,169)}")
E13, M13 = mono_masks(n13, a13)
best14 = 0
for i in range(13):
    a = [1] * 13
    a[i] = 2
    v = psi_int(E13, M13, a)
    best14 = max(best14, v)
print(f"C13(1,5) with one part doubled (N=14): Psi={best14}  ratio={Fraction(best14,196)}")
g14 = blowup(n13, a13, [2 if i == 0 else 1 for i in range(13)])
print("  direct bip of that 14-vertex blow-up:", bip_exact(*g14), " g6:", g6enc(*g14))
print("  deficit 1/25-1/28 =", Fraction(1, 25) - Fraction(1, 28))
print("  deficit 1/25-6/169 =", Fraction(1, 25) - Fraction(6, 169))
print("  deficit 1/25-7/200 =", Fraction(1, 25) - Fraction(7, 200))
