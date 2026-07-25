"""
Blow-up-closed search for a counterexample to  bip(G) <= N^2/25.

LEMMA (proved in the write-up, verified below):  for a blow-up
H[n_1,...,n_h]  (vertex u of H replaced by an independent set of size n_u,
edges of H replaced by complete bipartite graphs),

    bip( H[n_1,...,n_h] )  =  min_{X subset V(H)}  sum_{uv in E(H), uv monochromatic under X}  n_u n_v .

Proof: for x in [0,1]^h let F(x) = sum_{uv in E(H)} n_u n_v ( x_u x_v + (1-x_u)(1-x_v) ),
the expected number of monochromatic edges when each blob u is split with a
fraction x_u on one side, in the "aligned" way; every bipartition of the blow-up
that splits blob u into a part of size a_u is at least as costly as the value at
x_u = a_u/n_u by convexity ... in fact equality holds because there are no edges
inside a blob, so the monochromatic count is exactly F(a_u/n_u) with n_u^2 scaling.
F is MULTILINEAR, hence attains its minimum over [0,1]^h at a vertex x in {0,1}^h,
i.e. at a genuine cut X of H.  QED

Consequently, with  x_u = n_u / N,

    bip(H[n]) / N^2  =  min_X  Q_X(x),      Q_X(x) = sum_{uv mono under X} x_u x_v ,

so the quantity

    f(H) := max_{x in simplex}  min_{X subset V(H)}  Q_X(x)

is exactly  sup over all blow-ups of H  of  bip/N^2 .  The conjecture implies
f(H) <= 1/25 for every triangle-free H, and ANY triangle-free H with a RATIONAL x
attaining more than 1/25 disproves it (clear denominators to get an integral
blow-up).  Note f(H) >= 1/25 whenever H contains a 5-cycle (every C5 subgraph of a
triangle-free graph is induced; put mass 1/5 on it).

f is monotone under edge addition inside the triangle-free world, so it suffices
to scan MAXIMAL triangle-free graphs.  It is also blow-up invariant, so we may
further restrict to twin-free graphs (this is only used to shrink the list).

Everything reported as a lower bound on f is re-verified in exact Fraction
arithmetic over all 2^(h-1) cuts.
"""
import os, subprocess, sys
from fractions import Fraction
from itertools import combinations
import numpy as np

from f5lib import parse_graph6, adj_masks, bip

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")


def maximal_triangle_free(n):
    """connected, triangle-free, and every non-adjacent pair has a common
    neighbour (= maximal triangle-free); also drop graphs with twins."""
    p = subprocess.run([GENG, "-tcq", str(n)], capture_output=True, text=True)
    out = []
    for g6 in p.stdout.split():
        nn, edges = parse_graph6(g6)
        adj = adj_masks(nn, edges)
        ok = True
        for u in range(nn):
            for v in range(u + 1, nn):
                if not (adj[u] >> v) & 1:
                    if not (adj[u] & adj[v]):
                        ok = False
                        break
            if not ok:
                break
        if not ok:
            continue
        # twin-free (no two vertices with identical neighbourhoods)
        if len(set(adj)) != nn:
            continue
        out.append((nn, edges))
    return out


def cut_matrices(n, edges):
    """For each of the 2^(n-1) cuts X (vertex 0 fixed inside X), the symmetric
    0/1 matrix M with M[u][v]=1 iff uv is an edge monochromatic under X."""
    mats = []
    for rest in range(1 << (n - 1)):
        S = 1 | (rest << 1)
        M = np.zeros((n, n))
        for u, v in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                M[u, v] = M[v, u] = 1.0
        mats.append(M)
    return np.array(mats), [1 | (r << 1) for r in range(1 << (n - 1))]


def project_simplex(v):
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    theta = (css[rho] - 1) / (rho + 1.0)
    return np.maximum(v - theta, 0)


def maximin(n, edges, restarts=40, iters=400, seed=0):
    M, cuts = cut_matrices(n, edges)
    rng = np.random.default_rng(seed)
    best_val, best_x = -1.0, None
    for r in range(restarts):
        x = project_simplex(rng.random(n))
        step = 0.5
        for t in range(iters):
            q = 0.5 * np.einsum('kij,i,j->k', M, x, x)
            k = int(np.argmin(q))
            g = M[k] @ x                      # gradient of Q_k
            x = project_simplex(x + step * g)
            step *= 0.995
        q = 0.5 * np.einsum('kij,i,j->k', M, x, x)
        v = float(q.min())
        if v > best_val:
            best_val, best_x = v, x.copy()
    return best_val, best_x, cuts


def exact_minQ(n, edges, xnum, den):
    """min over ALL cuts of sum_{mono} x_u x_v, exact, with x_u = xnum[u]/den."""
    best = None
    for rest in range(1 << (n - 1)):
        S = 1 | (rest << 1)
        tot = 0
        for u, v in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += xnum[u] * xnum[v]
        if best is None or tot < best:
            best = tot
    return Fraction(best, den * den)


def rationalize(x, den):
    a = [int(round(t * den)) for t in x]
    d = sum(a)
    if d != den:                      # fix rounding drift on the largest entry
        a[int(np.argmax(a))] += den - d
    return a


def main(hmin, hmax):
    print("h   #maximal-tf-twinfree   best f(H) found   1/25 = 0.04")
    overall = []
    for h in range(hmin, hmax + 1):
        gs = maximal_triangle_free(h)
        rows = []
        for (n, edges) in gs:
            v, x, _ = maximin(n, edges, restarts=25, iters=300, seed=h)
            rows.append((v, n, edges, x))
        rows.sort(reverse=True, key=lambda r: r[0])
        print(f"{h:2d}  {len(gs):8d}             {rows[0][0] if rows else 0:.6f}")
        for v, n, edges, x in rows[:4]:
            # exact certification of the lower bound at several denominators
            best_exact = Fraction(0)
            best_a = None
            for den in (60, 120, 210, 420, 840, 2520):
                a = rationalize(x, den)
                if min(a) < 0:
                    continue
                val = exact_minQ(n, edges, a, den)
                if val > best_exact:
                    best_exact, best_a = val, (a, den)
            print(f"     m={len(edges):3d} numeric f>={v:.6f}  EXACT lower bound "
                  f"f(H) >= {best_exact} = {float(best_exact):.6f}  "
                  f"{'>1/25 !!!' if best_exact > Fraction(1,25) else ''}")
            print(f"        edges={edges}")
            print(f"        witness x = {best_a[0] if best_a else None} / {best_a[1] if best_a else None}")
            overall.append((float(best_exact), h, edges))
    overall.sort(reverse=True)
    print("\nBEST EXACTLY-CERTIFIED f(H) OVERALL:", overall[0][:2] if overall else None)


if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    main(a, b)
