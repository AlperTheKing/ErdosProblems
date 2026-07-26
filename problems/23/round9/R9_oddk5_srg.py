"""R9: triangle-free strongly regular graphs as EXACT psi/Lambda gap witnesses.

For a d-regular graph with adjacency spectrum bounded below by lambda_min:
    maxcut = max_{s in +-1} ( m/2 - (1/4) s^T A s ) <= m/2 - (n/4) lambda_min,
so                         bip = m - maxcut >= m/2 + (n/4) lambda_min      (*)
and if the odd girth is >= 5 then y == 1/5 covers every odd cycle, so
                            Lambda <= m/5.                                  (**)
Both bounds are EXACT rationals when lambda_min is an integer, which happens for every
strongly regular graph: A^2 = kI + lambda A + mu (J - I - A) forces
theta^2 - (lambda-mu) theta - (k-mu) = 0 on 1^perp.  We verify that matrix identity in
exact integer arithmetic, so lambda_min is certified without any floating point.

Everything below is built from scratch: GF(4), PG(2,4), the 56-hyperoval class,
the Steiner system S(3,6,22), and from it the M22, Gewirtz and Higman-Sims graphs.
"""
from fractions import Fraction as F
from itertools import combinations
from R9_oddk5_lib import G, bip, odd_girth, maxcut_local, cut_value, Cn

# ------------------------------------------------------------------ GF(4), PG(2,4)
MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]   # 2 = w, 3 = w^2
def add(a, b): return a ^ b
def mul(a, b): return MUL[a][b]

def pg24():
    vecs = [(a, b, c) for a in range(4) for b in range(4) for c in range(4)]
    vecs = [v for v in vecs if v != (0, 0, 0)]
    seen, pts = set(), []
    for v in vecs:
        if v in seen:
            continue
        cls = {tuple(mul(s, x) for x in v) for s in (1, 2, 3)}
        seen |= cls
        pts.append(min(cls))
    assert len(pts) == 21, len(pts)
    lines = []
    for L in pts:                      # dual: line with coefficient vector L
        line = frozenset(i for i, p in enumerate(pts)
                         if add(add(mul(p[0], L[0]), mul(p[1], L[1])), mul(p[2], L[2])) == 0)
        assert len(line) == 5
        lines.append(line)
    assert len(set(lines)) == 21
    return pts, lines

def hyperovals(pts, lines):
    coll = [[[False] * 21 for _ in range(21)] for _ in range(21)]
    onl = {}
    for L in lines:
        for t in combinations(sorted(L), 3):
            onl[t] = True
    hs = []
    for S in combinations(range(21), 6):
        good = True
        for t in combinations(S, 3):
            if t in onl:
                good = False
                break
        if good:
            hs.append(frozenset(S))
    return hs

def steiner_3_6_22():
    pts, lines = pg24()
    hs = hyperovals(pts, lines)
    assert len(hs) == 168, len(hs)
    # split the 168 hyperovals into the 3 PSL(3,4)-classes: same class <=> |H cap H'| even
    idx = {h: i for i, h in enumerate(hs)}
    seen = [False] * 168
    classes = []
    for i in range(168):
        if seen[i]:
            continue
        comp, st = [], [i]
        seen[i] = True
        while st:
            v = st.pop()
            comp.append(v)
            for j in range(168):
                if not seen[j] and len(hs[v] & hs[j]) % 2 == 0:
                    seen[j] = True
                    st.append(j)
        classes.append(comp)
    assert sorted(len(c) for c in classes) == [56, 56, 56], [len(c) for c in classes]
    INF = 21
    blocks = [frozenset(sorted(L) + [INF]) for L in lines] + [hs[i] for i in classes[0]]
    assert len(blocks) == 77
    # verify the Steiner property in exact combinatorics
    cnt = {}
    for B in blocks:
        assert len(B) == 6
        for t in combinations(sorted(B), 3):
            cnt[t] = cnt.get(t, 0) + 1
    assert len(cnt) == 1540 and set(cnt.values()) == {1}, (len(cnt), set(cnt.values()))
    return blocks           # on point set 0..21  (22 points)

# ------------------------------------------------------------------ the graphs
def higman_sims():
    blocks = steiner_3_6_22()
    n = 1 + 22 + 77
    INFV = 0
    P = lambda p: 1 + p
    B = lambda i: 23 + i
    E = []
    for p in range(22):
        E.append((INFV, P(p)))
    for i, b in enumerate(blocks):
        for p in b:
            E.append((P(p), B(i)))
    for i in range(77):
        for j in range(i + 1, 77):
            if not (blocks[i] & blocks[j]):
                E.append((B(i), B(j)))
    return G(n, E)

def m22_graph():
    blocks = steiner_3_6_22()
    E = [(i, j) for i in range(77) for j in range(i + 1, 77) if not (blocks[i] & blocks[j])]
    return G(77, E)

def gewirtz():
    blocks = steiner_3_6_22()
    sel = [b for b in blocks if 0 not in b]
    assert len(sel) == 56, len(sel)
    E = [(i, j) for i in range(56) for j in range(i + 1, 56) if not (sel[i] & sel[j])]
    return G(56, E)

def hoffman_singleton():
    # standard construction: 5 pentagons P_h, 5 pentagrams Q_i;
    # P_h[j] ~ Q_i[i*h + j mod 5]
    E = []
    Pv = lambda h, j: h * 5 + j
    Qv = lambda i, j: 25 + i * 5 + j
    for h in range(5):
        for j in range(5):
            E.append((Pv(h, j), Pv(h, (j + 1) % 5)))
            E.append((Qv(h, j), Qv(h, (j + 2) % 5)))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.append((Pv(h, j), Qv(i, (i * h + j) % 5)))
    return G(50, E)

def clebsch():
    # folded 5-cube: vertices = even-weight subsets of {0..4} (16), adjacent iff symmetric
    # difference has size 4  ->  SRG(16,5,0,2)
    vs = [s for s in range(32) if bin(s).count('1') % 2 == 0]
    idx = {s: i for i, s in enumerate(vs)}
    E = []
    for a in vs:
        for b in vs:
            if a < b and bin(a ^ b).count('1') == 4:
                E.append((idx[a], idx[b]))
    return G(16, E)

def petersen():
    return G(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] +
             [(5 + i, 5 + (i + 2) % 5) for i in range(5)])

# ------------------------------------------------------------------ certification
def srg_params(g):
    """exact integer verification that A^2 = kI + lam A + mu(J-I-A); returns (n,k,lam,mu)."""
    n = g.n
    adjset = [set(a) for a in g.adj]
    k = len(g.adj[0])
    for v in range(n):
        if len(g.adj[v]) != k:
            return None
    lam = mu = None
    for u in range(n):
        for v in range(u + 1, n):
            c = len(adjset[u] & adjset[v])
            if v in adjset[u]:
                if lam is None: lam = c
                elif lam != c: return None
            else:
                if mu is None: mu = c
                elif mu != c: return None
    return (n, k, lam, mu)

def lambda_min_exact(par):
    """for an SRG with integer eigenvalues: theta = ((lam-mu) -+ sqrt(D))/2, D=(lam-mu)^2+4(k-mu)"""
    n, k, lam, mu = par
    D = (lam - mu) ** 2 + 4 * (k - mu)
    r = int(round(D ** 0.5))
    assert r * r == D, "non-integral eigenvalues"
    s = ((lam - mu) - r)
    assert s % 2 == 0
    return s // 2

def report(name, g, verify_oddgirth=True, ls_iters=60):
    par = srg_params(g)
    assert par is not None, name + " is not strongly regular"
    n, k, lam, mu = par
    assert lam == 0, name + " has triangles"
    lmin = lambda_min_exact(par)
    m = g.m
    og = odd_girth(g) if verify_oddgirth else 5
    # exact spectral lower bound on bip:  bip >= m/2 + n*lmin/4 ; integrality allows ceil
    lb = F(m, 2) + F(n * lmin, 4)
    lb_int = -((-lb.numerator) // lb.denominator)      # ceil
    lamub = F(m, og)                                    # y == 1/og is feasible
    gap = F(lb_int) / lamub
    cut, side = maxcut_local(g, iters=ls_iters, seed=7)
    assert cut == cut_value(g, side)
    bip_ub = m - cut
    conj = F(n * n, 25)
    print(f"{name:16s} SRG{par} m={m:5d} oddgirth={og} lambda_min={lmin}")
    print(f"    bip >= {lb_int:6d}   (spectral, exact)      bip <= {bip_ub:6d} (local-search cut {cut})")
    print(f"    Lambda <= {str(lamub):>8s}  (y=1/{og})       psi/Lambda >= {str(gap):>10s} = {float(gap):.6f}")
    print(f"    conjecture ceiling N^2/25 = {str(conj):>10s}   bip/N^2 in [{float(F(lb_int,n*n)):.5f}, "
          f"{float(F(bip_ub,n*n)):.5f}]   {'OK' if bip_ub <= conj else '*** ABOVE 1/25 ***'}")
    return dict(name=name, par=par, m=m, lmin=lmin, bip_lb=lb_int, bip_ub=bip_ub,
                lam_ub=lamub, gap=gap, og=og)

if __name__ == "__main__":
    print("=" * 90)
    print("Triangle-free strongly regular graphs: exact psi/Lambda gap lower bounds")
    print("=" * 90)
    out = []
    out.append(report("Petersen", petersen()))
    out.append(report("Clebsch", clebsch()))
    out.append(report("Hoffman-Singleton", hoffman_singleton()))
    out.append(report("Gewirtz", gewirtz()))
    out.append(report("M22", m22_graph()))
    out.append(report("Higman-Sims", higman_sims(), ls_iters=40))
    print()
    print("best exact gap witness:", max(out, key=lambda r: r['gap'])['name'],
          max(out, key=lambda r: r['gap'])['gap'])
