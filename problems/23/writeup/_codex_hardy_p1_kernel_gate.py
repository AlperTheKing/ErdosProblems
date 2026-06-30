"""Gate the structural kernel condition for the Hardy Schur P1 lemma.

For O={v:T(v)>N}, U=V\\O, the Hardy matrix is

    H = diag(N-T) + Lstar,

where Lstar is a positive weighted sum of shortest odd-cycle Laplacians.

The principal block H_UU is positive definite if every connected component
of the Lstar support induced on U either:

  * has a cycle-conductance edge to O (Dirichlet boundary), or
  * contains a strict deficit vertex u with T[u] < N.

This script gates that component criterion on the same small battery used by
the Hardy/Schur probes.  It is a structural proxy for the P1 proof, not a
replacement for the proof.
"""

import random
import subprocess

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def cycle_edges(path):
    q = list(path)
    for i, u in enumerate(q):
        v = q[(i + 1) % len(q)]
        yield (u, v) if u < v else (v, u)


def support_kernel_ok(n, M, T, cyc):
    O = {v for v in range(n) if T[v] > n}
    if not O:
        return True, []
    U = [v for v in range(n) if v not in O]
    Uset = set(U)
    u_adj = {v: set() for v in U}
    boundary = {v: False for v in U}

    for f in M:
        for q in cyc[f]:
            for a, b in cycle_edges(q):
                au = a in Uset
                bu = b in Uset
                if au and bu:
                    u_adj[a].add(b)
                    u_adj[b].add(a)
                elif au and b in O:
                    boundary[a] = True
                elif bu and a in O:
                    boundary[b] = True

    seen = set()
    bad = []
    for root in U:
        if root in seen:
            continue
        comp = []
        stack = [root]
        seen.add(root)
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in u_adj[v]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        has_boundary = any(boundary[v] for v in comp)
        has_deficit = any(T[v] < n for v in comp)
        if not has_boundary and not has_deficit:
            bad.append(tuple(sorted(comp)))
    return not bad, bad


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, T, _mu, cyc = st
    if not M:
        return
    if not any(T[v] > n for v in range(n)):
        acc["noO"] += 1
        return
    acc["cuts"] += 1
    ok, bad = support_kernel_ok(n, M, T, cyc)
    if not ok:
        acc["fail"] += 1
        if acc["first"] is None:
            acc["first"] = (name, n, "".join(map(str, side)), bad, [str(x) for x in T])


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        scan_cut(name, n, adj, side, acc)


def main():
    acc = {"cuts": 0, "noO": 0, "fail": 0, "first": None}

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(f"census N={nn}: O-cuts={acc['cuts']} fail={acc['fail']}", flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)

    n, edges = mycielski(grN, grE)
    adj = adj_from_edges(n, edges)
    scan_cut("MycGrotzsch_N23", n, adj, maxcut_ls(n, adj), acc)

    for q in range(2, 16):
        n, edges, side = glued_c5_chain(q)
        scan_cut(f"chain{q}", n, adj_from_edges(n, edges), side, acc)

    for sizes in [
        (2, 1, 2, 1, 2),
        (2, 1, 2, 1, 3),
        (3, 2, 3, 2, 3),
        (4, 3, 4, 3, 4),
        (5, 4, 5, 4, 5),
        (2, 2, 2, 2, 2),
        (3, 3, 3, 3, 3),
    ]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 27:
            gfam(f"blow{sizes}", n, edges, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(island, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    gfam("island", n, edges, acc)

    rng = random.Random(37)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        edges = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, acc)

    print("=" * 70)
    print("O-cuts:", acc["cuts"], "noO:", acc["noO"], "random graphs:", made)
    print("kernel criterion failures:", acc["fail"], acc["first"] or "")


if __name__ == "__main__":
    main()
