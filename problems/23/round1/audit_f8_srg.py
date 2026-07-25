"""INDEPENDENT verification of the section-5 SRG claims.

Higman-Sims is built from the Witt design S(5,8,24) obtained from the extended
binary Golay code (lexicographic construction), NOT from PG(2,4)+hyperovals, so
this shares no code path with f8_families.py.
"""
import numpy as np
from fractions import Fraction
from itertools import combinations
from audit_f8_lib import mk, edges, trifree, bip_exact, g6enc


# ---------------------------------------------------------------- Golay -> S(5,8,24)
def golay24():
    """extended binary Golay [24,12,8] from the QR(11) generator matrix [I | B].
    Verified here by its weight enumerator 1 + 759 x^8 + 2576 x^12 + 759 x^16 + x^24."""
    from collections import Counter as _C
    gen = None
    for g in (3189, 2787):                     # the two QR generator polys of length 23
        rows = [g << k for k in range(12)]
        cw = []
        for msk in range(1 << 12):
            c, mm = 0, msk
            while mm:
                b = (mm & -mm).bit_length() - 1
                c ^= rows[b]
                mm &= mm - 1
            cw.append(c | ((bin(c).count('1') & 1) << 23))    # overall parity bit
        if dict(_C(bin(c).count('1') for c in cw)) == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}:
            gen = rows
            code = cw
            break
    assert gen is not None, "no QR generator gave the Golay weight enumerator"
    return code


def witt_5_8_24(code):
    oct_ = sorted(c for c in code if bin(c).count('1') == 8)
    assert len(oct_) == 759, len(oct_)
    return oct_


def steiner_3_6_22(oct_):
    """blocks of S(5,8,24) through two fixed points, minus those points"""
    p, q = 22, 23
    B = []
    for o in oct_:
        if (o >> p) & 1 and (o >> q) & 1:
            B.append(frozenset(i for i in range(22) if (o >> i) & 1))
    assert len(B) == 77, len(B)
    assert all(len(b) == 6 for b in B)
    cnt = {}
    for b in B:
        for t in combinations(sorted(b), 3):
            cnt[t] = cnt.get(t, 0) + 1
    assert len(cnt) == 1540 and set(cnt.values()) == {1}, (len(cnt), set(cnt.values()))
    return B


def higman_sims(blocks):
    N = 100
    E = []
    for p in range(22):
        E.append((0, 1 + p))
    for i, B in enumerate(blocks):
        for p in B:
            E.append((1 + p, 23 + i))
    for i in range(77):
        for j in range(i + 1, 77):
            if not (blocks[i] & blocks[j]):
                E.append((23 + i, 23 + j))
    return mk(N, sorted(set(E)))


def adjmat(n, adj):
    A = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            A[i, j] = (adj[i] >> j) & 1
    return A


def srg_check(n, adj, d, lam, mu):
    A = adjmat(n, adj)
    reg = bool(np.all(A.sum(1) == d))
    I = np.eye(n, dtype=np.int64)
    J = np.ones((n, n), dtype=np.int64)
    idt = bool(np.array_equal(A @ A + (mu - lam) * A - (d - mu) * I, mu * J))
    return reg, idt


def lmin(d, lam, mu):
    b = mu - lam
    disc = b * b + 4 * (d - mu)
    r = int(round(disc ** .5))
    assert r * r == disc
    return (-b - r) // 2


def best_cut(n, adj, rounds, seed):
    rng = np.random.default_rng(seed)
    nb = [[j for j in range(n) if (adj[i] >> j) & 1] for i in range(n)]
    deg = [len(x) for x in nb]
    m = sum(deg) // 2
    best, bs = m, None
    for _ in range(rounds):
        side = rng.integers(0, 2, n)
        ch = True
        while ch:
            ch = False
            for i in range(n):
                s = sum(1 for j in nb[i] if side[j] == side[i])
                if 2 * s - deg[i] > 0:
                    side[i] ^= 1
                    ch = True
        mono = sum(1 for i in range(n) for j in nb[i] if j > i and side[i] == side[j])
        if mono < best:
            best, bs = mono, side.copy()
    return best, bs, m


def induced(n, adj, keep):
    keep = sorted(keep)
    ix = {v: i for i, v in enumerate(keep)}
    a2 = [0] * len(keep)
    for v in keep:
        for w in keep:
            if v != w and (adj[v] >> w) & 1:
                a2[ix[v]] |= 1 << ix[w]
    return len(keep), a2


def kneser(nn, kk):
    V = list(combinations(range(nn), kk))
    return mk(len(V), [(i, j) for i in range(len(V)) for j in range(i + 1, len(V))
                       if not set(V[i]) & set(V[j])])


def clebsch():
    S = {1, 2, 4, 8, 15}
    return mk(16, [(i, j) for i in range(16) for j in range(i + 1, 16) if (i ^ j) in S])


def hoffman_singleton():
    ix, c = {}, 0
    for h in range(5):
        for j in range(5):
            ix[('P', h, j)] = c; c += 1
    for i in range(5):
        for j in range(5):
            ix[('Q', i, j)] = c; c += 1
    E = []
    for h in range(5):
        for j in range(5):
            E.append((ix[('P', h, j)], ix[('P', h, (j + 1) % 5)]))
    for i in range(5):
        for j in range(5):
            E.append((ix[('Q', i, j)], ix[('Q', i, (j + 2) % 5)]))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.append((ix[('P', h, j)], ix[('Q', i, (h * i + j) % 5)]))
    return mk(50, sorted(set(tuple(sorted(e)) for e in E)))


print("building Golay code ...", flush=True)
code = golay24()
oct_ = witt_5_8_24(code)
blocks = steiner_3_6_22(oct_)
HS = higman_sims(blocks)
print("S(3,6,22) verified (77 blocks, all 1540 triples once); HiS built independently.")

u = 0
v = 1
M22 = induced(*HS, [w for w in range(100) if w != u and not (HS[1][u] >> w) & 1])
GEW = induced(*HS, [w for w in range(100) if w not in (u, v)
                    and not (HS[1][u] >> w) & 1 and not (HS[1][v] >> w) & 1])

CASES = [("Petersen", kneser(5, 2), 3, 0, 1),
         ("Clebsch", clebsch(), 5, 0, 2),
         ("HoffmanSingleton", hoffman_singleton(), 7, 0, 1),
         ("Gewirtz", GEW, 10, 0, 2),
         ("M22graph", M22, 16, 0, 4),
         ("HigmanSims", HS, 22, 0, 6)]

print(f"\n{'graph':18s} {'n':>4} {'m':>5} {'d':>3} {'TF':>4} {'reg':>5} {'srg-id':>7} "
      f"{'lmin':>5} {'LB=n(d+lm)/4':>13} {'cut(UB)':>8} {'verdict':>26}")
for name, (n, adj), d, lam, mu in CASES:
    tf = trifree(n, adj)
    reg, idt = srg_check(n, adj, d, lam, mu)
    s = lmin(d, lam, mu)
    m = len(edges(n, adj))
    lb = Fraction(n * (d + s), 4)
    ub, side, m2 = best_cut(n, adj, 600 if n < 60 else 250, 12345)
    assert m2 == m
    ev = np.linalg.eigvalsh(adjmat(n, adj).astype(float))
    verdict = (f"bip = {ub} EXACT" if lb <= ub < lb + 1 else f"bip in [{-(-lb//1)},{ub}]")
    print(f"{name:18s} {n:>4} {m:>5} {d:>3} {str(tf):>4} {str(reg):>5} {str(idt):>7} "
          f"{s:>5} {str(lb):>13} {ub:>8} {verdict:>26}   "
          f"lmin(numeric)={ev[0]:.6f} ratio={str(Fraction(ub,n*n))}={ub/n**2:.7f}")
