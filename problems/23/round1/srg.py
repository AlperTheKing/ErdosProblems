"""
Triangle-free strongly regular graphs: exact construction, exact spectral lower
bound on bip, and the resulting EXACT odd-cycle-LP integrality gaps.

For a d-regular graph on N vertices with m edges,
    maxcut(G) = m/2 - (1/4) min_{x in {+-1}^N} x^T A x
and writing x = c*1 + x' with x' perp 1 (so 1^T A x' = d 1^T x' = 0),
    x^T A x = c^2 N d + x'^T A x' >= c^2 N d + lam_min' * (N - c^2 N) >= lam_min' * N
whenever lam_min' <= 0 <= d, where lam_min' is the least eigenvalue of A on 1^perp.
Hence
    maxcut(G) <= m/2 - N*lam_min'/4     and    bip(G) >= m/2 + N*lam_min'/4.
For a strongly regular graph, lam_min' is an integer root of a quadratic that we
verify by an EXACT integer matrix identity  A^2 = d I + lam A + mu (J - I - A).

Meanwhile every triangle-free graph has odd girth >= 5, so y == 1/5 is a feasible
fractional odd-cycle edge cover and
    tau*(G) <= |E|/5.
Any graph with  m/2 + N*lam_min'/4  >  m/5  therefore has an odd-cycle LP
integrality gap, certified entirely in integer arithmetic.
"""
from fractions import Fraction
from itertools import combinations
import numpy as np


# ------------------------------------------------------------------ graphs --

def hoffman_singleton():
    """Standard construction: 5 pentagons P_h, 5 pentagrams Q_i,
       P_h[j] ~ P_h[j+-1], Q_i[j] ~ Q_i[j+-2], P_h[j] ~ Q_i[h*i + j mod 5]."""
    def P(h, j):
        return h * 5 + (j % 5)

    def Q(i, j):
        return 25 + i * 5 + (j % 5)

    E = set()
    for h in range(5):
        for j in range(5):
            E.add(tuple(sorted((P(h, j), P(h, j + 1)))))
            E.add(tuple(sorted((Q(h, j), Q(h, j + 2)))))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.add(tuple(sorted((P(h, j), Q(i, (h * i + j) % 5)))))
    return 50, sorted(E)


def golay24():
    """Extended binary Golay code [24,12,8] as 4096 codewords (ints, 24 bits).
    Built from the cyclic [23,12,7] Golay code with generator polynomial
    g(x) = x^11 + x^10 + x^6 + x^5 + x^4 + x^2 + 1, plus an overall parity bit."""
    gpoly = 0
    for e in (11, 10, 6, 5, 4, 2, 0):
        gpoly |= 1 << e
    rows = []
    for i in range(12):
        w = gpoly << i                      # degree <= 22, fits 23 bits
        assert w >> 23 == 0
        if bin(w).count("1") % 2 == 1:      # append overall parity as bit 23
            w |= 1 << 23
        rows.append(w)
    words = set()
    for mask in range(1 << 12):
        w = 0
        mm = mask
        k = 0
        while mm:
            if mm & 1:
                w ^= rows[k]
            mm >>= 1
            k += 1
        words.add(w)
    return sorted(words)


def steiner_3_6_22():
    """S(3,6,22): the 77 blocks, as frozensets of {0..21}."""
    words = golay24()
    wt8 = [w for w in words if bin(w).count("1") == 8]
    assert len(wt8) == 759, len(wt8)
    blocks = []
    for w in wt8:
        if (w & 1) and ((w >> 1) & 1):
            s = frozenset(b - 2 for b in range(2, 24) if (w >> b) & 1)
            assert len(s) == 6
            blocks.append(s)
    assert len(blocks) == 77, len(blocks)
    # verify the 3-design property exactly
    cover = {}
    for B in blocks:
        for t in combinations(sorted(B), 3):
            cover[t] = cover.get(t, 0) + 1
    assert len(cover) == 1540 and set(cover.values()) == {1}
    return blocks


def higman_sims():
    """100 vertices: 0 = 'infinity', 1..22 = points, 23..99 = blocks."""
    blocks = steiner_3_6_22()
    E = set()
    for p in range(22):
        E.add((0, 1 + p))
    for k, B in enumerate(blocks):
        for p in B:
            E.add(tuple(sorted((1 + p, 23 + k))))
    for k in range(77):
        for l in range(k + 1, 77):
            if not (blocks[k] & blocks[l]):
                E.add((23 + k, 23 + l))
    return 100, sorted(E)


def m22_graph():
    """The 77 blocks of S(3,6,22), adjacent iff disjoint: srg(77,16,0,4)."""
    blocks = steiner_3_6_22()
    E = set()
    for k in range(77):
        for l in range(k + 1, 77):
            if not (blocks[k] & blocks[l]):
                E.add((k, l))
    return 77, sorted(E)


def gewirtz():
    """srg(56,10,0,2): blocks of S(3,6,22) avoiding a fixed point, adjacent iff
    disjoint."""
    blocks = [B for B in steiner_3_6_22() if 0 not in B]
    assert len(blocks) == 56, len(blocks)
    E = set()
    for k in range(56):
        for l in range(k + 1, 56):
            if not (blocks[k] & blocks[l]):
                E.add((k, l))
    return 56, sorted(E)


def clebsch():
    """Folded 5-cube: F_2^4 with u~v iff u+v in {e1,e2,e3,e4,1111}."""
    S = [1, 2, 4, 8, 15]
    E = set()
    for u in range(16):
        for s in S:
            v = u ^ s
            E.add(tuple(sorted((u, v))))
    return 16, sorted(E)


# ------------------------------------------------------------------ checks --

def adjmat(n, E):
    A = np.zeros((n, n), dtype=np.int64)
    for u, v in E:
        A[u, v] = A[v, u] = 1
    return A


def check_srg(n, E, d, lam, mu, name):
    A = adjmat(n, E)
    assert all(A[i].sum() == d for i in range(n)), f"{name}: not {d}-regular"
    J = np.ones((n, n), dtype=np.int64)
    I = np.eye(n, dtype=np.int64)
    lhs = A @ A
    rhs = d * I + lam * A + mu * (J - I - A)
    assert np.array_equal(lhs, rhs), f"{name}: srg identity fails"
    # triangle-free  <=>  lam == 0 (and A^2 identity holds)
    tf = (lam == 0)
    # least eigenvalue on 1^perp: root of  t^2 - (lam-mu) t - (d-mu) = 0
    disc = (lam - mu) ** 2 + 4 * (d - mu)
    r = int(round(disc ** 0.5))
    assert r * r == disc
    s = ((lam - mu) - r) // 2
    assert (lam - mu - r) % 2 == 0
    # exact verification that s is an eigenvalue-root
    assert s * s - (lam - mu) * s - (d - mu) == 0
    m = len(E)
    # maxcut <= m/2 - n*s/4 ; bip >= m - that
    bip_lb = Fraction(m, 2) + Fraction(n * s, 4)
    tau_ub = Fraction(m, 5)
    return dict(name=name, n=n, m=m, d=d, lam=lam, mu=mu, lam_min=s,
                triangle_free=tf, bip_lb=bip_lb, tau_ub=tau_ub,
                N2_25=Fraction(n * n, 25))


def local_search_cut(n, E, iters=400, seed=1):
    """Heuristic: find a cut with few monochromatic edges (UPPER bound on bip).
    Only used to *propose*; the returned count is then recomputed exactly."""
    import random
    rng = random.Random(seed)
    nbr = [[] for _ in range(n)]
    for u, v in E:
        nbr[u].append(v)
        nbr[v].append(u)
    best = None
    for _ in range(iters):
        side = [rng.randrange(2) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            order = list(range(n))
            rng.shuffle(order)
            for v in order:
                same = sum(1 for w in nbr[v] if side[w] == side[v])
                diff = len(nbr[v]) - same
                if same > diff:
                    side[v] ^= 1
                    improved = True
        mono = sum(1 for u, v in E if side[u] == side[v])
        if best is None or mono < best[0]:
            best = (mono, side[:])
    return best


def exact_mono(E, side):
    return sum(1 for u, v in E if side[u] == side[v])


if __name__ == "__main__":
    specs = [
        (clebsch(), 5, 0, 2, "Clebsch srg(16,5,0,2)"),
        (hoffman_singleton(), 7, 0, 1, "Hoffman-Singleton srg(50,7,0,1)"),
        (gewirtz(), 10, 0, 2, "Gewirtz srg(56,10,0,2)"),
        (m22_graph(), 16, 0, 4, "M22 graph srg(77,16,0,4)"),
        (higman_sims(), 22, 0, 6, "Higman-Sims srg(100,22,0,6)"),
    ]
    print(f"{'graph':32s} {'N':>4s} {'m':>5s} {'lmin':>5s} {'bip>=':>8s} "
          f"{'tau*<=':>8s} {'gap?':>5s} {'bip_ub':>7s} {'N^2/25':>8s} {'bip/N^2':>9s}")
    for (n, E), d, lam, mu, name in specs:
        info = check_srg(n, E, d, lam, mu, name)
        assert info["triangle_free"]
        mono, side = local_search_cut(n, E, iters=300 if n <= 100 else 50)
        mono = exact_mono(E, side)          # exact recount
        gap = "YES" if info["bip_lb"] > info["tau_ub"] else "no"
        print(f"{name:32s} {n:4d} {info['m']:5d} {info['lam_min']:5d} "
              f"{str(info['bip_lb']):>8s} {str(info['tau_ub']):>8s} {gap:>5s} "
              f"{mono:7d} {str(info['N2_25']):>8s} "
              f"{float(info['bip_lb'])/(n*n):9.5f}")
        if mono == info["bip_lb"]:
            print(f"{'':32s}   -> bip = {mono} EXACTLY (spectral lower bound attained "
                  f"by an explicit cut)")
