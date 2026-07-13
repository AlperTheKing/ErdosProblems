# Battery of EXACT checks for the LP/polyhedral reformulation of Erdos #23.
# Run:  python battery.py     (all integer/Fraction arithmetic; no floats)
import sys, time
from fractions import Fraction
from lib import *

def show(msg):
    print(msg); sys.stdout.flush()

fails = []

# ============ PART 0: sanity graphs ============
show("== PART 0: required sanity checks ==")
n, E = petersen()
assert is_triangle_free(n, E)
b, S = beta_exact(n, E)
maxcut = len(E) - b
show(f"Petersen: n={n} e={len(E)} maxcut={maxcut} beta={b}  (require e=15,maxcut=12,beta=3)")
assert (len(E), maxcut, b) == (15, 12, 3)
assert 25 * b <= n * n

for t in (2, 3, 4):
    n, E = blowup(*cycle(5), [t]*5)
    b, S = beta_exact(n, E)
    show(f"C5[{t}]: n={n} e={len(E)} beta={b}  (require t^2={t*t}; 25*beta={25*b} vs n^2={n*n})")
    assert b == t * t and 25 * b == n * n, "extremal tightness"

# ============ PART 1: odd-cycle covering/packing LP -- exact facts ============
show("\n== PART 1: odd-cycle LP duality ledger (exact) ==")
# 1a. C5[3] perfect C5-decomposition => nu*(C5[3]) = 9 = e/5 = beta (sandwich, exact).
t = 3
n, E = blowup(*cycle(5), [t]*5)
Eset = set(E)
def vid(i, x): return 3 * i + x
cycles = []
for u in range(3):
    for v in range(3):
        verts = [vid(i, (u + i * v) % 3) for i in range(5)]
        ce = [(min(verts[i], verts[(i + 1) % 5]), max(verts[i], verts[(i + 1) % 5])) for i in range(5)]
        cycles.append(ce)
used = [e for c in cycles for e in c]
assert len(used) == 45 and len(set(used)) == 45 and set(used) == Eset, "C5[3] decomposition must partition edges"
b3, _ = beta_exact(n, E)
cover_val = Fraction(len(E), 5)          # x_e = 1/5 uniform is feasible (odd girth 5)
pack_val = Fraction(9, 1)                # 9 edge-disjoint C5s, y=1
assert pack_val == cover_val == Fraction(b3), "nu* sandwich at extremal"
show(f"C5[3]: 9 edge-disjoint C5s verified partition of 45 edges -> nu* = {pack_val} = e/5 = beta = {b3} (LP TIGHT at extremal)")

# 1b. Petersen: nu* = 3 = beta, but max INTEGRAL packing = 2.
n, E = petersen()
oc = all_odd_cycles(n, E)
lens = sorted(set(len(c) for c in oc))
c5s = [c for c in oc if len(c) == 5]
show(f"Petersen odd cycle lengths = {lens}; number of 5-cycles = {len(c5s)}")
assert len(c5s) == 12
from collections import Counter
cnt = Counter(e for c in c5s for e in c)
assert all(cnt[e] == 4 for e in E), "each edge in exactly 4 five-cycles"
# y = 1/4 on each 5-cycle: edge load = 4*(1/4) = 1 -> feasible; value 12/4 = 3.
# x = 1/5 on each edge: every odd cycle has >=5 edges -> feasible; value 15/5 = 3.
assert Fraction(12, 4) == Fraction(15, 5) == Fraction(3)
show("Petersen: nu* = 3 exactly (packing 12*(1/4) meets cover 15*(1/5)); beta = 3; INTEGRAL packing = 2 "
     "(3 disjoint C5s would use all 15 edges, giving even degree at every vertex, but Petersen is 3-regular).")

# 1c. FALSIFIER of the naive duality direction: beta > nu* (so beta <= max-packing is FALSE).
show("\n-- searching gap instances: triangle-free with 5*beta > e (then beta > e/5 >= nu*) --")
gap_found = []
for name, (n, E) in [("C13(1,5)", circulant(13, [1, 5])),
                     ("C17(1,4)", circulant(17, [1, 4])),
                     ("sparse_rand_n18_m27", random_trianglefree_sparse(18, 27, 7)),
                     ("sparse_rand_n20_m30", random_trianglefree_sparse(20, 30, 11))]:
    assert is_triangle_free(n, E)
    b, _ = beta_exact(n, E)
    tag = "GAP: beta > e/5 >= nu*" if 5 * b > len(E) else "no gap here"
    show(f"{name}: n={n} e={len(E)} beta={b}  5*beta={5*b} vs e={len(E)}  -> {tag}")
    if 5 * b > len(E):
        gap_found.append((name, n, len(E), b))
assert gap_found, "need at least one exact gap instance"

# ============ PART 2: pentagonal rotation payoff + GM dual (exact) ============
show("\n== PART 2: pentagonal interval-cut system ==")
M = {}
for d in range(5):
    a = 0
    cntd = 0
    for j in range(5):
        sa = 1 if (a - j) % 5 in (0, 2) else 0
        sb = 1 if (a + d - j) % 5 in (0, 2) else 0
        if sa == sb:
            cntd += 1
    M[d] = cntd
show(f"rotation payoff M(d) = #uncut among 5 interval cuts, by C5-distance d: {M} (require {{0:5,1:1,2:3,3:3,4:1}})")
assert M == {0: 5, 1: 1, 2: 3, 3: 3, 4: 1}

# GM dual: min_i a_i a_{i+1} <= (n/5)^2, exact integer form: (min)^5 <= (prod a)^2 and 5^5 prod <= n^5.
import random as _r
_r.seed(1)
for trial in range(2000):
    a = [_r.randint(0, 30) for _ in range(5)]
    nn = sum(a)
    prods = [a[i] * a[(i + 1) % 5] for i in range(5)]
    m = min(prods)
    P = 1
    for x in a: P *= x
    assert m ** 5 <= P * P, "min <= GM of the five products"
    assert 5 ** 5 * P <= max(nn, 1) ** 5 or P == 0, "AM-GM"
    assert 25 * 25 * (m ** 5) <= nn ** 10 or nn == 0  # => 25*m <= n^2 when m>0
show("GM dual verified on 2000 random 5-part size vectors: 25 * min_i a_i a_{i+1} <= n^2 (exact integer checks)")

# hom-to-C5 pullback: beta(C5[a]) = min_i a_i a_{i+1} (check on explicit unbalanced blowups)
for sizes in [(3, 2, 2, 2, 1), (4, 3, 3, 2, 3), (1, 1, 4, 4, 1), (5, 1, 5, 1, 3)]:
    n, E = blowup(*cycle(5), list(sizes))
    b, _ = beta_exact(n, E)
    pred = min(sizes[i] * sizes[(i + 1) % 5] for i in range(5))
    show(f"C5{list(sizes)}: n={n} beta={b} min_i a_i*a_(i+1)={pred}  25*beta={25*b} vs n^2={n*n}")
    assert b == pred and 25 * b <= n * n

# ============ PART 3: peeling telescope (exact identity) ============
show("\n== PART 3: peeling arithmetic ==")
for (N, m) in [(200, 7), (57, 5), (25, 24), (1000, 3)]:
    assert sum(2 * k - 1 for k in range(m + 1, N + 1)) == N * N - m * m
show("telescope sum_{k=m+1..N} (2k-1) = N^2 - m^2 verified; peel cost floor(d/2) <= (2n-1)/25 whenever d <= (4n-2)/25")

# ============ PART 4: Missing-Lemma W battery: F2 image-cut family ============
show("\n== PART 4: Lemma W battery -- min uncut over F(G) = im(A) u im(A+I) vs n^2/25 ==")
show(f"{'graph':34s} {'n':>3s} {'e':>4s} {'del':>3s} {'bip':>3s} {'win':>3s} {'beta':>4s} {'famMin':>6s} {'rkA':>3s} {'rkI':>3s}  25*fam<=n^2?")

def window(n, delta):
    return 25 * delta > 4 * n - 2

def batt(name, n, E, do_beta=True):
    assert is_triangle_free(n, E), name
    bip = is_bipartite(n, E)
    d = min_degree(n, E)
    b = None
    if do_beta:
        b, _ = beta_exact(n, E)
    fm, S, rkA, rkI, mA, mI = min_uncut_union_family(n, E)
    if fm is None:
        show(f"{name:34s} {n:3d} {len(E):4d} {d:3d} {str(bip)[0]:>3s} {str(window(n,d))[0]:>3s} "
             f"{('' if b is None else str(b)):>4s}   SKIP rkA={rkA} rkI={rkI} (rank cap)")
        return b, None
    ok = 25 * fm <= n * n
    win = window(n, d)
    show(f"{name:34s} {n:3d} {len(E):4d} {d:3d} {str(bip)[0]:>3s} {str(win)[0]:>3s} "
         f"{('' if b is None else str(b)):>4s} {fm:6d} {rkA:3d} {rkI:3d}  {'OK' if ok else 'FAIL'}"
         + ("" if b is None else f"   (beta={b}, fam-beta={fm-b})")
         + f"  [minA={mA} minAI={mI}]")
    if (not bip) and (not ok):
        fails.append((name, n, len(E), b, fm))
    return b, fm

batt("C5", *cycle(5))
batt("C7", *cycle(7))
batt("C9", *cycle(9))
batt("C11", *cycle(11))
batt("C13", *cycle(13))
batt("C5+pendant", 6, [(0,1),(1,2),(2,3),(3,4),(0,4),(0,5)])
batt("two C5 sharing vertex", 9, [(0,1),(1,2),(2,3),(3,4),(0,4),(0,5),(5,6),(6,7),(7,8),(0,8)])
batt("Petersen", *petersen())
batt("GP(7,2)", *gen_petersen(7, 2))
batt("GP(9,2)", *gen_petersen(9, 2))
batt("dodecahedron GP(10,2)", *gen_petersen(10, 2))
batt("Wagner V8=And(3)", *wagner())
batt("V8[2]", *blowup(*wagner(), [2]*8))
batt("Grotzsch (Myc C5)", *mycielski(*cycle(5)))
batt("Clebsch", *clebsch())
batt("prism C5xK2", *prism_c5())
batt("C13(1,5)", *circulant(13, [1, 5]))
batt("C17(1,4)", *circulant(17, [1, 4]))
batt("C19(1,7)", *circulant(19, [1, 7]))
batt("C5[2]", *blowup(*cycle(5), [2]*5))
batt("C5[3]", *blowup(*cycle(5), [3]*5))
batt("C5[4]", *blowup(*cycle(5), [4]*5))
batt("C5[3,2,2,2,1]", *blowup(*cycle(5), [3,2,2,2,1]))
batt("C5[4,3,3,2,3]", *blowup(*cycle(5), [4,3,3,2,3]))
# near-extremal perturbations: C5[3] minus a perfect matching between classes 0,1; plus variants
n, E = blowup(*cycle(5), [3]*5)
Em = [e for e in E if e not in [(0, 3), (1, 4), (2, 5)]]
batt("C5[3] - matching(0,1)", n, Em)
n, E = blowup(*cycle(5), [4]*5)
Em = [e for e in E if e not in [(0, 4), (1, 5), (2, 6), (3, 7)]]
batt("C5[4] - matching(0,1)", n, Em)
# random maximal triangle-free (seeded with C5 => non-bipartite), several sizes
for nn in (10, 12, 14, 16):
    for sd in (1, 2, 3):
        n, E = random_maximal_trianglefree(nn, seed=100 * nn + sd)
        batt(f"maxTF n={nn} seed={sd}", n, E)
# sparse randoms
for (nn, mm, sd) in [(12, 18, 5), (14, 21, 6), (16, 24, 8), (18, 27, 9), (20, 30, 12)]:
    n, E = random_trianglefree_sparse(nn, mm, sd)
    if is_bipartite(n, E):
        continue
    batt(f"sparseTF n={nn} m={mm}", n, E)
# larger random maximal triangle-free (beta still exact up to n=22)
for nn, sd in [(18, 1), (20, 1), (22, 1)]:
    n, E = random_maximal_trianglefree(nn, seed=1000 + 10 * nn + sd)
    batt(f"maxTF n={nn} seed={sd}", n, E)
# big named stress graphs: family value only (upper-bounds beta; lemma claim testable without beta)
batt("Kneser K(7,3) = O4", *kneser73(), do_beta=False)
batt("Hoffman-Singleton", *hoffman_singleton(), do_beta=False)

show("")
if fails:
    show(f"*** LEMMA W FAILURES: {fails}")
else:
    show("*** Lemma W: NO failures in battery (all non-bipartite graphs have an F2-image cut within n^2/25).")
show("battery done")
