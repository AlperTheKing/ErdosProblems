"""Smoke tests for Q5_lib on objects whose exact values are known."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *

# C5
n, adj = blowup_C5(1)
print("C5 edges", edges_of(n, adj))
print("C5 bip", bip_exact(n, adj))
print("C5 triangle-free", is_triangle_free(n, adj))
w = {e: Fraction(1) for e in edges_of(n, adj)}
print("C5 min odd cycle (unit w)", min_odd_cycle(n, adj, w))
r = tau_star(n, adj, verbose=True)
print("C5 tau* =", r["value"], "cover", r["cover"], "packing", r["packing"])
ok, info = verify_cover(n, adj, r["cover"])
print("cover verified:", ok, info)
ok2, tot = verify_packing(n, adj, r["packing"], w)
print("packing verified:", ok2, tot)

# Petersen
pet = "IheA@GUAo"
n, adj = g6_decode(pet)
print("Petersen n", n, "|E|", len(edges_of(n, adj)), "tri-free", is_triangle_free(n, adj))
print("Petersen bip", bip_exact(n, adj)[0])
r = tau_star(n, adj)
print("Petersen tau* =", r["value"])

# K4 (has triangles; bip=1, tau*=?)
n = 4
adj = [frozenset(set(range(4)) - {i}) for i in range(4)]
print("K4 bip", bip_exact(n, adj)[0], "tau*", tau_star(n, adj)["value"])

# K5: bip = 2, tau* = 5/2 (classic fractional vertex)
n = 5
adj = [frozenset(set(range(5)) - {i}) for i in range(5)]
print("K5 bip", bip_exact(n, adj)[0], "tau*", tau_star(n, adj)["value"])
