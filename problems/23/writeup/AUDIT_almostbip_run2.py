#!/usr/bin/env python3
"""Round 2: push the almost-bipartite regime harder. Long odd cycle + bipartite appendages,
even-cycle+far-chord, odd-cycle glued to even-cycle, lollipops, bigger random almost-bip. EXACT."""
import sys, io, random
from fractions import Fraction
_stdout = sys.stdout; sys.stdout = io.StringIO()
from AUDIT_almostbip_Tuniform import Tuniform_maxslack, g6_encode, adj_of, has_triangle
from census_GPI import dec
sys.stdout = _stdout
random.seed(7)

def test(n, E, label, results, violations):
    adj = adj_of(n, E)
    if has_triangle(n, adj):
        return
    r = Tuniform_maxslack(n, E)
    if r is None: return
    if isinstance(r, tuple) and r and r[0] == 'GEOFAIL':
        print("GEOFAIL", label, r); return
    Gamma, K, maxT, slack, side, M, ell, T = r
    g6 = g6_encode(n, E)
    results.append((slack, n, Gamma, K, maxT, label, g6, len(M)))
    if slack < 0:
        violations.append((n, Gamma, K, maxT, label, g6))

results = []; violations = []; count = 0

# A: odd cycle C_{2L+1} with a pendant path of length p attached at vertex 0 (bipartite appendage)
for L in range(3, 9):
    base = 2 * L + 1
    for p in range(1, 6):
        n = base + p
        E = [(i, (i + 1) % base) for i in range(base)]
        prev = 0
        for _ in range(p):
            E.append((prev, n - (p - (_))));
        # build chain properly
        E = [(i, (i + 1) % base) for i in range(base)]
        prev = 0
        cur = base
        for _ in range(p):
            E.append((prev, cur)); prev = cur; cur += 1
        if n > 22: continue
        test(n, E, f"C{base}+path{p}", results, violations); count += 1

# B: odd cycle with a pendant EVEN cycle sharing one vertex (two cycles, one odd one even)
for L in range(3, 8):
    odd = 2 * L + 1
    for M2 in range(2, 6):
        even = 2 * M2
        n = odd + even - 1  # share vertex 0
        E = [(i, (i + 1) % odd) for i in range(odd)]
        # even cycle on vertices [0, odd, odd+1, ..., odd+even-2] back to 0
        ev = [0] + list(range(odd, odd + even - 1))
        for k in range(len(ev)):
            E.append((ev[k], ev[(k + 1) % len(ev)]))
        if n > 22: continue
        test(n, E, f"C{odd}_glue_C{even}", results, violations); count += 1

# C: long even cycle + single far chord at varying offset (one long odd cycle, large extra bipartite mass)
for L in range(6, 12):
    n0 = 2 * L
    for off in range(2, L + 1):
        # chord (0, off): cycle 0..off has length off; odd cycle exists iff off even (arc parity)
        a, b = 0, off
        E = [(i, (i + 1) % n0) for i in range(n0)] + [(a, b)]
        if n0 > 22: continue
        test(n0, E, f"C{n0}+chord(0,{off})", results, violations); count += 1

# D: two long odd cycles sharing a single vertex (2 bad edges, both large ell)
for L1 in range(3, 7):
    for L2 in range(L1, 7):
        o1 = 2 * L1 + 1; o2 = 2 * L2 + 1
        n = o1 + o2 - 1
        if n > 22: continue
        E = [(i, (i + 1) % o1) for i in range(o1)]
        ring2 = [0] + list(range(o1, o1 + o2 - 1))
        for k in range(len(ring2)):
            E.append((ring2[k], ring2[(k + 1) % len(ring2)]))
        test(n, E, f"C{o1}_share_C{o2}", results, violations); count += 1

# E: theta with longer paths (one odd cycle), many parity combos up to N=20
for a in range(2, 10):
    for b in range(a, 10):
        for c in range(b, 10):
            import AUDIT_almostbip_families as fam
            n, E = fam.theta_graph(a, b, c)
            if n > 21: continue
            test(n, E, f"theta({a},{b},{c})", results, violations); count += 1

# F: bigger random almost-bipartite, fewer added edges, larger N up to 18
def rand_bipartite(nA, nB, p):
    n = nA + nB; E = []
    for x in range(nA):
        for y in range(nA, n):
            if random.random() < p: E.append((x, y))
    return n, E
for trial in range(8000):
    nA = random.randint(5, 9); nB = random.randint(5, 9)
    if nA + nB > 18: continue
    p = random.uniform(0.2, 0.5)
    n, E = rand_bipartite(nA, nB, p)
    k = random.randint(1, 2)
    parts = list(range(nA)) if random.random() < 0.5 else list(range(nA, n))
    if len(parts) < 2: continue
    extra = set()
    for _ in range(k):
        u, v = random.sample(parts, 2); extra.add((min(u, v), max(u, v)))
    E = list(set((min(a, b), max(a, b)) for a, b in E) | extra)
    test(n, E, f"randbip2_{trial}", results, violations); count += 1

print(f"TESTED: {len(results)} (attempted {count})")
results.sort(key=lambda x: x[0])
print("\n=== 20 SMALLEST SLACK ===")
for slack, n, Gamma, K, maxT, label, g6, nM in results[:20]:
    print(f"  slack={slack}  N={n} Gamma={Gamma} K={K} maxT={maxT} |M|={nM}  {label}  g6={g6}")
if results:
    print(f"\nMIN SLACK = {results[0][0]}  ({results[0][5]}, g6={results[0][6]})")
print(f"\nVIOLATIONS (slack<0): {len(violations)}")
for v in violations: print("  VIOLATION", v)
