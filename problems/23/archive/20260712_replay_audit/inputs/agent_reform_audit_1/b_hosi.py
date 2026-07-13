# INDEPENDENT audit: Hoffman-Singleton claims (fam 50 <= 100, rank_F2(A) = 22) + exact beta certificate.
import numpy as np
from itertools import combinations

def P(h, j): return 5*h + j
def Q(i, k): return 25 + 5*i + k
E = set()
for h in range(5):
    for j in range(5):
        E.add(tuple(sorted((P(h, j), P(h, (j+1) % 5)))))
for i in range(5):
    for k in range(5):
        E.add(tuple(sorted((Q(i, k), Q(i, (k+2) % 5)))))
for h in range(5):
    for i in range(5):
        for j in range(5):
            E.add(tuple(sorted((P(h, j), Q(i, (h*i + j) % 5)))))
E = sorted(E); n = 50
assert len(E) == 175, len(E)
A = np.zeros((n, n), dtype=np.int64)
for u, v in E: A[u, v] = 1; A[v, u] = 1
deg = A.sum(1)
assert set(deg.tolist()) == {7}, "7-regular"
J = np.ones((n, n), dtype=np.int64); I = np.eye(n, dtype=np.int64)
# SRG(50,7,0,1) identity: A^2 = 7I + 0*A + 1*(J - I - A)  <=>  A^2 + A - 6I - J = 0  (exact integers)
lhs = A @ A + A - 6*I - J
assert not lhs.any(), "SRG(50,7,0,1) identity FAILED"
print("PASS  HoSi constructed: n=50 e=175 7-regular, A^2+A-6I-J=0 exactly (=> triangle-free, girth 5)")
# exact eigenvalue certificate: (A-2I)(A+3I) = J  => spectrum {7, 2, -3};  maxcut <= n*(k - lambda_min)/4 = 50*10/4 = 125
assert not ((A - 2*I) @ (A + 3*I) - J).any()
print("PASS  (A-2I)(A+3I) = J exactly => lambda_min = -3 => maxcut <= 50*(7+3)/4 = 125 => beta >= 175-125 = 50 (EXACT rational)")

# F2 ranks
def f2_basis(rows):
    basis = {}
    for r in rows:
        x = r
        while x:
            h = x.bit_length()-1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; break
    return list(basis.values())
adj = [0]*n
for u, v in E: adj[u] |= 1 << v; adj[v] |= 1 << u
bA = f2_basis(adj)
bI = f2_basis([adj[u] ^ (1 << u) for u in range(n)])
print(f"      rank_F2(A) = {len(bA)} (report claims 22); rank_F2(A+I) = {len(bI)}")

def min_uncut_span(basis):
    arr = np.zeros(1, dtype=np.uint64)
    for b in basis:
        arr = np.concatenate([arr, arr ^ np.uint64(b)])
    best = 10**9
    CH = 1 << 21
    for st in range(0, arr.shape[0], CH):
        a2 = arr[st:st+CH]
        acc = np.zeros(a2.shape, dtype=np.uint16)
        for u, v in E:
            acc += (((a2 >> np.uint64(u)) & np.uint64(1)) == ((a2 >> np.uint64(v)) & np.uint64(1)))
        best = min(best, int(acc.min()))
    return best

mA = min_uncut_span(bA) if len(bA) <= 24 else None
print(f"      min uncut over im(A)   = {mA}  (2^{len(bA)} cuts enumerated)")
mI = min_uncut_span(bI) if len(bI) <= 24 else "SKIP(rank>24)"
print(f"      min uncut over im(A+I) = {mI}")
fam = mA if not isinstance(mI, int) else min(mA, mI)
ok = (mA is not None) and fam <= 100 and fam >= 50
print(("PASS  " if ok else "FAIL  ") + f"HoSi fam = {fam} with exact sandwich 50 <= fam; report claim fam=50 <= 100 = n^2/25 "
      + ("CONFIRMED (fam = beta = 50, family achieves the spectral optimum)" if fam == 50 else f"MISMATCH got {fam}"))
