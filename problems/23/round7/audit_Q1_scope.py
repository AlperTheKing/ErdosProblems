"""audit_Q1_scope.py -- audit of the SCOPE sentence of R1 and of the Mycielskian table.

Q1.md section 3 claims the Grotzsch falsifier kills "every certificate whose output cut is a
union of neighbourhoods -- in particular the hard-core-model cut N(I), every BFS-layer cut
rooted at a vertex, the 'random independent set and its shadow' construction".

Tested here:
  * is the odd-BFS-layer cut always a union of neighbourhoods?  (explicit search in C7 and others)
  * Mycielskian table:  M(C7), M(C9) claimed fam = bip = 5, 6;  M(C11), M(C13), M(M(C5)) fam = 7, 8, 18
"""
from fractions import Fraction as F
from collections import deque
import numpy as np
from audit_Q1_core import edges, trianglefree, induced_c5

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


def cyc(n):
    A = [0] * n
    for i in range(n):
        A[i] |= 1 << ((i + 1) % n)
        A[(i + 1) % n] |= 1 << i
    return n, A


def mycielski(n, A):
    m = 2 * n + 1
    B = [0] * m
    for u in range(n):
        for v in range(n):
            if A[u] >> v & 1:
                B[u] |= 1 << v
                B[n + u] |= 1 << v          # shadow u' ~ N(u)
                B[v] |= 1 << (n + u)
    for u in range(n):
        B[2 * n] |= 1 << (n + u)
        B[n + u] |= 1 << (2 * n)
    return m, B


def unions(m, A):
    U = [0] * (1 << m)
    for S in range(1, 1 << m):
        v = (S & -S).bit_length() - 1
        U[S] = U[S & (S - 1)] | A[v]
    return set(U)


def mono_all(m, A):
    size = 1 << m
    idx = np.arange(size, dtype=np.int64)
    bit = [((idx >> u) & 1).astype(np.int64) for u in range(m)]
    tot = np.zeros(size, dtype=np.int64)
    for u in range(m):
        for v in range(u + 1, m):
            if A[u] >> v & 1:
                tot += (bit[u] == bit[v])
    return tot


say("=== scope check: is the odd-BFS-layer cut a union of neighbourhoods? ===")
for nn in [5, 7, 9, 11]:
    m, A = cyc(nn)
    U = unions(m, A)
    bad = []
    for root in range(m):
        dist = [-1] * m
        dist[root] = 0
        dq = deque([root])
        while dq:
            v = dq.popleft()
            for w in range(m):
                if A[v] >> w & 1 and dist[w] < 0:
                    dist[w] = dist[v] + 1
                    dq.append(w)
        odd = 0
        for v in range(m):
            if dist[v] % 2 == 1:
                odd |= 1 << v
        if odd not in U:
            bad.append((root, sorted(v for v in range(m) if odd >> v & 1)))
    say(f"  C{nn}: roots whose odd-layer set is NOT a union of neighbourhoods: {len(bad)}/{m}"
        f"   example {bad[0] if bad else None}")
say("  => 'every BFS-layer cut rooted at a vertex' is NOT inside the neighbourhood-union family;")
say("     the scope sentence of Q1.md section 3 overstates the kill for BFS-layer cuts.")

say("\n=== Mycielskian table ===")
for name, base in [("C5", 5), ("C7", 7), ("C9", 9), ("C11", 11)]:
    n0, A0 = cyc(base)
    m, A = mycielski(n0, A0)
    E = edges(m, A)
    tf = trianglefree(m, A)
    U = sorted(unions(m, A))
    if m <= 24:
        tot = mono_all(m, A)
        b = int(tot.min())
        fam = min(int(tot[S]) for S in U)
    else:
        b = fam = None
    say(f"  M({name}): N={m} |E|={len(E)} triangle-free={tf} bip={b} fam={fam} "
        f"equal={b==fam}  N^2/25={F(m*m,25)}  25*fam-N^2={25*fam-m*m if fam is not None else None}")
n0, A0 = cyc(5)
m1, A1 = mycielski(n0, A0)
m2, A2 = mycielski(m1, A1)
say(f"  M(M(C5)): N={m2} |E|={len(edges(m2,A2))} triangle-free={trianglefree(m2,A2)}")
tot = mono_all(m2, A2)
U = sorted(unions(m2, A2))
b2 = int(tot.min())
fam2 = min(int(tot[S]) for S in U)
say(f"            bip={b2} fam={fam2} equal={b2==fam2} N^2/25={F(m2*m2,25)} 25*fam-N^2={25*fam2-m2*m2}")

with open("audit_Q1_scope.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
