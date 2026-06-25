import sys
sys.path.insert(0, '.')
exec(open('ref_sublemma_check.py').read().split('if __name__')[0])
import numpy as np
import verify_bridge_QFC25 as vb

# Route (a): replace the uniform geodesic flow by the UNIT CURRENT FLOW (electrical),
# restricted to the geodesic (shortest-path DAG) so cycles stay odd & length ell.
# Claim under test: current flow satisfies vertex congestion 2*lam_v <= deg(v).
# We compute the current flow on the FULL bipartite graph B between u and v (the standard
# effective-resistance flow), then form lam_v = sum_M |through-flow at v| (vertex throughput).
# NOTE: the unrestricted current flow is NOT supported on geodesics, so cycles may be longer
# than ell -- but the colleague's route (a) explicitly proposes the current flow, so we test it
# as a congestion object. We measure 2*lam_v/deg_v.


def current_flow_potentials(N, adjB, u, v):
    # Solve Laplacian L phi = e_u - e_v on the connected component of u in B, phi[v]=0 ref.
    comp = [x for x in range(N) if blayers(N, adjB, u)[x] >= 0]
    idx = {x: i for i, x in enumerate(comp)}
    k = len(comp)
    Lap = np.zeros((k, k))
    for x in comp:
        for y in adjB[x]:
            Lap[idx[x], idx[x]] += 1
            Lap[idx[x], idx[y]] -= 1
    b = np.zeros(k)
    b[idx[u]] = 1.0
    b[idx[v]] = -1.0
    # ground vertex v
    Lap2 = Lap.copy()
    Lap2[idx[v], :] = 0
    Lap2[idx[v], idx[v]] = 1.0
    b2 = b.copy()
    b2[idx[v]] = 0.0
    phi = np.linalg.solve(Lap2, b2)
    pot = {x: phi[idx[x]] for x in comp}
    # vertex throughput = (1/2) sum_{edges at x} |current| , minus source/sink correction;
    # define lam_x = (1/2) sum_{y~x} |phi[x]-phi[y]| for interior, and for u/v it is the
    # injected unit so throughput counted as 1 (consistent with uniform flow convention).
    lam = {}
    for x in comp:
        through = 0.5 * sum(abs(pot[x] - pot[y]) for y in adjB[x])
        lam[x] = through
    return lam, comp


def check_current(N, A, label):
    adj = adjset(N, A)
    E = [(u, v) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj)
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in E:
        if side[u] != side[v]:
            adjB[u].add(v)
            adjB[v].add(u)
    lam = [0.0] * N
    for (u, v) in M:
        lf, comp = current_flow_potentials(N, adjB, u, v)
        for x in lf:
            lam[x] += lf[x]
    deg = [len(adj[u]) for u in range(N)]
    mr = max((2 * lam[v] / deg[v] if deg[v] > 0 else 0) for v in range(N))
    E2 = sum(l * l for l in lam)
    print(f"{label:12s} N={N}: CURRENT-flow max(2lam/deg)={mr:.3f}  E2={E2:.2f}  "
          f"E2<=N^2/25={N*N/25.0:.2f}? {E2<=N*N/25.0+1e-9}")


for (N, A, lab) in [(*vb.gpt_k23(), "K23-N13"), (*vb.c5n(1), "C5[1]"),
                    (*vb.c5n(2), "C5[2]"), (*vb.c5n(4), "C5[4]"), (*vb.petersen(), "Petersen")]:
    check_current(N, A, lab)
