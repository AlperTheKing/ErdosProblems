"""
R9 / Erdos #23 -- the STATIC branch: local discharging rules + a global potential Phi(G).

Two questions decided here, exactly.

(Q1) Does a global potential rescue "discharging with local cut hypotheses"?
     A scheme of that shape proves a statement of the form
         for every LOCALLY OPTIMAL cut (A,B):   mono(A,B) <= F(G)
     where F(G) is any graph functional whatsoever (the global potential).  Since F does not
     see the cut, a single graph carrying a bad locally optimal cut forces F(G) > N^2/25
     there, and the scheme cannot deliver the conjecture AT THAT GRAPH.

(Q2) How global must the cut hypothesis be?  Compute exactly, over the C5 blow-up family,
     the minimum size of an improving switch away from a "wrong" class cut whose mono mass
     already exceeds N^2/25 -- the LOCALITY RADIUS that any discharging scheme must exceed.
"""
from fractions import Fraction
from itertools import product
from R9_discharge_lib import (make_c5_blowup, bip_blowup_c5, sigma_values, mono_count,
                              min_improving_switch, num_edges, edges, witnesses,
                              bip_exact, induced_pentagons, odd_cycles_upto, g6_decode,
                              make_petersen, make_cycle, N14_G6)

def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- blow-up class cuts
def blowup_class_cut_stats(a, chi):
    """a = class sizes (5), chi = 2-colouring of the 5 classes.
    Returns (N, mono, monopairs)."""
    N = sum(a)
    mono = 0
    pairs = []
    for i in range(5):
        j = (i + 1) % 5
        if chi[i] == chi[j]:
            mono += a[i] * a[j]
            pairs.append((i, j))
    return N, mono, pairs


def blowup_sigma(a, chi):
    """sigma of a vertex of class i (all vertices of a class are twins)."""
    out = []
    for i in range(5):
        s = o = 0
        for j in ((i - 1) % 5, (i + 1) % 5):
            if chi[j] == chi[i]:
                s += a[j]
            else:
                o += a[j]
        out.append(o - s)
    return out


def blowup_switch_delta(a, chi, k):
    """Change in mono-edge count when flipping k_i vertices out of class i."""
    d = 0
    for i in range(5):
        j = (i + 1) % 5
        if chi[i] == chi[j]:
            d += (a[i] - k[i]) * (a[j] - k[j]) + k[i] * k[j] - a[i] * a[j]
        else:
            d += (a[i] - k[i]) * k[j] + k[i] * (a[j] - k[j])
    return d


def min_improving_switch_blowup(a, chi):
    """Exact minimum number of flipped vertices that strictly decreases the mono count.
    All vertices of a class are twins, so counting vectors k suffice."""
    best = None
    for k in product(*[range(x + 1) for x in a]):
        s = sum(k)
        if s == 0 or (best is not None and s >= best[0]):
            continue
        if blowup_switch_delta(a, chi, k) < 0:
            best = (s, k)
    return best


# ---------------------------------------------------------------- Q1
hdr("Q1.  Gate of the A19 witness  C5[7,7,12,7,12]  with the class cut {c0,c2}")
a = [7, 7, 12, 7, 12]
chi = [0, 1, 0, 1, 1]            # side of each class:  A = V0 u V2,  B = V1 u V3 u V4
N, mono, pairs = blowup_class_cut_stats(a, chi)
sig = blowup_sigma(a, chi)
print(f"  a={a}  N={N}  |E|={sum(a[i]*a[(i+1)%5] for i in range(5))}")
print(f"  bip = min_i a_i a_(i+1) = {bip_blowup_c5(a)}   N^2/25 = {Fraction(N*N,25)}"
      f"   conjecture holds here: {25*bip_blowup_c5(a) <= N*N}")
print(f"  chosen cut: monochromatic class pairs {pairs}, mono = {mono}")
print(f"  25*mono = {25*mono}  vs  N^2 = {N*N}   ->  25*mono > N^2 : {25*mono > N*N}")
print(f"  sigma per class = {sig}   all >= 0 : {all(s >= 0 for s in sig)}  (locally optimal)")
r = min_improving_switch_blowup(a, chi)
print(f"  smallest improving switch: size {r[0]} = {Fraction(r[0], N)} N = "
      f"{float(Fraction(r[0],N)):.4f} N, counting vector {r[1]}")
print()
print("  CONSEQUENCE (no global potential rescues local-cut discharging):")
print("  any valid scheme of the shape 'for every locally optimal cut, mono <= F(G)'")
print(f"  must have F(G) >= {mono} at this graph, while the target is N^2/25 = "
      f"{Fraction(N*N,25)}.")
print(f"  {mono} > {Fraction(N*N,25)}  =>  the scheme cannot prove bip <= N^2/25 at this")
print("  very graph, for EVERY functional F, i.e. for every global potential.")

# ---------------------------------------------------------------- Q2 locality radius
hdr("Q2.  LOCALITY RADIUS: max over blow-up shapes of (min improving switch)/N,")
print("     restricted to class cuts that already violate 25*mono > N^2.")
print("     (a discharging scheme whose cut hypothesis only rules out switches of size")
print("      <= sN is dead unless s exceeds this radius)")
best = None
DEN = 20
count = 0
for a0 in range(0, DEN + 1):
    for a1 in range(0, DEN + 1 - a0):
        for a2 in range(0, DEN + 1 - a0 - a1):
            for a3 in range(0, DEN + 1 - a0 - a1 - a2):
                a4 = DEN - a0 - a1 - a2 - a3
                a = [a0, a1, a2, a3, a4]
                Nv = DEN
                for chim in range(1, 31):     # colourings, skip all-equal (chi=0 / 31)
                    chi = [(chim >> i) & 1 for i in range(5)]
                    Nn, mono, pairs = blowup_class_cut_stats(a, chi)
                    if 25 * mono <= Nn * Nn:
                        continue
                    sg = blowup_sigma(a, chi)
                    if any(s < 0 for s in sg):
                        continue              # not even locally optimal
                    count += 1
                    rr = min_improving_switch_blowup(a, chi)
                    if rr is None:
                        continue
                    ratio = Fraction(rr[0], Nn)
                    if best is None or ratio > best[0]:
                        best = (ratio, a[:], chi[:], rr, mono, Nn)
print(f"  scanned {count} (shape, locally-optimal violating class cut) pairs at N={DEN}")
if best:
    ratio, a, chi, rr, mono, Nn = best
    print(f"  MAX radius = {ratio} = {float(ratio):.4f} N")
    print(f"    shape a={a}, chi={chi}, mono={mono}, 25*mono={25*mono} > N^2={Nn*Nn}")
    print(f"    smallest improving switch: {rr[0]} vertices, vector {rr[1]}")

# refine the best proportions at larger N
hdr("Q2b. refinement of the best proportions at larger N (exact)")
for scale in (2, 3):
    a2 = [x * scale for x in best[1]]
    chi2 = best[2]
    Nn, mono, pairs = blowup_class_cut_stats(a2, chi2)
    if 25 * mono <= Nn * Nn:
        print(f"  scale {scale}: no longer violating"); continue
    rr = min_improving_switch_blowup(a2, chi2)
    print(f"  a={a2}  N={Nn}  mono={mono}  25mono={25*mono}>N^2={Nn*Nn}  "
          f"min switch={rr[0]} = {Fraction(rr[0],Nn)} = {float(Fraction(rr[0],Nn)):.4f} N")

# ---------------------------------------------------------------- pentagon charging
hdr("Q3.  charging to induced pentagons")
print(f"{'graph':26s} {'N':>3s} {'bip':>4s} {'#C5ind':>7s} {'#C7ind':>7s}  comment")
for (name, n, adj) in witnesses():
    P = len(induced_pentagons(n, adj))
    S = len(odd_cycles_upto(n, adj, 7)) - P
    b = bip_exact(n, adj)
    c = ""
    if P == 0 and b > 0:
        c = "<== bip>0 with NO induced pentagon: kills every pentagon-supported scheme"
    print(f"{name:26s} {n:3d} {b:4d} {P:7d} {S:7d}  {c}")
print()
print("  the pentagon-mass form of the charge, psi <= (sum over induced C5 of prod x)^(2/5),")
print("  is exactly tight on C5 and fails on:")
for (name, n, adj) in witnesses():
    P = induced_pentagons(n, adj)
    x = [Fraction(1, n)] * n
    mass = sum(Fraction(1, n) ** 5 for _ in P)
    b = Fraction(bip_exact(n, adj), n * n)
    # compare b^5 with mass^2  (avoids fractional powers; equivalent to b <= mass^(2/5))
    lhs, rhs = b ** 5, mass ** 2
    print(f"    {name:26s} psi={str(b):>9s}  pentmass={str(mass):>12s}  "
          f"psi^5 <= pentmass^2 : {lhs <= rhs}")
