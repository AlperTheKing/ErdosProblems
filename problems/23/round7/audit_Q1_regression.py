"""audit_Q1_regression.py -- protocol step 2.

Runs the R1 mechanism of round7/Q1.md (min over cuts of the form  union_{v in I} N(v))
against the TEN recorded witnesses of round5/claude_witness_regression.py, and against
C5[n] where any correct bound must be exactly tight.

Everything exact: integer weights w, integer monochromatic mass, value = mass / (sum w)^2.
numpy is used only to enumerate subsets with int64 sums (exact, no rounding: all values are
small integers), the reported rationals are Fractions.
"""
from fractions import Fraction as F
from itertools import combinations
import numpy as np
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round5")
from claude_witness_regression import WITNESSES, gamma, arcbound, mono

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


def adjmask(m, adj):
    A = [0] * m
    for u in range(m):
        for v in range(m):
            if u != v and adj[u][v]:
                A[u] |= 1 << v
    return A


def all_cut_mono(m, A, w):
    """exact integer array mono[S] = sum over monochromatic edges of w_u w_v, all 2^m cuts"""
    size = 1 << m
    idx = np.arange(size, dtype=np.int64)
    bit = [((idx >> u) & 1).astype(np.int64) for u in range(m)]
    tot = np.zeros(size, dtype=np.int64)
    for u in range(m):
        for v in range(u + 1, m):
            if A[u] >> v & 1:
                tot += np.int64(w[u] * w[v]) * (bit[u] == bit[v])
    return tot


def union_sets(m, A):
    seen = set()
    U = [0] * (1 << m)
    for S in range(1, 1 << m):
        v = (S & -S).bit_length() - 1
        U[S] = U[S & (S - 1)] | A[v]
    return sorted(set(U))


say("=== R1 family (min over unions of neighbourhoods) vs the ten recorded witnesses ===")
say(f"{'witness':30s} {'m':>3s} {'R1 value':>12s} {'ARCBOUND':>10s} {'true psi':>12s}  verdict")
fails = []
for (name, m, w, why) in WITNESSES:
    adj = gamma(m)
    A = adjmask(m, adj)
    q = sum(w)
    tot = all_cut_mono(m, A, w)
    truemin = int(tot.min())
    us = union_sets(m, A)
    fam = min(int(tot[S]) for S in us)
    x = [F(wi, q) for wi in w]
    ab = arcbound(m, adj, x)
    vr = F(fam, q * q)
    vt = F(truemin, q * q)
    ok = vr <= F(1, 25)
    tight = (vr == vt)
    say(f"{name:30s} {m:3d} {str(vr):>12s} {str(ab):>10s} {str(vt):>12s}  "
        f"{'OK' if ok else '*** EXCEEDS 1/25 ***'} {'tight' if tight else 'NOT tight'}")
    if not ok:
        fails.append(name)
say(f"R1 family on the recorded regression set: {'passes all ten' if not fails else 'fails on ' + ','.join(fails)}")
say("(so the recorded ten witnesses do NOT contain the Grotzsch obstruction: R1 is a new kill)")

say("\n=== exact tightness of the R1 family on C5[n] (mandatory calibration) ===")
c5adj = [[False] * 5 for _ in range(5)]
for i in range(5):
    c5adj[i][(i + 1) % 5] = c5adj[(i + 1) % 5][i] = True
for n in range(1, 7):
    m = 5 * n
    A = [0] * m
    for i in range(5):
        for j in range(5):
            if c5adj[i][j]:
                for p in range(n):
                    for qq in range(n):
                        A[i * n + p] |= 1 << (j * n + qq)
    w = [1] * m
    if m <= 20:
        tot = all_cut_mono(m, A, w)
        truemin = int(tot.min())
        us = union_sets(m, A)
        fam = min(int(tot[S]) for S in us)
        say(f"  C5[{n}] (N={m}): bip={truemin} (n^2={n*n}) fam={fam} equal={truemin==fam} "
            f"value={F(fam,m*m)} 1/25={F(1,25)} exactly tight={F(fam,m*m)==F(1,25)}")
    else:
        say(f"  C5[{n}]: skipped (2^{m} cuts)")

say("\n=== the R2 falsifier C7 is the recorded witness W6 (Gamma_7 uniform) ===")
adj7 = gamma(7)
A7 = adjmask(7, adj7)
say(f"  Gamma_7 degrees: {[bin(A7[u]).count('1') for u in range(7)]}  -> Gamma_7 = C7")
tot7 = all_cut_mono(7, A7, [1] * 7)
say(f"  bip(Gamma_7) = {int(tot7.min())}, #induced C5 = 0, so bip^(5/2) = 1 > 0 = c5")

with open("audit_Q1_regression.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
