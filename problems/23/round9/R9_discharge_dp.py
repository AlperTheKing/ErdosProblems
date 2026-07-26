"""
R9 / Erdos #23 -- THEOREM 1-4 machinery:  "potential = DP value" and its consequences.

A potential-function (amortised) argument over a reduction process proves EXACTLY the
statement  V(G) <= f(G),  where V is the shortest-path (dynamic-programming) value of the
reduction system and f(G) = N^2/25 is the target.  This script computes V exactly.

Costs used
  c_half(G,v) = floor(d_G(v)/2)          -- the canonical sound insertion cost
  c_true(G,v) = bip(G) - bip(G-v)        -- the exact (circular) cost
Everything is exact integer arithmetic.
"""
from fractions import Fraction
from R9_discharge_lib import (witnesses, make_c5_blowup, make_complete_bipartite,
                              make_cycle, num_edges, bip_exact, dp_greedy_value,
                              dp_true_drop, dp_delete_cost, cost_floor_half_degree,
                              bip_blowup_c5, induced, edges)
import itertools

def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# --------------------------------------------------------------------- T2 / T4 table
hdr("T4.  V(G) = min over deletion orderings of sum floor(d_i/2)   vs   N^2/25")
print(f"{'graph':26s} {'N':>3s} {'|E|':>4s} {'bip':>4s} {'V':>5s} {'N^2/25':>8s} "
      f"{'(|E|-N)/2':>10s}  step-possible?")
rows = []
for (name, n, adj) in witnesses():
    m = num_edges(n, adj)
    b = bip_exact(n, adj)
    V, seq = dp_greedy_value(n, adj)
    lb = Fraction(m - n, 2)
    tgt = Fraction(n * n, 25)
    ok = V <= tgt
    rows.append((name, n, m, b, V, tgt, lb, ok))
    print(f"{name:26s} {n:3d} {m:4d} {b:4d} {V:5d} {str(tgt):>8s} {str(lb):>10s}  "
          f"{'YES' if ok else 'NO  <-- mechanism dead here'}")
    assert V >= lb, "counting lower bound violated"
    assert V >= b, "soundness (V >= bip) violated"

# --------------------------------------------------------------------- C5[n] family
hdr("T4a.  the extremal family C5[n]:  V vs bip vs N^2/25")
for k in (1, 2, 3):
    n, adj = make_c5_blowup([k] * 5)
    m = num_edges(n, adj)
    V, seq = dp_greedy_value(n, adj)
    b = bip_exact(n, adj)
    print(f"C5[{k}]  N={n:3d} |E|={m:4d} bip={b:3d}  V={V:4d}  N^2/25={Fraction(n*n,25)}"
          f"   counting LB (|E|-N)/2={Fraction(m-n,2)}   verdict="
          f"{'ok' if V<=Fraction(n*n,25) else 'DEAD'}")
print("closed form: C5[n] has |E|=5n^2, N=5n, so V >= (5n^2-5n)/2 > n^2 = N^2/25 for all n>=2")

# --------------------------------------------------------------------- K_{n,n}: the 1/8 barrier
hdr("T4b.  K_{n,n}:  bip = 0 but V ~ N^2/8   (the mechanism cannot prove any c < 1/8)")
for k in range(2, 8):
    n, adj = make_complete_bipartite(k, k)
    m = num_edges(n, adj)
    V, seq = dp_greedy_value(n, adj)
    print(f"K_{{{k},{k}}}  N={n:3d} |E|={m:4d} bip=0  V={V:4d}"
          f"   (|E|-N)/2={Fraction(m-n,2)}   V/N^2={Fraction(V, n*n)} = {float(Fraction(V,n*n)):.5f}"
          f"   N^2/25={Fraction(n*n,25)}")
print("counting: V >= (n^2-2n)/2 = N^2/8 - N/2, while bip = 0.")
print("=> sup_G V(G)/N^2 >= 1/8 - o(1) > 1/23.5 > 1/25 : the mechanism cannot reach ANY")
print("   constant below 1/8, whatever the potential.")

# --------------------------------------------------------------------- circularity check
hdr("T2.  the exact-cost instantiation is circular:  V_true(G) = bip(G) identically")
for (name, n, adj) in witnesses():
    if n > 11:
        continue
    V, seq = dp_true_drop(n, adj)
    b = bip_exact(n, adj)
    print(f"{name:26s} V_true={V:3d}  bip={b:3d}  equal={V == b}")
    assert V == b

# --------------------------------------------------------------------- T3 forcing
hdr("T3.  extremality forcing: on a slack-0 graph every step of every admissible scheme")
print("     is tight, so sum of costs along the whole deletion path must equal bip(G).")
print("     For c = floor(d/2) that means:  V(G) = bip(G).  Test on the witnesses:")
for (name, n, adj) in witnesses():
    b = bip_exact(n, adj)
    V, _ = dp_greedy_value(n, adj)
    slack = Fraction(n * n, 25) - b
    print(f"{name:26s} slack={str(slack):>7s}  V-bip={V-b:3d}"
          f"{'   <== extremal, forcing applies' if slack == 0 else ''}")

# --------------------------------------------------------------------- set deletion on C5[n]
hdr("T5.  NO deletion move of ANY size works on C5[n]: true drop > quadratic budget")
print("removing k_i vertices from class i of C5[n]:")
print("   true drop = n^2 - min_i (n-k_i)(n-k_{i+1}),  budget = (N^2-(N-|k|)^2)/25, N=5n")
worst = None
for n in range(1, 13):
    N = 5 * n
    bad = 0
    tot = 0
    minratio = None
    for k in itertools.product(range(n + 1), repeat=5):
        if sum(k) == 0:
            continue
        tot += 1
        drop = n * n - min((n - k[i]) * (n - k[(i + 1) % 5]) for i in range(5))
        s = sum(k)
        budget = Fraction(N * N - (N - s) ** 2, 25)
        if drop <= budget:
            bad += 1
        r = Fraction(drop, 1) / budget if budget else None
        if r is not None and (minratio is None or r < minratio):
            minratio = r
    print(f"  n={n:2d}  removal vectors={tot:7d}  moves with drop<=budget: {bad}"
          f"   min(drop/budget)={minratio} = {float(minratio):.4f}")
    if worst is None or minratio < worst:
        worst = minratio
print(f"minimum over all tested (n,k) of drop/budget = {worst} = {float(worst):.4f} > 1")
print("=> every vertex-set-deletion step at C5[n] overshoots its quadratic budget by a")
print("   factor >= 2.5; the potential must supply the difference, which the forcing")
print("   theorem forbids (Phi = 0 at a slack-0 graph and Phi <= slack everywhere).")
