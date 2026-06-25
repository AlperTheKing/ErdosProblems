"""STRESS the spread-geodesic congestion bound on a WIDER class of 2-connected edge-critical tri-free
atoms: subdivisions of K4/K5/K33, theta-graphs, prisms/Mobius-Kantor, generalized Petersen, random
2-connected tri-free graphs, C5[q] perturbations. For each that is 2-connected + edge-critical, check
   rho_spread <= max{1, n^2/(25 t)}   and   value 25t^2/n^2 <= t  (i.e. t <= n^2/25, the theorem).
Report worst ratio + any violation with the witness.
"""
import numpy as np
import random
from collections import deque, defaultdict
import verify_D25_lemma16 as L
from exp_lemma16_atoms import is_2connected, tau_of, is_edge_critical
from primal_packing_attempt import all_geodesics_load
from test_qfc_atoms import rho_spread


def from_edges(N, elist):
    A = [0]*N
    for (u, v) in elist:
        A[u] |= 1 << v; A[v] |= 1 << u
    return N, A


def is_triangle_free(N, A):
    adj = L.adjset(N, A)
    for u in range(N):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


def subdivided_complete(k, sub):
    """K_k with each edge subdivided 'sub' times (sub>=1 -> triangle-free if sub>=1 makes paths len>=2)."""
    base = [(i, j) for i in range(k) for j in range(i+1, k)]
    N = k; elist = []
    for (u, v) in base:
        prev = u
        for s in range(sub):
            w = N; N += 1; elist.append((prev, w)); prev = w
        elist.append((prev, v))
    return from_edges(N, elist)


def theta_graph(lens):
    """two endpoints joined by len(lens) internally-disjoint paths of given edge-lengths."""
    s, t = 0, 1; N = 2; elist = []
    for Ln in lens:
        prev = s
        for i in range(Ln-1):
            w = N; N += 1; elist.append((prev, w)); prev = w
        elist.append((prev, t))
    return from_edges(N, elist)


def gen_petersen(n, k):
    N = 2*n; elist = []
    for i in range(n):
        elist.append((i, (i+1) % n))           # outer
        elist.append((i, n+i))                  # spoke
        elist.append((n+i, n+((i+k) % n)))      # inner
    return from_edges(N, elist)


def c5q_perturb(q, seed):
    N, A = L.c5n(q)
    rng = random.Random(seed)
    # remove a random edge, add a random non-edge keeping triangle-free
    adj = L.adjset(N, A)
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    if edges:
        u, v = rng.choice(edges); A[u] &= ~(1 << v); A[v] &= ~(1 << u)
    for _ in range(40):
        a, b = rng.randrange(N), rng.randrange(N)
        if a != b and not ((A[a] >> b) & 1):
            A[a] |= 1 << b; A[b] |= 1 << a
            if is_triangle_free(N, A):
                break
            A[a] &= ~(1 << b); A[b] &= ~(1 << a)
    return N, A


def random_2conn_trifree(N, p, seed):
    rng = random.Random(seed)
    A = [0]*N
    for u in range(N):
        for v in range(u+1, N):
            if rng.random() < p:
                A[u] |= 1 << v; A[v] |= 1 << u
                if not is_triangle_free(N, A):
                    A[u] &= ~(1 << v); A[v] &= ~(1 << u)
    return N, A


def critical_atom_core(N, A):
    """peel to a 2-connected edge-critical core if possible; else return None. Simple greedy: remove
    edges that don't drop tau, then check 2-connectivity. (Just test the graph itself for atom-hood.)"""
    adj = L.adjset(N, A)
    if not is_2connected(N, adj):
        return None
    tau = tau_of(N, adj)
    if tau == 0:
        return None
    if not is_edge_critical(N, A, adj, tau):
        return None
    if not is_triangle_free(N, A):
        return None
    return (N, A, tau)


def check(label, builder):
    N, A = builder
    core = critical_atom_core(N, A)
    if core is None:
        return None
    N, A, tau = core
    r = rho_spread(N, A)
    if r is None:
        return None
    rho, t, NN = r
    bound = max(1.0, NN*NN/(25.0*t))
    ratio = rho/bound
    thm_ok = t <= NN*NN/25.0 + 1e-9
    flag = "VIOL" if rho > bound+1e-7 else ("THM-FAIL" if not thm_ok else "ok")
    print(f"  {label:22s} N={NN:3d} tau={t:3d} rho_spread={rho:.4f} bound={bound:.4f} ratio={ratio:.4f} "
          f"t<=n^2/25:{thm_ok} [{flag}]", flush=True)
    return ratio, (rho > bound+1e-7)


def main():
    worst = 0.0; viol = 0; tested = 0
    print("=== STRESS spread-geodesic congestion on atoms ===")
    builders = []
    for k in [4, 5]:
        for sub in [1, 2, 3]:
            builders.append((f"K{k}sub{sub}", subdivided_complete(k, sub)))
    for lens in [[4, 6], [4, 4, 4], [4, 6, 6], [5, 5, 5], [4, 4, 6], [6, 6, 6], [4, 6, 8]]:
        builders.append((f"theta{lens}", theta_graph(lens)))
    for (n, k) in [(5, 2), (7, 2), (8, 3), (9, 2), (10, 2), (10, 3), (11, 2)]:
        builders.append((f"GP({n},{k})", gen_petersen(n, k)))
    for q in [2, 3, 4]:
        for s in range(6):
            builders.append((f"C5[{q}]p{s}", c5q_perturb(q, s)))
    for N in [11, 12, 13, 14, 15]:
        for s in range(12):
            for p in [0.3, 0.4, 0.5]:
                builders.append((f"rnd{N}_{p}_{s}", random_2conn_trifree(N, p, s*100+int(p*10))))
    for label, b in builders:
        res = check(label, b)
        if res is not None:
            tested += 1; worst = max(worst, res[0]); viol += int(res[1])
    print(f"\n>>> tested {tested} atoms; spread-congestion VIOLATIONS={viol}; worst ratio={worst:.4f}")


if __name__ == "__main__":
    main()
