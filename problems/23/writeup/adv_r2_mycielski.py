#!/usr/bin/env python3
"""
Adversarial finder #3 for Erdos #23 Step-2 R2 MASTER INEQUALITY.

FAMILY: MYCIELSKIANS.  Mycielski's construction M(G) takes a graph G on vertices
v_0..v_{n-1} and produces a triangle-free graph (when G is triangle-free) with
chromatic number chi(M(G)) = chi(G)+1.  These are the canonical "high chromatic
number, no triangle" graphs (Grotzsch = M(C5)) and are prime suspects for a
master-inequality violation.

  Vertices of M(G):  v_0..v_{n-1}  (original copy)
                     u_0..u_{n-1}  (shadow copy, independent set)
                     w             (apex, joined to all shadows)
  Edges:  every original edge (v_i,v_j);
          for each original edge (v_i,v_j): add (u_i,v_j) and (u_j,v_i);
          w joined to every u_i.
  |V(M(G))| = 2n+1.  Triangle-free preserved.

We test:
  - M(C5)  = Grotzsch graph, n=11
  - M(C7)  , n=15
  - M(P_k) for paths P_k (k=2..7), n=2k+1
  - M(C5[2]) (balanced 2-blow-up of C5, base n=10) -> 21 vertices (> 16 cap;
    only built/checked if cap allows; we ALSO test the smaller M(C3-free)
    bases that fit under the n<=16 cap).
  - bonus: iterated M(M(C5)) is far too big; skipped.

This is a CLEAN-ROOM family generator.  It imports ONLY the cross-validated
reference checker problems/23/writeup/r2_check_ref.py (which itself imports
nothing from bridge/flagsdp/*).  We do NOT touch Step-2's flag_engine/master_ineq.

A SINGLE master violation (Gamma + D* > n^2) on a connected-B config REFUTES R2.
"""

import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from r2_check_ref import master_check  # cross-validated clean-room checker


# ----------------------------------------------------------------------------
# base-graph constructors (return (n, edges) with vertices 0..n-1)
# ----------------------------------------------------------------------------

def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)]


def path(k):
    """Path P_k on k vertices (k-1 edges)."""
    return k, [(i, i + 1) for i in range(k - 1)]


def c5_blowup2():
    """Balanced 2-blow-up of C5: 10 vertices, K_{2,2} between adjacent classes."""
    e = []
    for i in range(5):
        j = (i + 1) % 5
        ci = [2 * i, 2 * i + 1]
        cj = [2 * j, 2 * j + 1]
        for a in ci:
            for b in cj:
                e.append((a, b))
    return 10, e


# ----------------------------------------------------------------------------
# Mycielskian
# ----------------------------------------------------------------------------

def mycielskian(n, edges):
    """Return (N, E) of the Mycielskian M(G), G = (n, edges).
    Vertex layout: original i -> i ; shadow i -> n+i ; apex -> 2n.
    """
    N = 2 * n + 1
    apex = 2 * n
    E = []
    # original edges
    for (a, b) in edges:
        E.append((a, b))
    # cross edges: for each (a,b) in G add (shadow a, b) and (shadow b, a)
    for (a, b) in edges:
        E.append((n + a, b))
        E.append((n + b, a))
    # apex joined to every shadow
    for i in range(n):
        E.append((apex, n + i))
    return N, E


def is_triangle_free(N, E):
    adj = [set() for _ in range(N)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    for u in range(N):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


# ----------------------------------------------------------------------------
# edge list -> graph6 (column-major upper triangle, matching the ref decoder)
# ----------------------------------------------------------------------------

def to_graph6(N, E):
    eset = set()
    for a, b in E:
        if a > b:
            a, b = b, a
        eset.add((a, b))
    bits = []
    for j in range(1, N):
        for i in range(j):
            bits.append(1 if (i, j) in eset else 0)
    # pad to multiple of 6
    while len(bits) % 6:
        bits.append(0)
    out = [chr(N + 63)]
    for k in range(0, len(bits), 6):
        val = 0
        for t in range(6):
            val = (val << 1) | bits[k + t]
        out.append(chr(val + 63))
    return "".join(out)


# ----------------------------------------------------------------------------
# run the family
# ----------------------------------------------------------------------------

def build_family(cap=16):
    """Yield (name, N, E) for every Mycielskian we will test, respecting cap."""
    fam = []

    bn, be = cycle(5)
    fam.append(("M(C5)=Grotzsch", *mycielskian(bn, be)))

    bn, be = cycle(7)
    fam.append(("M(C7)", *mycielskian(bn, be)))

    for k in range(2, 8):
        bn, be = path(k)
        fam.append((f"M(P{k})", *mycielskian(bn, be)))

    # M(C5[2]): base n=10 -> 21 vertices.
    bn, be = c5_blowup2()
    fam.append(("M(C5[2])", *mycielskian(bn, be)))

    # also test a few more odd-cycle Mycielskians (all triangle-free, rising chi)
    bn, be = cycle(9)
    fam.append(("M(C9)", *mycielskian(bn, be)))

    out = []
    for name, N, E in fam:
        if N > cap:
            out.append((name, N, E, "OVER_CAP"))
        else:
            out.append((name, N, E, "OK"))
    return out


def main():
    cap = 16
    print("Adversarial #3 -- MYCIELSKIANS vs R2 master inequality")
    print("=" * 70)
    family = build_family(cap=cap)

    n_values = set()
    graphs_tested = 0
    violation = None
    min_master_slack = None
    tight = []
    skipped = []
    examined = []

    for name, N, E, status in family:
        if not is_triangle_free(N, E):
            print(f"  {name:18s} N={N:3d}  *** NOT TRIANGLE-FREE -- skip ***")
            continue
        if status == "OVER_CAP":
            g6 = to_graph6(N, E)
            print(f"  {name:18s} N={N:3d}  OVER CAP ({cap}) -- not brute-forced; graph6={g6}")
            skipped.append((name, N))
            continue

        res = master_check(N, E)
        n_values.add(N)
        graphs_tested += 1
        g6 = to_graph6(N, E)
        if res is None:
            print(f"  {name:18s} N={N:3d}  no connected-B config (SKIP by spec)  graph6={g6}")
            examined.append((name, N, None))
            continue
        ms = res["master_slack"]
        ls = res["worst_local_slack"]
        if min_master_slack is None or ms < min_master_slack:
            min_master_slack = ms
        if ms == 0:
            tight.append(name)
        print(f"  {name:18s} N={N:3d}  gamma={res['gamma']:4d}  D*={res['dstar']:3d}  "
              f"master_slack={ms:5d}  worst_local_slack={ls:5d}  N^2={N*N}")
        examined.append((name, N, res))
        if ms < 0 and violation is None:
            violation = (name, N, g6, E, res)
        if ls < 0 and violation is None:
            violation = (name, N, g6, E, res, "LOCAL")

    print("-" * 70)
    if violation:
        print("!!! VIOLATION FOUND !!!")
        print(violation)
    else:
        print("No master/local violation across the Mycielskian family.")
    print(f"n_values tested: {sorted(n_values)}")
    print(f"graphs tested:   {graphs_tested}")
    print(f"min master slack: {min_master_slack}")
    print(f"tight (slack 0): {tight}")
    print(f"over-cap skipped: {skipped}")
    return {
        "n_values": sorted(n_values),
        "graphs_tested": graphs_tested,
        "violation": violation,
        "min_master_slack": min_master_slack,
        "tight": tight,
        "skipped": skipped,
        "examined": examined,
    }


if __name__ == "__main__":
    main()
