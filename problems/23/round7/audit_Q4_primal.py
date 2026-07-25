"""AUDIT (adversarial, independent) of the Q4 primal certificates.

Nothing here is imported from the Q4 pipeline or from Q4_gate.py.  Own graph construction, own
cut enumeration (by exhaustive bipartition search, so the mask convention of the pickle is never
trusted), own polynomial arithmetic, own PSD test that emits an explicit LDL^T factorisation and
verifies  P A P^T == L D L^T  by exact rational matrix multiplication (so the PSD verdict does not
depend on my elimination code being bug-free).

Everything is Fraction / int.  No float touches an acceptance path.

Usage: python audit_Q4_primal.py <cert.pkl>
"""
import sys, pickle
from fractions import Fraction as F
from itertools import combinations


# ---------------------------------------------------------------- graphs, built my own way
def gamma_graph(n):
    """vertices i -> point i/n on R/Z ; i ~ j iff circular distance > 1/3, in EXACT rationals."""
    adj = [[False] * n for _ in range(n)]
    third = F(1, 3)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dd = min(F((i - j) % n, n), F((j - i) % n, n))
            adj[i][j] = dd > third
    return adj


def petersen_graph():
    """Kneser K(5,2): vertices = 2-subsets of {0..4}, adjacent iff disjoint."""
    V = sorted(combinations(range(5), 2))
    n = len(V)
    adj = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and not (set(V[i]) & set(V[j])):
                adj[i][j] = True
    return adj


def edges_of(adj):
    n = len(adj)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i][j]]


def triangle_free(adj):
    n = len(adj)
    return not any(adj[a][b] and adj[b][c] and adj[a][c] for a, b, c in combinations(range(n), 3))


# ---------------------------------------------------------------- polynomials (dicts exps->F)
def pmul(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = tuple(p + q for p, q in zip(ea, eb))
            out[e] = out.get(e, F(0)) + ca * cb
    return {e: c for e, c in out.items() if c}


def padd(a, b, sgn=1):
    out = dict(a)
    for e, c in b.items():
        out[e] = out.get(e, F(0)) + sgn * c
        if out[e] == 0:
            del out[e]
    return out


# ---------------------------------------------------------------- PSD with a checkable factor
def ldl_certificate(A):
    """A symmetric list-of-lists of Fractions.
    Returns (True, perm, L, D) with  A[perm][perm] == L D L^T,  D >= 0 entrywise, L unit lower
    triangular; or (False, reason).  The caller re-multiplies to confirm."""
    k = len(A)
    W = [row[:] for row in A]
    perm = list(range(k))
    L = [[F(1) if i == j else F(0) for j in range(k)] for i in range(k)]
    D = [F(0)] * k
    for s in range(k):
        # pivot: FIRST strictly positive diagonal (deliberately a different rule from the gate's max)
        p = -1
        for i in range(s, k):
            if W[i][i] > 0:
                p = i
                break
        if p < 0:
            # no positive diagonal left: trailing block must vanish identically
            for i in range(s, k):
                for j in range(s, k):
                    if W[i][j] != 0:
                        return (False, f"no positive pivot at step {s} but W[{i}][{j}]={W[i][j]}")
            for i in range(s, k):
                D[i] = F(0)
            return (True, perm, L, D)
        if p != s:
            W[s], W[p] = W[p], W[s]
            for r in range(k):
                W[r][s], W[r][p] = W[r][p], W[r][s]
            for t in range(s):               # swap only the already-computed part of L's rows
                L[s][t], L[p][t] = L[p][t], L[s][t]
            perm[s], perm[p] = perm[p], perm[s]
        d = W[s][s]
        D[s] = d
        for i in range(s + 1, k):
            f = W[i][s] / d
            L[i][s] = f
            if f:
                for j in range(s, k):
                    W[i][j] -= f * W[s][j]
    return (True, perm, L, D)


def psd_verified(A):
    """True iff A (symmetric) is PSD, established by an explicitly re-multiplied factorisation."""
    res = ldl_certificate(A)
    if res[0] is False:
        return False, res[1]
    _, perm, L, D = res
    k = len(A)
    if any(d < 0 for d in D):
        return False, "negative D entry"
    # re-multiply:  L D L^T  must equal  A permuted
    for i in range(k):
        for j in range(i, k):
            s = F(0)
            for t in range(min(i, j) + 1):
                if L[i][t] and L[j][t] and D[t]:
                    s += L[i][t] * D[t] * L[j][t]
            if s != A[perm[i]][perm[j]]:
                return False, f"reconstruction mismatch at ({i},{j})"
    return True, "psd (factorisation re-multiplied)"


# ---------------------------------------------------------------- main audit
def main(path):
    C = pickle.load(open(path, "rb"))
    m, n, d, c = C['m'], C['n'], C['d'], C['c']
    print(f"AUDIT {path}: pattern={m} n={n} multiplier degree={2*d} c={c}")
    fails = []

    def need(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        if not cond:
            fails.append(msg)

    need(isinstance(c, F) and c == 25, "c is the exact rational 25")
    need(d == 1, "multiplier degree 2d = 2")

    # A1 graph
    adj = petersen_graph() if str(m).lower() == 'petersen' else gamma_graph(int(m))
    need(len(adj) == n, f"n = {n} matches my rebuilt pattern")
    E = edges_of(adj)
    need(sorted(tuple(sorted(e)) for e in C['E']) == E,
         f"edge set of the pickle == my rebuilt pattern ({len(E)} edges)")
    need(triangle_free(adj), "pattern is triangle-free")
    need(len(set(map(tuple, C['E']))) == len(C['E']), "edge list has no repeats")

    # A2 every listed cut is realised by SOME genuine bipartition (mask convention not trusted)
    Emine = [tuple(sorted(e)) for e in C['E']]
    realised = {}
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        mono = frozenset(k for k, (u, v) in enumerate(Emine) if side[u] == side[v])
        realised.setdefault(mono, mask)
    allmono = set(realised)
    bad = [i for i, (msk, mono) in enumerate(C['cuts'])
           if frozenset(mono) not in allmono]
    need(not bad, f"all {len(C['cuts'])} listed monochromatic sets are realised by a genuine "
                  f"bipartition (searched all {1 << (n-1)} of them)")
    need(len({frozenset(mono) for _, mono in C['cuts']}) == len(C['cuts']),
         "listed cuts are pairwise distinct")

    qpolys = []
    for msk, mono in C['cuts']:
        q = {}
        for k in mono:
            u, v = Emine[k]
            e = [0] * n
            e[u] += 1
            e[v] += 1
            q[tuple(e)] = q.get(tuple(e), F(0)) + 1
        qpolys.append(q)

    # A3 multipliers: rational, nonnegative, degree 2, indices in range
    okty = all(isinstance(v, F) for v in C['nu'].values())
    need(okty, "every multiplier coefficient is an exact Fraction (no float)")
    need(all(v >= 0 for v in C['nu'].values()), "every multiplier coefficient is >= 0")
    need(all(0 <= S < len(qpolys) and len(mm) == n and sum(mm) == 2 * d
             for (S, mm) in C['nu']), "every multiplier monomial is degree 2d and indexes a listed cut")

    nu = [{} for _ in qpolys]
    for (S, mm), val in C['nu'].items():
        nu[S][tuple(mm)] = nu[S].get(tuple(mm), F(0)) + val

    # A4 normalisation  sum_S nu_S == 25 L^2
    Lp = {tuple(1 if i == j else 0 for i in range(n)): F(1) for j in range(n)}
    L2 = pmul(Lp, Lp)
    tot = {}
    for x in nu:
        tot = padd(tot, x)
    need(tot == {e: 25 * v for e, v in L2.items()}, "sum_S nu_S == 25 * L^2 exactly")

    # A5 identity  L^4 - sum nu_S q_S == sum_b v_b^T Q_b v_b  after x = y^2
    T = pmul(L2, L2)
    for x, q in zip(nu, qpolys):
        T = padd(T, pmul(x, q), sgn=-1)
    Ty = {tuple(2 * e for e in ex): cf for ex, cf in T.items()}
    G = {}
    symfail = 0
    for B, M in C['Q']:
        k = len(B)
        if any(M[i][j] != M[j][i] for i in range(k) for j in range(i + 1, k)):
            symfail += 1
        for i in range(k):
            for j in range(k):
                if M[i][j]:
                    e = tuple(B[i][t] + B[j][t] for t in range(n))
                    G[e] = G.get(e, F(0)) + M[i][j]
    G = {e: v for e, v in G.items() if v}
    need(Ty == G, f"L^4 - sum nu_S q_S == sum_b v_b^T Q_b v_b after x = y^2 "
                  f"({len(Ty)} monomials, {len(set(Ty) ^ set(G))} mismatched)")
    need(all(isinstance(M[i][j], (F, int)) and not isinstance(M[i][j], bool)
             for B, M in C['Q'] for i in range(len(B)) for j in range(len(B))),
         "every Gram entry is exact (Fraction or int); no float anywhere")
    print(f"  note: {symfail} of {len(C['Q'])} Gram blocks are stored non-symmetric "
          f"(only the symmetric part matters; I test (M+M^T)/2)")

    # A6 PSD of the SYMMETRISED blocks, each with a re-multiplied factorisation
    nbad = 0
    for bi, (B, M) in enumerate(C['Q']):
        k = len(B)
        A = [[(M[i][j] + M[j][i]) / 2 for j in range(k)] for i in range(k)]
        ok, info = psd_verified(A)
        if not ok:
            nbad += 1
            print(f"    block {bi} (size {k}): {info}")
    need(nbad == 0, f"all {len(C['Q'])} symmetrised Gram blocks PSD, each factorisation re-multiplied")

    # A7 the deduction itself, re-checked at random exact rational points of the simplex
    #    (not part of the proof, a consistency probe: min_S q_S(x) <= L(x)^2/25 must hold)
    import random
    random.seed(12345)
    worst = None
    for _ in range(300):
        w = [random.randint(0, 12) for _ in range(n)]
        if sum(w) == 0:
            continue
        x = [F(t, sum(w)) for t in w]
        best = min(sum(cf * eval_mon(ex, x) for ex, cf in q.items()) for q in qpolys)
        if worst is None or best > worst[0]:
            worst = (best, w)
    need(worst[0] <= F(1, 25), f"probe: max over 300 random rational points of min_S q_S = "
                               f"{worst[0]} <= 1/25   (argmax weights {worst[1]})")

    print("AUDIT VERDICT:", "CONFIRMED — certificate valid, max_x psi <= 1/25" if not fails
          else f"BROKEN ({len(fails)} failed checks)")
    return fails


def eval_mon(ex, x):
    v = F(1)
    for i, e in enumerate(ex):
        for _ in range(e):
            v *= x[i]
    return v


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Q4_cert_g8_d1.pkl")
