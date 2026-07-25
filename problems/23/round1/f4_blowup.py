"""Erdos #23, family F4.

(A) identify the rho-extremal graphs found by f4_step.exe
(B) exact table for the C5 blow-up family: bip, deficiency, one-vertex deletion,
    closed-neighbourhood peeling, 5-set deletion
(C) exact counterexample hunt over blow-ups of the reduced maximal triangle-free
    (RMTF) graphs on <= 12 vertices:  is there H and integer weights a with
        25 * bip(H[a]) > (sum a)^2   ?
    All arithmetic integer/Fraction.  bip(H[a]) = min over cuts S of V(H) of the
    a-weight of the uncut edges (Lemma A, proved in the write-up).
"""
import random, sys, glob, os
from fractions import Fraction
from itertools import combinations
from f1_bip import g6_decode, bip_bruteforce, blowup_bip, expand, is_triangle_free

random.seed(4)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- (A)
print("=== (A) rho-extremal graphs ===")
for g6 in ["DUW", "I?rFf_{N?", "J?bFF`wN?{?", "K???C@?kA]fs"]:
    n, E = g6_decode(g6)
    deg = [0]*n
    for u, v in E:
        deg[u] += 1; deg[v] += 1
    b = bip_bruteforce(n, E)
    drops = []
    for v in range(n):
        keep = [i for i in range(n) if i != v]
        idx = {w: i for i, w in enumerate(keep)}
        EE = [(idx[x], idx[y]) for (x, y) in E if x != v and y != v]
        drops.append(b - bip_bruteforce(n-1, EE))
    print(f"{g6}: n={n} m={len(E)} degs={sorted(deg)} bip={b} "
          f"drops={sorted(drops)} rho={min(drops)}")

# is the N=10 witness C5[2]?
C5 = [(0,1),(1,2),(2,3),(3,4),(4,0)]
N2, E2 = expand(5, C5, [2]*5)
import networkx as nx
G1 = nx.Graph(); G1.add_nodes_from(range(N2)); G1.add_edges_from(E2)
n10, E10 = g6_decode("I?rFf_{N?")
G2 = nx.Graph(); G2.add_nodes_from(range(n10)); G2.add_edges_from(E10)
print("N=10 witness isomorphic to C5[2]:", nx.is_isomorphic(G1, G2))
n11, E11 = g6_decode("J?bFF`wN?{?")
G3 = nx.Graph(); G3.add_nodes_from(range(n11)); G3.add_edges_from(E11)
N3, E3 = expand(5, C5, [3,2,2,2,2])
G4 = nx.Graph(); G4.add_nodes_from(range(N3)); G4.add_edges_from(E3)
print("N=11 witness isomorphic to C5[3,2,2,2,2]:", nx.is_isomorphic(G3, G4))

# ---------------------------------------------------------------- (B)
print()
print("=== (B) C5 blow-up family, exact ===")
print(" n     N   bip   N^2/25      D(G)   bip(G-v) D(G-v)   drop budget1   "
      "peel:bip(G-N[v]) budget_peel   drop5 budget5")
for n in range(1, 9):
    N = 5*n
    b = blowup_bip(5, C5, [n]*5)
    assert b == n*n
    bv = blowup_bip(5, C5, [n-1, n, n, n, n])
    D = Fraction(N*N, 25) - b
    Dv = Fraction((N-1)**2, 25) - bv
    budget1 = Fraction(2*N-1, 25)
    # peeling N[v]: v in part 1, N(v) = parts 2 and 5
    Npeel = N - (1 + 2*n)
    bpeel = 0                                   # K_{n,n} + (n-1) isolated vertices
    assert blowup_bip(5, C5, [n-1, 0, n, n, 0]) == 0
    budgetp = Fraction(N*N - Npeel**2, 25)
    b5 = blowup_bip(5, C5, [n-1]*5)
    budget5 = Fraction(N*N - (N-5)**2, 25)
    print(f"{n:2d} {N:5d} {b:5d} {str(Fraction(N*N,25)):>8} {str(D):>9} "
          f"{bv:7d} {str(Dv):>7} {b-bv:6d} {str(budget1):>7}   "
          f"{bpeel:14d} {str(budgetp):>11}   {b-b5:5d} {str(budget5):>7}")

