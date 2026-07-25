"""P2 / round 6 - EXACT verification, implementation #2 (INDEPENDENT of P2_verify.py).

Deliberately different code path everywhere:

  * positions are INTEGERS p_i over a common denominator M; adjacency is decided by the integer
    test  3 * min((p_i-p_j) mod M, (p_j-p_i) mod M) > M   (no Fraction comparison, no modular
    arithmetic on rationals);
  * weights are integers w_i over a common denominator q, and every quantity is computed as an
    integer numerator over an explicit integer denominator, converted to Fraction only at the end;
  * A is NOT computed as W - 2T; it is computed directly as the double sum
        A = sum_{u != v, d>1/3} (1/2 - d(u,v)) x_u x_v   (over ORDERED pairs)
    which is the "half-arc average" form of item 5;
  * m(b) is NOT computed from the identity m(b) = W - sum_{v~b} x_v g(v); the neighbourhood cut
    N(b) = {v : d(b,v) > 1/3} is built explicitly as a vertex set and its monochromatic mass is
    evaluated from scratch by a generic cut evaluator.  (This independently re-derives item 4.)
  * ARCBOUND enumerates cut points in the GAPS between consecutive atoms (two independent cut
    points), instead of (start, length) pairs.

Run:  python P2_verify2.py
"""
from fractions import Fraction as F
from itertools import combinations
import sys

TARGET = F(1, 25)
CEILING = F(1, 18)


class IConfig:
    """positions p_i in Z/M, integer weights w_i (sum q)."""

    def __init__(self, M, P, Wt, name=""):
        self.M, self.name = M, name
        self.P = [p % M for p in P]
        self.Wt = list(Wt)
        self.q = sum(Wt)
        self.n = len(P)
        assert len(set(self.P)) == self.n
        # integer circular distance numerator: dist = D[i][j] / M
        self.D = [[0] * self.n for _ in range(self.n)]
        self.adj = [[False] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue
                t = (self.P[i] - self.P[j]) % M
                d = min(t, M - t)
                self.D[i][j] = d
                self.adj[i][j] = (3 * d > M)

    def x(self, i):
        return F(self.Wt[i], self.q)

    # ---------- generic cut evaluator (the ONLY route to every cut value in this file)
    def cutvalue(self, side):
        """monochromatic mass of the cut (side, complement), exact."""
        num = 0
        for i, j in combinations(range(self.n), 2):
            if self.adj[i][j] and ((i in side) == (j in side)):
                num += self.Wt[i] * self.Wt[j]
        return F(num, self.q * self.q)

    def W(self):
        return self.cutvalue(set(range(self.n)))          # everything on one side = all edges mono

    def A(self):
        """direct double sum of (1/2 - d) over ordered far pairs."""
        tot = F(0)
        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.adj[i][j]:
                    tot += (F(1, 2) - F(self.D[i][j], self.M)) * self.x(i) * self.x(j)
        return tot

    def g(self, b):
        return sum(self.x(v) for v in range(self.n) if self.adj[b][v])

    def nbhd_cut(self, b):
        """m(b) computed as the value of the explicit cut whose side is N(b)."""
        side = {v for v in range(self.n) if self.adj[b][v]}
        return self.cutvalue(side), side

    def bounds(self, K):
        gs = [self.g(b) for b in range(self.n)]
        ms = [self.nbhd_cut(b)[0] for b in range(self.n)]
        out = []
        for k in range(K + 1):
            num = sum(self.x(b) * gs[b] ** k * ms[b] for b in range(self.n))
            den = sum(self.x(b) * gs[b] ** k for b in range(self.n))
            out.append(num / den)
        return out, gs, ms

    def arcbound(self):
        """min over arc cuts, enumerated by two independent cut points placed in the gaps."""
        order = sorted(range(self.n), key=lambda i: self.P[i])
        best, arg = self.W(), None
        for a in range(self.n):
            for b in range(self.n):
                if a == b:
                    continue
                # side = atoms strictly between gap a and gap b going forward
                side, t = set(), a
                while t != b:
                    side.add(order[t])
                    t = (t + 1) % self.n
                v = self.cutvalue(side)
                if v < best:
                    best, arg = v, tuple(sorted(side))
        return best, arg

    def psi(self):
        assert self.n <= 22
        best, arg = self.W(), None
        for mask in range(1 << (self.n - 1)):
            side = {i for i in range(self.n - 1) if (mask >> i) & 1}
            v = self.cutvalue(side)
            if v < best:
                best, arg = v, tuple(sorted(side))
        return best, arg


def three_cluster_int(n, den, name=None):
    """clusters at 0, 1/3, 2/3 with offsets i/den (i = 1..n); needs 3 | den... use M = 3*den."""
    M = 3 * den
    P = [j * den + 3 * i for j in range(3) for i in range(1, n + 1)]
    return IConfig(M, P, [1] * (3 * n), name or f"3cluster-int(n={n},eps=1/{den})")


def three_cluster_robust_int(n, den, shift, name=None):
    """cluster j shifted back by shift/(3*den) so that no distance is exactly 1/3."""
    M = 3 * den
    P = [(j * den + 3 * i - j * shift) % M for j in range(3) for i in range(1, n + 1)]
    return IConfig(M, P, [1] * (3 * n), name or f"3cluster-robust-int(n={n},eps=1/{den},shift={shift}/{M})")


def show(cfg, K=10, do_psi=True):
    W = cfg.W()
    A = cfg.A()
    bs, gs, ms = cfg.bounds(K)
    M = min(ms)
    crit = min([A] + bs)
    print(f"--- {cfg.name}  N={cfg.n}  M={cfg.M}")
    print(f"    W = {W} ({float(W):.6f})   Var(g)=0? {len(set(gs)) == 1}   g values = {sorted(set(gs))}")
    print(f"    A       = {A} = {float(A):.7f}  {'>' if A > TARGET else '<='} 1/25")
    print(f"    bound_k = " + ", ".join(f"{float(b):.6f}" for b in bs))
    print(f"    min_b m(b) = {M} = {float(M):.7f}  {'>' if M > TARGET else '<='} 1/25")
    print(f"    CRIT    = {crit} = {float(crit):.7f}  ->  "
          f"{'FALSIFIER (CRIT > 1/25)' if crit > TARGET else 'closed'}"
          f"   [ratio to 1/25 = {float(crit) * 25:.4f}]")
    ab, _ = cfg.arcbound()
    print(f"    ARCBOUND= {ab} = {float(ab):.7f}  {'>' if ab > TARGET else '<='} 1/25")
    if do_psi and cfg.n <= 22:
        ps, _ = cfg.psi()
        print(f"    psi     = {ps} = {float(ps):.7f}  {'>' if ps > TARGET else '<='} 1/25")
    assert crit < CEILING, "the proved ceiling CRIT < 1/18 was violated - re-check the theory"
    sys.stdout.flush()
    return crit, A, bs, ab


if __name__ == '__main__':
    print("=" * 100)
    print("independent implementation #2 - calibration on C5 (must be exactly 1/25 everywhere)")
    print("=" * 100)
    c5 = IConfig(5, [0, 1, 2, 3, 4], [1] * 5, "C5")
    crit, A, bs, ab = show(c5, K=6)
    assert A == TARGET and all(b == TARGET for b in bs) and ab == TARGET and c5.psi()[0] == TARGET
    print("    [OK]\n")

    print("=" * 100)
    print("independent re-verification of the falsifiers")
    print("=" * 100)
    tested = []
    for n, den in ((4, 300), (4, 1200), (5, 240), (5, 1000), (6, 1000)):
        tested.append(show(three_cluster_int(n, den), K=10, do_psi=(3 * n <= 21)))
        print()
    for n, den, sh in ((5, 100, 1), (5, 300, 1), (6, 200, 1), (7, 300, 1)):
        tested.append(show(three_cluster_robust_int(n, den, sh), K=10, do_psi=(3 * n <= 21)))
        print()

    nfals = sum(1 for c, *_ in tested if c > TARGET)
    print(f"{nfals} of {len(tested)} configurations are criterion falsifiers under implementation #2")

    print("\n" + "=" * 100)
    print("CROSS-CHECK against implementation #1 (P2_verify.py)")
    print("=" * 100)
    import P2_verify as V1
    pairs = [(V1.three_cluster(4, F(1, 300)), three_cluster_int(4, 300)),
             (V1.three_cluster(5, F(1, 240)), three_cluster_int(5, 240)),
             (V1.three_cluster(5, F(1, 1000)), three_cluster_int(5, 1000)),
             (V1.three_cluster(6, F(1, 1000)), three_cluster_int(6, 1000)),
             # eta = 1/(3*den) so that the two parametrisations describe the SAME configuration
             (V1.three_cluster_robust(5, F(1, 100), F(1, 300)), three_cluster_robust_int(5, 100, 1)),
             (V1.three_cluster_robust(5, F(1, 300), F(1, 900)), three_cluster_robust_int(5, 300, 1)),
             (V1.three_cluster_robust(6, F(1, 200), F(1, 600)), three_cluster_robust_int(6, 200, 1)),
             (V1.three_cluster_robust(7, F(1, 300), F(1, 900)), three_cluster_robust_int(7, 300, 1))]
    for a, b in pairs:
        b_bounds, _, b_ms = b.bounds(10)
        ok = (a.W() == b.W() and a.A() == b.A()
              and all(a.bound(k) == b_bounds[k] for k in range(11))
              and a.m() == b_ms and a.arcbound()[0] == b.arcbound()[0])
        print(f"    {a.name:44s} identical under both implementations: {ok}")
        assert ok
    print("\nALL EXACT CROSS-CHECKS PASSED.")
