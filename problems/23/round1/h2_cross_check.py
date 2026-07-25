"""H2: INDEPENDENT cross-check of the weighted-blow-up maximum.

Different algorithm from h2_opt.exe (which does integer steepest-ascent hill climbing):
here we maximise the CONTINUOUS objective
    g(H) = max_{x in simplex} min_{S subset V(H)} sum_{ij in E(H) monochromatic under S} x_i x_j
by projected-gradient ascent on a soft-min surrogate with annealed sharpness, from many
random starts, vectorised over all 2^(h-1) cuts with numpy.

Any x found with min_S q_S(x) > 1/25 would be a counterexample seed; we then round to
integers and verify exactly.  Reported number is 25 * g.
"""
import sys
import numpy as np
from h2_lib import g6_decode, num_edges


def cut_matrices(n, adj):
    """A[s] = 0/1 symmetric matrix of monochromatic edges under cut s (upper triangle)."""
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]
    ncut = 1 << (n - 1)
    M = np.zeros((ncut, n, n), dtype=np.float64)
    for s in range(ncut):
        side = s << 1
        for (u, v) in E:
            if ((side >> u) & 1) == ((side >> v) & 1):
                M[s, u, v] = 1.0
                M[s, v, u] = 1.0
    return M


def gmax(n, adj, starts=40, iters=600, rng=None):
    if rng is None:
        rng = np.random.default_rng(20260725)
    M = cut_matrices(n, adj)
    best = 0.0
    bestx = None
    for t in range(starts):
        x = rng.dirichlet(np.ones(n) * (0.4 if t else 5.0))
        for it in range(iters):
            beta = 200.0 * (1.0 + 40.0 * it / iters)
            Mx = M @ x                      # (ncut, n)
            q = 0.5 * np.einsum('sn,n->s', Mx, x)
            mn = q.min()
            wgt = np.exp(-beta * (q - mn))
            wgt /= wgt.sum()
            grad = np.einsum('s,sn->n', wgt, Mx)
            grad -= grad.mean()
            step = 0.05 / (1.0 + 6.0 * it / iters)
            x = x + step * grad / (np.abs(grad).max() + 1e-12)
            x = np.maximum(x, 0.0)
            s = x.sum()
            if s <= 0:
                break
            x /= s
        Mx = M @ x
        q = 0.5 * np.einsum('sn,n->s', Mx, x)
        v = q.min()
        if v > best:
            best, bestx = v, x.copy()
    return best, bestx


if __name__ == "__main__":
    files = sys.argv[1:] or ["h2_bases_all.g6"]
    worst = 0.0
    worst_line = None
    for fn in files:
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            n, adj = g6_decode(line)
            if n > 13:
                continue
            v, x = gmax(n, adj)
            r = 25.0 * v
            if r > worst:
                worst, worst_line = r, (line, n, x)
            flag = "  *** EXCEEDS 1/25 ***" if r > 1.0 + 1e-9 else ""
            print(f"{line}\th={n}\t25*g={r:.8f}{flag}")
            sys.stdout.flush()
    print(f"\nMAX over checked bases: 25*g = {worst:.8f}")
    if worst_line:
        print("argmax base:", worst_line[0], "x =", np.round(worst_line[2], 5))
