# INDEPENDENT audit of LP/W' report (Erdos #23). Exact integer arithmetic only.
# Sections: A exhaustive n=5,6,7 (independent gen) | B named-graph claims | C F2-degeneracy analysis.
import numpy as np, random, sys
from itertools import combinations

# ---------------- independent primitives ----------------
def edges_to_adj(n, edges):
    adj = [0]*n
    for u, v in edges:
        adj[u] |= 1 << v; adj[v] |= 1 << u
    return adj

def triangle_free(n, edges):
    adj = edges_to_adj(n, edges)
    return all((adj[u] & adj[v]) == 0 for u, v in edges)

def bipartite(n, edges):
    adj = edges_to_adj(n, edges); col = [-1]*n
    for s in range(n):
        if col[s] < 0:
            col[s] = 0; st = [s]
            while st:
                x = st.pop(); m = adj[x]
                while m:
                    b = m & -m; y = b.bit_length()-1; m ^= b
                    if col[y] < 0: col[y] = col[x]^1; st.append(y)
                    elif col[y] == col[x]: return False
    return True

def uncut(edges, S):
    return sum(1 for u, v in edges if ((S >> u) & 1) == ((S >> v) & 1))

def beta_py(n, edges):  # for small n, pure python
    best = len(edges)+1; arg = 0
    for S in range(1 << (n-1)):
        c = uncut(edges, S)
        if c < best: best = c; arg = S
    return best, arg

def beta_np(n, edges):  # exact, chunked numpy, vertex n-1 fixed side 0
    tot = 1 << (n-1); best = len(edges)+1; arg = 0
    CH = 1 << 20
    for st in range(0, tot, CH):
        S = np.arange(st, min(st+CH, tot), dtype=np.uint64)
        acc = np.zeros(S.shape, dtype=np.uint16)
        for u, v in edges:
            acc += (((S >> np.uint64(u)) & np.uint64(1)) == ((S >> np.uint64(v)) & np.uint64(1)))
        j = int(acc.argmin())
        if int(acc[j]) < best: best = int(acc[j]); arg = int(S[j])
    return best, arg

def f2_basis(rows):
    basis = {}
    for r in rows:
        x = r
        while x:
            h = x.bit_length()-1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; break
    return list(basis.values())

def span_list(basis):
    sp = [0]
    for b in basis:
        sp += [x ^ b for x in sp]
    return sp

def min_uncut_span_np(edges, basis):
    arr = np.zeros(1, dtype=np.uint64)
    for b in basis:
        arr = np.concatenate([arr, arr ^ np.uint64(b)])
    acc = np.zeros(arr.shape, dtype=np.uint16)
    for u, v in edges:
        acc += (((arr >> np.uint64(u)) & np.uint64(1)) == ((arr >> np.uint64(v)) & np.uint64(1)))
    j = int(acc.argmin())
    return int(acc[j]), int(arr[j])

def fam_info(n, edges, cap=24):
    """returns (famMin, rankA, rankAI, minA, minAI); None parts if rank>cap."""
    adj = edges_to_adj(n, edges)
    rowsA = adj
    rowsAI = [adj[u] ^ (1 << u) for u in range(n)]
    bA = f2_basis(rowsA); bI = f2_basis(rowsAI)
    mA = mI = None
    if len(bA) <= cap: mA, _ = min_uncut_span_np(edges, bA)
    if len(bI) <= cap: mI, _ = min_uncut_span_np(edges, bI)
    cands = [m for m in (mA, mI) if m is not None]
    return (min(cands) if cands else None), len(bA), len(bI), mA, mI

# constructors (independent where possible)
def cycle(k): return k, [(i, (i+1) % k) for i in range(k)]

def blowup(bn, bedges, sizes):
    offs = [0]
    for s in sizes: offs.append(offs[-1]+s)
    E = []
    for u, v in bedges:
        for a in range(offs[u], offs[u+1]):
            for b in range(offs[v], offs[v+1]):
                E.append((min(a, b), max(a, b)))
    return offs[-1], E

def petersen_kneser():  # STRUCTURALLY independent: 2-subsets of [5], adjacent iff disjoint
    vs = list(combinations(range(5), 2))
    idx = {v: i for i, v in enumerate(vs)}
    E = [(idx[a], idx[b]) for a in vs for b in vs if idx[a] < idx[b] and not set(a) & set(b)]
    return 10, E

def mycielski(n, edges):
    E = list(edges)
    for u, v in edges:
        E.append((min(u, n+v), max(u, n+v)))
        E.append((min(v, n+u), max(v, n+u)))
    E += [(n+i, 2*n) for i in range(n)]
    return 2*n+1, sorted(set(E))

def circulant(k, conn):
    ded = set()
    for i in range(k):
        for s in conn:
            ded.add((min(i, (i+s) % k), max(i, (i+s) % k)))
    return k, sorted(ded)

def clebsch():
    C = [1, 2, 4, 8, 15]; ded = set()
    for x in range(16):
        for c in C:
            y = x ^ c; ded.add((min(x, y), max(x, y)))
    return 16, sorted(ded)

def gen_petersen(k, step):
    E = [(i, (i+1) % k) for i in range(k)]
    E += [(k+i, k+(i+step) % k) for i in range(k)]
    E += [(i, k+i) for i in range(k)]
    return 2*k, sorted(set((min(u, v), max(u, v)) for u, v in E))

def parity_gram(n, edges):
    """(A^2 mod 2) as list of int bitmasks (row i = parities of |N(i) cap N(j)|)."""
    adj = edges_to_adj(n, edges)
    rows = []
    for i in range(n):
        r = 0
        for j in range(n):
            if bin(adj[i] & adj[j]).count('1') % 2: r |= 1 << j
        rows.append(r)
    return rows

OK = True
def req(cond, msg):
    global OK
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond: OK = False

# =============== SECTION B: named-graph claims ===============
print("== B: named graph claims (independent constructions) ==")
n, E = petersen_kneser()
req(triangle_free(n, E) and len(E) == 15, "Petersen(kneser form): n=10 e=15 triangle-free")
b, _ = beta_py(n, E)
req(b == 3, f"Petersen beta = 3 (got {b})")
fm, rA, rI, mA, mI = fam_info(n, E)
req(mA == 6, f"Petersen min over im(A) alone = 6 (got {mA})  [report: single-matrix version false, 6 > 4]")
req(fm == 3, f"Petersen union-family min = 3 = beta (got {fm}); rkA={rA} rkI={rI}")

n, E = mycielski(*cycle(5))
req(triangle_free(n, E) and not bipartite(n, E) and n == 11 and len(E) == 20, "Grotzsch: n=11 e=20 tf non-bip")
b, _ = beta_py(n, E)
fm, rA, rI, mA, mI = fam_info(n, E)
req(b == 4, f"Grotzsch beta = 4 (got {b})")
req(fm == 4, f"Grotzsch fam = 4 (got {fm}); rkA={rA} rkI={rI} minA={mA} minAI={mI}")
req(fm is not None and 25*fm <= n*n, "Grotzsch 25*fam <= n^2")

n, E = circulant(8, [1, 4])  # V8 = Wagner = And(3)
req(triangle_free(n, E) and not bipartite(n, E), "V8 tf non-bip")
b, _ = beta_py(n, E); fm, rA, rI, mA, mI = fam_info(n, E)
print(f"      V8: beta={b} fam={fm} rkA={rA} rkI={rI} bound floor(64/25)={64//25}")
req(fm <= 64//25, f"V8 fam <= 2 (got {fm})")

n, E = blowup(*circulant(8, [1, 4]), [2]*8)
b, _ = beta_np(n, E); fm, rA, rI, mA, mI = fam_info(n, E)
print(f"      V8[2]: n={n} beta={b} fam={fm} rkA={rA} rkI={rI} bound floor(256/25)={256//25}")
req(fm <= 256//25, f"V8[2] fam <= 10 (got {fm})")

n, E = clebsch()
req(triangle_free(n, E), "Clebsch tf")
b, _ = beta_np(n, E); fm, rA, rI, mA, mI = fam_info(n, E)
req(b == 8, f"Clebsch beta = 8 (got {b})")
req(fm == 8, f"Clebsch fam = 8 (got {fm})")
pg = parity_gram(n, E)
ident = all(pg[i] == (1 << i) for i in range(n))
req(ident and rA == 16, f"Clebsch A^2 == I mod 2, rank_F2(A) = 16 (got rkA={rA}) => im(A)=ALL subsets => W' test on Clebsch is VACUOUS (equals bare conjecture)")

n, E = circulant(13, [1, 5])
req(triangle_free(n, E) and not bipartite(n, E) and len(E) == 26, "C13(1,5): tf non-bip e=26")
b, _ = beta_py(n, E)
req(b == 6, f"C13(1,5) beta = 6 (got {b})")
req(5*b > len(E), f"C13(1,5): 5*beta={5*b} > e=26  => beta > e/5 >= nu*  (kills beta<=nu*)")
req(25*b <= 13*13, "C13(1,5) conjecture-consistent (25*6=150 <= 169)")

n, E = circulant(17, [1, 4])
req(triangle_free(n, E) and not bipartite(n, E) and len(E) == 34, "C17(1,4): tf non-bip e=34")
b, _ = beta_np(n, E)
req(b == 8, f"C17(1,4) beta = 8 (got {b})")
req(5*b > len(E), f"C17(1,4): 5*beta={5*b} > e=34")

# C5[3]: 9 edge-disjoint C5s partition (independent recipe x_i = a + i*b mod 3)
n, E = blowup(*cycle(5), [3]*5)
Eset = set(E)
allc = []
for a in range(3):
    for bb in range(3):
        verts = [3*i + ((a + i*bb) % 3) for i in range(5)]
        ce = [(min(verts[i], verts[(i+1) % 5]), max(verts[i], verts[(i+1) % 5])) for i in range(5)]
        allc += ce
req(len(allc) == 45 and len(set(allc)) == 45 and set(allc) == Eset,
    "C5[3]: 9 edge-disjoint C5s partition all 45 edges (independent det!=0 recipe) => nu* = 9 = e/5 = beta")
b3, _ = beta_np(n, E)
req(b3 == 9 and 25*b3 == n*n, f"C5[3] beta = 9 = n^2/25 (got {b3}) TIGHT")

# unbalanced blowups: beta = min a_i a_{i+1}
for sizes in [(3, 2, 2, 2, 1), (4, 3, 3, 2, 3), (1, 1, 4, 4, 1), (5, 1, 5, 1, 3)]:
    n, E = blowup(*cycle(5), list(sizes))
    b, _ = beta_np(n, E)
    pred = min(sizes[i]*sizes[(i+1) % 5] for i in range(5))
    req(b == pred and 25*b <= n*n, f"C5{list(sizes)}: beta={b} == min a_i a_(i+1)={pred}, 25b<=n^2")
    fm, rA, rI, mA, mI = fam_info(n, E)
    req(fm == b, f"C5{list(sizes)}: fam == beta (fam={fm}) [family contains optimal neighborhood cut]")

# pentagonal interval-cut identity on ARBITRARY hom-C5 graphs (not just complete blowups)
rng = random.Random(2026)
bad = 0
for trial in range(300):
    a = [rng.randint(0, 4) for _ in range(5)]
    if sum(x > 0 for x in a) < 3: continue
    offs = [0]
    for s in a: offs.append(offs[-1]+s)
    nT = offs[-1]
    E = []
    for i in range(5):
        j = (i+1) % 5
        for u in range(offs[i], offs[i+1]):
            for v in range(offs[j], offs[j+1]):
                if rng.random() < 0.6:
                    E.append((min(u, v), max(u, v)))
    if not E: continue
    classes = [set(range(offs[i], offs[i+1])) for i in range(5)]
    eclass = [sum(1 for u, v in E if (u in classes[i] and v in classes[(i+1) % 5]) or (v in classes[i] and u in classes[(i+1) % 5])) for i in range(5)]
    okk = True
    for j in range(5):
        T = 0
        for x in classes[j] | classes[(j+2) % 5]: T |= 1 << x
        if uncut(E, T) != eclass[(j+3) % 5]: okk = False
    if not okk: bad += 1
req(bad == 0, "interval-cut identity uncut(T_j) = e(V_j+3, V_j+4) on 300 random NON-complete hom-C5 graphs")

# GM dual, exact integers, independent check
badgm = 0
for trial in range(3000):
    a = [rng.randint(0, 40) for _ in range(5)]
    m = min(a[i]*a[(i+1) % 5] for i in range(5)); s = sum(a)
    if 25*25*(m**5) > s**10 and s > 0: badgm += 1
req(badgm == 0, "GM dual 25*min a_i a_(i+1) <= n^2 on 3000 random size-vectors (exact int)")

# peeling telescope
req(all(sum(2*k-1 for k in range(m+1, N+1)) == N*N - m*m for (N, m) in [(200, 7), (57, 5), (25, 24), (1000, 3), (12, 4)]),
    "peeling telescope sum(2k-1) = N^2 - m^2")

# Kneser(7,3): fam claim (beta skipped, n=35)
vs = list(combinations(range(7), 3)); idx = {v: i for i, v in enumerate(vs)}
E = [(idx[a], idx[b]) for a in vs for b in vs if idx[a] < idx[b] and not set(a) & set(b)]
n = 35
req(triangle_free(n, E) and not bipartite(n, E), "K(7,3) tf non-bip")
fm, rA, rI, mA, mI = fam_info(n, E)
print(f"      K(7,3): fam={fm} rkA={rA} rkI={rI} minA={mA} minAI={mI} bound floor(1225/25)={49}")
req(fm == 10 and 25*fm <= n*n, f"K(7,3) fam = 10 <= 49 (got {fm})")

# =============== SECTION C: F2 degeneracy of the family ===============
print("== C: degeneracy analysis of F(G) (NEW, adversarial) ==")
print("  THEOREM (parameter arithmetic): for an SRG(v,k,0,mu) with k,mu even:")
print("  A^2 = kI + mu(J-I-A) == 0 (mod 2), so (A+I)^2 == I (mod 2): A+I is INVERTIBLE over F2,")
print("  hence im(A+I) = F2^V = ALL subsets and W'(G) is verbatim 'beta(G) <= n^2/25'.")
for (v, k, mu, nm) in [(56, 10, 2, "Gewirtz"), (77, 16, 4, "M22"), (100, 22, 6, "Higman-Sims")]:
    print(f"    {nm}: SRG({v},{k},0,{mu}): k%2={k % 2} mu%2={mu % 2} -> A^2==0 mod 2 -> family DEGENERATE (contains every subset)")
print("  => the report's three 'best hunting grounds' cannot test W' beyond the bare conjecture;")
print("     they can only fail if Erdos #23 itself fails at n<=100 (excluded by the project's exact certificates for N<=200).")

# empirical degeneracy fraction on random tf non-bip graphs
for nn in (12, 14, 16):
    deg_full = 0; tot = 0
    for sd in range(250):
        rng2 = random.Random(90000+1000*nn+sd)
        adj = [0]*nn; E2 = set()
        for i in range(5):
            u, v = i, (i+1) % 5
            E2.add((min(u, v), max(u, v))); adj[u] |= 1 << v; adj[v] |= 1 << u
        pairs = [(u, v) for u in range(nn) for v in range(u+1, nn)]
        rng2.shuffle(pairs)
        keep = rng2.random()
        for u, v in pairs:
            if (u, v) in E2: continue
            if adj[u] & adj[v]: continue
            if rng2.random() < keep:
                E2.add((u, v)); adj[u] |= 1 << v; adj[v] |= 1 << u
        E2 = sorted(E2)
        if bipartite(nn, E2): continue
        tot += 1
        bA = f2_basis(adj); bI = f2_basis([adj[u] ^ (1 << u) for u in range(nn)])
        if len(bA) == nn or len(bI) == nn: deg_full += 1
    print(f"    random tf non-bip n={nn}: {deg_full}/{tot} graphs have A or A+I of FULL F2-rank (family = all subsets; W' test vacuous there)")

print("SECTION A (exhaustive n=5,6,7) starting...")
# =============== SECTION A: exhaustive n=5,6,7, independent ===============
for nn in (5, 6, 7):
    pairs = list(combinations(range(nn), 2)); P = len(pairs)
    pidx = {p: i for i, p in enumerate(pairs)}
    tris = [(1 << pidx[(a, b)]) | (1 << pidx[(b, c)]) | (1 << pidx[(a, c)]) for a, b, c in combinations(range(nn), 3)]
    masks = np.arange(1, 1 << P, dtype=np.uint32)
    keepm = np.ones(masks.shape, dtype=bool)
    for t in tris:
        keepm &= (masks & np.uint32(t)) != np.uint32(t)
    cand = masks[keepm].tolist()
    bound = nn*nn//25
    total = tested = fails = informative = famgtb = betabad = inf_pass = 0
    maskall = (1 << nn) - 1
    for mask in cand:
        edges = [pairs[i] for i in range(P) if (mask >> i) & 1]
        deg = [0]*nn
        for u, v in edges: deg[u] += 1; deg[v] += 1
        if min(deg) == 0: continue
        total += 1
        if bipartite(nn, edges): continue
        tested += 1
        adj = edges_to_adj(nn, edges)
        rowsAI = [adj[u] ^ (1 << u) for u in range(nn)]
        bA = f2_basis(adj); bI = f2_basis(rowsAI)
        inf = (len(bA) < nn and len(bI) < nn)
        if inf: informative += 1
        best = 10**9
        for sp in (span_list(bA), span_list(bI)):
            for S in sp:
                c = uncut(edges, S)
                if c < best: best = c
        b, _ = beta_py(nn, edges)
        if b > bound: betabad += 1
        if best > bound:
            fails += 1
            print(f"    W' FAIL n={nn}: edges={edges} fam={best} beta={b}")
        elif inf:
            inf_pass += 1
        if best > b: famgtb += 1
    print(f"  n={nn}: tf-noiso total={total}, NON-BIP TESTED={tested}, bound={bound}, W'FAILURES={fails}, "
          f"beta>bound(conj.viol)={betabad}, fam>beta={famgtb}, INFORMATIVE(both ranks<n)={informative} (passes among them={inf_pass})")

print("ALL-OK" if OK else "SOME-CHECKS-FAILED")
