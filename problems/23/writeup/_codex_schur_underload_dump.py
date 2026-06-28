"""Codex diagnostic: Schur complement of underload-grounded Laplacian.

N I - K = (diag(T)-K) + diag(N-T).  Let O={v:T(v)>N}.  The positive
underload diagonal on V\\O is essential.  This script eliminates V\\O and
prints the effective matrix on O:

  A_eff = A_OO - A_OQ A_QQ^{-1} A_QO,  A=N I-K.

PSD of A is equivalent to A_eff PSD when A_QQ is positive definite.
The dump is float-only and intended to reveal a structural formula.
"""

from fractions import Fraction as F

import numpy as np

from _h import dec, loads


def p_matrix(info):
    n = info["n"]
    M = info["M"]
    P = np.zeros((n, len(M)))
    for j, f in enumerate(M):
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            P[v, j] = c / den
    return P


def blowup_edges(n, edges, t):
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def dump(g6, t=1):
    n, e = dec(g6)
    if t != 1:
        n, e = blowup_edges(n, e, t)
    info = loads(n, e)
    P = p_matrix(info)
    K = P @ P.T
    A = n * np.eye(n) - K
    T = np.array([float(x) for x in info["T"]])
    O = [v for v in range(n) if T[v] > n + 1e-10]
    Q = [v for v in range(n) if v not in O]
    print(f"\nGRAPH {g6}[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])}")
    print(f"  overloaded O={O} overload={[T[v]-n for v in O]}")
    print(f"  underload sum={sum(max(0.0, n-T[v]) for v in range(n)):.6f}")
    print(f"  A min eig={np.linalg.eigvalsh(A).min():+.6e}")
    if not O:
        return
    Aoo = A[np.ix_(O, O)]
    Aqq = A[np.ix_(Q, Q)]
    Aoq = A[np.ix_(O, Q)]
    try:
        X = np.linalg.solve(Aqq, Aoq.T)
        eff = Aoo - Aoq @ X
        print(f"  A_QQ min eig={np.linalg.eigvalsh(Aqq).min():+.6e}")
        print(f"  eff min eig={np.linalg.eigvalsh(eff).min():+.6e}")
        print("  eff matrix:")
        for row in eff:
            print("   ", " ".join(f"{x:+.6f}" for x in row))
    except np.linalg.LinAlgError as exc:
        print(f"  Schur solve failed: {exc}")


if __name__ == "__main__":
    for case in [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
    ]:
        dump(*case)
