"""INDEPENDENT attack on  max_a psi(H,a)  for every reduced pattern.

Different algorithm from f8_wopt3.py (which used SLSQP on an epigraph form with a
*truncated* working set):  here we use the FULL set of colourings as the exact
oracle and run batched projected supergradient ascent from many random starts.

Two numbers are reported per pattern:
  bestpsi  = max over all visited a of the EXACT psi(H,a)  (a rigorous LOWER bound
             on max_a psi; if it ever exceeds 1/25 the conjecture is false)
  hit      = fraction of random starts whose local ascent reached 1/25 - 1e-9.
             This calibrates how reliable local optimisation is on this landscape:
             max_a psi >= 1/25 is PROVED (Lemma 6), so any start that ends below
             1/25 is a local optimiser failure.
"""
import glob, os, sys, time
import numpy as np
from audit_f8_lib import g6dec, edges

D = os.path.dirname(os.path.abspath(__file__))
TARGET = 1.0 / 25.0
rng = np.random.default_rng(20260725)
B = int(sys.argv[1]) if len(sys.argv) > 1 else 64      # batch (random starts)
IT = int(sys.argv[2]) if len(sys.argv) > 2 else 400    # ascent iterations
FILES = sys.argv[3:] if len(sys.argv) > 3 else sorted(glob.glob(os.path.join(D, 'f8_rmtf_*.g6')))


def proj_simplex(V):
    """columns of V -> Euclidean projection onto the probability simplex"""
    n, b = V.shape
    U = -np.sort(-V, axis=0)
    css = np.cumsum(U, axis=0) - 1.0
    ind = np.arange(1, n + 1)[:, None]
    cond = U - css / ind > 0
    rho = n - 1 - np.argmax(cond[::-1], axis=0)
    theta = css[rho, np.arange(b)] / (rho + 1.0)
    return np.maximum(V - theta, 0.0)


def rows_of(n, adj):
    E = edges(n, adj)
    m = len(E)
    side = np.arange(1 << (n - 1), dtype=np.int64) << 1
    M = np.empty((1 << (n - 1), m), dtype=bool)
    for k, (i, j) in enumerate(E):
        M[:, k] = (((side >> i) ^ (side >> j)) & 1) == 0
    M = np.unique(M, axis=0)
    return E, M


def run(n, adj):
    E, Mb = rows_of(n, adj)
    m = len(E)
    I = np.array([e[0] for e in E])
    J = np.array([e[1] for e in E])
    M = Mb.astype(np.float32)
    def psi_all(A):                      # A: (n,b) -> (rows,b)
        P = (A[I] * A[J]).astype(np.float32)
        return M @ P
    def starts(cnt):
        cols = []
        for _ in range(cnt):
            al = float(rng.choice([0.15, 0.4, 1.0, 3.0]))
            if rng.random() < 0.4:
                sup = rng.choice(n, size=int(rng.integers(3, n + 1)), replace=False)
                v = np.zeros(n)
                v[sup] = rng.dirichlet(np.ones(len(sup)) * al)
            else:
                v = rng.dirichlet(np.ones(n) * al)
            cols.append(v)
        return np.array(cols).T
    A = starts(B)
    A[:, 0] = 1.0 / n
    # seed a few starts with induced-C5 style weightings (support 5, weight 1/5)
    best = 0.0
    besta = None
    step = 0.5
    for it in range(IT):
        R = psi_all(A)
        arg = np.argmin(R, axis=0)
        val = R[arg, np.arange(B)]
        k = int(np.argmax(val))
        if val[k] > best:
            best, besta = float(val[k]), A[:, k].copy()
        G = np.zeros((n, B))
        for b in range(B):
            sel = Mb[arg[b]]
            ii, jj = I[sel], J[sel]
            np.add.at(G[:, b], ii, A[jj, b])
            np.add.at(G[:, b], jj, A[ii, b])
        eta = step * (0.997 ** it)
        A = proj_simplex(A + eta * G)
        if it % 97 == 96:                # random restarts of the worst half
            R2 = psi_all(A)
            v2 = R2.min(axis=0)
            bad = np.argsort(v2)[:B // 2]
            A[:, bad] = starts(len(bad))
    R = psi_all(A)
    fin = R.min(axis=0)
    hit = float(np.mean(fin >= TARGET - 1e-7))
    return best, besta, hit, M.shape[0], m


tot = 0
worst_hit = (2.0, None)
gmax = 0.0
t0 = time.time()
for fn in FILES:
    k = int(fn.rsplit('_', 1)[1].split('.')[0])
    lines = [l.strip() for l in open(fn) if l.strip()]
    if not lines:
        continue
    mx, mn_hit, over = 0.0, 1.0, []
    for l in lines:
        n, adj = g6dec(l)
        best, besta, hit, nr, m = run(n, adj)
        tot += 1
        mx = max(mx, best)
        mn_hit = min(mn_hit, hit)
        if hit < worst_hit[0]:
            worst_hit = (hit, l)
        if best > TARGET + 1e-9:
            over.append((l, best))
    gmax = max(gmax, mx)
    print(f"n={k:2d}  {len(lines):4d} patterns   max exact psi found = {mx:.12f}  "
          f"(target {TARGET:.12f}, excess {mx-TARGET:+.2e})   min hit-rate = {mn_hit:.3f}"
          + (f"   *** OVER: {over}" if over else ""), flush=True)
print(f"\nTOTAL {tot} patterns, global max exact psi = {gmax:.12f}, "
      f"worst start-hit-rate {worst_hit[0]:.3f} at {worst_hit[1]}  ({time.time()-t0:.0f}s)")
