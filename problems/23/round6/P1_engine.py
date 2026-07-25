"""P1 exact engine: probability measures on the circle R/Z with the far-relation d(x,y) > 1/3.

Everything is exact (fractions.Fraction).  A measure is a list of (position, weight) with
positions in [0,1) and weights summing to 1.

Quantities (all as in the round-6 chain):
    g(x)    = mu(N(x)),  N(x) = (x+1/3, x+2/3)          weighted degree
    W       = (1/2) int g dmu                           adjacent mass
    T       = (1/2) int int_{d>1/3} d                   mass-weighted distance
    rho     = T/W                                       mean adjacent distance
    A       = W - 2T = W(1-2 rho)                       half-arc bound (average of the ell=1/2 cuts)
    m(b)    = W - int_{N(b)} g dmu                      the arc cut at the 1/3-arc N(b)
    bound_k = (int g^k m dmu)/(int g^k dmu)
    nu      = g dmu (total mass 2W)
    kappa   = max over closed 1/3-windows I of nu(I) / (2W)
    B       = W - max_I nu(I) = W(1 - 2 kappa)          the best 1/3-arc cut
    ARCBOUND= min over ALL arc cuts of the monochromatic mass  (ground truth)

Facts used everywhere: a set of diameter <= 1/3 is independent (adjacency needs d > 1/3
STRICTLY), so a closed arc of length exactly 1/3 carries no edges and the cut it defines has
value W - nu(I).
"""
from fractions import Fraction as F
from itertools import combinations

THIRD = F(1, 3)
TARGET = F(1, 25)


def dist(p, q):
    """circular distance in R/Z"""
    d = abs(p - q) % 1
    return min(d, 1 - d)


class Meas:
    def __init__(self, pos, wt, normalize=True):
        pos = [F(p) % 1 for p in pos]
        wt = [F(w) for w in wt]
        # merge duplicates, drop zeros
        d = {}
        for p, w in zip(pos, wt):
            if w != 0:
                d[p] = d.get(p, F(0)) + w
        self.pos = sorted(d)
        self.wt = [d[p] for p in self.pos]
        if normalize:
            s = sum(self.wt)
            self.wt = [w / s for w in self.wt]
        self.n = len(self.pos)
        self._prep()

    def _prep(self):
        n, P, X = self.n, self.pos, self.wt
        self.adj = [[False] * n for _ in range(n)]
        self.d = [[F(0)] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dij = dist(P[i], P[j])
                self.d[i][j] = self.d[j][i] = dij
                a = dij > THIRD
                self.adj[i][j] = self.adj[j][i] = a
        self.g = [sum(X[j] for j in range(n) if self.adj[i][j]) for i in range(n)]
        self.W = sum(X[i] * self.g[i] for i in range(n)) / 2
        self.T = sum(X[i] * X[j] * self.d[i][j] for i in range(n) for j in range(i + 1, n)
                     if self.adj[i][j])
        self.nu = [X[i] * self.g[i] for i in range(n)]

    # ---------------- the proved bounds ----------------
    @property
    def A(self):
        return self.W - 2 * self.T

    @property
    def rho(self):
        return self.T / self.W if self.W else None

    @property
    def Eg2(self):
        return sum(self.wt[i] * self.g[i] ** 2 for i in range(self.n))

    @property
    def Varg(self):
        return self.Eg2 - 4 * self.W ** 2

    def m(self, i):
        """value of the arc cut at N(p_i) = (p_i+1/3, p_i+2/3)"""
        return self.W - sum(self.wt[j] * self.g[j] for j in range(self.n) if self.adj[i][j])

    def bound(self, k):
        num = sum(self.wt[i] * self.g[i] ** k * self.m(i) for i in range(self.n))
        den = sum(self.wt[i] * self.g[i] ** k for i in range(self.n))
        return num / den if den else None

    def best_window(self):
        """max over closed 1/3-windows of nu(I); returns (value, start atom index)."""
        best, arg = F(-1), None
        for i in range(self.n):
            a = self.pos[i]
            v = F(0)
            for j in range(self.n):
                off = (self.pos[j] - a) % 1
                if off <= THIRD:
                    v += self.nu[j]
            if v > best:
                best, arg = v, i
        return best, arg

    @property
    def B(self):
        return self.W - self.best_window()[0]

    @property
    def kappa(self):
        return self.best_window()[0] / (2 * self.W) if self.W else None

    # ---------------- ground truth ----------------
    def arcbound(self, with_arg=False):
        """min over all cyclic-interval cuts of the monochromatic mass."""
        n, X = self.n, self.wt
        best, arg = None, None
        for i in range(n):
            inI = [False] * n
            Ein = F(0)                      # edge mass inside I
            Eout = self.W                   # edge mass inside complement
            for L in range(0, n + 1):
                if L > 0:
                    v = (i + L - 1) % n
                    # v joins I
                    sin_ = sum(X[u] for u in range(n) if inI[u] and self.adj[u][v])
                    sout = self.g[v] - sin_
                    Ein += X[v] * sin_
                    Eout -= X[v] * sout
                    inI[v] = True
                val = Ein + Eout
                if best is None or val < best:
                    best, arg = val, (i, L)
        return (best, arg) if with_arg else best

    # ---------------- reporting ----------------
    def summary(self):
        A, B = self.A, self.B
        return dict(n=self.n, W=self.W, rho=self.rho, kappa=self.kappa, A=A, B=B,
                    b0=self.bound(0), b1=self.bound(1), b2=self.bound(2),
                    Varg=self.Varg, minAB=min(A, B), arc=self.arcbound())


def gamma(m, w):
    """weights w on the m equally spaced points of Gamma_m"""
    return Meas([F(k, m) for k in range(m)], [F(x) for x in w])


# ------------------------------------------------------------------ witnesses
WITNESSES = [
    ("W1 half-arc killer   G8", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
    ("W1' same on          G11", 11, [0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 1]),
    ("W1'' same on         G16", 16, [0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 1]),
    ("W2 five-atom extremal G5", 5, [1, 1, 1, 1, 1]),
    ("W3 uniform           G18", 18, [1] * 18),
    ("W4 uniform           G20", 20, [1] * 20),
    ("W5 three-atom path   G12", 12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0]),
    ("W6 seven-atom        G7", 7, [1] * 7),
    ("W7 unequal five-atom G20", 20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 1, 3]),
    ("R1 Gamma_11 residual G11", 11, [F(1, 17), F(3, 17), F(3, 34), 0, F(3, 17), F(3, 17), 0, 0,
                                      F(5, 34), F(5, 34), F(1, 34)]),
    ("R2 Gamma_40 case     G40", 40, [0] * 1 + [8] + [0] * 5 + [11] + [0] * 8 + [12] + [0] * 4
                                     + [12] + [0] * 10 + [11] + [0] * 7),
]


def show(tag, mu, extra_k=()):
    s = mu.summary()
    print(f"{tag:26s} n={s['n']:3d} W={float(s['W']):.6f} rho={float(s['rho']):.6f} "
          f"kap={float(s['kappa']):.6f} A={float(s['A']):.6f} B={float(s['B']):.6f} "
          f"b0={float(s['b0']):.6f} b1={float(s['b1']):.6f} "
          f"min(A,B)={float(s['minAB']):.6f} ARC={float(s['arc']):.6f} "
          f"{'OK' if s['minAB'] <= TARGET else '*** min(A,B) > 1/25 ***'}")
    return s


if __name__ == '__main__':
    print("exact check of the two-family bound  min(A,B) <= 1/25  on the round-5 witnesses")
    print("(A = W-2T half-arc average, B = best 1/3-arc cut; both are >= ARCBOUND >= psi)\n")
    worst = None
    for name, m, w in WITNESSES:
        mu = gamma(m, w)
        s = show(name, mu)
        assert s['A'] >= s['arc'], (name, "A is not an upper bound!")
        assert s['B'] >= s['arc'], (name, "B is not an upper bound!")
        assert s['b0'] >= s['arc']
        if worst is None or s['minAB'] > worst[1]:
            worst = (name, s['minAB'])
    print(f"\nworst witness for min(A,B): {worst[0]}  {worst[1]} = {float(worst[1]):.6f}"
          f"   (1/25 = 0.04)")
