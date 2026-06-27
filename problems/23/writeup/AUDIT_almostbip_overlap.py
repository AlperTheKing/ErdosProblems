#!/usr/bin/env python3
"""Probe the LOAD-CONCENTRATION danger: multiple long odd cycles whose shortest B-geodesics
OVERLAP on shared vertices (the only way maxT could climb toward/above K). EXACT Fractions."""
import sys, io
from fractions import Fraction
_stdout = sys.stdout; sys.stdout = io.StringIO()
from AUDIT_almostbip_Tuniform import Tuniform_maxslack, g6_encode, adj_of, has_triangle
sys.stdout = _stdout

results = []; violations = []; count = 0
def test(n, E, label):
    global count
    adj = adj_of(n, E)
    if has_triangle(n, adj): return
    r = Tuniform_maxslack(n, E)
    if r is None: return
    if isinstance(r, tuple) and r and r[0] == 'GEOFAIL':
        print("GEOFAIL", label, r); return
    Gamma, K, maxT, slack, side, M, ell, T = r
    g6 = g6_encode(n, E)
    results.append((slack, n, Gamma, K, maxT, label, g6, len(M)))
    if slack < 0: violations.append((n, Gamma, K, maxT, label, g6))
    count += 1

# Two odd cycles sharing a PATH of length s (book/theta of odd cycles). Sharing a path makes
# the two bad edges' geodesics overlap on the shared path => max concentration.
# Build: shared path P = 0-1-...-s. Then two ears each an odd-length path back from s to 0.
def two_odd_share_path(s, e1, e2):
    """shared path length s (edges), two ears of edge-lengths e1,e2 from vertex s back to vertex 0.
    Cycle_i length = s + e_i ; odd iff s+e_i odd."""
    n = s + 1
    E = [(i, i + 1) for i in range(s)]
    def ear(elen):
        nonlocal n
        prev = s
        for _ in range(elen - 1):
            cur = n; n += 1
            E.append((prev, cur)); prev = cur
        E.append((prev, 0))
    ear(e1); ear(e2)
    return n, E

for s in range(1, 6):
    for e1 in range(2, 8):
        for e2 in range(e1, 8):
            n, E = two_odd_share_path(s, e1, e2)
            if n > 22: continue
            test(n, E, f"share_path(s={s},e1={e1},e2={e2})")

# Two odd cycles sharing a single EDGE (s=1) but many length combos already above.
# Three odd cycles sharing one vertex (sunflower) - geodesics meet at the center vertex.
def sunflower(ear_lens):
    n = 1
    E = []
    for L in ear_lens:  # each ear is an odd cycle through center 0 of length L (edges)
        prev = 0
        for _ in range(L - 1):
            cur = n; n += 1
            E.append((prev, cur)); prev = cur
        E.append((prev, 0))
    return n, E
for combo in [(5,5),(5,5,5),(5,7),(7,7),(5,5,7),(5,9),(7,9),(9,9),(5,5,5,5),(5,7,9)]:
    n, E = sunflower(list(combo))
    if n > 22: continue
    test(n, E, f"sunflower{combo}")

# Mobius-Kantor style: long even cycle with several evenly spaced far chords (multiple long odd cycles overlapping arcs)
def cycle_with_chords(n0, chords):
    E = [(i, (i + 1) % n0) for i in range(n0)] + list(chords)
    return n0, E
for n0 in [10, 12, 14, 16]:
    # parallel far chords offset by n0/2 -> several long odd cycles
    for half in range(2, n0 // 2):
        chords = []
        for a in range(0, n0 - half, 2):
            chords.append((a, a + half))
        if not chords: continue
        n, E = cycle_with_chords(n0, chords)
        test(n, E, f"C{n0}+parallel(half={half})")

results.sort(key=lambda x: x[0])
print(f"TESTED overlap structures: {len(results)}")
print("\n=== 15 SMALLEST SLACK ===")
for slack, n, Gamma, K, maxT, label, g6, nM in results[:15]:
    print(f"  slack={slack}  N={n} Gamma={Gamma} K={K} maxT={maxT} |M|={nM}  {label}  g6={g6}")
if results: print(f"\nMIN SLACK = {results[0][0]}  ({results[0][5]}, g6={results[0][6]})")
print(f"\nVIOLATIONS (slack<0): {len(violations)}")
for v in violations: print("  VIOLATION", v)
