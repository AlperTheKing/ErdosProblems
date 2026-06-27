#!/usr/bin/env python3
"""
Independent re-implementation #2 of Erdos #23 Step-2 R2 MASTER INEQUALITY checker.

CLEAN-ROOM: no import of bridge/flagsdp/*.py or any other agent's checker.
Uses only nauty geng (-tc) for connected triangle-free graph enumeration and own code.

For a triangle-free simple connected graph G on n vertices:
  1. MAX CUT by brute force over 2^(n-1) masks (vertex 0 fixed to side 0).
  2. CONNECTED-B filter: B=(V, cut-edges) must be connected. Skip G if no max cut has connected B.
  3. GAMMA-MIN selection among connected-B max cuts; require all bad edges have a B-path
     (else that cut is invalid -> excluded from selection).
  4. Bad edges M = monochromatic edges. Skip config if |M|<1.
  5. d_B(u,v) shortest path dist in B; ell=d_B+1; Gamma = sum_{(u,v) in M} ell^2.
  6. For each shortest bad geodesic C (shortest u-v B-path for a bad edge), D(C):
       K = V minus vertices(C); Mp = bad edges with both ends in K; Be = cut edges both ends in K.
       D(C) = max(0, max over 2-colorings 'mask' of K of (dM - dB)).  |K|>20 -> undefined, skip C.
  7. D*(G) = min over all shortest bad geodesics C of D(C).
  8. MASTER:  Gamma + D* <= n^2.   LOCAL: Gamma + D(C) <= n^2 for every shortest C.

Reports per-n counts of master/local violations, min master slack, and confirms tight cases.
"""

import sys
import subprocess
from collections import deque
from itertools import combinations, product

GENG = r"E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"


# ---------------------------------------------------------------------------
# graph6 decode (own implementation; column-major upper triangle)
# ---------------------------------------------------------------------------
def decode_graph6(line):
    """Decode a single graph6 line to (n, adj) where adj is list of sets."""
    s = line.strip()
    if not s:
        return None
    data = [ord(c) - 63 for c in s]
    n = data[0]
    # bit stream from remaining bytes, 6 bits each, MSB first
    bits = []
    for byte in data[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    adj = [set() for _ in range(n)]
    idx = 0
    # column-major: for j in 1..n-1, for i in 0..j-1
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, adj


def edges_of(adj):
    n = len(adj)
    es = []
    for i in range(n):
        for j in adj[i]:
            if i < j:
                es.append((i, j))
    return es


# ---------------------------------------------------------------------------
# max cut by brute force, fix vertex 0 to side 0
# ---------------------------------------------------------------------------
def all_max_cuts(n, edge_list):
    """Return (maxval, list_of_side_arrays) over all 2^(n-1) colorings, v0 fixed."""
    best = -1
    cuts = []
    for code in range(1 << (n - 1)):
        side = [0] * n
        for v in range(1, n):
            side[v] = (code >> (v - 1)) & 1
        cv = 0
        for (u, w) in edge_list:
            if side[u] != side[w]:
                cv += 1
        if cv > best:
            best = cv
            cuts = [side[:]]
        elif cv == best:
            cuts.append(side[:])
    return best, cuts


def b_connected(n, side, edge_list):
    """B = cut edges. Return True if B spans all n vertices connectedly from vertex 0."""
    badj = [[] for _ in range(n)]
    for (u, w) in edge_list:
        if side[u] != side[w]:
            badj[u].append(w)
            badj[w].append(u)
    seen = [False] * n
    dq = deque([0])
    seen[0] = True
    cnt = 1
    while dq:
        x = dq.popleft()
        for y in badj[x]:
            if not seen[y]:
                seen[y] = True
                cnt += 1
                dq.append(y)
    return cnt == n


def b_adj(n, side, edge_list):
    badj = [[] for _ in range(n)]
    for (u, w) in edge_list:
        if side[u] != side[w]:
            badj[u].append(w)
            badj[w].append(u)
    return badj


def bfs_dist_and_parents(n, badj, src):
    """BFS distances from src in B; parents = list of predecessor-sets for path recovery."""
    dist = [-1] * n
    parents = [[] for _ in range(n)]
    dist[src] = 0
    dq = deque([src])
    while dq:
        x = dq.popleft()
        for y in badj[x]:
            if dist[y] == -1:
                dist[y] = dist[x] + 1
                parents[y].append(x)
                dq.append(y)
            elif dist[y] == dist[x] + 1:
                parents[y].append(x)
    return dist, parents


def all_shortest_paths(parents, src, dst):
    """Enumerate all shortest src->dst paths as vertex lists (including endpoints)."""
    paths = []
    def rec(node, acc):
        if node == src:
            paths.append([src] + acc[::-1])
            return
        for p in parents[node]:
            rec(p, acc + [node])
    if dst == src:
        return [[src]]
    rec(dst, [])
    return paths


# ---------------------------------------------------------------------------
# Gamma + connected-B max-cut selection
# ---------------------------------------------------------------------------
def gamma_for_cut(n, side, edge_list):
    """
    Compute (gamma, bad_edges, badj) for a given cut.
    Returns gamma=None if some bad edge has no B-path (cut invalid for selection).
    """
    badj = b_adj(n, side, edge_list)
    bad = [(u, w) for (u, w) in edge_list if side[u] == side[w]]
    # distances: cache BFS per source as needed
    distcache = {}
    gamma = 0
    for (u, w) in bad:
        if u not in distcache:
            d, _ = bfs_dist_and_parents(n, badj, u)
            distcache[u] = d
        d = distcache[u][w]
        if d == -1:
            return None, bad, badj  # invalid cut
        ell = d + 1
        gamma += ell * ell
    return gamma, bad, badj


def select_config(n, edge_list):
    """
    Among connected-B max cuts with all-bad-edges-reachable, pick min-Gamma.
    Returns (side, gamma, bad, badj) or None if no valid connected-B max cut, or
    ('NO_BAD',) if min-gamma config has no bad edges (skip config).
    """
    maxval, cuts = all_max_cuts(n, edge_list)
    best = None  # (gamma, side, bad, badj)
    for side in cuts:
        if not b_connected(n, side, edge_list):
            continue
        gamma, bad, badj = gamma_for_cut(n, side, edge_list)
        if gamma is None:
            continue  # invalid: a bad edge with no B-path
        if best is None or gamma < best[0]:
            best = (gamma, side, bad, badj)
    if best is None:
        return None
    gamma, side, bad, badj = best
    return side, gamma, bad, badj


# ---------------------------------------------------------------------------
# D(C)
# ---------------------------------------------------------------------------
def compute_DC(n, Cverts, bad, edge_list, side, max_k=20):
    """D(C) = max(0, max_mask (dM - dB)) over 2-colorings of K = V\\C. None if |K|>max_k."""
    Cset = set(Cverts)
    K = [v for v in range(n) if v not in Cset]
    k = len(K)
    if k > max_k:
        return None
    Kset = set(K)
    # Mp: bad edges with BOTH endpoints in K
    Mp = [(a, b) for (a, b) in bad if a in Kset and b in Kset]
    # Be: cut edges with BOTH endpoints in K
    Be = [(a, b) for (a, b) in edge_list if a in Kset and b in Kset and side[a] != side[b]]
    if k == 0:
        return max(0, 0)
    pos = {v: i for i, v in enumerate(K)}
    best = 0  # max(0, ...) so start at 0
    # iterate over 2^k masks; k<=20 -> up to ~1M, fine
    for code in range(1 << k):
        dM = 0
        for (a, b) in Mp:
            if ((code >> pos[a]) & 1) != ((code >> pos[b]) & 1):
                dM += 1
        dB = 0
        for (a, b) in Be:
            if ((code >> pos[a]) & 1) != ((code >> pos[b]) & 1):
                dB += 1
        val = dM - dB
        if val > best:
            best = val
    return best


def evaluate_graph(n, adj):
    """
    Returns dict with keys: skip (bool), reason, gamma, Dstar, master_slack,
    master_viol(bool), local_viol(bool), undefined_all(bool).
    Or None-config skip.
    """
    edge_list = edges_of(adj)
    sel = select_config(n, edge_list)
    if sel is None:
        return {"skip": True, "reason": "no_connected_B_maxcut"}
    side, gamma, bad, badj = sel
    if len(bad) < 1:
        return {"skip": True, "reason": "no_bad_edges"}

    # Enumerate all shortest bad geodesics C (all bad edges, all shortest u-v B-paths).
    DC_values = []
    distcache = {}
    parcache = {}
    for (u, w) in bad:
        if u not in parcache:
            d, p = bfs_dist_and_parents(n, badj, u)
            distcache[u] = d
            parcache[u] = p
        d = distcache[u]
        p = parcache[u]
        if d[w] == -1:
            # should not happen for selected cut, but be safe
            continue
        sps = all_shortest_paths(p, u, w)
        for C in sps:
            dc = compute_DC(n, C, bad, edge_list, side)
            if dc is None:
                continue  # |K|>20 -> C undefined, skip it
            DC_values.append(dc)

    if not DC_values:
        return {"skip": True, "reason": "all_C_undefined"}

    Dstar = min(DC_values)
    Dmax_local = max(DC_values)  # local worst (largest D(C)) drives local violation
    n2 = n * n
    master_slack = n2 - (gamma + Dstar)
    master_viol = (gamma + Dstar) > n2
    local_viol = (gamma + Dmax_local) > n2
    return {
        "skip": False,
        "gamma": gamma,
        "Dstar": Dstar,
        "Dmax_local": Dmax_local,
        "master_slack": master_slack,
        "master_viol": master_viol,
        "local_viol": local_viol,
        "side": side,
        "n": n,
    }


# ---------------------------------------------------------------------------
# tight-case constructions
# ---------------------------------------------------------------------------
def cycle_adj(verts):
    n = len(verts)
    adj = [set() for _ in range(n)]
    for i in range(n):
        a = verts[i]
        b = verts[(i + 1) % n]
        adj[a].add(b)
        adj[b].add(a)
    return adj


def C5_blowup2_adj():
    """Balanced C5 blow-up x2: 5 parts of size 2, n=10. Part i ~ part i+1 (mod 5), complete bipartite."""
    parts = [[2 * i, 2 * i + 1] for i in range(5)]
    adj = [set() for _ in range(10)]
    for i in range(5):
        for a in parts[i]:
            for b in parts[(i + 1) % 5]:
                adj[a].add(b)
                adj[b].add(a)
    return adj


def graph6_encode(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    # pad to multiple of 6
    while len(bits) % 6 != 0:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        val = 0
        for b in range(6):
            val = (val << 1) | bits[k + b]
        out += chr(val + 63)
    return out


# ---------------------------------------------------------------------------
# main sweep
# ---------------------------------------------------------------------------
def run_sweep(nlo, nhi):
    per_n = []
    first_master_viol = None
    first_local_viol = None
    for n in range(nlo, nhi + 1):
        proc = subprocess.Popen([GENG, "-tc", str(n)], stdout=subprocess.PIPE, text=True)
        configs = 0
        master_v = 0
        local_v = 0
        min_slack = None
        for line in proc.stdout:
            dec = decode_graph6(line)
            if dec is None:
                continue
            gn, adj = dec
            res = evaluate_graph(gn, adj)
            if res.get("skip"):
                continue
            configs += 1
            if min_slack is None or res["master_slack"] < min_slack:
                min_slack = res["master_slack"]
            if res["master_viol"]:
                master_v += 1
                if first_master_viol is None:
                    g6 = graph6_encode(gn, adj)
                    first_master_viol = f"{g6} (Gamma={res['gamma']},D*={res['Dstar']},n^2={gn*gn})"
            if res["local_viol"]:
                local_v += 1
                if first_local_viol is None:
                    g6 = graph6_encode(gn, adj)
                    first_local_viol = f"{g6} (Gamma={res['gamma']},Dmax={res['Dmax_local']},n^2={gn*gn})"
        proc.wait()
        per_n.append({
            "n": n,
            "configs": configs,
            "master_viol": master_v,
            "local_viol": local_v,
            "min_master_slack": (min_slack if min_slack is not None else 0),
        })
        print(f"n={n}: configs={configs} master_viol={master_v} local_viol={local_v} min_slack={min_slack}", flush=True)
    return per_n, first_master_viol, first_local_viol


def check_tight_cases():
    cases = {}
    # C5, C7, C9, C11
    for name, m in [("C5", 5), ("C7", 7), ("C9", 9), ("C11", 11)]:
        adj = cycle_adj(list(range(m)))
        res = evaluate_graph(m, adj)
        cases[name] = res
    # C5[2]
    adj = C5_blowup2_adj()
    res = evaluate_graph(10, adj)
    cases["C5[2]"] = res
    return cases


if __name__ == "__main__":
    nlo = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    nhi = int(sys.argv[2]) if len(sys.argv) > 2 else 11

    print("=== TIGHT CASES ===", flush=True)
    tc = check_tight_cases()
    all_zero = True
    for name in ["C5", "C7", "C9", "C5[2]", "C11"]:
        r = tc[name]
        slack = r.get("master_slack")
        print(f"{name}: gamma={r.get('gamma')} D*={r.get('Dstar')} master_slack={slack} "
              f"master_viol={r.get('master_viol')} local_viol={r.get('local_viol')}", flush=True)
        if slack != 0:
            all_zero = False
    print(f"tight_cases_slack0 = {all_zero}", flush=True)

    print("=== SWEEP ===", flush=True)
    per_n, fmv, flv = run_sweep(nlo, nhi)
    print("per_n:", per_n, flush=True)
    print("first_master_viol:", fmv, flush=True)
    print("first_local_viol:", flv, flush=True)
