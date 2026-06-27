#!/usr/bin/env python3
"""
Adversarial finder #4 for Erdos #23 Step-2 R2 MASTER INEQUALITY.

FAMILY: named triangle-free graphs + triangle-free circulants.
  - Petersen (n=10)
  - Grotzsch (n=11)
  - Clebsch (n=16)
  - Wagner / Mobius-Kantor M8 (n=8)
  - triangle-free circulant graphs C_n(1,k) for n<=16

We reuse the cross-validated clean-room checker r2_check_ref.master_check(n, edges).
No import of bridge/flagsdp/*.

A single master violation (gamma + D* > n^2) on a connected-B config REFUTES R2.
"""

import sys
import os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from r2_check_ref import master_check  # noqa: E402


def is_triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if adj[u] & adj[v]:
                return False
    return True


def norm_edges(edges):
    """Normalize to sorted tuples, dedup, no self loops."""
    s = set()
    for a, b in edges:
        if a == b:
            continue
        s.add((min(a, b), max(a, b)))
    return sorted(s)


# ----------------------------------------------------------------------
# Named graphs
# ----------------------------------------------------------------------

def petersen():
    """Petersen graph, n=10. Outer 5-cycle 0..4, inner pentagram 5..9
    (5-i-6-i ... ), spokes i--i+5. Standard Kneser(5,2) construction."""
    edges = []
    # outer cycle
    for i in range(5):
        edges.append((i, (i + 1) % 5))
    # spokes
    for i in range(5):
        edges.append((i, i + 5))
    # inner pentagram: inner vertex 5+i connects to 5+(i+2)%5
    for i in range(5):
        edges.append((5 + i, 5 + (i + 2) % 5))
    return 10, norm_edges(edges)


def grotzsch():
    """Grotzsch graph (Mycielskian of C5), n=11, triangle-free, chromatic 4.
    Vertices: 0 apex; 1..5 outer C5; 6..10 mirror.
    Construction (Mycielski of C5 with base verts u_0..u_4):
      - base C5 on u_0..u_4
      - copies v_0..v_4: v_i adjacent to neighbors of u_i in base
      - apex w adjacent to all v_i.
    Map: u_i = i (0..4 as 1..5?), use indices:
      base = 0..4, copies = 5..9, apex = 10.
    """
    base = list(range(5))      # 0..4
    copy = list(range(5, 10))  # 5..9
    apex = 10
    edges = []
    # base C5
    for i in range(5):
        edges.append((base[i], base[(i + 1) % 5]))
    # v_i adjacent to neighbors of u_i in base: u_i ~ u_{i-1}, u_{i+1}
    for i in range(5):
        for j in ((i - 1) % 5, (i + 1) % 5):
            edges.append((copy[i], base[j]))
    # apex to all copies
    for i in range(5):
        edges.append((apex, copy[i]))
    return 11, norm_edges(edges)


def clebsch():
    """Clebsch graph (folded 5-cube), n=16, triangle-free, 5-regular.
    Vertices = GF(2)^4 = 0..15. Folded 5-cube: connect x,y if they differ
    in exactly one of the 4 coordinates, OR x XOR y == 0b1111 (the "fold").
    This is the standard triangle-free Clebsch (16 vertices, degree 5)."""
    edges = []
    for x in range(16):
        for k in range(4):
            y = x ^ (1 << k)
            if x < y:
                edges.append((x, y))
        # fold: complement
        y = x ^ 0b1111
        if x < y:
            edges.append((x, y))
    return 16, norm_edges(edges)


def wagner():
    """Wagner graph V8 = Mobius-Kantor M(8,3)? No: Wagner graph = Mobius
    ladder M8 on 8 vertices: cycle 0-1-...-7-0 plus diameters i--i+4.
    Wagner graph IS triangle-free."""
    edges = []
    for i in range(8):
        edges.append((i, (i + 1) % 8))
    for i in range(4):
        edges.append((i, i + 4))
    return 8, norm_edges(edges)


# ----------------------------------------------------------------------
# Triangle-free circulants C_n(1,k)
# ----------------------------------------------------------------------

def circulant(n, conns):
    """Circulant graph C_n(conns): vertex i ~ i+/-c for each c in conns."""
    edges = []
    for i in range(n):
        for c in conns:
            j = (i + c) % n
            edges.append((i, j))
    return n, norm_edges(edges)


def gen_circulants(nmax=16):
    """All connected triangle-free circulants C_n(1,k), 5<=n<=nmax, 2<=k<=n//2.
    Returns list of (name, n, edges)."""
    out = []
    for n in range(5, nmax + 1):
        for k in range(2, n // 2 + 1):
            nn, edges = circulant(n, [1, k])
            if not is_triangle_free(nn, edges):
                continue
            out.append((f"C{n}(1,{k})", nn, edges))
    return out


def main():
    cap = 16
    fams = []
    fams.append(("Wagner", *wagner()))
    fams.append(("Petersen", *petersen()))
    fams.append(("Grotzsch", *grotzsch()))
    fams.append(("Clebsch", *clebsch()))
    fams.extend(gen_circulants(cap))

    print("Adversarial #4: named triangle-free + circulants C_n(1,k) n<=16")
    print("=" * 78)

    n_values = set()
    graphs_tested = 0
    violations = []
    min_master_slack = None
    tight = []
    skipped_tf = []
    skipped_cfg = []

    for name, n, edges in fams:
        if n > cap:
            continue
        if not is_triangle_free(n, edges):
            skipped_tf.append(name)
            print(f"  {name:14s} n={n:2d}: NOT triangle-free -> SKIP")
            continue
        res = master_check(n, edges)
        n_values.add(n)
        if res is None:
            skipped_cfg.append(name)
            print(f"  {name:14s} n={n:2d}: no connected-B config (SKIP)")
            continue
        graphs_tested += 1
        ms = res["master_slack"]
        wls = res["worst_local_slack"]
        if min_master_slack is None or ms < min_master_slack:
            min_master_slack = ms
        if ms == 0:
            tight.append(name)
        viol = ms < 0 or wls < 0
        flag = "  *** VIOLATION ***" if viol else ""
        print(f"  {name:14s} n={n:2d}: gamma={res['gamma']:4d} D*={res['dstar']:3d} "
              f"master_slack={ms:5d} worst_local_slack={wls:5d}{flag}")
        if viol:
            violations.append((name, n, edges, res))

    print("=" * 78)
    print(f"graphs_tested={graphs_tested}  n_values={sorted(n_values)}")
    print(f"min_master_slack={min_master_slack}")
    print(f"tight (master_slack==0): {tight}")
    print(f"skipped (not tri-free): {skipped_tf}")
    print(f"skipped (no connected-B config): {skipped_cfg}")
    if violations:
        print("VIOLATIONS FOUND:")
        for name, n, edges, res in violations:
            print(f"  {name} n={n} edges={edges} res={res}")
    else:
        print("NO MASTER OR LOCAL VIOLATIONS.")


if __name__ == "__main__":
    main()
