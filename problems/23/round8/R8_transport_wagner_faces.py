"""Face-by-face maximisation of the Wagner certificate product (all 255 supports)."""
import sys, numpy as np
sys.path.insert(0, ".")
from R8_transport_lib import *
from R8_transport_geomval import perfect_cuts

G = wagner(); cuts, cyc = perfect_cuts(G); n = G.n; k = len(cuts)
M = []
for S in cuts:
    A = np.zeros((n, n))
    for u, v in G.edges:
        if ((S >> u) & 1) == ((S >> v) & 1):
            A[u, v] = A[v, u] = 0.5
    M.append(A)

def logF(x):
    t = 0.0
    for A in M:
        q = x @ A @ x
        if q <= 1e-300: return -1e18
        t += np.log(q)
    return t / k

rng = np.random.default_rng(11)
best, bx, bs = -1e18, None, None
for supp in range(1, 1 << n):
    idx = [i for i in range(n) if (supp >> i) & 1]
    if len(idx) < 4: continue
    for _ in range(12):
        x = np.zeros(n); x[idx] = rng.random(len(idx)) + 0.05; x /= x.sum()
        cur, step = logF(x), 0.5
        if cur < -1e17: continue
        for _ in range(2000):
            g = np.zeros(n); ok = True
            for A in M:
                q = x @ A @ x
                if q <= 1e-300: ok = False; break
                g += 2 * (A @ x) / q
            if not ok: break
            g /= k
            y = x * np.exp(np.clip(step * g, -50, 50)); y[[i for i in range(n) if not (supp >> i) & 1]] = 0
            s = y.sum()
            if s <= 0: break
            y /= s
            v = logF(y)
            if v > cur + 1e-16: cur, x = v, y
            else:
                step *= 0.55
                if step < 1e-13: break
        if cur > best: best, bx, bs = cur, x.copy(), supp
print("Wagner faces: max over ALL 255 supports of prod nu^(1/5) = %.12f   (1/25 = 0.04)" % np.exp(best))
print("   argmax support =", [i for i in range(n) if (bs >> i) & 1], " x =", np.round(bx, 6))
print("   excess over 1/25: %.3e" % (np.exp(best) - 0.04))
