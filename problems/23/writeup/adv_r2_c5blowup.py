#!/usr/bin/env python3
"""
Adversarial finder #1 for Erdos #23 Step-2 R2 MASTER INEQUALITY.

FAMILY: weighted C5 blow-ups.  Replace each of the 5 vertices of C5 by an
independent set ("class") of size a_i (i=0..4), and join classes of cyclically
adjacent C5 vertices by a complete bipartite graph (K_{a_i,a_j}).  No edges
inside a class.  The result is always triangle-free (C5 has no triangle, and a
blow-up of a triangle-free graph is triangle-free).

We enumerate class-size vectors (a,b,c,d,e) of positive integers summing to
n, for n in {10,...,16}, up to cyclic rotation + reflection (dihedral group D5)
to avoid isomorphic duplicates.  We ALSO include the balanced blow-ups
C5[2] (n=10) and C5[3] (n=15), plus a spread of unbalanced ones.

For each blow-up graph we call the cross-validated reference checker
master_check(n, edges) from r2_check_ref.py and test:
    MASTER:  Gamma(G) + D*(G) <= n^2   (master_slack >= 0)
    LOCAL :  Gamma(G) + D(C)  <= n^2 for every shortest C (worst_local_slack >= 0)

A single master violation (slack < 0) on a connected-B config refutes R2.

NOTE: master_check brute-forces max cut over 2^(n-1) masks AND enumerates all
max cuts the same way, so n is capped at 16 (2^15 = 32768 masks; the all-cut
enumeration loop is the cost, fine up to ~16-17).
"""

import sys
import os
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_check_ref import master_check  # cross-validated clean-room checker


def c5_blowup_edges(sizes):
    """Edge list for the C5 blow-up with class sizes `sizes` = (a0..a4).
    Vertices are numbered 0..n-1 by concatenating the 5 classes in order.
    Edges: complete bipartite between classes i and (i+1) mod 5."""
    assert len(sizes) == 5
    # vertex index ranges per class
    starts = []
    s = 0
    for sz in sizes:
        starts.append(s)
        s += sz
    n = s
    classes = [list(range(starts[i], starts[i] + sizes[i])) for i in range(5)]
    edges = []
    for i in range(5):
        j = (i + 1) % 5
        for u in classes[i]:
            for v in classes[j]:
                edges.append((u, v) if u < v else (v, u))
    return n, edges


def canonical_d5(vec):
    """Canonical representative of a 5-vector under the dihedral group D5
    (5 rotations x 2 reflections = 10 symmetries).  Returns the lexicographically
    smallest tuple among all images."""
    v = list(vec)
    cands = []
    for r in range(5):
        rot = v[r:] + v[:r]
        cands.append(tuple(rot))
        cands.append(tuple(rot[::-1]))
    return min(cands)


def compositions_5(n, max_part=None):
    """All ordered 5-tuples of positive ints summing to n (compositions of n
    into exactly 5 positive parts).  Optionally cap each part at max_part."""
    if max_part is None:
        max_part = n
    out = []
    for a in range(1, max_part + 1):
        for b in range(1, max_part + 1):
            for c in range(1, max_part + 1):
                for d in range(1, max_part + 1):
                    e = n - (a + b + c + d)
                    if 1 <= e <= max_part:
                        out.append((a, b, c, d, e))
    return out


def distinct_blowups(n):
    """All distinct (up to D5) C5 blow-up class-size vectors summing to n."""
    seen = set()
    reps = []
    for vec in compositions_5(n):
        can = canonical_d5(vec)
        if can not in seen:
            seen.add(can)
            reps.append(can)
    reps.sort()
    return reps


def main():
    ns = [10, 11, 12, 13, 14, 15, 16]
    print("Adversarial finder #1: weighted C5 blow-ups vs R2 MASTER inequality")
    print("=" * 74)

    total_graphs = 0
    total_configs = 0       # connected-B configs that master_check actually evaluated
    master_violations = []  # (n, sizes, edges, res)
    local_violations = []   # (n, sizes, edges, res)
    tight_master = []       # (n, sizes) with master_slack == 0
    tight_local = []        # (n, sizes) with worst_local_slack == 0
    global_min_master_slack = None
    n_values_done = []

    for n in ns:
        reps = distinct_blowups(n)
        n_master_viol = 0
        n_local_viol = 0
        n_configs = 0
        n_min_slack = None
        for sizes in reps:
            total_graphs += 1
            gn, edges = c5_blowup_edges(sizes)
            assert gn == n
            res = master_check(n, edges)
            if res is None:
                # not a connected-B config with a bad edge: skip (e.g. blow-ups
                # whose max cut is bipartite-clean, or B disconnected).
                continue
            n_configs += 1
            total_configs += 1
            ms = res["master_slack"]
            ls = res["worst_local_slack"]
            if n_min_slack is None or ms < n_min_slack:
                n_min_slack = ms
            if global_min_master_slack is None or ms < global_min_master_slack:
                global_min_master_slack = ms
            if ms < 0:
                n_master_viol += 1
                master_violations.append((n, sizes, edges, res))
            if ls < 0:
                n_local_viol += 1
                local_violations.append((n, sizes, edges, res))
            if ms == 0:
                tight_master.append((n, sizes, res))
            if ls == 0:
                tight_local.append((n, sizes, res))
        n_values_done.append(n)
        print(f"n={n:2d}: blowup_classes(distinct)={len(reps):4d}  "
              f"connectedB_configs={n_configs:4d}  "
              f"master_viol={n_master_viol}  local_viol={n_local_viol}  "
              f"min_master_slack={n_min_slack}")
        sys.stdout.flush()

    print("-" * 74)
    print(f"TOTAL blow-up graphs tested : {total_graphs}")
    print(f"TOTAL connected-B configs   : {total_configs}")
    print(f"MASTER violations (slack<0) : {len(master_violations)}")
    print(f"LOCAL  violations (slack<0) : {len(local_violations)}")
    print(f"GLOBAL min master slack     : {global_min_master_slack}")
    print()

    # report tight (slack 0) master examples, dedup by (n)
    print("TIGHT master-slack==0 blow-ups (first few per n):")
    by_n = {}
    for (n, sizes, res) in tight_master:
        by_n.setdefault(n, []).append((sizes, res))
    for n in sorted(by_n):
        items = by_n[n]
        sample = items[:6]
        print(f"  n={n}: count={len(items)}  e.g. "
              + ", ".join(f"{s}->slack0(gamma={r['gamma']})" for s, r in sample))

    if master_violations:
        print()
        print("!!! MASTER VIOLATIONS FOUND !!!")
        for (n, sizes, edges, res) in master_violations[:20]:
            print(f"  n={n} sizes={sizes} res={res}")
            print(f"    edges={edges}")
    else:
        print()
        print("No MASTER violations among C5 blow-ups in n=10..16.")

    if local_violations:
        print()
        print("Local-only violations (master held, local failed):")
        for (n, sizes, edges, res) in local_violations[:20]:
            if (n, sizes, edges, res) not in master_violations:
                print(f"  n={n} sizes={sizes} res={res}")

    return {
        "n_values": n_values_done,
        "total_graphs": total_graphs,
        "total_configs": total_configs,
        "master_violations": master_violations,
        "local_violations": local_violations,
        "tight_master": tight_master,
        "global_min_master_slack": global_min_master_slack,
    }


if __name__ == "__main__":
    main()
