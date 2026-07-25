"""beta(H) = sup_x  bip(H[x]) / (sum x)^2   over nonnegative vertex weights x.

FACT (proved in the write-up): for a blow-up H[x] the maximum cut is attained by a
class-respecting bipartition, because each blow-up class is an independent set, so the
cut value is a linear function of the number of vertices of that class placed on one side.
Hence

    bip(H[x]) = min_{S subset V(H)}  sum_{uv in E(H), u,v both in S or both outside} x_u x_v .

Everything below is EXACT integer arithmetic (weights are integers summing to D; float64 is
used only for the matmul, where all values are integers < 2^53 so the products are exact).

If ever 25*bip > D^2 for a triangle-free H, that is an explicit counterexample to Erdos #23.
"""
import numpy as np, itertools, random

# ---------------------------------------------------------------- graph6 helpers
def g6_decode(line, n=None):
    line = line.strip()
    if n is None:
        n = ord(line[0]) - 63
    data = [ord(c) - 63 for c in line[1:]]
    bits = []
    for d in data:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    edges, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


# ---------------------------------------------------------------- core machinery
class Template:
    """Precomputed mono-incidence matrix of all class-respecting cuts of H."""

    def __init__(self, n, edges):
        self.n, self.edges = n, list(edges)
        m = len(self.edges)
        nm = 1 << (n - 1)            # cuts with vertex 0 fixed on side 0
        M = np.empty((nm, m), dtype=np.float64)
        eu = np.array([e[0] for e in self.edges], dtype=np.int64)
        ev = np.array([e[1] for e in self.edges], dtype=np.int64)
        for s in range(nm):
            mask = s << 1
            bu = (mask >> eu) & 1
            bv = (mask >> ev) & 1
            M[s] = (bu == bv)
        self.M = M                    # (#cuts, #edges) 1 = edge monochromatic
        self.eu, self.ev = eu, ev

    def bip(self, w):
        """exact integer bip(H[w]) plus the argmin cut mask"""
        w = np.asarray(w, dtype=np.float64)
        p = w[self.eu] * w[self.ev]
        vals = self.M @ p
        i = int(np.argmin(vals))
        return int(round(vals[i])), (i << 1)

    def bip_batch(self, W):
        """W: (k, n) integer weight rows -> (k,) bip values"""
        W = np.asarray(W, dtype=np.float64)
        P = W[:, self.eu] * W[:, self.ev]        # (k, m)
        vals = self.M @ P.T                       # (#cuts, k)
        return vals.min(axis=0)


def maximize(tmpl, D, restarts=40, seed=0, starts_extra=()):
    """max over integer w >= 0, sum w = D, of bip(H[w]) -- hill climbing on unit transfers."""
    n = tmpl.n
    rng = np.random.default_rng(seed)
    mv = np.array([(i, j) for i in range(n) for j in range(n) if i != j])
    MI, MJ = mv[:, 0], mv[:, 1]
    nmv = len(mv)
    delta = np.zeros((nmv, n), dtype=np.float64)
    delta[np.arange(nmv), MI] = -1.0
    delta[np.arange(nmv), MJ] += 1.0

    base = np.full(n, D // n, dtype=np.float64)
    base[: D - int(base.sum())] += 1
    starts = [base] + [np.asarray(s, dtype=np.float64) for s in starts_extra]
    for _ in range(restarts):
        w = np.bincount(rng.integers(0, n, D), minlength=n).astype(np.float64)
        starts.append(w)

    best, bestw = -1, None
    for w in starts:
        w = w.copy()
        cur = tmpl.bip(w)[0]
        for _ in range(400):
            cand = w[None, :] + delta
            ok = cand.min(axis=1) >= 0
            vals = np.where(ok, tmpl.bip_batch(cand), -1.0)
            k = int(np.argmax(vals))
            if vals[k] > cur:
                cur = int(round(vals[k])); w = cand[k]
            else:
                break
        if cur > best:
            best, bestw = cur, [int(x) for x in w]
    return best, bestw


def maximize_exhaustive(tmpl, D):
    """exact max over all integer compositions of D into n parts (small cases only)"""
    n = tmpl.n
    best, bestw = -1, None
    for w in itertools.combinations(range(D + n - 1), n - 1):
        prev, comp = -1, []
        for c in w:
            comp.append(c - prev - 1); prev = c
        comp.append(D + n - 1 - prev - 1)
        v = tmpl.bip(comp)[0]
        if v > best:
            best, bestw = v, comp
    return best, bestw


# ---------------------------------------------------------------- validation helper
def explicit_blowup(n, edges, w):
    """build the actual blow-up graph H[w] as (N, edge list)"""
    off, N = [], 0
    for i in range(n):
        off.append(N); N += w[i]
    E = []
    for (u, v) in edges:
        for a in range(w[u]):
            for b in range(w[v]):
                E.append((off[u] + a, off[v] + b))
    return N, E


def bip_bruteforce(N, E):
    """exact bip over ALL 2^(N-1) bipartitions (not only class-respecting)"""
    best = None
    eu = np.array([e[0] for e in E], dtype=np.int64); ev = np.array([e[1] for e in E], dtype=np.int64)
    for s in range(1 << (N - 1)):
        mask = s << 1
        bu = (mask >> eu) & 1
        bv = (mask >> ev) & 1
        v = int(np.sum(bu == bv))
        if best is None or v < best:
            best = v
    return best
