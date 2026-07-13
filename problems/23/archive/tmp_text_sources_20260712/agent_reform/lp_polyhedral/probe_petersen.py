# Probe: which linear-algebraic cut families contain a near-optimal cut of Petersen?
from lib import *
import numpy as np
from itertools import combinations

n, E = petersen()
b, Sopt = beta_exact(n, E)
print("beta =", b, "one optimal S =", bin(Sopt))

# all optimal cuts
opts = []
for S in range(1 << (n - 1)):
    if uncut_of(n, E, S) == b:
        opts.append(S)
print("number of optimal cut-sides (vertex n-1 fixed out):", len(opts))
print("sizes of optimal sides:", sorted(set(bin(S).count('1') for S in opts)))

def span_basis(vecs):
    basis = {}
    for vec in vecs:
        x = vec
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return basis

def in_span(basis, x):
    while x:
        h = x.bit_length() - 1
        if h in basis:
            x ^= basis[h]
        else:
            return False
    return True

adj = edges_to_adj(n, E)
A_cols = adj
AI_cols = [adj[u] ^ (1 << u) for u in range(n)]

bA = span_basis(A_cols)
bAI = span_basis(AI_cols)
print("rank A =", len(bA), " rank A+I =", len(bAI))

for name, basis in [("im(A)", bA), ("im(A+I)", bAI)]:
    hits = [S for S in opts if in_span(basis, S) or in_span(basis, S ^ ((1 << n) - 1))]
    print(f"optimal cuts inside {name} (S or complement): {len(hits)}")

# min uncut over im(A+I) and over union
def min_over_span(basis):
    arr = np.zeros(1, dtype=np.uint32)
    for v in basis.values():
        arr = np.concatenate([arr, arr ^ np.uint32(v)])
    acc = np.zeros(arr.shape, dtype=np.uint16)
    for u, v in E:
        acc += (((arr >> np.uint32(u)) & 1) == ((arr >> np.uint32(v)) & 1))
    i = int(acc.argmin())
    return int(acc[i]), int(arr[i])

mA = min_over_span(bA)
mAI = min_over_span(bAI)
print("min uncut over im(A)   =", mA)
print("min uncut over im(A+I) =", mAI)
print("floor(n^2/25) =", n * n // 25)

# Also: min uncut over im(A) shifted by each single vertex (affine family A y + e_u)
best = 99
for u in range(n):
    arr = np.zeros(1, dtype=np.uint32)
    for v in bA.values():
        arr = np.concatenate([arr, arr ^ np.uint32(v)])
    arr ^= np.uint32(1 << u)
    acc = np.zeros(arr.shape, dtype=np.uint16)
    for x, y in E:
        acc += (((arr >> np.uint32(x)) & 1) == ((arr >> np.uint32(y)) & 1))
    best = min(best, int(acc.min()))
print("min uncut over im(A) + e_u (any u):", best)
