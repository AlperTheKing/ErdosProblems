"""Independent EXHAUSTIVE confirmation of the graphs Theorem E newly settles, and
exact quantification of the residual for the graphs it does not settle.

For a graph G on n vertices and an integer budget q, we enumerate EVERY composition
of q into n non-negative parts (zeros included) and check 25*M(a) <= q^2 exactly.
This does not use Theorem E at all -- it is a blind check of its conclusion.
"""
import sys, itertools
from fractions import Fraction as Fr
import numpy as np
import R9_thmD_lib as L
import R9_thmD_coverage as CV


def batched_max25M(G, q, chunk=40000, report=True):
    """returns (max over compositions of 25*M(a) - q^2, argmax a, count)."""
    n, adj = G
    Mm, E = L._mono_matrix(G)
    Mm = Mm.astype(np.int32)
    eu = np.array([e[0] for e in E]); ev = np.array([e[1] for e in E])
    best, besta, cnt = None, None, 0
    buf = []

    def flush(buf):
        nonlocal best, besta, cnt
        if not buf:
            return
        A = np.array(buf, dtype=np.int64)
        P = A[:, eu] * A[:, ev]
        vals = P @ Mm.T.astype(np.int64)
        m = vals.min(axis=1)
        k = int(m.argmax())
        cnt += len(buf)
        if best is None or m[k] > best:
            best, besta = int(m[k]), list(A[k])

    def rec(i, rem, cur):
        nonlocal buf
        if i == n - 1:
            buf.append(cur + [rem])
            if len(buf) >= chunk:
                flush(buf); buf = []
            return
        for v in range(rem + 1):
            rec(i + 1, rem - v, cur + [v])
    rec(0, q, [])
    flush(buf)
    return 25 * best - q * q, besta, cnt


def residual_bound(G, a):
    """min over (complete induced blow-up, assignment, cut) of  yhat_i yhat_{i+1} + BAD_i,
    in units of 1/q^2.  Returns (bound, description)."""
    n, adj = G
    best = None
    for C in L.induced_C5s(G):
        for cls in CV.blowups_from_C5(G, C):
            adm = CV.admissible(G, cls)
            inB = {v: m for m in range(5) for v in cls[m]}
            W = [v for v in range(n) if v not in inB]
            if any(not adm[v] for v in W):
                continue
            for combo in itertools.product(*[adm[v] for v in W]):
                asg = dict(zip(W, combo))
                yh = [sum(a[v] for v in cls[m]) for m in range(5)]
                for v, m in asg.items():
                    yh[m] += a[v]
                for i in range(5):
                    B_i = 0
                    for u in W:
                        for v in adj[u]:
                            if v in inB or v <= u:
                                continue
                            du, dv = asg[u], asg[v]
                            d = (du - dv) % 5
                            if d == 0:
                                B_i += a[u] * a[v]
                            elif d in (2, 3):
                                centre = (dv + 1) % 5 if d == 2 else (du + 1) % 5
                                if centre != i and centre != (i + 1) % 5:
                                    B_i += a[u] * a[v]
                    val = yh[i] * yh[(i + 1) % 5] + B_i
                    if best is None or val < best[0]:
                        best = (val, C, [sorted(c) for c in cls], i, dict(asg), B_i)
    return best


if __name__ == '__main__':
    print("=" * 78)
    print("P. Blind exhaustive confirmation of  25*M(a) <= q^2  on E-COVERED graphs")
    print("   (Theorem E claims this for ALL x; here every integer x on the grid)")
    print("=" * 78)
    N = L.named_graphs()
    N['And(6)=G17'] = L.andrasfai(6)
    tests = [('Wagner=And(3)', 24), ('Wagner=And(3)', 25), ('C5[2,2,1,1,1]', 20),
             ('And(4)=G11', 11), ('And(4)=G11', 12), ('C5[2]', 15),
             ('And(5)=G14', 10), ('C5[3,1,2,2,1]', 12)]
    for name, q in tests:
        G = N[name]
        d, a, cnt = batched_max25M(G, q)
        print("  %-16s n=%2d q=%2d : %8d compositions, max(25M - q^2) = %5d  %s   %s"
              % (name, G[0], q, cnt, d, "VIOLATION!" if d > 0 else "ok",
                 a if d >= 0 else ""))

    print("=" * 78)
    print("Q. The RESIDUAL: graphs not E-covered, and how much is missing")
    print("=" * 78)
    for name, a in [('Petersen', [1] * 10), ('Grotzsch', [3] * 5 + [0] * 6),
                    ('MTF14', [1] * 14)]:
        G = N[name]
        q = sum(a)
        r = residual_bound(G, a)
        M = L.psi_int(G, a)
        if r is None:
            print("  %-12s : no admissible blow-up assignment at all" % name)
            continue
        val, C, cls, i, asg, B_i = r
        print("  %-12s a=%s q=%d : psi=%s  bestE-bound=%s (=%s + BAD %s)  1/25 = %s"
              % (name, a, q, Fr(M, q * q), Fr(val, q * q), Fr(val - B_i, q * q),
                 Fr(B_i, q * q), Fr(1, 25)))
        print("               witness: pentagon %s classes %s cut %d assignment %s"
              % (str(C), cls, i, asg))
    # Petersen at its true maximiser
    G = N['Petersen']
    a = [4, 4, 4, 4, 4] + [0] * 5
    r = residual_bound(G, a)
    print("  Petersen at a C5-concentration a=%s : psi=%s  E-bound=%s"
          % (a, Fr(L.psi_int(G, a), sum(a) ** 2), Fr(r[0], sum(a) ** 2)))
