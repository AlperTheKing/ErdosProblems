"""AUDIT of round6/P2.md -- INDEPENDENT exact re-implementation.

Written from the definitions in the chain statement, deliberately NOT reading P2_verify*.py.
A measure is a list of (position numerator, integer weight) over denominators (M, Q=sum w).
All acceptance-path arithmetic is INTEGER (numerators over Q^2 / Q^2*M); Fractions only for display.

Definitions used (chain items 1/3/4/5):
    adjacency  u~v   iff  circular distance d(u,v) > 1/3          [3*|u-v|_circ > M on integers]
    mono(S)    = sum over UNORDERED adjacent pairs inside S or inside S^c of x_u x_v
    psi        = min over ALL 2^{n-1} bipartitions of mono
    ARCBOUND   = min over cyclic-interval sides of mono
    g(u)       = sum_{v ~ u} x_v ;  W = (1/2) sum x_u g(u) = sum_{u<v,u~v} x_u x_v
    T          = sum_{u<v,u~v} d(u,v) x_u x_v ;   A = W - 2T
    m(b)       = W - sum_{u ~ b} x_u g(u)                          (item 4)
    bound_k    = sum_b x_b g(b)^k m(b) / sum_b x_b g(b)^k
"""
from fractions import Fraction as F
from itertools import combinations


class Measure:
    def __init__(self, M, pos, w):
        assert len(pos) == len(w)
        assert all(0 <= p < M for p in pos)
        assert sorted(pos) == list(pos) and len(set(pos)) == len(pos)
        assert all(wi > 0 for wi in w)
        self.M, self.pos, self.n = M, list(pos), len(pos)
        self.w = list(w)
        self.Q = sum(w)
        self.x = [F(wi, self.Q) for wi in w]
        n = self.n
        self.d = [[0] * n for _ in range(n)]
        self.adj = [[False] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                t = (pos[i] - pos[j]) % M
                dd = min(t, M - t)
                self.d[i][j] = dd
                self.adj[i][j] = (3 * dd > M)
        self.edges = [(i, j) for i, j in combinations(range(n), 2) if self.adj[i][j]]
        self.ew = [(i, j, w[i] * w[j]) for i, j in self.edges]          # integer edge weights
        self.Wn = sum(e[2] for e in self.ew)                            # W  = Wn / Q^2
        self.Tn = sum(self.d[i][j] * ww for i, j, ww in self.ew)        # T  = Tn / (Q^2 M)
        self.gn = [sum(w[j] for j in range(n) if self.adj[i][j]) for i in range(n)]   # g = gn/Q
        self.mn = [self.Wn - sum(w[j] * self.gn[j] for j in range(n) if self.adj[i][j])
                   for i in range(n)]                                   # m(b) = mn/Q^2

    # ---------------- moments (exact)
    def g(self):     return [F(v, self.Q) for v in self.gn]
    def W(self):     return F(self.Wn, self.Q ** 2)
    def T(self):     return F(self.Tn, self.Q ** 2 * self.M)
    def A(self):     return self.W() - 2 * self.T()

    def A_direct(self):
        """A as the ORDERED double integral of (1/2 - d) over far pairs = 2 * unordered sum."""
        return 2 * sum((F(1, 2) - F(self.d[i][j], self.M)) * self.x[i] * self.x[j] for i, j in self.edges)

    def var_g(self):
        e1 = F(sum(self.w[i] * self.gn[i] for i in range(self.n)), self.Q ** 2)
        e2 = F(sum(self.w[i] * self.gn[i] ** 2 for i in range(self.n)), self.Q ** 3)
        return e2 - e1 ** 2

    # ---------------- cuts (integer numerators over Q^2)
    def mono_n(self, inS):
        return sum(ww for i, j, ww in self.ew if inS[i] == inS[j])

    def mono(self, inS):
        return F(self.mono_n(inS), self.Q ** 2)

    def psi_n(self):
        best = None
        for mask in range(1 << (self.n - 1)):
            inS = [(mask >> i) & 1 for i in range(self.n - 1)] + [0]
            v = self.mono_n(inS)
            if best is None or v < best:
                best = v
        return best

    def psi(self):
        return F(self.psi_n(), self.Q ** 2)

    def _blocks(self):
        for i in range(self.n):
            for L in range(self.n + 1):
                inS = [0] * self.n
                for t in range(L):
                    inS[(i + t) % self.n] = 1
                yield i, L, inS

    def arcbound_n(self, want_arc=False):
        best, barc = None, None
        for i, L, inS in self._blocks():
            v = self.mono_n(inS)
            if best is None or v < best:
                best, barc = v, (i, L)
        return (best, barc) if want_arc else best

    def arcbound(self):
        return F(self.arcbound_n(), self.Q ** 2)

    def arc_len_class(self, i, L):
        """(min,max) length of an arc realising support-block (start i, length L), as Fractions."""
        if L == 0:
            return (F(0), F(0))
        if L == self.n:
            return (F(1), F(1))
        first, last = self.pos[i], self.pos[(i + L - 1) % self.n]
        prev, nxt = self.pos[(i - 1) % self.n], self.pos[(i + L) % self.n]
        span = F((last - first) % self.M, self.M)
        return (span, span + F((first - prev) % self.M, self.M) + F((nxt - last) % self.M, self.M))

    def min_over_arcs_of_length(self, lo, hi):
        """min of mono over arcs whose length may be chosen inside [lo,hi]."""
        best = None
        for i, L, inS in self._blocks():
            a, b = self.arc_len_class(i, L)
            if b < lo or a > hi:
                continue
            v = self.mono_n(inS)
            if best is None or v < best:
                best = v
        return None if best is None else F(best, self.Q ** 2)

    def m_free(self):
        """min over b in the WHOLE circle of mono(N(b)); N(b) is an independent arc for every b,
        so this is a legal (stronger) arc bound.  O(n) distinct sets: work in units of 1/(6M)."""
        S6 = 6 * self.M
        cands = set()
        for p in self.pos:
            for off in (2 * self.M + 1, 2 * self.M - 1, -2 * self.M + 1, -2 * self.M - 1):
                cands.add((6 * p + off) % S6)
        best = None
        for c in cands:
            inS = [1 if min((6 * p - c) % S6, (c - 6 * p) % S6) > 2 * self.M else 0 for p in self.pos]
            v = self.mono_n(inS)
            if best is None or v < best:
                best = v
        return F(best, self.Q ** 2)

    # ---------------- the item-5 hierarchy
    def m_formula(self):
        return [F(v, self.Q ** 2) for v in self.mn]

    def m_direct(self):
        """m(b) recomputed from scratch as mono(N(b)) -- independent re-derivation of item 4."""
        out = []
        for b in range(self.n):
            inS = [1 if self.adj[b][j] else 0 for j in range(self.n)]
            out.append(F(self.mono_n(inS), self.Q ** 2))
        return out

    def bound_k(self, k):
        num = sum(self.w[b] * self.gn[b] ** k * self.mn[b] for b in range(self.n))
        den = sum(self.w[b] * self.gn[b] ** k for b in range(self.n))
        if den == 0:
            return None
        return F(num, den * self.Q ** 2)

    def min_m_supp(self):
        return F(min(self.mn), self.Q ** 2)

    # ---------------- the item-7 criterion
    def item7_hypotheses(self):
        W, T = self.W(), self.T()
        return (F(12, 100) < W < F(1, 5),
                2 * T < W - F(1, 25),
                4 * W ** 2 + self.var_g() < W - F(1, 25))

    def is_item7_falsifier(self):
        h1, h2, h3 = self.item7_hypotheses()
        return h1 and h2 and h3 and self.min_m_supp() > F(1, 25)

    def report(self, name, do_psi=True, do_arc=True):
        W, T, A = self.W(), self.T(), self.A()
        assert A == self.A_direct(), "A identity failed"
        assert self.m_formula() == self.m_direct(), "item-4 identity FAILED"
        b0 = self.bound_k(0)
        g = self.g()
        assert b0 == W - sum(self.x[i] * g[i] ** 2 for i in range(self.n)), "bound_0 identity failed"
        ab = self.arcbound() if do_arc else None
        ps = self.psi() if (do_psi and self.n <= 24) else None
        h1, h2, h3 = self.item7_hypotheses()
        print(f"--- {name}  (M={self.M}, n={self.n}, |E|={len(self.edges)})")
        print(f"    W={W}={float(W):.7f}  T/W={T/W if W else '-'}  Var(g)={self.var_g()}")
        print(f"    A={A}={float(A):.7f}   bound_0={b0}={float(b0):.7f}")
        print(f"    min_b m(b)={self.min_m_supp()}={float(self.min_m_supp()):.7f}")
        print("    bound_k k=0..6: " + " ".join(f"{float(self.bound_k(k)):.6f}" for k in range(7)))
        print("    bound_k k=20,60,200: " + " ".join(f"{float(self.bound_k(k)):.6f}" for k in (20, 60, 200)))
        if ab is not None:
            print(f"    ARCBOUND={ab}={float(ab):.7f}" + (f"   psi={ps}={float(ps):.7f}" if ps is not None else ""))
        print(f"    item-7 hyps: W in (.12,.2)={h1}  2T<W-1/25={h2}  4W^2+Var<W-1/25={h3}"
              f"  => FALSIFIER: {self.is_item7_falsifier()}")
        return dict(W=W, T=T, A=A, b0=b0, minm=self.min_m_supp(), arc=ab, psi=ps,
                    fals=self.is_item7_falsifier())


def gamma_measure(m, w):
    pos = [i for i in range(m) if w[i] > 0]
    return Measure(m, pos, [w[i] for i in pos])
