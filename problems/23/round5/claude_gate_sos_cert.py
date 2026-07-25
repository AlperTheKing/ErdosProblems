"""ROOT-AGENT GATE (Claude): independent exact verification of the round-4 H5 SOS certificate.

Shares NO code with the constructor or with H5_verify.py: polynomials are dicts
{exponent tuple -> Fraction}, expanded by hand; positive semidefiniteness is tested by my own
rational LDL^T with symmetric pivoting; nothing from sympy is used.

The certificate claims, for C5 with edges e = (u,v):

    (1)  sum_e lambda_e(z)  ==  (sum_j z_j)^2                       (quadratic forms in z)
    (2)  every lambda_e has NONNEGATIVE coefficients
    (3)  every Gram block G_b is symmetric PSD
    (4)  (sum_j y_j^2)^4  -  25 * sum_e lambda_e(y^2) * y_u^2 y_v^2
             ==  sum_b sum_{i,j} G_b[i,j] * y^{m_i} * y^{m_j}

Consequence, which is what must be checked to be the right statement: put x_j = y_j^2 >= 0 with
sum x = 1.  Then (1) makes (lambda_e(x))_e a probability distribution over the EDGES, depending on
x; (2) keeps it nonnegative; (3)+(4) give  1 - 25*sum_e lambda_e(x) x_u x_v >= 0, i.e.

        sum_e lambda_e(x) x_u x_v  <=  1/25 ,   hence   min_e x_u x_v <= 1/25 ,

and for C5, psi(C5,x) = min over edges of x_u x_v.  So the certificate proves max_x psi(C5,x) <= 1/25
with an x-DEPENDENT multiplier - the shape R3-C1 proved to be necessary.
"""
import json
import sys
from fractions import Fraction as F
from itertools import combinations


# ---------------------------------------------------------------- polynomial arithmetic

def pmul(a, b):
    out = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            out[e] = out.get(e, F(0)) + ca * cb
    return {e: c for e, c in out.items() if c != 0}


def padd(a, b):
    out = dict(a)
    for e, c in b.items():
        out[e] = out.get(e, F(0)) + c
    return {e: c for e, c in out.items() if c != 0}


def pscale(a, s):
    return {e: c * s for e, c in a.items() if c * s != 0}


def psub(a, b):
    return padd(a, pscale(b, F(-1)))


def mono(n, idx, deg=1, coef=F(1)):
    e = [0] * n
    e[idx] += deg
    return {tuple(e): coef}


# ---------------------------------------------------------------- exact PSD test

def is_psd(M):
    """rational LDL^T with symmetric pivoting; returns (ok, info)"""
    n = len(M)
    A = [[F(M[i][j]) for j in range(n)] for i in range(n)]
    piv = list(range(n))
    for k in range(n):
        # pick the largest remaining diagonal entry as pivot
        best = max(range(k, n), key=lambda i: A[i][i])
        if A[best][best] < 0:
            return False, f"negative diagonal {A[best][best]} at step {k}"
        if A[best][best] == 0:
            # the whole remaining row/col must vanish
            for i in range(k, n):
                for j in range(k, n):
                    if A[i][j] != 0 and i != j:
                        pass
            for i in range(k, n):
                if A[i][i] == 0:
                    for j in range(k, n):
                        if A[i][j] != 0:
                            return False, f"zero pivot with nonzero off-diagonal at ({i},{j})"
            break
        if best != k:
            A[k], A[best] = A[best], A[k]
            for r in range(n):
                A[r][k], A[r][best] = A[r][best], A[r][k]
            piv[k], piv[best] = piv[best], piv[k]
        d = A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / d
            if f == 0:
                continue
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
            for j in range(k, n):
                A[j][i] = A[i][j]
    return True, None


# ---------------------------------------------------------------- verification

def verify(path):
    d = json.load(open(path))
    n = d['n']
    E = [tuple(e) for e in d['edges']]
    lam = d['lambda']                      # lam[i][j] indexed by edge? read the shape
    print(f"certificate for {d['graph']}, n={n}, |E|={len(E)}, claim: {d['claim']}")

    # --- lambda: a list of n x n rational matrices, one per edge, giving lambda_e(z) = z^T L_e z
    if isinstance(lam[0][0], list):
        Ls = lam
    else:
        Ls = [lam]
    assert len(Ls) == len(E), f"expected {len(E)} lambda blocks, got {len(Ls)}"
    Lmats = [[[F(str(v)) for v in row] for row in Le] for Le in Ls]

    # (2) nonnegative coefficients
    neg = [(k, i, j) for k, Le in enumerate(Lmats) for i in range(n) for j in range(n) if Le[i][j] < 0]
    print(f"  (2) all lambda coefficients nonnegative: {not neg}" + (f"  first negative {neg[:1]}" if neg else ""))

    # (1) sum_e lambda_e(z) == (sum z)^2
    S = [[sum(Lmats[k][i][j] for k in range(len(E))) for j in range(n)] for i in range(n)]
    ok1 = all(S[i][j] == 1 for i in range(n) for j in range(n))
    print(f"  (1) sum_e lambda_e == (sum z)^2 : {ok1}")
    if not ok1:
        bad = [(i, j, S[i][j]) for i in range(n) for j in range(n) if S[i][j] != 1]
        print("      offending entries:", bad[:6])

    # (3) Gram blocks PSD
    ok3 = True
    for b in d['gram']:
        G = [[F(str(v)) for v in row] for row in b['G']]
        sym = all(G[i][j] == G[j][i] for i in range(len(G)) for j in range(len(G)))
        psd, info = is_psd(G)
        if not (sym and psd):
            ok3 = False
            print(f"      block {b['label']}: symmetric={sym} psd={psd} {info}")
    print(f"  (3) every Gram block symmetric and PSD (own rational LDL^T): {ok3}")

    # (4) the polynomial identity, expanded by hand in the y variables
    Y2 = [mono(n, j, 2) for j in range(n)]                       # y_j^2
    sumY2 = {}
    for t in Y2:
        sumY2 = padd(sumY2, t)
    lhs = sumY2
    for _ in range(3):
        lhs = pmul(lhs, sumY2)                                    # (sum y^2)^4
    acc = {}
    for k, (u, v) in enumerate(E):
        le = {}
        for i in range(n):
            for j in range(n):
                c = Lmats[k][i][j]
                if c:
                    le = padd(le, pmul(pscale(Y2[i], c), Y2[j]))   # lambda_e(y^2)
        acc = padd(acc, pmul(le, pmul(Y2[u], Y2[v])))
    lhs = psub(lhs, pscale(acc, F(25)))

    rhs = {}
    for b in d['gram']:
        ms = [tuple(mm) for mm in b['ymonomials']]
        G = [[F(str(v)) for v in row] for row in b['G']]
        for i in range(len(ms)):
            for j in range(len(ms)):
                if G[i][j]:
                    e = tuple(a + bb for a, bb in zip(ms[i], ms[j]))
                    rhs[e] = rhs.get(e, F(0)) + G[i][j]
    rhs = {e: c for e, c in rhs.items() if c != 0}
    diff = psub(lhs, rhs)
    ok4 = not diff
    print(f"  (4) polynomial identity holds exactly: {ok4}" +
          (f"   residual has {len(diff)} monomials, e.g. {list(diff.items())[:3]}" if diff else ""))

    # sharpness: uniform x on C5 attains 1/25
    x = [F(1, n)] * n
    val = min(x[u] * x[v] for (u, v) in E)
    print(f"  sharpness: min over edges at uniform x = {val} = 1/25 : {val == F(1,25)}")

    verdict = (not neg) and ok1 and ok3 and ok4
    print(f"\n  ROOT GATE VERDICT: {'CONFIRMED - exact SOS proof of max psi(C5) <= 1/25' if verdict else 'NOT CONFIRMED'}")
    return verdict


if __name__ == '__main__':
    p = sys.argv[1] if len(sys.argv) > 1 else '../round4/H5_certificate_C5.json'
    sys.exit(0 if verify(p) else 1)
