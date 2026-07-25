"""
audit_G7_struct.py -- INDEPENDENT re-implementation of the structural claims of
round3/G7.md.  Nothing is imported from G7_*.py.  Graphs are stored as
frozensets of frozenset edges; isomorphism is decided by nauty `labelg`
canonical graph6 strings (NOT networkx VF2, which is what the target used).
All arithmetic is exact (int / Fraction).
"""
import itertools, subprocess, os, sys
from fractions import Fraction

LABELG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\labelg.exe"


# ---------------------------------------------------------------- graph type
class Gr:
    def __init__(self, verts, edges=()):
        self.V = list(verts)
        self.E = set()
        for u, v in edges:
            self.add(u, v)

    def add(self, u, v):
        assert u != v
        assert u in self.V and v in self.V, (u, v)
        self.E.add(frozenset((u, v)))

    def adj(self, v):
        return set(w for e in self.E if v in e for w in e if w != v)

    def n(self):
        return len(self.V)

    def m(self):
        return len(self.E)

    def induced(self, S):
        S = [v for v in self.V if v in set(S)]
        Ss = set(S)
        return Gr(S, [tuple(e) for e in self.E if set(e) <= Ss])

    def relabel(self, f):
        return Gr([f[v] for v in self.V], [(f[u], f[v]) for u, v in map(tuple, self.E)])


def g6(g):
    """my own graph6 encoder (upper triangle, column-major)"""
    V = list(g.V)
    idx = {v: i for i, v in enumerate(V)}
    n = len(V)
    A = [[0] * n for _ in range(n)]
    for e in g.E:
        u, v = tuple(e)
        A[idx[u]][idx[v]] = A[idx[v]][idx[u]] = 1
    bits = []
    for j in range(n):
        for i in range(j):
            bits.append(A[i][j])
    assert n <= 62
    out = [chr(n + 63)]
    while len(bits) % 6:
        bits.append(0)
    for t in range(0, len(bits), 6):
        val = 0
        for b in bits[t:t + 6]:
            val = 2 * val + b
        out.append(chr(val + 63))
    return ''.join(out)


_CANON = {}


def canon(g):
    s = g6(g)
    if s in _CANON:
        return _CANON[s]
    r = subprocess.run([LABELG, '-q'], input=s + '\n', capture_output=True, text=True)
    c = r.stdout.strip()
    assert c, (s, r.stderr)
    _CANON[s] = c
    return c


def iso(g, h):
    return g.n() == h.n() and g.m() == h.m() and canon(g) == canon(h)


# ------------------------------------------------------------ constructions
def Gamma_BT(i):
    """Brandt-Thomasse p.3 VERBATIM: V={1..3i-1}, j ~ j+i,...,j+2i-1 mod 3i-1."""
    m = 3 * i - 1
    lab = lambda t: (t - 1) % m + 1
    g = Gr(range(1, m + 1))
    for j in range(1, m + 1):
        for d in range(i, 2 * i):
            k = lab(j + d)
            if k != j:
                g.add(j, k)
    return g


def Gamma_dist(i):
    """the circular-distance form asserted in G7.md Theorem B2"""
    m = 3 * i - 1
    g = Gr(range(1, m + 1))
    for j in range(1, m + 1):
        for k in range(j + 1, m + 1):
            d = (k - j) % m
            if min(d, m - d) >= i:
                g.add(j, k)
    return g


def Upsilon(i, drop_y=False, drop_2i=False):
    """Brandt-Thomasse p.4 VERBATIM."""
    assert i >= 2
    m = 3 * i - 1
    g = Gamma_BT(i)
    for t in 'xyabcuvw':
        g.V.append(t)
    g.add('x', 'y')
    for t in 'abc':
        g.add('x', t)
    for t in 'uvw':
        g.add('y', t)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']          # induced 6-cycle in this order
    for t in range(6):
        g.add(cyc[t], cyc[(t + 1) % 6])
    X = list(range(1, i + 1))
    Y = list(range(i + 1, 2 * i + 1))
    Z = list(range(2 * i + 1, 3 * i))
    assert len(Z) == i - 1
    for j in X:
        g.add('a', j); g.add('u', j)
    for j in Y:
        g.add('b', j); g.add('v', j)
    for j in Z:
        g.add('c', j); g.add('w', j)
    dele = ([ 'y'] if drop_y else []) + ([2 * i] if drop_2i else [])
    return g.induced([v for v in g.V if v not in dele])


def BT_weights(i, drop_y, drop_2i):
    """Brandt-Thomasse Theorem 3 (p.4) verbatim integer weights."""
    if not drop_y and not drop_2i:
        w = {'x': 1, 'y': 1, 1: 1, 2 * i: 1, 'c': 3 * i - 3, 'w': 3 * i - 3,
             'u': 3 * i - 2, 'v': 3 * i - 2, 'a': 3 * i - 2, 'b': 3 * i - 2}
        return w, 9 * i - 6, 27 * i - 19
    if drop_y and not drop_2i:
        w = {1: 1, 2 * i: 1, 'x': 2, 'w': 3 * i - 4, 'u': 3 * i - 3, 'v': 3 * i - 3,
             'c': 3 * i - 3, 'a': 3 * i - 2, 'b': 3 * i - 2}
        return w, 9 * i - 7, 27 * i - 22
    if not drop_y and drop_2i:
        w = {'x': 1, 'y': 1, 1: 2, i: 2, 'b': 3 * i - 3, 'v': 3 * i - 3,
             'c': 3 * i - 3, 'w': 3 * i - 3, 'u': 3 * i - 2, 'a': 3 * i - 2}
        return w, 9 * i - 7, 27 * i - 22
    w = {'x': 2, 1: 2, i: 2, 'v': 3 * i - 4, 'w': 3 * i - 4, 'u': 3 * i - 3,
         'b': 3 * i - 3, 'c': 3 * i - 3, 'a': 3 * i - 2}
    return w, 9 * i - 8, 27 * i - 25


def mycielski_C5():
    g = Gr(['u%d' % j for j in range(5)] + ['v%d' % j for j in range(5)] + ['z'])
    for j in range(5):
        g.add('u%d' % j, 'u%d' % ((j + 1) % 5))
        g.add('v%d' % j, 'u%d' % ((j + 1) % 5))
        g.add('v%d' % j, 'u%d' % ((j - 1) % 5))
        g.add('z', 'v%d' % j)
    return g


# ------------------------------------------------------------------ checks
def triangle_free(g):
    for e in g.E:
        u, v = tuple(e)
        if g.adj(u) & g.adj(v):
            return False
    return True


def maximal_tf(g):
    if not triangle_free(g):
        return False
    for u, v in itertools.combinations(g.V, 2):
        if frozenset((u, v)) not in g.E and not (g.adj(u) & g.adj(v)):
            return False
    return True


def twin_free(g):
    for u, v in itertools.combinations(g.V, 2):
        if g.adj(u) == g.adj(v):
            return False
    return True


def alpha(g, w=None):
    V = list(g.V)
    n = len(V)
    idx = {v: t for t, v in enumerate(V)}
    A = [0] * n
    for e in g.E:
        u, v = tuple(e)
        A[idx[u]] |= 1 << idx[v]
        A[idx[v]] |= 1 << idx[u]
    wt = [1] * n if w is None else [w[v] for v in V]
    best = [0]

    def rec(cand, cur):
        if cur + sum(wt[t] for t in range(n) if cand >> t & 1) <= best[0]:
            return
        if cand == 0:
            best[0] = max(best[0], cur)
            return
        t = min(t for t in range(n) if cand >> t & 1)
        rec(cand & ~(1 << t) & ~A[t], cur + wt[t])
        rec(cand & ~(1 << t), cur)
    rec((1 << n) - 1, 0)
    return best[0]


def chi(g, cap=7):
    V = list(g.V)
    n = len(V)
    idx = {v: t for t, v in enumerate(V)}
    nb = [[] for _ in range(n)]
    for e in g.E:
        u, v = tuple(e)
        nb[idx[u]].append(idx[v]); nb[idx[v]].append(idx[u])
    order = sorted(range(n), key=lambda t: -len(nb[t]))

    def ok(k):
        col = [-1] * n

        def rec(p, used):
            if p == n:
                return True
            t = order[p]
            for c in range(min(used + 1, k)):
                if any(col[s] == c for s in nb[t]):
                    continue
                col[t] = c
                if rec(p + 1, max(used, c + 1)):
                    return True
                col[t] = -1
            return False
        return rec(0, 0)
    for k in range(1, cap + 1):
        if ok(k):
            return k
    return None


def odd_girth_five(g):
    """returns an induced C5 (as a vertex list) or None"""
    V = list(g.V)
    for S in itertools.combinations(V, 5):
        sub = g.induced(S)
        if sub.m() != 5:
            continue
        if all(len(sub.adj(v)) == 2 for v in S):
            # 2-regular with 5 vertices and 5 edges and connected => C5
            seen = {S[0]}
            stack = [S[0]]
            while stack:
                x = stack.pop()
                for y in sub.adj(x):
                    if y not in seen:
                        seen.add(y); stack.append(y)
            if len(seen) == 5:
                return list(S)
    return None


def hom_exists(g, h):
    """exhaustive backtracking: is there a homomorphism g -> h?"""
    GV = list(g.V); HV = list(h.V)
    gadj = {v: g.adj(v) for v in GV}
    hadj = {v: h.adj(v) for v in HV}
    f = {}

    def rec(p):
        if p == len(GV):
            return True
        v = GV[p]
        for t in HV:
            good = True
            for u in gadj[v]:
                if u in f and f[u] not in hadj[t]:
                    good = False; break
            if good:
                f[v] = t
                if rec(p + 1):
                    return True
                del f[v]
        return False
    return rec(0)


def wdeg(g, w):
    return {v: sum(w[u] for u in g.adj(v)) for v in g.V}


# -------------------------------------------------------------------- main
def main():
    out = []
    P = lambda s: (print(s), out.append(s), sys.stdout.flush())

    P('=== A. Gamma_i: BT verbatim definition vs the circular-distance form ===')
    for i in range(1, 13):
        a, b = Gamma_BT(i), Gamma_dist(i)
        same = (a.E == b.E)
        reg = set(len(a.adj(v)) for v in a.V)
        P('  i=%2d n=%2d m=%3d  BTdef==distform:%s  regular:%s  deg=%s  tf=%s'
          % (i, a.n(), a.m(), same, len(reg) == 1, sorted(reg), triangle_free(a)))
        assert same, i

    P('')
    P('=== B. Gamma_i structural ===')
    for i in range(1, 10):
        g = Gamma_BT(i)
        al = alpha(g)
        P('  Gamma_%d n=%2d deg=%d tf=%s maxTF=%s twinfree=%s alpha=%d chi=%s '
          'delta_reg=%s inducedC5=%s'
          % (i, g.n(), i, triangle_free(g), maximal_tf(g), twin_free(g), al,
             chi(g), Fraction(i, 3 * i - 1),
             odd_girth_five(g) is not None))
        assert triangle_free(g) and maximal_tf(g)
        if i >= 2:
            assert twin_free(g) and al == i

    P('')
    P('=== C. Vega graphs: BT Theorem 3 weights, exact regularity ===')
    fams = [(False, False, 'Ups_%d', lambda i: 3 * i + 7),
            (True, False, 'Ups_%d-y', lambda i: 3 * i + 6),
            (False, True, 'Ups_%d-2i', lambda i: 3 * i + 6),
            (True, True, 'Ups_%d-y-2i', lambda i: 3 * i + 5)]
    for i in range(2, 8):
        for dy, d2, nm, nf in fams:
            g = Upsilon(i, dy, d2)
            w0, sdeg, stot = BT_weights(i, dy, d2)
            w = {v: w0.get(v, 3) for v in g.V}
            D = wdeg(g, w)
            reg = len(set(D.values())) == 1
            tot = sum(w.values())
            d = list(D.values())[0]
            dreg = Fraction(d, tot)
            t = dreg.denominator and None
            # solve dreg = s/(3s-1)
            s = Fraction(dreg.numerator, 1) / (3 * dreg - 0) if False else None
            # s/(3s-1)=r  =>  s = r/(3r-1)
            ss = dreg / (3 * dreg - 1)
            P('  %-12s n=%2d(exp %2d) m=%3d tf=%s maxTF=%s twinfree=%s regular=%s '
              'deg=%d(exp %d) tot=%d(exp %d) delta_reg=%s = t/(3t-1) with t=%s'
              % (nm % i, g.n(), nf(i), g.m(), triangle_free(g), maximal_tf(g),
                 twin_free(g), reg, d, sdeg, tot, stot, dreg, ss))
            assert g.n() == nf(i) and triangle_free(g) and maximal_tf(g) and twin_free(g)
            assert reg and d == sdeg and tot == stot
            assert ss.denominator == 1
    P('')
    P('  chi / alpha of the Vega graphs (i=2..6):')
    for i in range(2, 7):
        for dy, d2, nm, nf in fams:
            g = Upsilon(i, dy, d2)
            P('    %-12s chi=%s alpha=%d inducedC5=%s'
              % (nm % i, chi(g), alpha(g), odd_girth_five(g) is not None))

    P('')
    P('=== D. delta_reg ladder identity (exact) ===')
    for j in range(2, 9):
        for k, (dy, d2, nm, _) in enumerate(fams):
            _, sdeg, stot = BT_weights(j, dy, d2)
            r = Fraction(sdeg, stot)
            t = r / (3 * r - 1)
            P('  %-12s delta_reg=%-10s  t=%s  (9j-6,9j-7,9j-7,9j-8)=%d'
              % (nm % j, r, t, [9 * j - 6, 9 * j - 7, 9 * j - 7, 9 * j - 8][k]))
            assert t == [9 * j - 6, 9 * j - 7, 9 * j - 7, 9 * j - 8][k]

    P('')
    P('=== E. identifications ===')
    P('  Ups_2-y-2i ~= Grotzsch(Mycielski C5): %s'
      % iso(Upsilon(2, True, True), mycielski_C5()))
    P('  Ups_2-y    ~= Ups_2-2i             : %s'
      % iso(Upsilon(2, True, False), Upsilon(2, False, True)))
    for i in range(3, 7):
        P('  Ups_%d-y    ~= Ups_%d-2i             : %s'
          % (i, i, iso(Upsilon(i, True, False), Upsilon(i, False, True))))

    P('')
    P('=== F. Theorem B1 (collapse): induced subgraphs of Upsilon_i ===')
    for i in range(2, 8):
        full = Upsilon(i)
        for dy, d2, nm, _ in fams[1:]:
            dele = (['y'] if dy else []) + ([2 * i] if d2 else [])
            ind = full.induced([v for v in full.V if v not in dele])
            P('  %-12s induced in Ups_%d: %s' % (nm % i, i, iso(ind, Upsilon(i, dy, d2))))
            assert iso(ind, Upsilon(i, dy, d2))
        ind = full.induced([v for v in full.V if isinstance(v, int)])
        P('  Gamma_%-6d induced in Ups_%d: %s' % (i, i, iso(ind, Gamma_BT(i))))
        assert iso(ind, Gamma_BT(i))

    P('')
    P('=== G. Theorem B2 (chain): Ups_i = Ups_{i+1} - {i+1,2i+2,3i+2} ===')
    for i in range(2, 13):
        m = i + 1
        big = Upsilon(m)
        D = [m, 2 * m, 3 * m - 1]
        assert D == [i + 1, 2 * i + 2, 3 * i + 2], (D, i)
        ind = big.induced([v for v in big.V if v not in D])
        small = Upsilon(i)
        # explicit map claimed in G7.md: psi_D(j) = j - #{d in D : d < j}
        f = {}
        for v in ind.V:
            f[v] = v if not isinstance(v, int) else v - sum(1 for d in D if d < v)
        mapped = ind.relabel(f)
        entrywise = (set(map(frozenset, mapped.E)) == set(map(frozenset, small.E))
                     and set(mapped.V) == set(small.V))
        P('  i=%2d  |Ups_%d - D| = %d  explicit-map-entrywise-equal: %s  nauty-iso: %s'
          % (i, m, ind.n(), entrywise, iso(ind, small)))
        assert entrywise and iso(ind, small)

    P('')
    P('=== H. Jin falsifier: homomorphisms Gamma_i -> C5 ===')
    C5 = Gr(range(5), [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    for i in range(2, 11):
        g = Gamma_BT(i)
        h = hom_exists(g, C5)
        al = alpha(g)
        P('  Gamma_%-2d n=%2d delta_reg=%-7s > 10/29 : %-5s  alpha=%d  chi_f>=n/alpha=%s  '
          'hom->C5: %s  chi=%s'
          % (i, g.n(), Fraction(i, 3 * i - 1), Fraction(i, 3 * i - 1) > Fraction(10, 29),
             al, Fraction(g.n(), al), h, chi(g)))

    P('')
    P('=== I. Grotzsch = Ups_2-{y,4}: BT weighting is Haggkvist 29-vertex 10-regular ===')
    g = Upsilon(2, True, True)
    w0, sdeg, stot = BT_weights(2, True, True)
    w = {v: w0.get(v, 3) for v in g.V}
    P('  weights: %s' % sorted(((str(k), v) for k, v in w.items())))
    P('  total=%d  weighted degrees=%s  chi=%s  tf=%s'
      % (sum(w.values()), sorted(set(wdeg(g, w).values())), chi(g), triangle_free(g)))
    P('  blow-up N=%d, delta=%d, delta/N=%s vs 10/29=%s'
      % (sum(w.values()), sdeg, Fraction(sdeg, sum(w.values())), Fraction(10, 29)))

    P('')
    P('=== J. Corollary 4.3(4) check: order <= 3i-4 whenever delta_reg > i/(3i-1) ===')
    bad = []
    for i in range(2, 40):
        thr = Fraction(i, 3 * i - 1)
        lst = []
        for j in range(1, 60):
            if Fraction(j, 3 * j - 1) > thr:
                lst.append(('Gamma_%d' % j, 3 * j - 1))
        for j in range(2, 20):
            for k, (dy, d2, nm, nf) in enumerate(fams):
                _, sdeg, stot = BT_weights(j, dy, d2)
                if Fraction(sdeg, stot) > thr:
                    lst.append((nm % j, nf(j)))
        mx = max(o for _, o in lst) if lst else 0
        if mx > 3 * i - 4:
            bad.append((i, mx))
    P('  violations of "at most 3i-4 vertices" for i=2..39: %s' % (bad or 'NONE'))

    P('')
    P('=== K. the ladder L_t ===')
    for t in list(range(2, 14)) + [20, 30]:
        thr = Fraction(t, 3 * t - 1)
        lst = []
        for j in range(1, 80):
            if Fraction(j, 3 * j - 1) > thr:
                lst.append(('Gamma_%d' % j, 3 * j - 1))
        for j in range(2, 30):
            for k, (dy, d2, nm, nf) in enumerate(fams):
                _, sdeg, stot = BT_weights(j, dy, d2)
                if Fraction(sdeg, stot) > thr:
                    lst.append((nm % j, nf(j)))
        P('  t=%2d band delta> %-10s |L_t|=%2d maxorder=%2d  vega=%s'
          % (t, thr, len(lst), max(o for _, o in lst),
             [nm for nm, _ in lst if nm.startswith('Ups')]))

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'audit_G7_struct_out.txt'), 'w') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
