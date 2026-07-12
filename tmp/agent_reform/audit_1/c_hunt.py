# INDEPENDENT adversarial hunt for W' failures where the report under-sampled:
# graphs with BOTH A and A+I singular over F2 (the only graphs where W' says more than the bare conjecture),
# window degrees, structured families the battery did not include (C7/C9/C11 blowups, Mycielski tower, circulant sweep).
import numpy as np, random
from itertools import combinations

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

def f2_basis(rows):
    basis = {}
    for r in rows:
        x = r
        while x:
            h = x.bit_length()-1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; break
    return list(basis.values())

def min_uncut_span(edges, basis, cap=24):
    if len(basis) > cap: return None
    arr = np.zeros(1, dtype=np.uint64)
    for b in basis:
        arr = np.concatenate([arr, arr ^ np.uint64(b)])
    best = 10**9
    CH = 1 << 21
    for st in range(0, arr.shape[0], CH):
        a2 = arr[st:st+CH]
        acc = np.zeros(a2.shape, dtype=np.uint16)
        for u, v in edges:
            acc += (((a2 >> np.uint64(u)) & np.uint64(1)) == ((a2 >> np.uint64(v)) & np.uint64(1)))
        best = min(best, int(acc.min()))
    return best

def fam(n, edges, cap=24):
    adj = edges_to_adj(n, edges)
    bA = f2_basis(adj); bI = f2_basis([adj[u] ^ (1 << u) for u in range(n)])
    mA = min_uncut_span(edges, bA, cap); mI = min_uncut_span(edges, bI, cap)
    cands = [m for m in (mA, mI) if m is not None]
    return (min(cands) if cands else None), len(bA), len(bI)

def beta_np(n, edges):
    tot = 1 << (n-1); best = len(edges)+1
    CH = 1 << 20
    for st in range(0, tot, CH):
        S = np.arange(st, min(st+CH, tot), dtype=np.uint64)
        acc = np.zeros(S.shape, dtype=np.uint16)
        for u, v in edges:
            acc += (((S >> np.uint64(u)) & np.uint64(1)) == ((S >> np.uint64(v)) & np.uint64(1)))
        best = min(best, int(acc.min()))
    return best

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

def gen_petersen(k, step):
    E = [(i, (i+1) % k) for i in range(k)]
    E += [(k+i, k+(i+step) % k) for i in range(k)]
    E += [(i, k+i) for i in range(k)]
    return 2*k, sorted(set((min(u, v), max(u, v)) for u, v in E))

failures = []
def check(name, n, E, do_beta=True, cap=24):
    if not triangle_free(n, E):
        print(f"  {name}: NOT triangle-free, skip"); return
    if bipartite(n, E):
        print(f"  {name}: bipartite, skip"); return
    bound = n*n//25
    fm, rA, rI, = fam(n, E, cap)
    b = beta_np(n, E) if (do_beta and n <= 25) else None
    degfull = (rA == n or rI == n)
    tag = "DEGEN(full-rank)" if degfull else "informative"
    stat = "OK" if (fm is not None and fm <= bound) else ("SKIP" if fm is None else "**W'FAIL**")
    print(f"  {name:28s} n={n:3d} e={len(E):3d} beta={b if b is not None else '?':>4} fam={fm if fm is not None else 'SKIP':>4} "
          f"bound={bound:3d} rkA={rA} rkI={rI} {tag:16s} {stat}")
    if fm is not None and fm > bound:
        failures.append((name, n, len(E), b, fm))

print("== E: structured families the battery did NOT include ==")
check("C7[2]", *blowup(*cycle(7), [2]*7))
check("C7[3]", *blowup(*cycle(7), [3]*7))
check("C9[2]", *blowup(*cycle(9), [2]*9))
check("C11[2]", *blowup(*cycle(11), [2]*11))
n, E = blowup(*cycle(7), [3]*7)
rng = random.Random(5)
for t in range(3):
    Em = list(E)
    rem = rng.sample(range(len(Em)), 6)
    Em = [e for i, e in enumerate(Em) if i not in rem]
    check(f"C7[3]-6edges s{t}", n, Em)
n, E = blowup(*cycle(9), [2]*9)
Em = [e for i, e in enumerate(E) if i % 9 != 0]
check("C9[2]-sparse-del", n, Em)
check("GP(11,2)", *gen_petersen(11, 2))
check("GP(13,2)", *gen_petersen(13, 2), do_beta=False)
n5, E5 = cycle(5)
nM, EM = mycielski(n5, E5)
nM2, EM2 = mycielski(nM, EM)
check("Mycielski^2(C5)", nM2, EM2, do_beta=True)   # n=23
# near-extremal at scale: C5[5] minus matchings (n=25, bound=25)
n, E = blowup(*cycle(5), [5]*5)
Em = [e for e in E if e not in [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]]
check("C5[5]-matching(0,1)", n, Em, do_beta=False)
Em2 = [e for e in Em if e not in [(5, 10), (6, 11), (7, 12), (8, 13), (9, 14)]]
check("C5[5]-2matchings", n, Em2, do_beta=False)
check("C5[5]", *blowup(*cycle(5), [5]*5), do_beta=False)

print("== E2: circulant sweep C_n(1,k) and C_n(1,k,l), triangle-free non-bipartite, n <= 28 ==")
cnt = 0
for nn in range(10, 29):
    for k in range(2, nn//2 + 1):
        conn = [1, k]
        # triangle-free test via construction
        n2, E2 = circulant(nn, conn)
        if not triangle_free(n2, E2) or bipartite(n2, E2): continue
        if len(E2) <= nn*nn//25: continue  # vacuous (empty-set cut works)
        check(f"C{nn}(1,{k})", n2, E2, do_beta=(nn <= 22))
        cnt += 1
tri = 0
for nn in range(13, 26):
    for k in range(2, nn//2):
        for l in range(k+1, nn//2 + 1):
            n2, E2 = circulant(nn, [1, k, l])
            if not triangle_free(n2, E2) or bipartite(n2, E2): continue
            if len(E2) <= nn*nn//25: continue
            check(f"C{nn}(1,{k},{l})", n2, E2, do_beta=(nn <= 20))
            tri += 1
            if tri >= 14: break
        if tri >= 14: break
    if tri >= 14: break

print("== F: random hunt restricted to INFORMATIVE graphs (both A, A+I singular) ==")
rng = random.Random(777)
stats = {}
for nn, samples in [(12, 300), (15, 300), (16, 200), (20, 120)]:
    tested = inform = famgtb = fails_n = 0
    maxmargin = -10**9
    for sd in range(samples):
        style = sd % 3
        adj = [0]*nn; E2 = set()
        def add(u, v):
            E2.add((min(u, v), max(u, v))); adj[u] |= 1 << v; adj[v] |= 1 << u
        for i in range(5): add(i, (i+1) % 5)
        pairs = [(u, v) for u in range(nn) for v in range(u+1, nn)]
        rng.shuffle(pairs)
        pkeep = 1.0 if style == 0 else (0.25 + 0.5*rng.random())
        for u, v in pairs:
            if (u, v) in E2 or (adj[u] & adj[v]): continue
            if rng.random() <= pkeep: add(u, v)
        E2 = sorted(E2)
        if bipartite(nn, E2): continue
        tested += 1
        fm, rA, rI = fam(nn, E2)
        if rA == nn or rI == nn: continue
        inform += 1
        b = beta_np(nn, E2)
        bound = nn*nn//25
        if fm > b: famgtb += 1
        margin = 25*fm - nn*nn
        maxmargin = max(maxmargin, margin)
        if fm > bound:
            fails_n += 1
            print(f"  *** W' FAIL n={nn} seed={sd}: beta={b} fam={fm} bound={bound} edges={E2}")
    stats[nn] = (tested, inform, famgtb, fails_n, maxmargin)
    print(f"  n={nn}: tested={tested} informative(both-singular)={inform} fam>beta={famgtb} W'fails={fails_n} max(25*fam-n^2)={maxmargin}")

print("HUNT FAILURES:", failures if failures else "NONE")
