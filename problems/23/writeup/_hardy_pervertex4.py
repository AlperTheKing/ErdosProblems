"""FINAL: how non-local must the (H) certificate be at N=23?  Compare the true near-null eigenvector of H
(the direction that nearly violates PSD) to the natural weights (ones, T, d) at the failing vertices 2,22.

If the minimal eigenvector concentrates on a few vertices far from 2/22, then NO per-vertex/weighted-diagonal
certificate with a local geometric weight can work, and (H) genuinely needs the global cycle coupling.  This
quantifies the negative result and identifies the 'hard core' support.
"""
import math, random
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski
from _hardy_gate import build_H, BETA


def build_H_true_float(n, M, ell, T, cyc):
    H = [[0.0] * n for _ in range(n)]
    for v in range(n):
        H[v][v] = float(n) - float(T[v])
    for f in M:
        Qs = cyc[f]; L = ell[f]
        beta = L / (2 + 2 * math.cos(math.pi / L))
        w = beta / len(Qs)
        for Q in Qs:
            Ql = list(Q)
            for i in range(len(Ql)):
                a = Ql[i]; b = Ql[(i + 1) % len(Ql)]
                H[a][a] += w; H[b][b] += w
                H[a][b] -= w; H[b][a] -= w
    return H


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    import numpy as np
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    st = struct_for_side(m2N, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    n = m2N
    Hf = build_H_true_float(n, M, ell, T, cyc)
    A = np.array(Hf)
    w, V = np.linalg.eigh(A)
    v0 = V[:, 0]               # eigenvector of smallest eigenvalue
    v0 = v0 / np.max(np.abs(v0))
    print("min eig =", float(w[0]), " 2nd =", float(w[1]))
    Hrat = build_H(n, M, ell, T, cyc, BETA)
    diag = [float(Hrat[v][v]) for v in range(n)]
    order = sorted(range(n), key=lambda v: -abs(v0[v]))
    print("near-null eigenvector |components| (top 8 vertices):")
    for v in order[:8]:
        print("   v=%2d  evec=%+.3f  T_v=%7.3f  H[v][v]=%7.3f  overloaded=%s"
              % (v, v0[v], float(T[v]), diag[v], T[v] > F(n)))
    print("failing-certificate vertices 2,22:  evec[2]=%.3f evec[22]=%.3f" % (v0[2], v0[22]))
    # correlation of eigenvector with T (load): if low, T is the wrong weight
    Tn = np.array([float(T[v]) for v in range(n)])
    Tn = Tn / np.linalg.norm(Tn)
    e = v0 / np.linalg.norm(v0)
    print("cos(near-null evec, load T) =", float(abs(np.dot(Tn, e))))
    ones = np.ones(n) / math.sqrt(n)
    print("cos(near-null evec, ones)   =", float(abs(np.dot(ones, e))))


if __name__ == "__main__":
    main()
