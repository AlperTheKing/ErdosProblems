"""P2 / round 6 - EXACT verification, implementation #1.

Checks, in exact rational arithmetic, the quantities of the item-7 criterion for a measure on the
circle given as a finite list of (position, weight) with positions in Q/Z and weights in Q:

    adjacency      u ~ v   iff   circular distance d(u,v) > 1/3
    g(b)           = sum_{v ~ b} x_v                          (far mass = weighted degree)
    W              = sum_{u<v, u~v} x_u x_v
    T              = sum_{u<v, u~v} d(u,v) x_u x_v
    A              = W - 2T                                   (half-arc average)
    m(b)           = W - sum_{v ~ b} x_v g(v)                  (value of the neighbourhood cut N(b))
    bound_k        = sum_b x_b g(b)^k m(b) / sum_b x_b g(b)^k
    CRIT           = min(A, bound_0, ..., bound_K)
    ARCBOUND       = min over ALL arc cuts of the monochromatic mass   (brute force)
    psi            = min over ALL cuts of the monochromatic mass       (brute force, N <= 22)

Everything is Fraction; no floating point is used on any acceptance path.

Run:  python P2_verify.py
"""
from fractions import Fraction as F
from itertools import combinations
import sys

ONE_THIRD = F(1, 3)
TARGET = F(1, 25)


# --------------------------------------------------------------------------- basic geometry
def cdist(p, q):
    """exact circular distance on R/Z."""
    t = (p - q) % 1
    return min(t, 1 - t)


class Config:
    """A finite measure on the circle: positions (Fractions in [0,1)) and weights summing to 1."""

    def __init__(self, pos, wt, name=""):
        assert len(pos) == len(wt)
        self.name = name
        self.pos = [F(p) % 1 for p in pos]
        s = sum(F(w) for w in wt)
        assert s > 0
        self.x = [F(w) / s for w in wt]
        self.n = len(pos)
        assert len(set(self.pos)) == self.n, "duplicate positions"
        self.d = [[cdist(self.pos[i], self.pos[j]) for j in range(self.n)] for i in range(self.n)]
        self.adj = [[i != j and self.d[i][j] > ONE_THIRD for j in range(self.n)] for i in range(self.n)]

    # ---- primary invariants
    def W(self):
        return sum(self.x[u] * self.x[v] for u, v in combinations(range(self.n), 2) if self.adj[u][v])

    def T(self):
        return sum(self.d[u][v] * self.x[u] * self.x[v]
                   for u, v in combinations(range(self.n), 2) if self.adj[u][v])

    def g(self):
        return [sum(self.x[v] for v in range(self.n) if self.adj[b][v]) for b in range(self.n)]

    def A(self):
        return self.W() - 2 * self.T()

    def m(self):
        W, g = self.W(), self.g()
        return [W - sum(self.x[v] * g[v] for v in range(self.n) if self.adj[b][v])
                for b in range(self.n)]

    def bound(self, k):
        g, m = self.g(), self.m()
        num = sum(self.x[b] * g[b] ** k * m[b] for b in range(self.n))
        den = sum(self.x[b] * g[b] ** k for b in range(self.n))
        assert den > 0
        return num / den

    def var_g(self):
        g = self.g()
        e1 = sum(self.x[b] * g[b] for b in range(self.n))
        e2 = sum(self.x[b] * g[b] ** 2 for b in range(self.n))
        return e2 - e1 * e1

    def crit(self, K=12):
        vals = [self.A()] + [self.bound(k) for k in range(K + 1)]
        return min(vals), vals

    # ---- ground truth
    def mono(self, side):
        """monochromatic mass of the cut with the given side (a set of vertex indices)."""
        return sum(self.x[u] * self.x[v] for u, v in combinations(range(self.n), 2)
                   if self.adj[u][v] and ((u in side) == (v in side)))

    def arcbound(self):
        """min over all arc cuts.  An arc cut side is a cyclic interval of the position order."""
        order = sorted(range(self.n), key=lambda i: self.pos[i])
        best = self.W()          # empty arc
        bestarc = (0, 0)
        for i in range(self.n):
            side = set()
            for l in range(1, self.n):
                side.add(order[(i + l - 1) % self.n])
                v = self.mono(side)
                if v < best:
                    best, bestarc = v, (i, l)
        return best, bestarc

    def psi(self):
        """min over ALL cuts (brute force).  Only for small n."""
        assert self.n <= 24
        best = self.W()
        bestside = frozenset()
        for mask in range(1 << (self.n - 1)):
            side = {i for i in range(self.n - 1) if mask >> i & 1}
            v = self.mono(side)
            if v < best:
                best, bestside = v, frozenset(side)
        return best, bestside


# --------------------------------------------------------------------------- the constructions
def three_cluster(n, eps, name=None):
    """n atoms per cluster, clusters at 0, 1/3, 2/3, offsets eps, 2eps, ..., n eps, equal weights.

    (j,i) ~ (j+1,i') iff i' > i;  atoms at equal offsets in different clusters sit at distance
    exactly 1/3 and are therefore NOT adjacent."""
    eps = F(eps)
    pos, wt = [], []
    for j in range(3):
        for i in range(1, n + 1):
            pos.append(F(j, 3) + i * eps)
            wt.append(1)
    return Config(pos, wt, name or f"3cluster(n={n},eps={eps})")


def three_cluster_robust(n, eps, eta, name=None):
    """Same, but cluster j is shifted by -j*eta with 0 < eta << eps, so that NO pair of atoms sits
    at distance exactly 1/3 (the configuration is then stable under small perturbations)."""
    eps, eta = F(eps), F(eta)
    pos, wt = [], []
    for j in range(3):
        for i in range(1, n + 1):
            pos.append((F(j, 3) + i * eps - j * eta) % 1)
            wt.append(1)
    return Config(pos, wt, name or f"3cluster-robust(n={n},eps={eps},eta={eta})")


def c5():
    return Config([F(i, 5) for i in range(5)], [1] * 5, "C5 (extremal)")


def gamma_uniform(m):
    return Config([F(i, m) for i in range(m)], [1] * m, f"Gamma_{m} uniform")


# --------------------------------------------------------------------------- reporting helpers
def report(cfg, K=8, do_psi=True, do_arc=True):
    W, T, Ahalf = cfg.W(), cfg.T(), cfg.A()
    g, m = cfg.g(), cfg.m()
    bs = [cfg.bound(k) for k in range(K + 1)]
    cr = min([Ahalf] + bs)
    print(f"--- {cfg.name}   N={cfg.n}")
    print(f"    W        = {W} = {float(W):.6f}      (need (0.12,0.2) for the open region)")
    print(f"    T/W      = {T/W if W else '-'} = {float(T/W) if W else 0:.6f}")
    print(f"    Var(g)   = {cfg.var_g()} = {float(cfg.var_g()):.8f}")
    print(f"    A        = {Ahalf} = {float(Ahalf):.6f}   {'>' if Ahalf > TARGET else '<='} 1/25")
    print(f"    bound_0  = {bs[0]} = {float(bs[0]):.6f}   {'>' if bs[0] > TARGET else '<='} 1/25")
    print(f"    bound_k  = " + ", ".join(f"{float(b):.6f}" for b in bs))
    print(f"    min_b m(b) = {min(m)} = {float(min(m)):.6f}   "
          f"{'>' if min(m) > TARGET else '<='} 1/25   (the FULL neighbourhood-cut family)")
    print(f"    CRIT     = {cr} = {float(cr):.6f}   "
          f"{'*** CRITERION FALSIFIER ***' if cr > TARGET else 'closed by the criterion'}")
    if do_arc:
        ab, arc = cfg.arcbound()
        print(f"    ARCBOUND = {ab} = {float(ab):.6f}   {'>' if ab > TARGET else '<='} 1/25"
              f"   (arc start/len = {arc})")
    if do_psi and cfg.n <= 22:
        ps, side = cfg.psi()
        print(f"    psi      = {ps} = {float(ps):.6f}   {'>' if ps > TARGET else '<='} 1/25")
    sys.stdout.flush()
    return cr


# --------------------------------------------------------------------------- main
if __name__ == '__main__':
    print("=" * 100)
    print("CALIBRATION: the extremal C5 must give A = bound_k = ARCBOUND = psi = 1/25 exactly")
    print("=" * 100)
    cfg = c5()
    report(cfg, K=6)
    assert cfg.A() == TARGET and all(cfg.bound(k) == TARGET for k in range(7))
    assert cfg.arcbound()[0] == TARGET and cfg.psi()[0] == TARGET
    print("    [calibration OK: every quantity is exactly 1/25]\n")

    print("=" * 100)
    print("CALIBRATION 2: uniform measures on Gamma_m (far-regular, so every bound_k = W - 4W^2)")
    print("=" * 100)
    for m in (7, 8, 11, 14, 18):
        c = gamma_uniform(m)
        report(c, K=4, do_psi=(m <= 18))
        gg = c.g()
        assert len(set(gg)) == 1, "uniform on Gamma_m should be far-regular"
        assert all(c.bound(k) == c.W() - 4 * c.W() ** 2 for k in range(5))
    print()

    print("=" * 100)
    print("THE FALSIFIER FAMILY: 3 clusters at 0, 1/3, 2/3 with n atoms each")
    print("=" * 100)
    for n, eps in ((4, F(1, 300)), (4, F(1, 1200)), (5, F(1, 240)), (5, F(1, 1000)),
                   (6, F(1, 1000)), (8, F(1, 4000))):
        report(three_cluster(n, eps), K=8, do_psi=(3 * n <= 21))
        print()

    print("=" * 100)
    print("THE ROBUST FALSIFIER: same but no pair at distance exactly 1/3")
    print("=" * 100)
    for n, eps, eta in ((5, F(1, 100), F(1, 10000)), (5, F(1, 300), F(1, 30000)),
                        (6, F(1, 200), F(1, 20000)), (7, F(1, 300), F(1, 30000))):
        report(three_cluster_robust(n, eps, eta), K=10, do_psi=(3 * n <= 21))
        print()
