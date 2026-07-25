"""H1 core: EXACT arc-cut computations on the circle R/Z.

Gamma: x ~ y  iff  circular distance d(x,y) > 1/3.
For an atomic probability measure mu = sum w_i delta_{p_i}:
   W        = sum over unordered adjacent pairs of w_i w_j
   mono(A)  = adjacent mass inside A  +  adjacent mass inside A^c
   ARCBOUND = min over ARCS A of mono(A)
An arc meets the atom set in a cyclic interval, and every cyclic interval is
realised by an arc, so ARCBOUND = min over cyclic intervals.

All arithmetic is Fraction / integer.  Floating point is never used.
"""
from fractions import Fraction as F

THIRD = F(1, 3)


def circdist(a, b):
    d = (a - b) % 1
    return min(d, 1 - d)


class Meas:
    """Atomic measure with exact rational positions and weights."""

    def __init__(self, pos, w, normalise=True):
        pos = [F(p) % 1 for p in pos]
        w = [F(x) for x in w]
        assert all(x > 0 for x in w)
        z = sorted(zip(pos, w))
        self.pos = [p for p, _ in z]
        self.w = [x for _, x in z]
        assert len(set(self.pos)) == len(self.pos), "duplicate positions"
        self.n = len(self.pos)
        tot = sum(self.w)
        if normalise:
            self.w = [x / tot for x in self.w]
            tot = F(1)
        self.tot = tot
        n = self.n
        self.adj = [[False] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if circdist(self.pos[i], self.pos[j]) > THIRD:
                    self.adj[i][j] = self.adj[j][i] = True
        self.W = sum(self.w[i] * self.w[j]
                     for i in range(n) for j in range(i + 1, n) if self.adj[i][j])
        # T = sum over adjacent pairs of w_i w_j d(p_i,p_j)
        self.T = sum(self.w[i] * self.w[j] * circdist(self.pos[i], self.pos[j])
                     for i in range(n) for j in range(i + 1, n) if self.adj[i][j])

    # ---- arcs -------------------------------------------------------
    def cyclic_intervals(self):
        """yield (start, length, membership tuple) for every cyclic interval."""
        n = self.n
        yield (0, 0, tuple([False] * n))
        for s in range(n):
            mem = [False] * n
            for L in range(1, n + 1):
                mem[(s + L - 1) % n] = True
                yield (s, L, tuple(mem))
            # reset
        return

    def mono_of(self, mem):
        n = self.n
        return sum(self.w[i] * self.w[j]
                   for i in range(n) for j in range(i + 1, n)
                   if self.adj[i][j] and mem[i] == mem[j])

    def arcbound(self):
        """exact ARCBOUND together with all minimising (start,length) pairs."""
        n = self.n
        best = self.W          # empty arc
        args = [(0, 0)]
        for s in range(n):
            mem = [False] * n
            cut = F(0)
            for L in range(1, n + 1):
                k = (s + L - 1) % n
                # adding atom k to the arc
                delta = F(0)
                for j in range(n):
                    if j == k or not self.adj[k][j]:
                        continue
                    if mem[j]:
                        delta -= self.w[k] * self.w[j]
                    else:
                        delta += self.w[k] * self.w[j]
                cut += delta
                mem[k] = True
                mono = self.W - cut
                if mono < best:
                    best, args = mono, [(s, L)]
                elif mono == best:
                    args.append((s, L))
        return best, args

    def arc_mem(self, s, L):
        mem = [False] * self.n
        for t in range(L):
            mem[(s + t) % self.n] = True
        return tuple(mem)

    def arc_mass(self, s, L):
        return sum(self.w[(s + t) % self.n] for t in range(L))

    # ---- derived quantities ----------------------------------------
    def qmax(self):
        """max over c of mu([c, c+1/3)) -- attained with c just at an atom."""
        best = F(0)
        for i in range(self.n):
            c = self.pos[i]
            m = sum(self.w[j] for j in range(self.n)
                    if (self.pos[j] - c) % 1 < THIRD)
            best = max(best, m)
        return best

    def balanced_arcs(self):
        """for each start s, the largest arc of mass <= 1/2 and the smallest of mass >= 1/2."""
        out = []
        for s in range(self.n):
            m = F(0)
            lo = (s, 0)
            hi = None
            for L in range(1, self.n + 1):
                m += self.w[(s + L - 1) % self.n]
                if m <= F(1, 2):
                    lo = (s, L)
                else:
                    hi = (s, L)
                    break
            out.append((lo, hi))
        return out

    def fiveblock_min(self):
        """min over choices of 5 cut points (gaps between consecutive atoms) of
        W + 4 P0 + 2 P1, i.e. 5 * (the 5-block bound).  Returns (value, cuts)."""
        from itertools import combinations
        n = self.n
        if n < 5:
            return None, None
        best = None
        bestc = None
        for cuts in combinations(range(n), 5):
            # block i = atoms [cuts[i], cuts[i+1])
            blocks = []
            for i in range(5):
                a, b = cuts[i], cuts[(i + 1) % 5]
                idx = []
                j = a
                while j != b:
                    idx.append(j)
                    j = (j + 1) % n
                blocks.append(idx)
            P0 = F(0)
            P1 = F(0)
            for i in range(5):
                B = blocks[i]
                for u in range(len(B)):
                    for v in range(u + 1, len(B)):
                        if self.adj[B[u]][B[v]]:
                            P0 += self.w[B[u]] * self.w[B[v]]
                C = blocks[(i + 1) % 5]
                for u in B:
                    for v in C:
                        if self.adj[u][v]:
                            P1 += self.w[u] * self.w[v]
            val = self.W + 4 * P0 + 2 * P1
            if best is None or val < best:
                best, bestc = val, cuts
        return best, bestc


# ---- standard test measures -----------------------------------------
def uniform_gamma(m):
    return Meas([F(j, m) for j in range(m)], [F(1)] * m)


def weighted_gamma(m, weights):
    pos = [F(j, m) for j in range(m) if weights[j] > 0]
    w = [F(weights[j]) for j in range(m) if weights[j] > 0]
    return Meas(pos, w)


def three_atom_path(eps=F(1, 100)):
    return Meas([F(0), THIRD + eps, F(2, 3) + 2 * eps], [F(1), F(1), F(1)])


def two_antipodal():
    return Meas([F(0), F(1, 2)], [F(1), F(1)])
