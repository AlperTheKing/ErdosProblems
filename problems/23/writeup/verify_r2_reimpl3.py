#!/usr/bin/env python3
"""
Independent re-implementation #3 of Erdos #23 Step-2 R2 MASTER INEQUALITY checker.

CLEAN ROOM: written from the problem spec only. Does NOT import / read any other
bridge/flagsdp/*.py file. Uses only geng.exe + this code.

Spec recap (per the task):
  1. MAX CUT over a triangle-free connected graph G (brute force over 2^(n-1) masks,
     vertex 0 fixed to side 0).
  2. CONNECTED-B FILTER: B = (V, cut-edges). Keep only max cuts whose B is connected.
     If no max cut has connected B -> SKIP G.
  3. GAMMA-MIN SELECTION: among valid connected-B max cuts, choose the one minimizing Gamma.
  4. BAD EDGES M = monochromatic edges. If |M| < 1 -> SKIP this config.
  5. For each bad edge (u,v): d_B(u,v) = shortest dist in B (cut edges only); ell = d_B+1.
     GAMMA = sum_{(u,v) in M} ell^2.  A cut with a bad edge having no B-path is INVALID
     (excluded from selection).
  6. SHORTEST BAD GEODESIC C = a shortest u-v B-path for a bad edge (vertices incl. endpoints).
  7. D(C): K = V minus vertices(C). Mp = bad edges with both ends in K. Be = cut edges both ends in K.
     Over every 2-coloring 'mask' of K: dM = #cut-monochromatic-edge crossings, dB = #cut-edge crossings,
     D(C) = max(0, max_mask (dM - dB)). If |K| > 20 -> treat C as undefined (skip it).
  8. D*(G) = min over ALL shortest bad geodesics C of D(C).
  9. MASTER:  Gamma + D* <= n^2.   LOCAL: Gamma + D(C) <= n^2 for EVERY shortest C.

We also confirm the five tight cases (C5, C7, C9, C5[2], C11) give master slack exactly 0.
"""

import sys
import subprocess
from collections import deque
from itertools import product

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


# ---------------------------------------------------------------------------
# graph6 decode (column-major upper triangle)
# ---------------------------------------------------------------------------
def decode_graph6(line):
    """Return (n, adj) where adj is a list of int bitmasks (adjacency)."""
    bs = line.strip()
    if not bs:
        return None
    data = [ord(c) - 63 for c in bs]
    n = data[0]
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    adj = [0] * n
    idx = 0
    # column-major: for j in 1..n-1, for i in 0..j-1
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= (1 << j)
                adj[j] |= (1 << i)
            idx += 1
    return n, adj


def edges_from_adj(n, adj):
    es = []
    for i in range(n):
        m = adj[i] >> (i + 1)
        j = i + 1
        while m:
            if m & 1:
                es.append((i, j))
            m >>= 1
            j += 1
    return es


def is_triangle_free(n, adj):
    for u in range(n):
        nb = adj[u]
        v = 0
        m = nb
        while m:
            if m & 1:
                # common neighbours of u and v among > v? any common neighbour => triangle
                if adj[u] & adj[v]:
                    return False
            m >>= 1
            v += 1
    return True


def is_connected_graph(n, adj):
    if n == 0:
        return True
    seen = 1  # bit 0
    stack = [0]
    while stack:
        u = stack.pop()
        nb = adj[u] & ~seen
        v = 0
        m = nb
        while m:
            if m & 1:
                seen |= (1 << v)
                stack.append(v)
            m >>= 1
            v += 1
    return seen == (1 << n) - 1


# ---------------------------------------------------------------------------
# Max cut (brute force over 2^(n-1), vertex 0 fixed side 0)
# ---------------------------------------------------------------------------
def all_max_cuts(n, edges):
    """Return (best, list_of_side_arrays) for cuts achieving max cut size.
       side is a tuple of length n with side[0]==0."""
    best = -1
    cuts = []
    # iterate over assignments of vertices 1..n-1
    for assign in range(1 << (n - 1)):
        side = [0] * n
        a = assign
        for v in range(1, n):
            side[v] = a & 1
            a >>= 1
        c = 0
        for (u, w) in edges:
            if side[u] != side[w]:
                c += 1
        if c > best:
            best = c
            cuts = [tuple(side)]
        elif c == best:
            cuts.append(tuple(side))
    return best, cuts


# ---------------------------------------------------------------------------
# BFS distances in B (cut-edge subgraph) using bitmask adjacency of B
# ---------------------------------------------------------------------------
def build_B_adj(n, edges, side):
    """bitmask adjacency restricted to cut edges (side[u]!=side[v])."""
    badj = [0] * n
    for (u, w) in edges:
        if side[u] != side[w]:
            badj[u] |= (1 << w)
            badj[w] |= (1 << u)
    return badj


def B_connected(n, badj):
    seen = 1
    stack = [0]
    while stack:
        u = stack.pop()
        m = badj[u] & ~seen
        v = 0
        mm = m
        while mm:
            if mm & 1:
                seen |= (1 << v)
                stack.append(v)
            mm >>= 1
            v += 1
    return seen == (1 << n) - 1


def bfs_dist_and_preds(n, badj, src):
    """BFS from src in B. Return (dist list with -1 for unreachable,
       preds: list of predecessor-bitmasks forming the shortest-path DAG)."""
    dist = [-1] * n
    preds = [0] * n  # bitmask of predecessors on a shortest path
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        m = badj[u]
        v = 0
        mm = m
        while mm:
            if mm & 1:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    preds[v] |= (1 << u)
                    q.append(v)
                elif dist[v] == dist[u] + 1:
                    preds[v] |= (1 << u)
                mm >>= 1
                v += 1
            else:
                mm >>= 1
                v += 1
    return dist, preds


def enumerate_geodesics(src, dst, preds):
    """Enumerate all shortest src->dst paths via predecessor-DAG.
       Returns list of paths (each a list of vertices from src to dst inclusive)."""
    paths = []

    def rec(node, acc):
        if node == src:
            paths.append([src] + acc[::-1])  # acc holds reversed tail
            return
        p = preds[node]
        v = 0
        mm = p
        while mm:
            if mm & 1:
                rec(v, acc + [node])
            mm >>= 1
            v += 1

    # acc collects nodes from dst-1 ... we build by recursion; simplest:
    def rec2(node):
        if node == src:
            return [[src]]
        out = []
        p = preds[node]
        v = 0
        mm = p
        while mm:
            if mm & 1:
                for pre in rec2(v):
                    out.append(pre + [node])
            mm >>= 1
            v += 1
        return out

    return rec2(dst)


# ---------------------------------------------------------------------------
# D(C) computation
# ---------------------------------------------------------------------------
def compute_D(n, C_vertices, bad_edges, cut_edges):
    """C_vertices: set of vertices on geodesic. Return D(C) or None if |K|>20."""
    Cset = set(C_vertices)
    K = [v for v in range(n) if v not in Cset]
    if len(K) > 20:
        return None
    # local index for K
    idx = {v: i for i, v in enumerate(K)}
    Mp = [(idx[a], idx[b]) for (a, b) in bad_edges if a in idx and b in idx]
    Be = [(idx[a], idx[b]) for (a, b) in cut_edges if a in idx and b in idx]
    kk = len(K)
    if kk == 0:
        return 0
    best = 0  # max(0, ...)
    # brute over all 2^kk masks (fix nothing: full freedom since this is a separate coloring)
    for mask in range(1 << kk):
        dM = 0
        for (a, b) in Mp:
            if ((mask >> a) ^ (mask >> b)) & 1:
                dM += 1
        dB = 0
        for (a, b) in Be:
            if ((mask >> a) ^ (mask >> b)) & 1:
                dB += 1
        val = dM - dB
        if val > best:
            best = val
    return best


# ---------------------------------------------------------------------------
# Per-config R2 evaluation for a chosen (G, side)
# ---------------------------------------------------------------------------
def gamma_for_cut(n, edges, side, badj):
    """Compute (Gamma, bad_edges, cut_edges, valid) for a given connected-B cut.
       valid=False if some bad edge has no B-path."""
    bad_edges = []
    cut_edges = []
    for (u, w) in edges:
        if side[u] != side[w]:
            cut_edges.append((u, w))
        else:
            bad_edges.append((u, w))
    if not bad_edges:
        return None  # |M|<1 -> skip
    Gamma = 0
    # need distances: do BFS from each distinct bad-edge endpoint
    dist_cache = {}
    for (u, w) in bad_edges:
        if u not in dist_cache:
            dist_cache[u] = bfs_dist_and_preds(n, badj, u)
        d = dist_cache[u][0][w]
        if d == -1:
            return ("invalid", bad_edges, cut_edges)
        ell = d + 1
        Gamma += ell * ell
    return (Gamma, bad_edges, cut_edges)


def evaluate_G(n, adj, edges):
    """Return dict with master/local results, or None if G skipped.
       Selection: among valid connected-B max cuts pick min Gamma."""
    best_cut_size, cuts = all_max_cuts(n, edges)
    # gather valid connected-B cuts with their Gamma
    candidates = []  # (Gamma, side, badj, bad_edges, cut_edges)
    for side in cuts:
        badj = build_B_adj(n, edges, side)
        if not B_connected(n, badj):
            continue
        res = gamma_for_cut(n, edges, side, badj)
        if res is None:
            # |M|<1 for this cut -> this cut contributes no config; skip cut
            continue
        if res[0] == "invalid":
            continue
        Gamma, bad_edges, cut_edges = res
        candidates.append((Gamma, side, badj, bad_edges, cut_edges))
    if not candidates:
        return None  # no valid connected-B max cut with >=1 bad edge -> SKIP G
    # min Gamma selection
    candidates.sort(key=lambda x: x[0])
    Gamma, side, badj, bad_edges, cut_edges = candidates[0]

    # Enumerate all shortest bad geodesics (all bad edges, all shortest u-v B-paths)
    n2 = n * n
    min_DC = None
    local_min_slack = None  # min over C of (n^2 - Gamma - D(C)); local viol if <0
    any_local_viol = False
    dstar_undefined_all = True

    dist_cache = {}
    for (u, w) in bad_edges:
        if u not in dist_cache:
            dist_cache[u] = bfs_dist_and_preds(n, badj, u)
        dist, preds = dist_cache[u]
        # geodesics from u to w
        geos = enumerate_geodesics(u, w, preds)
        for path in geos:
            DC = compute_D(n, path, bad_edges, cut_edges)
            if DC is None:
                continue  # |K|>20: C undefined, skip
            dstar_undefined_all = False
            if min_DC is None or DC < min_DC:
                min_DC = DC
            slack_local = n2 - Gamma - DC
            if local_min_slack is None or slack_local < local_min_slack:
                local_min_slack = slack_local
            if slack_local < 0:
                any_local_viol = True

    if min_DC is None:
        # All geodesics had |K|>20 -> D* undefined; cannot evaluate master via D*.
        # Treat as skipped for master (D* undefined). Report undefined.
        return {
            "Gamma": Gamma,
            "Dstar": None,
            "master_slack": None,
            "master_viol": False,
            "local_viol": False,
            "local_min_slack": None,
            "skipped_dstar_undef": True,
            "side": side,
        }

    Dstar = min_DC
    master_slack = n2 - Gamma - Dstar
    master_viol = master_slack < 0
    return {
        "Gamma": Gamma,
        "Dstar": Dstar,
        "master_slack": master_slack,
        "master_viol": master_viol,
        "local_viol": any_local_viol,
        "local_min_slack": local_min_slack,
        "skipped_dstar_undef": False,
        "side": side,
    }


# ---------------------------------------------------------------------------
# Tight-case builders
# ---------------------------------------------------------------------------
def cycle_graph(k):
    adj = [0] * k
    for i in range(k):
        j = (i + 1) % k
        adj[i] |= (1 << j)
        adj[j] |= (1 << i)
    return k, adj


def c5_blowup_x2():
    """Balanced C5 blow-up x2: 5 parts of size 2 (n=10). Edge between u,v iff their
       parts are adjacent on C5. No edges within a part (independent set)."""
    n = 10
    # part of vertex v = v // 2 ; part order 0..4 in a 5-cycle
    adj = [0] * n
    for a in range(n):
        for b in range(a + 1, n):
            pa, pb = a // 2, b // 2
            if pa == pb:
                continue
            if (pa - pb) % 5 == 1 or (pb - pa) % 5 == 1:
                adj[a] |= (1 << b)
                adj[b] |= (1 << a)
    return n, adj


def eval_named(n, adj, label):
    edges = edges_from_adj(n, adj)
    r = evaluate_G(n, adj, edges)
    return label, r


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def run_range(nmin, nmax):
    per_n = []
    first_viol = None
    for n in range(nmin, nmax + 1):
        proc = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True)
        configs = 0
        master_viol = 0
        local_viol = 0
        min_master_slack = None
        for line in proc.stdout.splitlines():
            dec = decode_graph6(line)
            if dec is None:
                continue
            nn, adj = dec
            # geng -tc already gives connected triangle-free; sanity not re-checked for speed,
            # but evaluate_G handles connected-B filtering.
            edges = edges_from_adj(nn, adj)
            r = evaluate_G(nn, adj, edges)
            if r is None:
                continue
            if r.get("skipped_dstar_undef"):
                continue
            configs += 1
            if r["master_slack"] is not None:
                if min_master_slack is None or r["master_slack"] < min_master_slack:
                    min_master_slack = r["master_slack"]
            if r["master_viol"]:
                master_viol += 1
                if first_viol is None:
                    first_viol = (line.strip(), r["Gamma"], r["Dstar"], nn)
            if r["local_viol"]:
                local_viol += 1
                if first_viol is None:
                    first_viol = (line.strip(), r["Gamma"], r["Dstar"], nn)
        per_n.append({
            "n": n,
            "configs": configs,
            "master_viol": master_viol,
            "local_viol": local_viol,
            "min_master_slack": (min_master_slack if min_master_slack is not None else -999),
        })
        print(f"n={n}: configs={configs} master_viol={master_viol} "
              f"local_viol={local_viol} min_master_slack={min_master_slack}",
              flush=True)
    return per_n, first_viol


if __name__ == "__main__":
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 11

    # Tight cases
    print("=== TIGHT CASES ===", flush=True)
    tight = []
    for label, (n, adj) in [
        ("C5", cycle_graph(5)),
        ("C7", cycle_graph(7)),
        ("C9", cycle_graph(9)),
        ("C5[2]", c5_blowup_x2()),
        ("C11", cycle_graph(11)),
    ]:
        edges = edges_from_adj(n, adj)
        r = evaluate_G(n, adj, edges)
        tight.append((label, r))
        if r is None:
            print(f"{label}: SKIPPED (no valid connected-B max cut w/ bad edge)", flush=True)
        else:
            print(f"{label}: n={n} Gamma={r['Gamma']} D*={r['Dstar']} "
                  f"master_slack={r['master_slack']} master_viol={r['master_viol']} "
                  f"local_viol={r['local_viol']}", flush=True)
    tight_all_zero = all(
        (r is not None and r["master_slack"] == 0) for _, r in tight
    )
    print(f"TIGHT all slack0: {tight_all_zero}", flush=True)

    print("=== RANGE ===", flush=True)
    per_n, first_viol = run_range(nmin, nmax)
    print("FIRST VIOLATION:", first_viol, flush=True)
