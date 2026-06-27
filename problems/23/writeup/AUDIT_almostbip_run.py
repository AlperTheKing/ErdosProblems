#!/usr/bin/env python3
"""Run the T_uniform GPI test over almost-bipartite families. EXACT Fractions. Report min slack + violations."""
import sys, io, random
from fractions import Fraction
_stdout = sys.stdout; sys.stdout = io.StringIO()
from AUDIT_almostbip_Tuniform import Tuniform_maxslack, g6_encode, adj_of, has_triangle
import AUDIT_almostbip_families as fam
from census_GPI import dec
sys.stdout = _stdout

random.seed(20260626)

def test(n, E, label, results, violations):
    adj = adj_of(n, E)
    if has_triangle(n, adj):
        return  # not triangle-free, skip
    r = Tuniform_maxslack(n, E)
    if r is None:
        return  # bipartite / no valid gamma-min connected-B cut
    if isinstance(r, tuple) and r and r[0] == 'GEOFAIL':
        print(f"  GEOFAIL {label}: {r}")
        return
    Gamma, K, maxT, slack, side, M, ell, T = r
    g6 = g6_encode(n, E)
    results.append((slack, n, Gamma, K, maxT, label, g6, len(M)))
    if slack < 0:
        violations.append((n, Gamma, K, maxT, label, g6))

results = []
violations = []
count = 0

# --- Family 1: single long odd cycles C_{2L+1}, N=11..21 (1 bad edge, ell=N, 1 shortest cycle) ---
for L in range(5, 11):
    n, E = fam.long_odd_cycle(L)
    test(n, E, f"C{2*L+1}", results, violations); count += 1

# --- Family 2: even cycle + chord creating a long odd cycle, all chord positions, L=5..9 ---
for L in range(5, 10):
    n0 = 2 * L
    for a in range(n0):
        for b in range(a + 2, n0):
            if (a == 0 and b == n0 - 1):  # adjacent on cycle
                continue
            n, E = fam.even_cycle_plus_chord(L, a, b)
            test(n, E, f"C{n0}+chord({a},{b})", results, violations); count += 1

# --- Family 3: theta graphs (two endpoints, 3 paths). parities chosen for long odd cycles ---
for a in range(2, 8):
    for b in range(a, 8):
        for c in range(b, 8):
            # need at least one odd cycle: two paths of differing parity
            n, E = fam.theta_graph(a, b, c)
            if n > 20: continue
            test(n, E, f"theta({a},{b},{c})", results, violations); count += 1

# --- Family 4: grid + one edge making a long odd cycle ---
for (r, c) in [(3, 4), (3, 5), (4, 4), (3, 6), (4, 5), (2, 7), (2, 8), (2, 9)]:
    n0, E0 = fam.grid(r, c)
    if n0 > 20: continue
    # try several extra edges connecting far corners (even Manhattan distance => odd cycle)
    for e in [(0, n0 - 1), (0, c - 1 + c), (r - 1, c), (0, (r - 1) * c)]:
        u, v = e
        if u == v or v >= n0: continue
        n, E = fam.grid_plus_edge(r, c, e)
        test(n, E, f"grid{r}x{c}+{e}", results, violations); count += 1

# --- Family 5: subdivided small odd graphs (subdivide edges of C5/Petersen-ish to raise ell) ---
# subdivide one edge of C5 by t => odd cycle length 5+t; pick t to keep odd & long
for base_L in [5, 7]:
    n0, E0 = fam.long_odd_cycle(base_L)  # C_{2L+1}
    for t in [2, 4, 6]:  # subdivide edge 0 by t (adds t vertices) keeping odd? length=2L+1+t
        n, E = fam.subdivide(n0, E0, {0}, t)
        if n > 22: continue
        test(n, E, f"C{2*base_L+1}_sub1x{t}", results, violations); count += 1

# --- Family 6: even cycle + TWO chords (a couple of bad edges, each long) ---
for L in range(5, 9):
    n0 = 2 * L
    chords = []
    for a in range(0, n0, 2):
        for b in range(a + 3, n0, 2):  # spacing for long odd cycles
            chords.append((a, b))
    # try pairs of chords that are "parallel" (non-crossing) to keep few shortest cycles
    for i in range(len(chords)):
        for j in range(i + 1, len(chords)):
            c1, c2 = chords[i], chords[j]
            n, E = fam.even_cycle(L)
            E = list(E) + [c1, c2]
            test(n, E, f"C{n0}+2chord{c1}{c2}", results, violations); count += 1

# --- Family 7: random almost-bipartite: random bipartite + k random odd-closing edges ---
def rand_bipartite(nA, nB, p):
    n = nA + nB
    E = []
    for a in range(nA):
        for b in range(nA, n):
            if random.random() < p:
                E.append((a, b))
    return n, E

for trial in range(4000):
    nA = random.randint(4, 8); nB = random.randint(4, 8)
    if nA + nB > 18: continue
    p = random.uniform(0.25, 0.55)
    n, E = rand_bipartite(nA, nB, p)
    # add 1-3 within-part edges (odd-closing) far apart
    k = random.randint(1, 3)
    parts = list(range(nA)) if random.random() < 0.5 else list(range(nA, n))
    if len(parts) < 2: continue
    extra = set()
    for _ in range(k):
        u, v = random.sample(parts, 2)
        extra.add((min(u, v), max(u, v)))
    E = list(set(map(lambda e: (min(e), max(e)), E)) | extra)
    test(n, E, f"randbip{trial}", results, violations); count += 1

# ---- report ----
print(f"TESTED (triangle-free, non-bipartite, valid gamma-min cut): {len(results)} graphs (attempted {count})")
results.sort(key=lambda x: x[0])
print("\n=== 15 SMALLEST SLACK (K - maxT) ===")
for slack, n, Gamma, K, maxT, label, g6, nM in results[:15]:
    print(f"  slack={slack}  N={n} Gamma={Gamma} K={K} maxT={maxT} |M|={nM}  {label}  g6={g6}")

if results:
    mn = results[0]
    print(f"\nMIN SLACK overall = {mn[0]}  (N={mn[1]}, {mn[5]}, g6={mn[6]})")
print(f"\nVIOLATIONS (slack<0): {len(violations)}")
for v in violations:
    print("  VIOLATION", v)
