"""A7: the N=14 extremal graph M?AE@bH{AYN_LgBs? -- every claim in Q5.md sec 2,
recomputed independently and exactly.

Claims audited:
  bip = 7                                        (own exhaustive cut enumeration)
  z == 1/5 feasible for Q(G)                     (own odd-cycle enumeration)
  z == 1/5 is a VERTEX of Q(G): 92 tight 5-cycles, incidence rank 32 = |E|
  tau* = 32/5, gap 3/5                           (own exact LP, two-sided certificate)
"""
from fractions import Fraction as F
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import (g6, E_of, tri_free, bip, all_cycles, tau_star_exact,
                          NAMED_G6, _solve_ls)

FAIL = []


def chk(name, got, want):
    good = (got == want)
    if not good:
        FAIL.append((name, got, want))
    print(f"  {'OK  ' if good else 'FAIL'} {name}: got {got}  want {want}")


n, A = g6(NAMED_G6["N14"])
E = E_of(n, A)
print(f"N={n} |E|={len(E)} triangle-free={tri_free(n, A)}")
chk("N", n, 14)
chk("|E|", len(E), 32)
chk("triangle-free", tri_free(n, A), True)

b, S = bip(n, A)
chk("bip (exhaustive 2^13 cuts)", b, 7)

C = all_cycles(n, A, only_odd=True)
lens = {}
for c in C:
    lens[len(c)] = lens.get(len(c), 0) + 1
print("  odd cycle length spectrum:", dict(sorted(lens.items())))
chk("number of 5-cycles", lens.get(5, 0), 92)
chk("odd girth", min(lens), 5)

# z == 1/5 feasible and its value
z = {e: F(1, 5) for e in E}
minodd = min(sum(z[e] for e in c) for c in C)
chk("min odd-cycle z-length at z=1/5", minodd, F(1))
chk("value of z=1/5", sum(z.values()), F(32, 5))

# vertex test: rank of the tight (= 5-cycle) incidence matrix over Q
tight = [c for c in C if sum(z[e] for e in c) == 1]
chk("number of tight constraints", len(tight), 92)
ei = {e: i for i, e in enumerate(E)}
rows = [[F(1) if E[i] in set(c) else F(0) for i in range(len(E))] for c in tight]
# exact Gaussian elimination -> rank


def rank(rows, ncol):
    M = [r[:] for r in rows]
    r = 0
    for c in range(ncol):
        p = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(ncol)]
        r += 1
        if r == len(M):
            break
    return r


rk = rank(rows, len(E))
chk("exact rank of the 92 tight 5-cycles", rk, 32)
print("  => z=1/5 has 32 = |E| linearly independent tight constraints and z_e = 1/5 > 0"
      " for every e, so it is a VERTEX of Q(G).")

# tau* two-sided
val, zz, pack, Call = tau_star_exact(n, A, verbose=True)
chk("tau*", val, F(32, 5))
chk("gap bip - tau*", b - val, F(3, 5))
print(f"  packing uses {len(pack)} cycles, weights {sorted(set(str(w) for _, w in pack))}")
load = {e: F(0) for e in E}
for cyc, w in pack:
    for e in cyc:
        load[e] += w
chk("packing feasible (all loads <= 1)", all(load[e] <= 1 for e in E), True)
chk("packing value == tau*", sum(w for _, w in pack), val)
mo = min(sum(zz[e] for e in c) for c in Call)
chk("cover feasible (min odd-cycle length >= 1)", mo >= 1, True)
chk("cover value == tau*", sum(zz.values()), val)

# uniform-x quantities of section 3.5
x = [F(1, n)] * n
e_ = sum(x[u] * x[v] for (u, v) in E)
chk("e (uniform)", e_, F(8, 49))
chk("Lambda (uniform) = tau*/N^2", val / (n * n), F(8, 245))
chk("psi (uniform) = bip/N^2", F(b, n * n), F(1, 28))
chk("psi > Lambda here", F(b, n * n) > val / (n * n), True)
chk("psi <= e - 4e^2", F(b, n * n) <= e_ - 4 * e_ * e_, True)
chk("psi <= 1/25", F(b, n * n) <= F(1, 25), True)

print("\nFAILURES:", len(FAIL))
for f in FAIL:
    print("   ", f)
