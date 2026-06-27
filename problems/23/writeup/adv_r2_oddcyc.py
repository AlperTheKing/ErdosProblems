#!/usr/bin/env python3
"""
Adversarial finder #2 for Erdos #23 Step-2 R2 MASTER INEQUALITY.

Family targeted: ODD CYCLES & LADDERS.
  - C_{2k+1} for n = 5..15 (odd cycles).
  - Cycles with one or two extra non-triangle chords (chord must not create a
    triangle: endpoints at cycle-distance >= 2; two chords also kept tri-free).
  - Mobius-Kantor graph (generalized Petersen GP(8,3), n=16, triangle-free).
  - Mobius-ladder / Wagner V_{2k} (n up to 16; the ones that are triangle-free).
    V_{2k} = cycle C_{2k} plus the k "diameters" i ~ i+k.  V_{2k} is triangle-free
    iff 2k >= 8 (V_6 = K_{3,3}? no: V_6 = K_{3,3} is bipartite triangle-free too;
    but V_6 has chords i~i+3 of a C_6 -> creates 4-cycles, no triangle). We test
    all 2k in {6,8,10,12,14,16} and keep only triangle-free ones.

Master inequality (R2): for a triangle-free simple graph G on n vertices, after
max-cut + connected-B filter + Gamma-min selection,  Gamma(G) + D*(G) <= n^2,
and the LOCAL form Gamma + D(C) <= n^2 for every shortest bad geodesic C.

We reuse the cross-validated reference checker problems/23/writeup/r2_check_ref.py
(master_check). A SINGLE master violation (master_slack < 0) REFUTES R2.

We cap n at 16 (brute max cut over 2^(n-1) masks is fine to n<=18; D(C) skipped
if |K|>20).  For the larger members we report whichever config is a connected-B
config; if a member is rejected (no connected-B max cut / no bad edge) we record
that and move on.
"""

import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from r2_check_ref import master_check  # cross-validated clean-room checker


def cycle_edges(verts):
    e = []
    k = len(verts)
    for i in range(k):
        e.append((verts[i], verts[(i + 1) % k]))
    return e


def has_triangle(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if adj[u] & adj[v]:
                return True
    return False


def cyc_dist(i, j, n):
    d = abs(i - j)
    return min(d, n - d)


def gen_members():
    """Yield (name, n, edges). All are triangle-free by construction/filter."""
    members = []

    # ---- 1. Odd cycles C_{2k+1}, n=5..15 ----
    for n in range(5, 16, 2):  # 5,7,9,11,13,15
        members.append((f"C{n}", n, cycle_edges(list(range(n)))))

    # ---- 2. Cycles (odd AND even, 5..16) with ONE extra non-triangle chord ----
    # A chord (i,j) on C_n avoids a triangle iff cycle-distance >= 2 (a distance-1
    # chord is already an edge; distance-2 chord (i,i+2) would close a triangle
    # i,i+1,i+2 -> EXCLUDE). So require cyc_dist >= 3 for safety against triangle,
    # but also keep distance-2? distance-2 chord i~i+2 + path i,i+1,i+2 = triangle
    # -> exclude. So min chord distance is 3.
    for n in range(5, 17):
        base = cycle_edges(list(range(n)))
        base_set = set(frozenset(e) for e in base)
        seen = set()
        for i in range(n):
            for j in range(i + 1, n):
                if frozenset((i, j)) in base_set:
                    continue
                if cyc_dist(i, j, n) < 3:
                    continue  # would create a triangle with a cycle path
                cand = base + [(i, j)]
                if has_triangle(n, cand):
                    continue
                key = (n, i, j)
                if key in seen:
                    continue
                seen.add(key)
                members.append((f"C{n}+chord({i},{j})", n, cand))

    # ---- 3. Cycles with TWO extra non-triangle chords (5..14 to keep count sane) ----
    for n in range(5, 15):
        base = cycle_edges(list(range(n)))
        base_set = set(frozenset(e) for e in base)
        chords = []
        for i in range(n):
            for j in range(i + 1, n):
                if frozenset((i, j)) in base_set:
                    continue
                if cyc_dist(i, j, n) < 3:
                    continue
                chords.append((i, j))
        from itertools import combinations
        for c1, c2 in combinations(chords, 2):
            cand = base + [c1, c2]
            if has_triangle(n, cand):
                continue
            members.append((f"C{n}+2ch{c1}{c2}", n, cand))

    # ---- 4. Mobius-ladder / Wagner V_{2k}: C_{2k} plus diameters i ~ i+k ----
    for half in range(3, 9):  # 2k = 6,8,10,12,14,16
        nn = 2 * half
        e = cycle_edges(list(range(nn)))
        for i in range(half):
            e.append((i, i + half))
        if has_triangle(nn, e):
            continue  # V_6 has triangles? check by filter
        members.append((f"V{nn}(Mobius-ladder)", nn, e))

    # ---- 5. Mobius-Kantor graph GP(8,3), n=16 ----
    # outer cycle u_0..u_7 (i ~ i+1 mod 8), spokes u_i ~ v_i,
    # inner edges v_i ~ v_{i+3 mod 8}.
    n = 16
    e = []
    for i in range(8):
        e.append((i, (i + 1) % 8))            # outer C8
        e.append((i, 8 + i))                  # spokes
        e.append((8 + i, 8 + ((i + 3) % 8)))  # inner skip-3
    members.append(("Mobius-Kantor GP(8,3)", n, e))

    # also Petersen GP(5,2) (n=10, triangle-free, girth 5) as a bonus stress case
    n = 10
    e = []
    for i in range(5):
        e.append((i, (i + 1) % 5))
        e.append((i, 5 + i))
        e.append((5 + i, 5 + ((i + 2) % 5)))
    members.append(("Petersen GP(5,2)", n, e))

    # ---- 6. Balanced odd-cycle blow-ups Cm[2], Cm[3] (tight-family stress) ----
    def blowup(cyc_n, t):
        e = []
        for i in range(cyc_n):
            j = (i + 1) % cyc_n
            ci = [t * i + r for r in range(t)]
            cj = [t * j + r for r in range(t)]
            for a in ci:
                for b in cj:
                    e.append((a, b))
        return cyc_n * t, e

    for cm in (5, 7):
        for t in (2, 3):
            nn, e = blowup(cm, t)
            if nn <= 16 and not has_triangle(nn, e):
                members.append((f"C{cm}[{t}]", nn, e))

    return members


def main():
    members = gen_members()
    n_values = sorted(set(m[1] for m in members))
    print(f"Adversarial R2 odd-cycle/ladder family: {len(members)} members, "
          f"n values {n_values}")
    print("=" * 78)

    tested = 0
    skipped = 0
    violations = []
    tight = []         # master_slack == 0
    min_master_slack = None
    worst_local_slack_min = None

    for name, n, edges in members:
        if n > 18:
            print(f"  SKIP {name} (n={n} too big for brute max-cut)")
            skipped += 1
            continue
        if has_triangle(n, edges):
            print(f"  SKIP {name} (has triangle)")
            skipped += 1
            continue
        try:
            res = master_check(n, edges)
        except Exception as ex:
            print(f"  ERR  {name} (n={n}): {ex}")
            skipped += 1
            continue
        if res is None:
            # not a connected-B config (no connected-B max cut / no bad edge)
            print(f"  ----  {name:28s} n={n:2d}: NOT a connected-B config (skip)")
            skipped += 1
            continue
        tested += 1
        ms = res["master_slack"]
        ls = res["worst_local_slack"]
        if min_master_slack is None or ms < min_master_slack:
            min_master_slack = ms
        if worst_local_slack_min is None or ls < worst_local_slack_min:
            worst_local_slack_min = ls
        flag = ""
        if ms < 0:
            flag = "  <<< MASTER VIOLATION"
            violations.append((name, n, edges, res))
        elif ls < 0:
            flag = "  <<< LOCAL VIOLATION (master OK)"
        if ms == 0:
            tight.append(name)
            flag += "  [TIGHT master slack 0]"
        print(f"  test {name:28s} n={n:2d}: gamma={res['gamma']:4d} "
              f"dstar={res['dstar']:3d} master_slack={ms:5d} "
              f"worst_local_slack={ls:5d}{flag}")

    print("=" * 78)
    print(f"tested={tested}  skipped={skipped}  master_violations={len(violations)}")
    print(f"min_master_slack_seen={min_master_slack}  "
          f"min_worst_local_slack_seen={worst_local_slack_min}")
    print(f"tight (master slack 0): {tight}")
    if violations:
        print("\n!!! MASTER VIOLATIONS FOUND !!!")
        for name, n, edges, res in violations:
            print(f"  {name}  n={n}")
            print(f"    edges={sorted(tuple(sorted(e)) for e in edges)}")
            print(f"    {res}")
    else:
        print("\nNo master violations in the odd-cycle/ladder family.")
    return violations, min_master_slack, tight, tested, n_values


if __name__ == "__main__":
    main()
