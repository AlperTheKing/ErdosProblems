"""R8 stability: core toolkit for psi(H,x) = min over bipartitions of monochromatic weight.

Exact rational arithmetic (fractions.Fraction) decides every accepted claim.
Floating point is used only to *guide* search; every reported optimum is re-checked exactly.

psi(H,x) = min_{S subset V} sum_{uv in E, both in S or both outside S} x_u x_v
Conjecture: max_{x in simplex} psi(H,x) <= 1/25 for every triangle-free H.
"""
from fractions import Fraction as F
from itertools import combinations
import numpy as np

# ---------------------------------------------------------------- graphs

class Graph:
    __slots__ = ("n", "edges", "adj", "name")

    def __init__(self, n, edges, name=""):
        self.n = n
        es = set()
        for (u, v) in edges:
            if u == v:
                raise ValueError("loop")
            es.add((min(u, v), max(u, v)))
        self.edges = sorted(es)
        self.name = name
        self.adj = [0] * n
        for (u, v) in self.edges:
            self.adj[u] |= 1 << v
            self.adj[v] |= 1 << u

    def is_triangle_free(self):
        for (u, v) in self.edges:
            if self.adj[u] & self.adj[v]:
                return False
        return True

    def neighbors(self, v):
        return [u for u in range(self.n) if (self.adj[v] >> u) & 1]

    def induced_C5s(self):
        """All induced 5-cycles, returned as cyclic vertex tuples (each cycle once)."""
        out = []
        seen = set()
        for combo in combinations(range(self.n), 5):
            sub = [[u for u in combo if (self.adj[v] >> u) & 1] for v in combo]
            if any(len(s) != 2 for s in sub):
                continue
            # degree 2 in the induced subgraph on 5 vertices and connected => C5
            idx = {v: i for i, v in enumerate(combo)}
            start = combo[0]
            prev, cur = start, sub[0][0]
            cyc = [start, cur]
            ok = True
            for _ in range(3):
                nxt = [w for w in sub[idx[cur]] if w != prev]
                if len(nxt) != 1:
                    ok = False
                    break
                prev, cur = cur, nxt[0]
                cyc.append(cur)
            if not ok or len(set(cyc)) != 5:
                continue
            key = tuple(sorted(combo))
            if key in seen:
                continue
            seen.add(key)
            out.append(tuple(cyc))
        return out

    def g6(self):
        n = self.n
        bits = []
        for j in range(1, n):
            for i in range(j):
                bits.append(1 if (self.adj[i] >> j) & 1 else 0)
        while len(bits) % 6:
            bits.append(0)
        s = chr(n + 63)
        for k in range(0, len(bits), 6):
            val = 0
            for b in bits[k:k + 6]:
                val = 2 * val + b
            s += chr(val + 63)
        return s


def from_g6(s):
    s = s.strip()
    n = ord(s[0]) - 63
    assert 0 <= n <= 62, "only small graph6 supported"
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]:
                edges.append((i, j))
            p += 1
    return Graph(n, edges)


# ---------------------------------------------------------------- named test graphs

def C(n):
    return Graph(n, [(i, (i + 1) % n) for i in range(n)], name=f"C{n}")


def blowup_C5(sizes):
    """C5[n1..n5]; classes in cyclic order, complete between consecutive classes."""
    starts, tot = [], 0
    for s in sizes:
        starts.append(tot)
        tot += s
    edges = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                edges.append((starts[i] + a, starts[j] + b))
    return Graph(tot, edges, name="C5[" + ",".join(map(str, sizes)) + "]")


def blowup_classes(sizes):
    starts, tot, cls = [], 0, []
    for i, s in enumerate(sizes):
        starts.append(tot)
        tot += s
        cls += [i] * s
    return cls


def petersen():
    edges = [(i, (i + 1) % 5) for i in range(5)]
    edges += [(i, i + 5) for i in range(5)]
    edges += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return Graph(10, edges, name="Petersen")


def grotzsch():
    """Mycielskian of C5: C5 on 0..4, shadows 5..9, apex 10."""
    edges = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        edges.append((5 + i, (i + 1) % 5))
        edges.append((5 + i, (i - 1) % 5))
        edges.append((5 + i, 10))
    return Graph(11, edges, name="Grotzsch")


def circle_graph(m):
    """Gamma_m: vertices Z_m, u~v iff 3*circdist(u,v) > m.  Gamma_{3k-1} = Andrasfai And(k)."""
    edges = []
    for u in range(m):
        for v in range(u + 1, m):
            d = min(v - u, m - (v - u))
            if 3 * d > m:
                edges.append((u, v))
    return Graph(m, edges, name=f"Gamma_{m}")


def wagner():
    """Wagner / Moebius-Kantor V8 = Gamma_8 (the 8-vertex circle graph); = And(3)."""
    g = circle_graph(8)
    g.name = "Wagner(Gamma_8)"
    return g


def K(a, b):
    return Graph(a + b, [(i, a + j) for i in range(a) for j in range(b)], name=f"K_{a},{b}")


def TESTSUITE():
    ts = [C(5), blowup_C5([2, 2, 2, 2, 2]), blowup_C5([3, 1, 2, 2, 1]),
          blowup_C5([2, 0, 2, 2, 2]), blowup_C5([3, 3, 3, 3, 2]),
          petersen(), grotzsch(), wagner(), circle_graph(11), circle_graph(14),
          C(7), K(3, 3), C(6), Graph(1, [], name="K1")]
    return ts


# ---------------------------------------------------------------- exact psi

def cut_mono_masks(g):
    """For each of the 2^(n-1) bipartitions (S with 0 in S), the list of monochromatic edges."""
    n, E = g.n, g.edges
    out = []
    for S in range(1 << (n - 1)):
        Sm = (S << 1) | 1
        mono = [k for k, (u, v) in enumerate(E) if (((Sm >> u) & 1) == ((Sm >> v) & 1))]
        out.append((Sm, mono))
    return out


def psi_exact(g, x, cuts=None):
    """Exact psi and an argmin cut mask."""
    if cuts is None:
        cuts = cut_mono_masks(g)
    E = g.edges
    best, bestS = None, None
    for (Sm, mono) in cuts:
        val = F(0)
        for k in mono:
            u, v = E[k]
            val += x[u] * x[v]
        if best is None or val < best:
            best, bestS = val, Sm
            if best == 0:
                break
    return best, bestS


def cut_matrix_stack(g):
    """numpy array Q[S] = 0/1 incidence of monochromatic edges, plus edge endpoint arrays."""
    n, E = g.n, g.edges
    m = len(E)
    ncut = 1 << (n - 1)
    Q = np.zeros((ncut, m), dtype=np.float64)
    for S in range(ncut):
        Sm = (S << 1) | 1
        for k, (u, v) in enumerate(E):
            if ((Sm >> u) & 1) == ((Sm >> v) & 1):
                Q[S, k] = 1.0
    eu = np.array([e[0] for e in E], dtype=np.int64)
    ev = np.array([e[1] for e in E], dtype=np.int64)
    return Q, eu, ev


def psi_float_all(g, x, cache=None):
    """psi value and full vector of cut values (float)."""
    if cache is None:
        cache = cut_matrix_stack(g)
    Q, eu, ev = cache
    p = x[eu] * x[ev]
    vals = Q @ p
    return vals.min(), vals


def grad_of_cut(g, S_index, x, cache):
    """gradient of q_S at x (float)."""
    Q, eu, ev = cache
    grd = np.zeros(g.n)
    row = Q[S_index]
    np.add.at(grd, eu, row * x[ev])
    np.add.at(grd, ev, row * x[eu])
    return grd


# ---------------------------------------------------------------- optimiser

def maximize_psi(g, starts=None, n_random=200, iters=400, seed=0, tol=1e-13):
    """Sequential-LP ascent on max_x min_S q_S(x).  Guided by floats; caller must polish exactly.

    OPTIMISER DISCIPLINE: every induced C5 at weight 1/5 is used as a start (plus random starts).
    """
    from scipy.optimize import linprog
    rng = np.random.default_rng(seed)
    cache = cut_matrix_stack(g)
    Q, eu, ev = cache
    n = g.n
    S0 = []
    for cyc in g.induced_C5s():
        x = np.zeros(n)
        for v in cyc:
            x[v] = 0.2
        S0.append(x)
    if starts:
        S0 += [np.array(s, dtype=float) for s in starts]
    # uniform + random
    S0.append(np.ones(n) / n)
    for _ in range(n_random):
        z = rng.random(n) ** 2
        S0.append(z / z.sum())

    results = []
    for x0 in S0:
        x = x0.copy()
        radius = 0.25
        val, _ = psi_float_all(g, x, cache)
        for _ in range(iters):
            p = x[eu] * x[ev]
            vals = Q @ p
            # gradient of q_S wrt x: G[S] = sum over mono edges of (x_v e_u + x_u e_v)
            Gu = Q * x[ev][None, :]
            Gv = Q * x[eu][None, :]
            G = np.zeros((Q.shape[0], n))
            np.add.at(G.T, eu, Gu.T)
            np.add.at(G.T, ev, Gv.T)
            # LP: max t  s.t.  vals + G d >= t,  sum d = 0,  x+d>=0,  |d|<=radius
            # variables (d, t)
            A_ub = np.hstack([-G, np.ones((Q.shape[0], 1))])
            b_ub = vals
            A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
            b_eq = [0.0]
            lo = np.maximum(-x, -radius)
            hi = np.full(n, radius)
            bounds = [(lo[i], hi[i]) for i in range(n)] + [(None, None)]
            r = linprog(c=np.concatenate([np.zeros(n), [-1.0]]), A_ub=A_ub, b_ub=b_ub,
                        A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
            if not r.success:
                break
            d = r.x[:n]
            # exact line search on the true (non-linearised) psi
            best_s, best_v = 0.0, val
            for s in (1.0, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001):
                y = x + s * d
                y = np.maximum(y, 0.0)
                if y.sum() <= 0:
                    continue
                y = y / y.sum()
                v2, _ = psi_float_all(g, y, cache)
                if v2 > best_v + tol:
                    best_s, best_v = s, v2
                    break
            if best_s == 0.0:
                radius *= 0.4
                if radius < 1e-11:
                    break
                continue
            y = np.maximum(x + best_s * d, 0.0)
            x = y / y.sum()
            val = best_v
        results.append((val, x))
    results.sort(key=lambda t: -t[0])
    return results


def rationalize(x, q):
    """Round x to rationals with denominator q, renormalised to sum 1."""
    num = [int(round(xi * q)) for xi in x]
    s = sum(num)
    if s != q:
        # fix by adjusting the largest entry
        k = max(range(len(num)), key=lambda i: num[i])
        num[k] += q - s
    if min(num) < 0:
        return None
    return [F(t, q) for t in num]


def best_rational_polish(g, x, denoms=(5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 75, 80, 90, 100,
                                       120, 125, 140, 150, 175, 200, 210, 240, 250, 280, 300)):
    cuts = cut_mono_masks(g)
    best = (F(0), None, None)
    for q in denoms:
        xr = rationalize(x, q)
        if xr is None:
            continue
        v, _ = psi_exact(g, xr, cuts)
        if v > best[0]:
            best = (v, xr, q)
    return best
