"""
FULLY INDEPENDENT re-implementation of the GPI / T_uniform pipeline for Erdos #23.
Does NOT import census_GPI. Re-implements:
  graph6 decode, brute max-cut, gamma-min connected-B max-cut, shortest geodesics,
  T_uniform, K = N + (N^2 - Gamma). Verifies U: max_v T_uniform <= K (exact Fractions).
"""
import sys, subprocess
from fractions import Fraction
from collections import deque
from itertools import product

GENG = "E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

# ---------- graph6 decode ----------
def g6_decode(s):
    """Decode nauty graph6 -> (n, adjacency-as-set-of-frozensets)."""
    data = [ord(c) - 63 for c in s]
    # number of vertices
    if data[0] != 63:
        n = data[0]; rest = data[1:]
    else:
        # big n encodings
        if data[1] != 63:
            n = (data[1] << 12) | (data[2] << 6) | data[3]
            rest = data[4:]
        else:
            n = (data[2] << 30)|(data[3]<<24)|(data[4]<<18)|(data[5]<<12)|(data[6]<<6)|data[7]
            rest = data[8:]
    # bit vector of upper triangle, column-major (j from 1..n-1, i from 0..j-1)
    bits = []
    for x in rest:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges

def adjmat(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return adj

# ---------- brute max cut (all max-cut side vectors) ----------
def all_max_cuts(n, edges):
    """Return list of side-vectors (tuple of 0/1) achieving max cut. Fix vertex0 side=0."""
    best = -1
    res = []
    for mask in range(1 << (n - 1)):
        side = [0] * n
        for i in range(n - 1):
            if (mask >> i) & 1:
                side[i + 1] = 1
        cut = 0
        for u, v in edges:
            if side[u] != side[v]:
                cut += 1
        if cut > best:
            best = cut
            res = [tuple(side)]
        elif cut == best:
            res.append(tuple(side))
    return best, res

# ---------- B-connectivity (cut subgraph connected) and gamma ----------
def cut_edges(edges, side):
    return [(u, v) for (u, v) in edges if side[u] != side[v]]

def is_B_connected(n, edges, side):
    """The bipartite cut graph B = (V, cut edges). Connected means all n vertices
    are in one component when restricted to cut edges (every vertex must be incident).
    We require the cut subgraph to span and be connected on its non-isolated support,
    but for Gamma we need d_B (distance in B). Convention (census_GPI): connected-B
    means the graph on cut edges is connected and spans all vertices."""
    ce = cut_edges(edges, side)
    adjB = [set() for _ in range(n)]
    for u, v in ce:
        adjB[u].add(v); adjB[v].add(u)
    # all vertices must have a B-edge (spanning) and be one component
    if any(len(adjB[x]) == 0 for x in range(n)):
        return False, adjB
    seen = {0}
    dq = deque([0])
    while dq:
        x = dq.popleft()
        for y in adjB[x]:
            if y not in seen:
                seen.add(y); dq.append(y)
    return (len(seen) == n), adjB

def bfs_dist(adjB, s, n):
    dist = [-1] * n
    dist[s] = 0
    dq = deque([s])
    while dq:
        x = dq.popleft()
        for y in adjB[x]:
            if dist[y] == -1:
                dist[y] = dist[x] + 1
                dq.append(y)
    return dist

def gamma_of_cut(n, edges, side):
    """Return (Gamma, M, ell, adjB) for a connected-B cut, else None.
    M = bad (monochromatic) edges. ell[f] = d_B(u,v)+1 (shortest odd cycle length)."""
    ok, adjB = is_B_connected(n, edges, side)
    if not ok:
        return None
    M = [(u, v) for (u, v) in edges if side[u] == side[v]]
    ell = {}
    Gamma = 0
    for (u, v) in M:
        dist = bfs_dist(adjB, u, n)
        dv = dist[v]
        if dv == -1:
            return None  # endpoints not connected in B (shouldn't happen if spanning+connected)
        L = dv + 1
        ell[(u, v)] = L
        Gamma += L * L
    return Gamma, M, ell, adjB

def gamma_min_cut(n, edges):
    """Among ALL max cuts that are connected-B, pick the one minimizing Gamma.
    Returns (side, Gamma, M, ell, adjB) or None if no connected-B max cut."""
    mc, cuts = all_max_cuts(n, edges)
    best = None
    for side in cuts:
        r = gamma_of_cut(n, edges, side)
        if r is None:
            continue
        Gamma, M, ell, adjB = r
        if best is None or Gamma < best[1]:
            best = (side, Gamma, M, ell, adjB)
    return best

# ---------- shortest B-geodesics between bad endpoints ----------
def all_shortest_paths(adjB, s, t, n):
    """All shortest paths s->t in B (vertex lists)."""
    dist = bfs_dist(adjB, s, n)
    if dist[t] == -1:
        return []
    # backtrack from t along decreasing-dist edges
    paths = []
    def rec(x, acc):
        if x == s:
            paths.append([s] + acc[::-1])
            return
        for y in adjB[x]:
            if dist[y] == dist[x] - 1:
                rec(y, acc + [x])
    rec(t, [])
    return paths

# ---------- T_uniform ----------
def t_uniform(n, edges, side, M, ell, adjB):
    """T_uniform(v) = sum over bad edges f of ell(f) * (#shortest cycles of f through v)/(#shortest cycles of f).
    A 'shortest cycle' of f=(u,v) = a shortest B-geodesic from u to v plus the bad edge.
    Vertices on the cycle = vertices on the geodesic path."""
    T = [Fraction(0) for _ in range(n)]
    for (u, v) in M:
        Ps = all_shortest_paths(adjB, u, v, n)
        nf = len(Ps)
        assert nf > 0
        share = Fraction(ell[(u, v)], nf)
        for P in Ps:
            for vert in P:
                T[vert] += share
    return T

def check_graph(n, edges):
    res = gamma_min_cut(n, edges)
    if res is None:
        return None  # no connected-B max cut -> not a config under test
    side, Gamma, M, ell, adjB = res
    T = t_uniform(n, edges, side, M, ell, adjB)
    maxT = max(T) if T else Fraction(0)
    K = n + (n * n - Gamma)
    return dict(n=n, Gamma=Gamma, K=Fraction(K), maxT=maxT, slack=Fraction(K) - maxT,
                side=side, M=M, ell=ell)

# ---------- C5 blow-up ----------
def c5_blowup(t):
    """Balanced C5[t]: 5 groups of t vertices; group i fully joined to group i+1 (mod5),
    no edges inside a group. N=5t, triangle-free, Gamma=N^2."""
    n = 5 * t
    grp = [list(range(i * t, (i + 1) * t)) for i in range(5)]
    edges = []
    for i in range(5):
        for a in grp[i]:
            for b in grp[(i + 1) % 5]:
                edges.append((a, b))
    return n, edges

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "census"
    if mode == "census":
        lo = int(sys.argv[2]); hi = int(sys.argv[3])
        global_min_slack = None
        viol = []
        for N in range(lo, hi + 1):
            out = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
            cnt = 0
            tight = 0
            worst = None
            for g6 in out:
                n, edges = g6_decode(g6)
                r = check_graph(n, edges)
                if r is None:
                    continue
                cnt += 1
                slack = r["slack"]
                if global_min_slack is None or slack < global_min_slack:
                    global_min_slack = slack
                if worst is None or slack < worst:
                    worst = slack
                if slack == 0:
                    tight += 1
                if slack < 0:
                    viol.append((g6, r["n"], r["Gamma"], str(r["K"]), str(r["maxT"])))
            print(f"N={N}: configs(connected-B max cut)={cnt} | violations(slack<0)={len([v for v in viol if g6_decode(v[0])[0]==N])} | tight(slack=0)={tight} | worst_slack={worst}")
        print("GLOBAL min_slack =", global_min_slack)
        print("VIOLATIONS =", viol)
    elif mode == "blowup":
        for t in [2, 3, 4]:
            n, edges = c5_blowup(t)
            r = check_graph(n, edges)
            print(f"C5[{t}] N={n} Gamma={r['Gamma']} K={r['K']} maxT={r['maxT']} slack={r['slack']} "
                  f"tight(maxT==N)={r['maxT']==n}")
    elif mode == "witness":
        g6 = sys.argv[2]
        n, edges = g6_decode(g6)
        r = check_graph(n, edges)
        if r is None:
            print(f"{g6}: NO connected-B max cut")
        else:
            print(f"{g6} N={r['n']} Gamma={r['Gamma']} K={r['K']} maxT={r['maxT']} slack={r['slack']}")
            print("  side=", r["side"])
            print("  M=", r["M"])
            print("  ell=", {k: v for k, v in r["ell"].items()})
