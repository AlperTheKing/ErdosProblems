# symmetrization lens -- exact-arithmetic sanity checks (integers/Fractions only)
import itertools

def beta_exact_int(n, edges):
    # min over 2-colorings (vertex 0 fixed) of # monochromatic edges (unit weights)
    best = None
    for m in range(1 << (n - 1)):
        c = [0] + [(m >> i) & 1 for i in range(n - 1)]
        mono = 0
        for (u, v) in edges:
            if c[u] == c[v]:
                mono += 1
        if best is None or mono < best:
            best = mono
    return best

# --- Petersen ---
outer = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
spokes = [(i, i + 5) for i in range(5)]
inner = [(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
P = outer + spokes + inner
bP = beta_exact_int(10, P)
print("Petersen: e=%d beta=%d (expect 3); bound N^2/25=4; OK=%s" % (len(P), bP, bP == 3 and bP <= 4), flush=True)
assert bP == 3

# --- C5 ---
C5 = [(i, (i + 1) % 5) for i in range(5)]
b5 = beta_exact_int(5, C5)
print("C5: beta=%d (expect 1 = 25/25)" % b5, flush=True)
assert b5 == 1

# --- balanced C5 blow-ups: beta must be exactly k^2 = N^2/25 ---
def blowup_c5(k):
    n = 5 * k
    parts = [list(range(i * k, (i + 1) * k)) for i in range(5)]
    edges = []
    for i in range(5):
        for u in parts[i]:
            for v in parts[(i + 1) % 5]:
                edges.append((u, v))
    return n, edges

for k in (2, 3):
    n, E = blowup_c5(k)
    b = beta_exact_int(n, E)
    print("C5-blowup k=%d N=%d: beta=%d expect %d -> %s" % (k, n, b, k * k, b == k * k), flush=True)
    assert b == k * k

def beta_bitmask(n, edges):
    nbr = [0] * n
    for u, v in edges:
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u
    full = (1 << n) - 1
    e = len(edges)
    best = None
    for S in range(1 << (n - 1)):   # vertex n-1 always outside S
        comp = full & ~S
        cut = 0
        t = S
        while t:
            v = (t & -t).bit_length() - 1
            cut += bin(nbr[v] & comp).count('1')
            t &= t - 1
        mono = e - cut
        if best is None or mono < best:
            best = mono
    return best

n, E = blowup_c5(4)
b = beta_bitmask(n, E)
print("C5-blowup k=4 N=20: beta=%d expect 16 -> %s" % (b, b == 16), flush=True)
assert b == 16

# --- fractional cut = integral cut on Petersen (per-vertex affinity check) ---
# t in {0,1/2,1}^10 scaled by 2 -> t in {0,1,2}; 4*cut = sum over edges t_u(2-t_v)+t_v(2-t_u); max must be 4*12=48
best = 0
for t in itertools.product((0, 1, 2), repeat=10):
    c4 = 0
    for (u, v) in P:
        c4 += t[u] * (2 - t[v]) + t[v] * (2 - t[u])
    if c4 > best:
        best = c4
print("Petersen fractional-grid 4*maxcut = %d (expect 48; no fractional gain) -> %s" % (best, best == 48), flush=True)
assert best == 48
print("ALL BASIC CHECKS PASS", flush=True)
