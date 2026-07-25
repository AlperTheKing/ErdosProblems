"""Basic exact table for the R8 testbed + the two transport quantities.

  bip(G)                       exact
  minU(G) = min_S |U(S)|       the "Mantel-support" of the best cut
  25*bip <= N^2 ?              conjecture check
  5*minU <= 2N ?               CONJECTURE T check in the vertex-transitive case
"""
from R8_transport_lib import *
from fractions import Fraction

rows = []
for G in testbed():
    best_c, best_U = G.m, G.n
    argU = None
    for S in G.all_cuts():
        mono = G.mono_edges(S)
        U = 0
        for u, v in mono:
            U |= (1 << u) | (1 << v)
        if len(mono) < best_c:
            best_c = len(mono)
        if popcount(U) < best_U:
            best_U = popcount(U)
            argU = (S, mono)
    rows.append((G, best_c, best_U, argU))

print("%-22s %3s %4s %5s %6s %8s %8s %8s" %
      ("graph", "N", "|E|", "tri-f", "bip", "N^2/25", "minU", "2N/5"))
for G, b, u, arg in rows:
    print("%-22s %3d %4d %5s %6d %8.3f %8d %8.3f  %s" %
          (G.name, G.n, G.m, G.triangle_free(), b, G.n ** 2 / 25.0, u, 2 * G.n / 5.0,
           "OK" if 5 * u <= 2 * G.n else "T-FAIL(if vtx-trans)"))
print()
for G, b, u, arg in rows:
    S, mono = arg
    print("%-22s min-|U| cut S=%s mono=%s" % (G.name, bin(S)[2:].zfill(G.n)[::-1], mono))
