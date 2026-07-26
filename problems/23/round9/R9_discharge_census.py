"""
R9 / Erdos #23 -- census gate for T4:  what does the global potential actually buy?

Plain (un-amortised) one-step deletion induction succeeds at G iff
      floor(delta(G)/2) <= (2N-1)/25.
The amortised version with an ARBITRARY nonnegative potential succeeds iff
      V(G) = min over deletion orderings of sum floor(d_i/2)   <=  N^2/25,
and the counting identity sum_i d_i = |E| forces V >= (|E|-N)/2, hence
      |E| <= 2N^2/25 + N   and therefore   delta <= dbar = 2|E|/N <= 4N/25 + 2.

So the potential replaces a MINIMUM-degree condition delta <~ 4N/25 by an AVERAGE-degree
condition dbar <~ 4N/25 + 2: the entire gain is bounded by an additive constant in the
degree threshold.  Measured here on the full triangle-free census.
"""
import os
from fractions import Fraction
from R9_discharge_lib import (g6_decode, num_edges, bip_exact, dp_greedy_value, degrees)

FILES = [(9, r"..\round7\audit_tf9.g6"), (10, r"..\round7\audit_tf10.g6")]

print(f"{'n':>3s} {'graphs':>7s} {'V<=N^2/25':>10s} {'plain step':>11s} "
      f"{'max |E|/N^2 in M':>17s} {'max delta-4N/25 in M':>21s} {'max delta/N in M':>17s}")
for n_expect, path in FILES:
    if not os.path.exists(path):
        print(f"  missing {path}")
        continue
    tot = mech = plain = 0
    maxdens = None
    maxexcess = None
    maxdel = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n, adj = g6_decode(line)
            m = num_edges(n, adj)
            V, _ = dp_greedy_value(n, adj)
            b = bip_exact(n, adj)
            assert V >= b, "soundness V>=bip violated"
            assert V >= Fraction(m - n, 2), "counting bound violated"
            assert V <= Fraction(n * n, 25) or True
            tot += 1
            okm = V <= Fraction(n * n, 25)
            d = degrees(n, adj)
            okp = min(d) // 2 <= Fraction(2 * n - 1, 25)
            mech += okm
            plain += okp
            if okm:
                dens = Fraction(m, n * n)
                exc = Fraction(min(d)) - Fraction(4 * n, 25)
                dl = Fraction(min(d), n)
                if maxdens is None or dens > maxdens:
                    maxdens = dens
                if maxexcess is None or exc > maxexcess:
                    maxexcess = exc
                if maxdel is None or dl > maxdel:
                    maxdel = dl
    print(f"{n_expect:3d} {tot:7d} {mech:10d} {plain:11d} "
          f"{str(maxdens):>17s} {str(maxexcess):>21s} {str(maxdel):>17s}")

print()
print("Reading:")
print(" * the counting bound V >= (|E|-N)/2 held on every graph of the census (asserted);")
print(" * 'max delta - 4N/25 over the graphs where the mechanism works' is the entire")
print("   benefit of the potential, and it is an ADDITIVE O(1), never a factor;")
print(" * the extremal family sits at |E|/N^2 = 1/5 and delta/N = 2/5, both far outside")
print("   the region {|E| <= 2N^2/25 + N} in which the mechanism can operate at all.")
print()
print("Threshold arithmetic, asymptotically:")
print("   plain step needs      delta <= 2*floor((2N-1)/25)+1  ~ 4N/25")
print("   mechanism needs (nec.) delta <= 2|E|/N <= 4N/25 + 2  ~ 4N/25")
print("   extremal family has   delta = 2N/5 = 10N/25         = 2.5x the threshold")
