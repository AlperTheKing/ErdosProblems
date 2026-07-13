# symmetrization lens -- reduced patterns (twin-free, maximal triangle-free, no nonadjacent
# domination) on n=5,6,7 vertices: enumerate up to iso; maximize beta(H,x) over the simplex
# (float supergradient search) then snap to exact rationals and evaluate EXACTLY.
# Also: exact C5 formula check beta(C5,x)=min_i x_i x_{i+1}; named battery
# (Wagner V8 = Andrasfai(3), Petersen, C11(1,4) = Andrasfai(4), Groetzsch).
from fractions import Fraction
from itertools import combinations, permutations
import random

ONE25 = Fraction(1, 25)

def canon(n, edges):
    best = None
    for p in permutations(range(n)):
        t = tuple(sorted(tuple(sorted((p[u], p[v]))) for (u, v) in edges))
        if best is None or t < best:
            best = t
    return best

def gen_patterns(n):
    pairs = list(combinations(range(n), 2))
    ne = len(pairs)
    seen = set()
    out = []
    for gm in range(1 << ne):
        if gm % 500000 == 0 and gm:
            print("  ... n=%d mask %d/%d, found %d" % (n, gm, 1 << ne, len(out)), flush=True)
        adj = [0] * n
        edges = []
        ok = True
        for i in range(ne):
            if (gm >> i) & 1:
                u, v = pairs[i]
                if adj[u] & adj[v]:
                    ok = False
                    break
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                edges.append((u, v))
        if not ok:
            continue
        maximal = True
        for (u, v) in pairs:
            if not (adj[u] >> v) & 1 and not (adj[u] & adj[v]):
                maximal = False
                break
        if not maximal:
            continue
        dom = False
        for u in range(n):
            for v in range(n):
                if u != v and not (adj[u] >> v) & 1 and not (adj[v] & ~adj[u]):
                    dom = True
                    break
            if dom:
                break
        if dom:
            continue
        c = canon(n, edges)
        if c not in seen:
            seen.add(c)
            out.append(edges)
    return out

def mono_tables(n, edges):
    tabs = []
    for m in range(1 << (n - 1)):
        c = [0] + [(m >> i) & 1 for i in range(n - 1)]
        tabs.append([k for k, (u, v) in enumerate(edges) if c[u] == c[v]])
    return tabs

def beta_float(n, edges, tabs, x):
    pe = [x[u] * x[v] for (u, v) in edges]
    best = None
    act = []
    for m, tab in enumerate(tabs):
        s = 0.0
        for k in tab:
            s += pe[k]
        if best is None or s < best - 1e-13:
            best = s
            act = [m]
        elif s < best + 1e-13:
            act.append(m)
    return best, act

def maximize_beta(n, edges, restarts=40, iters=250, seed=1):
    tabs = mono_tables(n, edges)
    rnd = random.Random(seed)
    bestv = -1.0
    bestx = None
    for r in range(restarts):
        x = [rnd.random() + 0.05 for _ in range(n)]
        s = sum(x)
        x = [xi / s for xi in x]
        for k in range(1, iters + 1):
            v, act = beta_float(n, edges, tabs, x)
            g = [0.0] * n
            for m in act:
                for kk in tabs[m]:
                    u, vv = edges[kk]
                    g[u] += x[vv] / len(act)
                    g[vv] += x[u] / len(act)
            eta = 0.3 / k ** 0.7
            x = [max(xi + eta * gi, 0.0) for xi, gi in zip(x, g)]
            s = sum(x)
            x = [xi / s for xi in x]
        v, _ = beta_float(n, edges, tabs, x)
        if v > bestv:
            bestv = v
            bestx = x[:]
    return bestv, bestx

def beta_exact(n, edges, xr):
    best = None
    for m in range(1 << (n - 1)):
        c = [0] + [(m >> i) & 1 for i in range(n - 1)]
        mono = Fraction(0)
        for (u, v) in edges:
            if c[u] == c[v]:
                mono += xr[u] * xr[v]
        if best is None or mono < best:
            best = mono
    return best

def snap_exact(n, edges, x, maxden=100):
    xr = [Fraction(xi).limit_denominator(maxden) for xi in x]
    s = sum(xr)
    if s == 0:
        return None, None
    xr = [xi / s for xi in xr]
    return beta_exact(n, edges, xr), xr

# --- exact C5 formula check ---
rnd = random.Random(7)
C5 = [(i, (i + 1) % 5) for i in range(5)]
for _ in range(200):
    xr = [Fraction(rnd.randint(1, 20)) for _ in range(5)]
    s = sum(xr)
    xr = [a / s for a in xr]
    assert beta_exact(5, C5, xr) == min(xr[i] * xr[(i + 1) % 5] for i in range(5))
print("C5 formula beta(C5,x)=min_i x_i x_{i+1}: 200/200 exact checks PASS", flush=True)

# --- enumerate reduced patterns ---
for n in (5, 6, 7):
    pats = gen_patterns(n)
    print("n=%d reduced patterns (up to iso): %d" % (n, len(pats)), flush=True)
    for edges in pats:
        bv, bx = maximize_beta(n, edges, restarts=40, iters=250, seed=11)
        be, xr = snap_exact(n, edges, bx)
        supp = [i for i in range(n) if xr[i] > 0]
        flag = "REFUTES-CONJECTURE" if (be is not None and be > ONE25) else ("=1/25" if be == ONE25 else "<1/25")
        print("  pattern e=%d %s : float max=%.6f exact-snap beta=%s (%s) support=%s"
              % (len(edges), edges, bv, be, flag, supp), flush=True)

# --- named battery ---
def wagner():
    E = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
    return 8, E

def petersen():
    E = ([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)] + [(i, i + 5) for i in range(5)]
         + [(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)])
    return 10, E

def c11_14():
    E = []
    for i in range(11):
        for d in (1, 4):
            j = (i + d) % 11
            E.append((min(i, j), max(i, j)))
    return 11, sorted(set(E))

def groetzsch():
    # outer o0..o4 = 0..4 (C5), inner i0..i4 = 5..9, apex 10; i_j ~ o_{j-1}, o_{j+1}; apex ~ all i_j
    E = [(i, (i + 1) % 5) for i in range(5)]
    for j in range(5):
        E += [(5 + j, (j - 1) % 5), (5 + j, (j + 1) % 5), (5 + j, 10)]
    return 11, E

for name, (n, E) in [("Wagner-V8(=Andrasfai3)", wagner()), ("Petersen", petersen()),
                     ("C11(1,4)(=Andrasfai4)", c11_14()), ("Groetzsch", groetzsch())]:
    xu = [Fraction(1, n)] * n
    bu = beta_exact(n, E, xu)
    bv, bx = maximize_beta(n, E, restarts=12, iters=200, seed=3)
    be, xr = snap_exact(n, E, bx)
    supp = [i for i in range(n) if xr[i] > 0]
    print("%s: n=%d e=%d uniform beta=%s (=%.6f, 1/25=0.04); search max float=%.6f exact-snap=%s support=%s%s"
          % (name, n, len(E), bu, float(bu), bv, be, supp,
             "  REFUTES-CONJECTURE" if be is not None and be > ONE25 else ""), flush=True)
print("PATTERN SEARCH DONE", flush=True)
