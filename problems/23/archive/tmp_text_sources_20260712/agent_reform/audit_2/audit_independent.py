# ADVERSARIAL AUDIT (independent recompute) of the GW-uncut-energy report.
# Zero code shared with tmp/agent_reform/gw_geometric/*: different maxcut algorithm
# (popcount over adjacency bitmasks), independent graph constructions, hom search with
# different vertex order + full counting, plus TWO STRENGTHENINGS:
#   (S-A) assert non-C5-hom (author's script printed but never asserted it),
#   (S-B) exact-rational UNIQUENESS certificate for the Petersen maxcut-SDP optimum
#         (report says "the SDP-optimal embedding" -- uniqueness was unproved).
# All load-bearing arithmetic: int / Fraction. Floats appear nowhere.
from fractions import Fraction as F
from itertools import combinations, product
import sys

FAILS = []
def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name} {detail}")
    if not cond:
        FAILS.append(name)

# ---------------- independent maxcut (popcount over adjacency masks) ----------------
def maxcut_fast(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    best = 0
    for m in range(1 << (n - 1)):          # vertex n-1 fixed on side 0
        comp = full & ~m
        c = 0
        mm = m
        while mm:
            b = mm & -mm
            v = b.bit_length() - 1
            c += bin(adj[v] & comp).count("1")
            mm ^= b
        if c > best:
            best = c
    return best

def beta(n, edges):
    return len(edges) - maxcut_fast(n, edges)

def triangle_free(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return all((adj[u] & adj[v]) == 0 for u, v in edges)

def degrees(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d

# ---------------- independent constructions ----------------
def circulant(n, conns):
    E = set()
    for v in range(n):
        for c in conns:
            E.add((min(v, (v + c) % n), max(v, (v + c) % n)))
    return n, sorted(E)

def petersen():  # Kneser(5,2)
    vs = list(combinations(range(5), 2))
    ix = {s: i for i, s in enumerate(vs)}
    E = [(ix[a], ix[b]) for a, b in combinations(vs, 2) if not (set(a) & set(b))]
    return 10, E, vs

def grotzsch():  # explicit Mycielski of C5: u0..u4, w0..w4, z
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))                    # cycle u
        E.append((5 + i, (i + 1) % 5))                # w_i ~ u_{i+1}
        E.append((5 + i, (i - 1) % 5))                # w_i ~ u_{i-1}
        E.append((10, 5 + i))                         # z ~ w_i
    return 11, sorted(set((min(a, b), max(a, b)) for a, b in E))

def mu3_c5():  # generalized Mycielskian, 3 levels + apex, n=16
    def vid(l, i): return 5 * l + i
    E = set()
    for i in range(5):
        E.add((min(vid(0, i), vid(0, (i + 1) % 5)), max(vid(0, i), vid(0, (i + 1) % 5))))
    for l in (1, 2):
        for i in range(5):
            for d in (1, -1):
                a, b = vid(l, i), vid(l - 1, (i + d) % 5)
                E.add((min(a, b), max(a, b)))
    for i in range(5):
        E.add((min(15, vid(2, i)), max(15, vid(2, i))))
    return 16, sorted(E)

def blowup(n, edges, t):  # balanced blow-up H[t]
    N = n * t
    E = []
    for u, v in edges:
        for a in range(t):
            for b in range(t):
                E.append((u * t + a, v * t + b))
    return N, E

def c5_blowup_sizes(sizes):
    offs, s = [], 0
    for x in sizes:
        offs.append(s)
        s += x
    E = []
    for k in range(5):
        k2 = (k + 1) % 5
        for i in range(sizes[k]):
            for j in range(sizes[k2]):
                E.append((offs[k] + i, offs[k2] + j))
    return s, E

# ---------------- hom-to-C5: BFS-order backtracking, COUNTS all homs ----------------
def count_homs_C5(n, edges, cap=10**9):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    # BFS order (different from author's degree order)
    order, seen = [], [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        queue = [s]
        while queue:
            x = queue.pop(0)
            order.append(x)
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    queue.append(y)
    pos = [-1] * n
    cnt = 0
    def bt(i):
        nonlocal cnt
        if cnt >= cap:
            return
        if i == n:
            cnt += 1
            return
        v = order[i]
        for c in range(5):
            good = True
            for w in adj[v]:
                if pos[w] >= 0 and (c - pos[w]) % 5 not in (1, 4):
                    good = False
                    break
            if good:
                pos[v] = c
                bt(i + 1)
                pos[v] = -1
    bt(0)
    return cnt

# ---------------- exact rational linear algebra ----------------
def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]

def mat_rank_det_fraction(M):
    A = [[F(x) for x in row] for row in M]
    n = len(A)
    det = F(1)
    rank = 0
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            det = F(0)
            continue
        if piv != r:
            A[r], A[piv] = A[piv], A[r]
            det = -det
        det *= A[r][c]
        inv = 1 / A[r][c]
        A[r] = [x * inv for x in A[r]]
        for i in range(n):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        rank += 1
        r += 1
    if rank < n:
        det = F(0)
    return rank, det

print("=" * 78)
print("BLOCK 1: scan candidates -- independent beta, triangle-free, WINDOW, non-C5-hom")
print("=" * 78)
nP, EP, _ = petersen()
cands = [
    ("Petersen",            nP, EP,                          3, F(3, 4)),
    ("And(3)=C8(1,4)",      *circulant(8,  (1, 4)),          2, F(25, 32)),
    ("And(4)=C11(1,4)",     *circulant(11, (1, 4)),          4, F(100, 121)),
    ("And(5)=C14(1,4,7)",   *circulant(14, (1, 4, 7)),       6, F(75, 98)),
    ("And(6)=C17(1,4,7)",   *circulant(17, (1, 4, 7)),       9, F(225, 289)),
    ("Groetzsch",           *grotzsch(),                     4, F(100, 121)),
    ("mu_3(C5)",            *mu3_c5(),                       5, F(125, 256)),
]
for name, n, E, beta_claim, ratio_claim in cands:
    tf = triangle_free(n, E)
    b = beta(n, E)
    homs = count_homs_C5(n, E)
    degs = degrees(n, E)
    dmin = min(degs)
    ratio = F(25 * b, n * n)
    in_window = (25 * dmin > 4 * n) and (5 * dmin <= 2 * n)  # family form: >4N/25 strictly, <=2N/5
    check(f"{name}: triangle-free", tf)
    check(f"{name}: beta == {beta_claim}", b == beta_claim, f"(beta={b}, e={len(E)}, maxcut={len(E)-b})")
    check(f"{name}: 25*beta/N^2 == {ratio_claim}", ratio == ratio_claim, f"(={ratio})")
    check(f"{name}: NOT hom to C5 (0 homs, exhaustive count)", homs == 0, f"(homs={homs})")
    check(f"{name}: in min-degree window (25*dmin>4n, 5*dmin<=2n)", in_window, f"(dmin={dmin}, n={n})")
# hom-search positive controls
c5n, c5e = circulant(5, (1,))
check("control: #homs(C5->C5) == 10 (= automorphisms; C5 is a core)", count_homs_C5(*circulant(5, (1,))) == 10)
check("control: homs(C7->C5) > 0", count_homs_C5(*circulant(7, (1,))) > 0)
check("control: homs(K3->C5) == 0", count_homs_C5(3, [(0, 1), (1, 2), (0, 2)]) == 0)

print()
print("=" * 78)
print("BLOCK 2: T5 multilinearity -- FULL bipartition brute force (no twin reduction)")
print("=" * 78)
n5, E5 = circulant(5, (1,))
mc5 = maxcut_fast(n5, E5)
check("maxcut(C5) == 4", mc5 == 4)
for t in (2, 3):
    N, E = blowup(5, E5, t)
    mc = maxcut_fast(N, E)
    check(f"maxcut(C5[{t}]) == {t*t}*4 (full brute, 2^{N-1} cuts)", mc == t * t * 4, f"(={mc})")
    check(f"beta(C5[{t}]) == {t*t} == N^2/25 (TIGHT)", len(E) - mc == t * t)
nW, EW = circulant(8, (1, 4))
mcW = maxcut_fast(nW, EW)
NW2, EW2 = blowup(8, EW, 2)
mcW2 = maxcut_fast(NW2, EW2)
check("maxcut(And(3)) == 10", mcW == 10)
check("maxcut(And(3)[2]) == 40 == 4*maxcut(And(3)) (full brute 2^15)", mcW2 == 40, f"(={mcW2})")
NP2, EP2 = blowup(10, EP, 2)
mcP2 = maxcut_fast(NP2, EP2)
check("maxcut(Petersen[2]) == 48 == 4*12 (full brute 2^19, no twin argument)", mcP2 == 48, f"(={mcP2})")

print()
print("=" * 78)
print("BLOCK 3: Petersen spectral calibration -- polynomial certs + SDP UNIQUENESS")
print("=" * 78)
# p(x)=32x^5-40x^3+10x+1 ; q(x)=16x^4-8x^3-16x^2+8x+1 ; T5 Chebyshev identity, coefficientwise
pc = [1, 10, 0, -40, 0, 32]            # ascending coeffs of p
qc = [1, 8, -16, -8, 16]               # ascending coeffs of q
conv = [0] * 6
for i, a in enumerate([1, 2]):         # (2x+1) ascending: [1,2]
    for j, b in enumerate(qc):
        conv[i + j] += a * b
check("p == (2x+1)*q coefficientwise", conv == pc, f"(conv={conv})")
t5c = [0, 5, 0, -20, 0, 16]            # T5 ascending
check("p == 2*T5 + 1 coefficientwise (so p(cos a)=2cos(5a)+1)",
      [2 * c for c in t5c][0] + 1 == pc[0] and all(2 * t5c[i] == pc[i] for i in range(1, 6)))
def qval(x): return 16 * x**4 - 8 * x**3 - 16 * x**2 + 8 * x + 1
sign_table = [(F(-1), 1), (F(-9, 10), -1), (F(0), 1), (F(2, 3), 1), (F(7, 10), -1), (F(1), 1)]
ok = True
for x, s in sign_table:
    v = qval(x)
    ok &= (v > 0) if s > 0 else (v < 0)
check("q sign table -1:+, -9/10:-, 0:+, 2/3:+, 7/10:-, 1:+  => 4 roots bracketed,"
      " exactly one in (2/3,7/10)", ok)
check("q(2/3) == 1/81 exactly", qval(F(2, 3)) == F(1, 81))
check("q(7/10) == -89/625 exactly", qval(F(7, 10)) == F(-89, 625))
# roots of q are cos(2pi k/15), k in {1,2,4,7} (p(cos)=2cos(5a)+1=0 since 5a = 2pi k/3, k not= 0 mod 3;
# none equals -1/2 since k != 5). Positive ones: k=1,2; cos(4pi/15) is the SMALLER positive root
# => cos(4pi/15) in (2/3,7/10) => cos(4pi/15) > 2/3 => U_spec = 15(1-arccos(-2/3)/pi) > 4. [math steps]
print("   [math] root identification: {cos 2pi k/15 : k=1,2,4,7} = all 4 roots; smaller positive = cos(4pi/15)")

# ---- SDP uniqueness strengthening (exact over Q) ----
A = [[0] * 10 for _ in range(10)]
for u, v in EP:
    A[u][v] = A[u][v] = 1
    A[u][v] = 1
    A[v][u] = 1
I = [[1 if i == j else 0 for j in range(10)] for i in range(10)]
J = [[1] * 10 for _ in range(10)]
def madd(*Ms):
    return [[sum(M[i][j] for M in Ms) for j in range(10)] for i in range(10)]
def mscal(c, M):
    return [[c * M[i][j] for j in range(10)] for i in range(10)]
Am3 = madd(A, mscal(-3, I))
Am1 = madd(A, mscal(-1, I))
Ap2 = madd(A, mscal(2, I))
Z = matmul(matmul(Am3, Am1), Ap2)
check("(A-3I)(A-I)(A+2I) == 0  (spectrum subset of {3,1,-2})", all(all(x == 0 for x in r) for r in Z))
trA = sum(A[i][i] for i in range(10))
trA2 = sum(A[i][j] * A[j][i] for i in range(10) for j in range(10))
# multiplicities (a,b,c) of (3,1,-2): a+b+c=10, 3a+b-2c=0, 9a+b+4c=30 -> unique integer solution
sol = None
for a in range(11):
    for b in range(11 - a):
        c = 10 - a - b
        if 3 * a + b - 2 * c == trA and 9 * a + b + 4 * c == trA2:
            sol = (a, b, c)
check("multiplicities (3,1,-2) == (1,5,4) via trace system", sol == (1, 5, 4), f"(sol={sol}, trA={trA}, trA2={trA2})")
# spectral projections as rational polynomials in A: P1=(A-I)(A+2I)/10, P5=-(A-3I)(A+2I)/6, P4=(A-3I)(A-I)/15
P1 = [[F(x, 10) for x in row] for row in matmul(Am1, Ap2)]
P5 = [[F(-x, 6) for x in row] for row in matmul(Am3, Ap2)]
P4 = [[F(x, 15) for x in row] for row in matmul(Am3, Am1)]
def fr_matmul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(10)) for j in range(10)] for i in range(10)]
for nameP, P in (("P1", P1), ("P5", P5), ("P4", P4)):
    check(f"{nameP} idempotent (exact)", fr_matmul(P, P) == P)
S = [[5 * P1[i][j] + 3 * P5[i][j] for j in range(10)] for i in range(10)]
check("A+2I == 5*P1 + 3*P5 (PSD certificate: nonneg combo of projections)",
      all(S[i][j] == Ap2[i][j] for i in range(10) for j in range(10)))
# X* = I -(2/3)A + (1/6)(J-I-A): the canonical embedding Gram; verify X* == (5/2) P4 exactly
Xs = [[F(1) if i == j else (F(-2, 3) if A[i][j] == 1 else F(1, 6)) for j in range(10)] for i in range(10)]
check("X* == (5/2)*P4 exactly (PSD, rank 4, diag 1, range = E_{-2})",
      all(Xs[i][j] == F(5, 2) * P4[i][j] for i in range(10) for j in range(10)))
obj = sum(F(1) - Xs[u][v] for u, v in EP) / 2
check("SDP objective at X* == 25/2 (matches eigenvalue bound e/2*(1-lmin/d))", obj == F(25, 2))
# duality: for feasible X, obj = e/2 - <A,X>/4 and <A+2I, X> >= 0 => obj <= 25/2,
# equality => (A+2I)X = 0 => range(X) in E_{-2} => X = P4 M P4, diag constraints pin X uniquely iff
# Gram of {u_v u_v^T} (= entrywise SQUARE of X*) is nonsingular:
G = [[Xs[i][j] ** 2 for j in range(10)] for i in range(10)]
rk, det = mat_rank_det_fraction(G)
check("UNIQUENESS: rank(X*^{o2}) == 10 (det != 0) => SDP optimum is the UNIQUE X*",
      rk == 10 and det != 0, f"(rank={rk}, det={det})")

print()
print("=" * 78)
print("BLOCK 4: insertion-chain identities + embedding-level cross-checks")
print("=" * 78)
okA = all(5 * (3 * t * t + 2 * t * j) == (4 * t + j) ** 2 - (t - j) ** 2
          for t in range(1, 101) for j in range(0, t + 1))
check("25*U_pent(t,t,t,t,j) == (4t+j)^2 - (t-j)^2  for t<=100", okA)
okB = all(5 * ((j + 1) * (j + 1) + 2 * j * (j + 1) + 2 * j * j) == (5 * j + 2) ** 2 + 1
          for j in range(0, 201))
check("pentagram overdraft at (j+1,j+1,j,j,j): 25*U_pent - n^2 == 1  for j<=200", okB)
okC = all((5 * j + 2) ** 2 - 25 * j * j == 20 * j + 4 for j in range(0, 201))
check("cut-embedding slack at same prefix: n^2 - 25*j^2 == 20j+4", okC)
# embedding-level: theta/pi rational machinery, independent implementation
def theta_over_pi(a, b):
    d = abs(a - b) % 2
    return min(d, 2 - d)
def U_emb(edges, ang):
    return sum(1 - theta_over_pi(ang[u], ang[v]) for u, v in edges)
n7, E7 = c5_blowup_sizes((2, 2, 1, 1, 1))
sizes = (2, 2, 1, 1, 1)
cls = []
for k, s in enumerate(sizes):
    cls += [k] * s
angp = [F(4 * cls[v], 5) for v in range(n7)]
Up = U_emb(E7, angp)
check("pentagram U on C5[2,2,1,1,1] == 2 == (49+1)/25 (overdraft 1/25 live check)", Up == 2, f"(U={Up})")
b7 = beta(n7, E7)
check("beta(C5[2,2,1,1,1]) == 1 == cut-embedding value j^2 (brute)", b7 == 1, f"(beta={b7})")
# And(4) winding-4 embedding: U == 4 == beta (independent recompute of author's block (f))
n11, E11 = circulant(11, (1, 4))
angw = [F(8 * v, 11) % 2 for v in range(11)]
Uw = U_emb(E11, angw)
check("And(4) winding-4 circulant embedding: U == 4 == beta(And(4))", Uw == 4, f"(U={Uw})")
# T1 >= direction spot check: 60 random rational embeddings of Petersen, U >= beta = 3
import random
random.seed(1723)
okT1 = True
for _ in range(60):
    ang = [F(random.randrange(0, 7200), 3600) for _ in range(10)]
    if U_emb(EP, ang) < 3:
        okT1 = False
check("T1 lower bound: U(f) >= beta on 60 random exact embeddings of Petersen", okT1)

print()
print("=" * 78)
print("BLOCK 5: T4 cheap-vertex inequality on random triangle-free graphs (brute)")
print("=" * 78)
okT4 = True
for trial in range(25):
    N = random.randrange(6, 12)
    order = list(combinations(range(N), 2))
    random.shuffle(order)
    adjs = [set() for _ in range(N)]
    E = []
    for (u, v) in order:
        if not (adjs[u] & adjs[v]):
            adjs[u].add(v)
            adjs[v].add(u)
            E.append((u, v))
    d = degrees(N, E)
    v0 = min(range(N), key=lambda x: d[x])
    Em = [(a, b) for (a, b) in E if v0 not in (a, b)]
    relab = {x: i for i, x in enumerate([x for x in range(N) if x != v0])}
    Em = [(relab[a], relab[b]) for a, b in Em]
    bG = beta(N, E)
    bGm = beta(N - 1, Em)
    if not bG <= bGm + d[v0] // 2:
        okT4 = False
check("beta(G) <= beta(G-v) + floor(deg/2) on 25 random maximal tri-free graphs", okT4)

print()
print("=" * 78)
if FAILS:
    print(f"AUDIT RESULT: {len(FAILS)} FAILURES: {FAILS}")
    sys.exit(1)
print("AUDIT RESULT: ALL INDEPENDENT CHECKS PASSED")
