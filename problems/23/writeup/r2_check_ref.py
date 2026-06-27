#!/usr/bin/env python3
"""
Independent re-implementation #1 (REFERENCE) of Erdos #23 Step-2 R2 MASTER INEQUALITY.

CLEAN ROOM: This file imports nothing from bridge/flagsdp/*. It uses only the
standard library plus geng.exe output. It re-derives every quantity from the
problem statement.

For a triangle-free simple connected graph G on n vertices:
  1. MAX CUT: brute force over 2^(n-1) vertex 2-colorings (vertex 0 fixed to side 0),
     maximize the number of cut edges (endpoints on opposite sides).
  2. CONNECTED-B FILTER: among all maximum cuts, keep those whose cut-edge graph B
     is connected (spans all n vertices reachable from vertex 0 via cut edges).
  3. GAMMA-MIN SELECTION: among connected-B max cuts with >=1 bad (monochromatic)
     edge and where every bad edge has a B-path, pick the cut minimizing Gamma.
  4. Gamma(G) = sum over bad edges (u,v) of ell^2, ell = d_B(u,v)+1.
  5. D(C) over shortest bad geodesics; D*(G) = min over all shortest bad geodesics.
  6. MASTER:  Gamma + D* <= n^2.   LOCAL: Gamma + D(C) <= n^2 for every shortest C.

Exposes master_check(n, edges) -> dict or None.
"""

import sys
import os
import subprocess
from collections import deque
from itertools import combinations

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


def decode_graph6(line):
    """Decode a graph6 string to (n, edges). Column-major upper triangle."""
    line = line.strip()
    data = [ord(c) - 63 for c in line]
    n = data[0]
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def is_triangle_free(n, adj):
    """Check triangle-free (defensive; geng -t already guarantees it)."""
    for u in range(n):
        nbrs = adj[u]
        for v in nbrs:
            if v <= u:
                continue
            # common neighbor => triangle
            if adj[u] & adj[v]:
                return False
    return True


def bfs_dist(n, badj, src, dst):
    """Shortest distance src->dst in graph given by adjacency-set list badj.
    Returns -1 if unreachable."""
    if src == dst:
        return 0
    seen = [False] * n
    seen[src] = True
    q = deque([(src, 0)])
    while q:
        u, d = q.popleft()
        for w in badj[u]:
            if not seen[w]:
                if w == dst:
                    return d + 1
                seen[w] = True
                q.append((w, d + 1))
    return -1


def all_shortest_paths(n, badj, src, dst):
    """Return a list of all shortest src->dst paths (each a vertex list incl.
    endpoints) in graph badj. Empty list if unreachable."""
    # BFS layering
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for w in badj[u]:
            if dist[w] == -1:
                dist[w] = dist[u] + 1
                q.append(w)
    if dist[dst] == -1:
        return []
    # Backtrack: predecessors on shortest-path DAG
    paths = []
    target_d = dist[dst]

    def backtrack(v, acc):
        if v == src:
            paths.append([src] + acc[::-1])
            return
        for w in badj[v]:
            if dist[w] == dist[v] - 1:
                backtrack(w, acc + [v])

    backtrack(dst, [])
    return paths


def compute_DC(n, C_vertices, bad_edges, cut_edges):
    """D(C): K = V \\ C. Mp = bad edges within K, Be = cut edges within K.
    D(C) = max(0, max over 2-colorings mask of K of (#cut-bad - #cut-cut)).
    Returns None if |K| > 20 (treat C as undefined)."""
    Cset = set(C_vertices)
    K = [v for v in range(n) if v not in Cset]
    if len(K) > 20:
        return None
    if not K:
        # no vertices outside C: dM=dB=0 always -> D(C)=0
        return 0
    pos = {v: i for i, v in enumerate(K)}
    Mp = [(pos[a], pos[b]) for (a, b) in bad_edges
          if a in pos and b in pos]
    Be = [(pos[a], pos[b]) for (a, b) in cut_edges
          if a in pos and b in pos]
    m = len(K)
    best = 0  # max(0, ...)
    # Fix K[0] to side 0 by symmetry (dM,dB invariant under global flip).
    for mask in range(1 << (m - 1)):
        full = mask << 1  # bit 0 (K[0]) stays 0
        dM = 0
        for a, b in Mp:
            if ((full >> a) ^ (full >> b)) & 1:
                dM += 1
        dB = 0
        for a, b in Be:
            if ((full >> a) ^ (full >> b)) & 1:
                dB += 1
        val = dM - dB
        if val > best:
            best = val
    return best


def master_check(n, edges):
    """Main entry. Returns dict(gamma, dstar, master_slack, worst_local_slack)
    or None if G is not a connected-B config (no connected-B max cut, or |M|<1
    among valid cuts)."""
    # adjacency sets
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    # ---- 1. MAX CUT by brute force over 2^(n-1) masks (vertex 0 -> side 0) ----
    E = edges
    best_cut = -1
    for half in range(1 << (n - 1)):
        side = (half << 1)  # bit 0 = vertex 0 = side 0
        c = 0
        for a, b in E:
            if ((side >> a) ^ (side >> b)) & 1:
                c += 1
        if c > best_cut:
            best_cut = c

    # ---- enumerate ALL maximum cuts, build candidate configs ----
    candidates = []  # each: (gamma, side_int)
    for half in range(1 << (n - 1)):
        side = (half << 1)
        cut_edges = []
        bad_edges = []
        for a, b in E:
            if ((side >> a) ^ (side >> b)) & 1:
                cut_edges.append((a, b))
            else:
                bad_edges.append((a, b))
        if len(cut_edges) != best_cut:
            continue
        # ---- 2. CONNECTED-B FILTER (B spans all n vertices, reachable from 0)
        badj = [set() for _ in range(n)]
        for a, b in cut_edges:
            badj[a].add(b)
            badj[b].add(a)
        # connectivity over all n vertices via cut edges
        seen = [False] * n
        seen[0] = True
        st = [0]
        cnt = 1
        while st:
            u = st.pop()
            for w in badj[u]:
                if not seen[w]:
                    seen[w] = True
                    cnt += 1
                    st.append(w)
        if cnt != n:
            continue  # B not connected -> reject this cut
        # ---- 4. bad edges; require >=1 ----
        if len(bad_edges) < 1:
            continue
        # ---- 5. Gamma: each bad edge must have a B-path; else invalid cut ----
        gamma = 0
        valid = True
        for (u, v) in bad_edges:
            d = bfs_dist(n, badj, u, v)
            if d < 0:
                valid = False
                break
            ell = d + 1
            gamma += ell * ell
        if not valid:
            continue
        candidates.append((gamma, side, cut_edges, bad_edges, badj))

    if not candidates:
        return None

    # ---- 3. GAMMA-MIN SELECTION ----
    gamma_min = min(c[0] for c in candidates)
    chosen = [c for c in candidates if c[0] == gamma_min]
    # tie-break is irrelevant for the inequality value of Gamma; but D* / local
    # depend on the chosen cut. Take the first gamma-min cut (deterministic).
    gamma, side, cut_edges, bad_edges, badj = chosen[0]

    # ---- 6/7/8. D(C) over all shortest bad geodesics; D* = min ----
    # Collect every shortest u-v B-path for every bad edge.
    DC_values = []
    for (u, v) in bad_edges:
        paths = all_shortest_paths(n, badj, u, v)
        for path in paths:
            dc = compute_DC(n, path, bad_edges, cut_edges)
            if dc is None:
                continue  # undefined C skipped
            DC_values.append(dc)

    if not DC_values:
        # All geodesics undefined (|K|>20). With n<=11 this never triggers.
        return None

    dstar = min(DC_values)
    worst_DC = max(DC_values)  # worst local => largest D(C) => smallest local slack
    master_slack = n * n - gamma - dstar
    worst_local_slack = n * n - gamma - worst_DC
    return {
        "gamma": gamma,
        "dstar": dstar,
        "master_slack": master_slack,
        "worst_local_slack": worst_local_slack,
    }


def run_sweep(nmax=11):
    print("Erdos #23 R2 MASTER INEQUALITY -- REFERENCE clean-room checker")
    print("=" * 70)
    overall_first_viol = None
    for n in range(5, nmax + 1):
        try:
            proc = subprocess.run(
                [GENG, "-tc", str(n)],
                capture_output=True, text=True, timeout=100000,
            )
        except Exception as e:
            print(f"n={n}: geng FAILED: {e}")
            break
        configs = 0
        master_viol = 0
        local_viol = 0
        min_master_slack = None
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            gn, edges = decode_graph6(line)
            res = master_check(gn, edges)
            if res is None:
                continue
            configs += 1
            ms = res["master_slack"]
            ls = res["worst_local_slack"]
            if min_master_slack is None or ms < min_master_slack:
                min_master_slack = ms
            if ms < 0:
                master_viol += 1
                if overall_first_viol is None:
                    overall_first_viol = (line.strip(), res)
            if ls < 0:
                local_viol += 1
                if overall_first_viol is None:
                    overall_first_viol = (line.strip(), res)
        print(f"n={n:2d}: configs={configs:7d}  master_viol={master_viol}  "
              f"local_viol={local_viol}  min_master_slack={min_master_slack}")
        sys.stdout.flush()
    if overall_first_viol:
        print("FIRST VIOLATION:", overall_first_viol)
    else:
        print("No violations found in the swept range.")


# ---------------- explicit tight constructions ----------------

def cycle_edges(verts):
    e = []
    k = len(verts)
    for i in range(k):
        e.append((verts[i], verts[(i + 1) % k]))
    return e


def check_tights():
    print()
    print("Explicit tight constructions (expect master slack EXACTLY 0):")
    print("-" * 70)
    results = {}

    # C5, C7, C9, C11 : odd cycles
    for k in (5, 7, 9, 11):
        e = cycle_edges(list(range(k)))
        r = master_check(k, e)
        results[f"C{k}"] = r
        print(f"C{k:<3}: {r}")

    # C5[2]: balanced C5 blow-up x2, n=10. Replace each vertex of C5 by 2
    # vertices; edges between blow-up classes of adjacent C5 vertices form a
    # complete bipartite K_{2,2}; no edges inside a class (independent sets).
    # vertices: class i -> {2i, 2i+1}, i in 0..4. C5 adjacency i ~ i+1 mod 5.
    e = []
    for i in range(5):
        j = (i + 1) % 5
        ci = [2 * i, 2 * i + 1]
        cj = [2 * j, 2 * j + 1]
        for a in ci:
            for b in cj:
                e.append((a, b))
    r = master_check(10, e)
    results["C5[2]"] = r
    print(f"C5[2]: {r}")

    all_zero = all(r is not None and r["master_slack"] == 0
                   for r in results.values())
    print(f"ALL FIVE master slack == 0 : {all_zero}")
    return results, all_zero


if __name__ == "__main__":
    nmax = 11
    if len(sys.argv) > 1:
        nmax = int(sys.argv[1])
    check_tights()
    print()
    run_sweep(nmax)
