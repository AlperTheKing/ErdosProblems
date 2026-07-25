"""AUDIT ENGINE -- independent re-implementation (auditor of round6/P1.md).

Deliberately different data structures from P1_engine.py:
  * a measure is stored as (q, [(k_i, w_i)]) with positions k_i/q, k_i INTEGERS, so the
    adjacency test is the pure-integer  3*min(dk, q-dk) > q   (no Fraction 1/3 anywhere);
  * cuts are stored as integer bitmasks, monochromatic mass is recomputed from the edge list
    every time (no incremental update, so an incremental-update bug cannot be shared);
  * psi is a brute force over all 2^(n-1) bitmasks; arcbound restricts to cyclic-interval
    bitmasks generated independently of the psi loop;
  * pentagonality is enumerated over ALL 5-tuples of cut positions WITH REPETITION (so empty
    blocks are allowed -- P1_pentagon.py only enumerates 5 DISTINCT cut points);
  * an independent hom-to-C5 backtracking test, to cross-check pentagonality.

Everything exact (fractions.Fraction / int).
"""
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement

TARGET = F(1, 25)


class M:
    def __init__(self, q, items):
        """q = denominator of the positions, items = [(int position, weight)] weights>0."""
        d = {}
        for k, w in items:
            w = F(w)
            if w != 0:
                d[k % q] = d.get(k % q, F(0)) + w
        s = sum(d.values())
        self.q = q
        self.k = sorted(d)
        self.x = [d[k] / s for k in self.k]
        self.n = len(self.k)
        n = self.n
        self.adj = [[False] * n for _ in range(n)]
        self.dist = [[F(0)] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dk = abs(self.k[i] - self.k[j]) % q
                dk = min(dk, q - dk)
                a = 3 * dk > q                       # d > 1/3, pure integer test
                self.adj[i][j] = self.adj[j][i] = a
                self.dist[i][j] = self.dist[j][i] = F(dk, q)
        self.E = [(i, j) for i in range(n) for j in range(i + 1, n) if self.adj[i][j]]
        self.w = {(i, j): self.x[i] * self.x[j] for (i, j) in self.E}

    # ---------- primitives -------------------------------------------------
    def mono(self, mask):
        """monochromatic mass of the cut given by the bitmask"""
        return sum(w for (i, j), w in self.w.items()
                   if ((mask >> i) & 1) == ((mask >> j) & 1))

    @property
    def W(self):
        return sum(self.w.values())

    @property
    def T(self):
        return sum(self.w[e] * self.dist[e[0]][e[1]] for e in self.E)

    @property
    def g(self):
        return [sum(self.x[j] for j in range(self.n) if self.adj[i][j]) for i in range(self.n)]

    @property
    def Varg(self):
        g = self.g
        e1 = sum(self.x[i] * g[i] for i in range(self.n))
        e2 = sum(self.x[i] * g[i] ** 2 for i in range(self.n))
        return e2 - e1 ** 2

    def m(self, b):
        """value of the cut whose side is the neighbourhood arc N(p_b)"""
        g = self.g
        return self.W - sum(self.x[j] * g[j] for j in range(self.n) if self.adj[b][j])

    def bound(self, kk):
        g = self.g
        num = sum(self.x[i] * g[i] ** kk * self.m(i) for i in range(self.n))
        den = sum(self.x[i] * g[i] ** kk for i in range(self.n))
        return num / den if den else None

    # ---------- ground truth ----------------------------------------------
    def psi(self):
        best = None
        for mask in range(1 << (self.n - 1)):
            v = self.mono(mask)
            if best is None or v < best:
                best = v
        return best

    def arc_masks(self):
        out = []
        for i in range(self.n):
            for L in range(self.n + 1):
                mask = 0
                for t in range(L):
                    mask |= 1 << ((i + t) % self.n)
                out.append(mask)
        return sorted(set(out))

    def arcbound(self, with_arg=False):
        best, arg = None, None
        for mask in self.arc_masks():
            v = self.mono(mask)
            if best is None or v < best:
                best, arg = v, mask
        return (best, arg) if with_arg else best

    def arcbound_continuous(self):
        """same thing computed a second way: sweep the two endpoints over gap midpoints of
        the circle (all real arcs), 2q^2 candidates, to confirm the cyclic-interval family
        really is the whole arc family."""
        q = self.q
        cand = set()
        for a in range(2 * q):
            for b in range(2 * q):
                mask = 0
                for i, ki in enumerate(self.k):
                    t = (2 * ki - a) % (2 * q)
                    if t < (b - a) % (2 * q):
                        mask |= 1 << i
                cand.add(mask)
        return min(self.mono(mask) for mask in cand)

    # ---------- pentagonality ---------------------------------------------
    def pentagon(self):
        """all 5-block cyclic decompositions, empty blocks ALLOWED.
        returns (best bound, blocks, q-vector) or None."""
        n = self.n
        best = None
        for cuts in combinations_with_replacement(range(n), 5):
            c = list(cuts)
            blocks = [list(range(c[i], c[i + 1])) for i in range(4)]
            blocks.append(list(range(c[4], n)) + list(range(0, c[0])))
            allidx = sorted(t for b in blocks for t in b)
            assert allidx == list(range(n)), (cuts, blocks)
            ok = True
            for i in range(5):
                u = blocks[i] + blocks[(i + 1) % 5]
                for p, r in combinations(u, 2):
                    if self.adj[p][r]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            qv = [sum(self.x[t] for t in b) for b in blocks]
            vals = []
            for i in range(5):
                vals.append(sum(self.x[p] * self.x[r]
                                for p in blocks[(i + 2) % 5] for r in blocks[(i + 4) % 5]
                                if self.adj[p][r]))
            v = min(vals)
            if best is None or v < best[0]:
                best = (v, blocks, qv, vals)
        return best

    def hom_C5(self):
        """independent check: does the far-graph admit ANY homomorphism to C5
        (no cyclic-order requirement)?  DFS with pruning."""
        n = self.n
        nb = [[j for j in range(n) if self.adj[i][j]] for i in range(n)]
        c5 = [[(a - b) % 5 in (1, 4) for b in range(5)] for a in range(5)]
        col = [-1] * n

        def bt(i):
            if i == n:
                return True
            for c in range(5):
                if all(col[j] < 0 or c5[c][col[j]] for j in nb[i]):
                    col[i] = c
                    if bt(i + 1):
                        return True
                    col[i] = -1
            return False
        return bt(0)


def gam(q, w):
    return M(q, [(k, w[k]) for k in range(q)])


WIT = [
    ("W1 half-arc killer  G8", gam(8, [0, 1, 0, 1, 2, 0, 2, 1])),
    ("W1' same on         G11", gam(11, [0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 1])),
    ("W1'' same on        G16", gam(16, [0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 1])),
    ("W2 five-atom extremal G5", gam(5, [1] * 5)),
    ("W3 uniform          G18", gam(18, [1] * 18)),
    ("W4 uniform          G20", gam(20, [1] * 20)),
    ("W5 three-atom path  G12", gam(12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0])),
    ("W6 seven-atom       G7", gam(7, [1] * 7)),
    ("W7 unequal five-atom G20", gam(20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0,
                                          0, 0, 0, 1, 3])),
    ("R1 Gamma_11 residual G11", gam(11, [F(1, 17), F(3, 17), F(3, 34), 0, F(3, 17), F(3, 17),
                                          0, 0, F(5, 34), F(5, 34), F(1, 34)])),
    ("R2 Gamma_40 case    G40", M(40, [(1, 8), (7, 11), (16, 12), (21, 12), (32, 11)])),
]

CE = M(20, [(k, 1) for k in (0, 1, 6, 7, 12, 13, 14, 19)])          # the item-7 witness
CE8 = gam(8, [1] * 8)                                               # equally spaced Wagner


if __name__ == '__main__':
    print("independent engine, exact.  1/25 =", float(TARGET))
    hdr = f"{'measure':26s} {'n':>2s} {'W':>9s} {'A':>9s} {'b0':>9s} {'b1':>9s} {'b2':>9s} " \
          f"{'ARC':>9s} {'psi':>9s} pent homC5"
    print(hdr)
    for tag, mu in WIT + [("CE V8 on G20 (item 7)", CE), ("CE V8 equally spaced G8", CE8)]:
        A = mu.W - 2 * mu.T
        pb = mu.pentagon()
        arc = mu.arcbound()
        psi = mu.psi()
        assert psi <= arc, (tag, "psi > arcbound!")
        print(f"{tag:26s} {mu.n:2d} {float(mu.W):9.6f} {float(A):9.6f} {float(mu.bound(0)):9.6f} "
              f"{float(mu.bound(1)):9.6f} {float(mu.bound(2)):9.6f} {float(arc):9.6f} "
              f"{float(psi):9.6f} {'Y' if pb else 'n':4s} {'Y' if mu.hom_C5() else 'n'}")
        if pb:
            assert pb[0] >= arc, (tag, "pentagon bound below ARCBOUND")
            assert pb[0] <= TARGET, (tag, "pentagon bound above 1/25")
