r"""RCC FAMILY HARNESS v2 (2026-07-08, Fable-5). GPT-Pro reply 4 path-B: targeted dual-falsifier families.
F1 (guarded complete C5-book, params p,q,rX,rY) and F2 (escaping neutral-lens necklace, param k).
v1 FINDING: GPT-Pro's guard multiplicity rX=q-1 leaves the global X-block flip NEUTRAL, so the true max cut
recolors the books and the Hall pressure evaporates (F1(3,3) true max 28/29 -> |S|=1). v2 uses rX>=q, rY>=p
(strictly losing block flips) and a CHUNKED numpy exhaustive max-cut up to n<=27 (2^26 states); for larger n a
flip-stability NECESSARY check (singletons+pairs+shores+blocks) marks 'nec-only'.
Pipeline verdicts (A-E protocol): A declared-not-max / B tri-or-ell violation / C ledger-sep [not checked v1] /
D primal cover+Door cert (exact-verified) / E-cand primal infeasible (escalate). SSE-relevant cut = the
Gamma-MIN max cut (B-connected). Exact Fractions for all certs. Run from problems/23/writeup.
"""
import json
from itertools import combinations
from fractions import Fraction
from collections import deque
import numpy as np
from scipy.optimize import linprog


# ---------- builders ----------

def build_f1(p, q, rX, rY):
    names = []
    def add(v): names.append(v); return len(names) - 1
    X = [add('X%d' % i) for i in range(p)]
    B0 = add('B0')
    Y = [add('Y%d' % j) for j in range(q)]
    A0 = add('A0'); C0 = add('C0')
    GX = {(i, t): add('GX%d_%d' % (i, t)) for i in range(p) for t in range(rX)}
    GY = {(j, t): add('GY%d_%d' % (j, t)) for j in range(q) for t in range(rY)}
    red = set(X + [B0] + Y)
    side = [0 if v in red else 1 for v in range(len(names))]
    cut = []
    for i in range(p): cut.append((X[i], A0))
    cut.append((A0, B0)); cut.append((B0, C0))
    for j in range(q): cut.append((C0, Y[j]))
    for (i, t), g in GX.items(): cut.append((X[i], g))
    for (j, t), g in GY.items(): cut.append((Y[j], g))
    bad = [(X[i], Y[j]) for i in range(p) for j in range(q)]
    blocks = [set(X), set(Y), set(X) | {A0}, set(Y) | {C0}, {A0, B0}, {B0, C0}, {A0, B0, C0}]
    return 'F1(%d,%d;g%d,%d)' % (p, q, rX, rY), names, cut, bad, side, blocks


def build_f2(k):
    names = []
    def add(v): names.append(v); return len(names) - 1
    P = [add('p%d' % i) for i in range(k)]
    lens = {}
    for i in range(k):
        lens[i] = dict(b=add('b%d' % i), bb=add('bb%d' % i), y=add('y%d' % i), w=add('w%d' % i),
                       r2=add('r2_%d' % i), a=add('a%d' % i), c=add('c%d' % i),
                       r1=add('r1_%d' % i), r3=add('r3_%d' % i))
    blue = set()
    for i in range(k):
        blue |= {lens[i]['a'], lens[i]['c'], lens[i]['r1'], lens[i]['r3']}
    side = [0 if v not in blue else 1 for v in range(len(names))]
    cut, bad = [], []
    shores = []
    for i in range(k):
        L = lens[i]; pi = P[i]; pi1 = P[(i + 1) % k]
        cut += [(pi, L['a']), (L['a'], L['b']), (L['b'], L['c']), (L['c'], L['y']),
                (pi1, L['c']), (L['c'], L['bb']), (L['bb'], L['a']), (L['a'], L['w']),
                (pi, L['r1']), (L['r1'], L['r2']), (L['r2'], L['r3']), (L['r3'], pi1)]
        bad += [(pi, L['y']), (pi1, L['w']), (pi, pi1)]
        shores.append({L['a'], L['b'], L['bb'], L['c'], L['y'], L['w']})
    bad = sorted(set((min(e), max(e)) for e in bad))
    cut = sorted(set((min(e), max(e)) for e in cut))
    return 'F2(%d)' % k, names, cut, bad, side, shores


# ---------- exact graph utilities ----------

def check_simple_trifree(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if v in adj[u]:
            return False, 'dup edge %s' % ((u, v),)
        adj[u].add(v); adj[v].add(u)
    for u in range(n):
        for v in adj[u]:
            if v > u:
                if adj[u] & adj[v]:
                    return False, 'triangle at %s' % ((u, v),)
    return True, adj


def blue_ell(adj_blue, u, v):
    d = {u: 0}; Q = deque([u])
    while Q:
        x = Q.popleft()
        for y in adj_blue[x]:
            if y not in d:
                d[y] = d[x] + 1; Q.append(y)
    return None if v not in d else d[v] + 1


def geodesic_support(adj_blue, u, v):
    ds = {u: 0}; Q = deque([u])
    while Q:
        x = Q.popleft()
        for y in adj_blue[x]:
            if y not in ds: ds[y] = ds[x] + 1; Q.append(y)
    dt = {v: 0}; Q = deque([v])
    while Q:
        x = Q.popleft()
        for y in adj_blue[x]:
            if y not in dt: dt[y] = dt[x] + 1; Q.append(y)
    D = ds.get(v)
    if D is None:
        return frozenset()
    edges = set()
    for x in ds:
        if x in dt and ds[x] + dt[x] == D:
            for y in adj_blue[x]:
                if y in ds and y in dt and ds[y] == ds[x] + 1 and ds[y] + dt[y] == D:
                    edges.add((min(x, y), max(x, y)))
    return frozenset(edges)


def exhaustive_maxcut(n, edges, side_decl, cap=4000):
    """Chunked numpy exhaustive max cut (vertex 0 fixed side 0). n <= 27."""
    NS = 1 << (n - 1)
    CH = 1 << 22
    maxval = -1
    count = 0
    keep = []
    for start in range(0, NS, CH):
        stop = min(start + CH, NS)
        s_arr = np.arange(start, stop, dtype=np.uint32)
        total = np.zeros(stop - start, dtype=np.int16)
        for (u, v) in edges:
            if u == 0:
                total += ((s_arr >> np.uint32(v - 1)) & 1).astype(np.int16)
            elif v == 0:
                total += ((s_arr >> np.uint32(u - 1)) & 1).astype(np.int16)
            else:
                total += (((s_arr >> np.uint32(u - 1)) ^ (s_arr >> np.uint32(v - 1))) & 1).astype(np.int16)
        cmax = int(total.max())
        if cmax > maxval:
            maxval = cmax; count = 0; keep = []
        if cmax == maxval:
            idxs = np.where(total == maxval)[0]
            count += len(idxs)
            for s in idxs[:max(0, cap - len(keep))]:
                keep.append(start + int(s))
    decl_bits = 0
    for v in range(1, n):
        if side_decl[v] != side_decl[0]:
            decl_bits |= (1 << (v - 1))
    decl_val = sum(1 for (u, v) in edges if ((decl_bits >> (u - 1)) & 1 if u else 0) != ((decl_bits >> (v - 1)) & 1 if v else 0))
    sides = []
    for s in keep:
        sd = [0] * n
        for v in range(1, n):
            sd[v] = (s >> (v - 1)) & 1
        sides.append(sd)
    return maxval, decl_val, count, sides


def flip_stable(n, edges, side, blocks):
    """NECESSARY max-cut check: no improving single, pair, or block flip."""
    def cutsize(sd):
        return sum(1 for (u, v) in edges if sd[u] != sd[v])
    base = cutsize(side)
    for v in range(n):
        sd = list(side); sd[v] ^= 1
        if cutsize(sd) > base:
            return False, ('single', v)
    for a in range(n):
        for b in range(a + 1, n):
            sd = list(side); sd[a] ^= 1; sd[b] ^= 1
            if cutsize(sd) > base:
                return False, ('pair', (a, b))
    for blk in blocks:
        sd = list(side)
        for v in blk: sd[v] ^= 1
        if cutsize(sd) > base:
            return False, ('block', sorted(blk))
    return True, base


def gamma_of(n, edges, side):
    adjb = [set() for _ in range(n)]
    bad = []
    for u, v in edges:
        if side[u] != side[v]:
            adjb[u].add(v); adjb[v].add(u)
        else:
            bad.append((u, v))
    for u, v in bad:
        if blue_ell(adjb, u, v) is None:
            return None, None, None
    G = sum(blue_ell(adjb, u, v) ** 2 for u, v in bad)
    return G, bad, adjb


# ---------- LP layer ----------

def sepf(U, e):
    return (e[0] in U) != (e[1] in U)


def structured_family(n, adjb, S, F, extra_shores=()):
    fam = set()
    for v in range(1, n):
        fam.add(frozenset([v]))
    for a in range(1, n):
        for b in range(a + 1, n):
            fam.add(frozenset([a, b]))
        fam.add(frozenset(x for x in range(1, n) if x != a))
    adj2 = [set(x for x in adjb[v]) for v in range(n)]
    for (a, b) in F:
        adj2[a].discard(b); adj2[b].discard(a)
    seen = set()
    for v in range(n):
        if v in seen: continue
        comp = {v}; Q = deque([v])
        while Q:
            x = Q.popleft()
            for y in adj2[x]:
                if y not in comp: comp.add(y); Q.append(y)
        seen |= comp
        if 0 not in comp and 0 < len(comp) < n:
            fam.add(frozenset(comp))
        elif 0 in comp and 0 < n - len(comp):
            fam.add(frozenset(set(range(n)) - comp))
    for sh in extra_shores:
        s2 = frozenset(sh) if 0 not in sh else frozenset(set(range(n)) - set(sh))
        if 0 < len(s2) < n:
            fam.add(s2)
    return sorted(fam, key=lambda U: (len(U), sorted(U)))


def primal_lp(S, F, O, sigma, fam):
    nU = len(fam)
    A_ub, b_ub = [], []
    for e in S:
        A_ub.append([-1.0 if sepf(U, e) else 0.0 for U in fam]); b_ub.append(-1.0)
    for c in F:
        A_ub.append([1.0 if sepf(U, c) else 0.0 for U in fam]); b_ub.append(1.0)
    row = [float(sum(1 for c in O if sepf(U, c))) for U in fam]
    A_ub.append(row); b_ub.append(float(sigma))
    res = linprog(c=np.zeros(nU), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * nU, method='highs')
    if not res.success:
        return False, None, None
    lam = {fam[i]: res.x[i] for i in range(nU) if res.x[i] > 1e-9}
    ext = sum(res.x[i] * sum(1 for c in O if sepf(fam[i], c)) for i in range(nU))
    return True, lam, ext


def exact_primal_check(S, F, O, sigma, lam_f):
    lam = {U: Fraction(w).limit_denominator(10 ** 4) for U, w in lam_f.items()}
    covmin = min(sum(w for U, w in lam.items() if sepf(U, e)) for e in S) if S else Fraction(1)
    scale = Fraction(1) if covmin >= 1 else Fraction(1) / covmin
    for c in F:
        if sum(w for U, w in lam.items() if sepf(U, c)) * scale > 1:
            return False, None
    ext = sum(sum(w for U, w in lam.items() if sepf(U, c)) for c in O) * scale
    if ext > sigma:
        return False, None
    return True, ext


# ---------- pipeline ----------

def analyze(name, names, cut_intent, bad_intent, side, blocks, report):
    n = len(names)
    edges = sorted(set((min(u, v), max(u, v)) for u, v in cut_intent + bad_intent))
    ok, adj_or_msg = check_simple_trifree(n, edges)
    if not ok:
        report(name, 'B', 'not simple/tri-free: %s' % adj_or_msg); return
    print("  %s: n=%d edges=%d tri-free OK" % (name, n, len(edges)), flush=True)
    if n <= 27:
        maxval, decl_val, nmax, sides = exhaustive_maxcut(n, edges, side)
        mc_mode = 'exhaustive'
        print("    maxcut=%d declared=%d #maxcuts=%d %s" % (maxval, decl_val, nmax,
              '(declared IS max)' if decl_val == maxval else '(A: DECLARED NOT MAX)'), flush=True)
        if decl_val != maxval:
            report(name, 'A', 'declared cut %d < max %d (guards insufficient); analyzing true Gamma-min max cut anyway'
                   % (decl_val, maxval))
    else:
        st, info = flip_stable(n, edges, side, blocks)
        mc_mode = 'nec-only'
        if not st:
            report(name, 'A(nec)', 'improving flip found: %s' % (info,)); return
        sides = [list(side)]
        print("    flip-stable (nec-only): base cut verified stable under singles+pairs+blocks", flush=True)
    best = None
    nb = 0
    for sd in sides:
        G, bad, adjb = gamma_of(n, edges, sd)
        if G is None:
            continue
        nb += 1
        if best is None or G < best[0]:
            best = (G, sd, bad, adjb)
    if best is None:
        report(name, 'NOTE', 'no B-connected max cut among %d enumerated' % len(sides)); return
    G, sd, bad, adjb = best
    ells = {e: blue_ell(adjb, e[0], e[1]) for e in bad}
    S = [e for e in bad if ells[e] == 5]
    if not S:
        report(name, 'NOTE', 'no ell5 atoms at Gamma-min max cut (Gamma=%d, ells=%s)' % (G, sorted(set(ells.values())))); return
    Pe = {e: geodesic_support(adjb, e[0], e[1]) for e in S}
    F = sorted(set().union(*Pe.values()))
    cutE = [(u, v) for (u, v) in edges if sd[u] != sd[v]]
    Fset = set(F)
    O = [c for c in cutE if c not in Fset]
    sigma = len(cutE) - len(bad)
    hall = len(S) <= len(F)
    print("    [%s] Gamma-min=%d (of %d B-conn maxcuts) N^2=%d | ells=%s |S|=%d |F|=%d |O|=%d sigma=%d HALL=%s"
          % (mc_mode, G, nb, n * n, sorted(set(ells.values())), len(S), len(F), len(O), sigma, hall), flush=True)
    fam = structured_family(n, adjb, S, F, blocks)
    feas, lam, ext = primal_lp(S, F, O, sigma, fam)
    if feas:
        okx, ext_exact = exact_primal_check(S, F, O, sigma, lam)
        report(name, 'D', 'primal cover+Door cert (fam %d, ext~%.3f, exact=%s ext=%s); Hall=%s Gamma=%d/%d [%s]'
               % (len(fam), ext, okx, ext_exact, hall, G, n * n, mc_mode))
    else:
        report(name, 'E-cand', 'primal INFEASIBLE (fam %d, Door sigma=%d, Hall=%s) [%s] -- ESCALATE'
               % (len(fam), sigma, hall, mc_mode))


def main():
    results = []
    def report(name, verdict, msg):
        results.append((name, verdict, msg))
        print("  >> %s VERDICT %s: %s" % (name, verdict, msg), flush=True)
    print("RCC FAMILY HARNESS v2: guard-corrected F1 + F2 necklace | chunked maxcut n<=27 | A-E")
    print("=" * 100)
    for (p, q) in [(2, 2), (3, 2), (3, 3)]:
        analyze(*build_f1(p, q, rX=q, rY=p), report)
    for (p, q, rX, rY) in [(3, 3, 4, 4)]:
        pass  # n=31 > 27; enable in v3 nec-only if needed
    for k in [2, 3]:
        analyze(*build_f2(k), report)
    print("=" * 100)
    for r in results:
        print("   %-16s %-8s %s" % r)
    json.dump([list(r) for r in results], open('../../../tmp/claude_rcc_family_v2.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
