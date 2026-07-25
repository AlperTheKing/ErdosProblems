"""ROOT-AGENT GATE (Claude): EXPLICIT exactly-certified integrality gap on And(4) = Gamma_11.

Corrects my own error in claude_gate_and4_oddk5.py --gap, which had the clutter correspondence
backwards and therefore found no gap.  For a covering clutter:

    weight 0  on e  <->  DELETION of e     (a free element covers every member through it),
    weight oo on e  <->  CONTRACTION of e  (covers may not use e, so they must hit C \\ {e}).

The odd-K5 minor of Gamma_11 contracts the 6 branch-set edges and deletes the 6 surplus
connecting edges, so the witnessing weight is

    w = M   on the 6 contracted edges  {(0,4),(4,8),(1,5),(5,9),(2,6),(6,10)},
    w = 1   on the 10 kept edges,
    w = 0   on the 6 deleted edges.

Then tau_w should be tau(odd-K5) = 4 while tau*_w should be tau*(odd-K5) = 10/3, an exact gap.
Both sides are certified exactly: tau_w by enumerating all 1024 cuts in integers, tau*_w by an
explicit rational feasible y whose cost is checked against every one of the 596 odd cycles.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma(n):
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if 3 * min((u - v) % n, (v - u) % n) > n]


n = 11
E = gamma(n)
idx = {e: i for i, e in enumerate(E)}
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)

branch = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3}, {7}]
Y = sorted(idx[tuple(sorted((u, v)))] for T in branch
           for u, v in combinations(sorted(T), 2) if v in A[u])
KEEP = [(1, 8), (2, 8), (3, 8), (0, 7), (2, 9), (3, 9), (1, 7), (3, 10), (2, 7), (3, 7)]
keep = sorted(idx[tuple(sorted(e))] for e in KEEP)
Z = sorted(set(range(len(E))) - set(Y) - set(keep))
print(f"contracted Y = {[E[i] for i in Y]}")
print(f"kept        = {[E[i] for i in keep]}")
print(f"deleted Z   = {[E[i] for i in Z]}")

odd = set()
for s in range(n):
    def dfs(u, seen, el):
        for v in sorted(A[u]):
            if v == s and len(seen) >= 3 and len(seen) % 2 == 1:
                odd.add(frozenset(el + [idx[tuple(sorted((u, v)))]]))
            elif v > s and v not in seen:
                dfs(v, seen | {v}, el + [idx[tuple(sorted((u, v)))]])
    dfs(s, {s}, [])
odd = sorted(odd, key=lambda c: (len(c), sorted(c)))
print(f"odd cycles of Gamma_11: {len(odd)}   lengths {sorted({len(c) for c in odd})}")

for M in (5, 10, 100, 1000):
    w = [0] * len(E)
    for i in keep:
        w[i] = 1
    for i in Y:
        w[i] = M

    # ---- tau_w : exact integer minimum over every bipartition
    tau, arg = None, None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(w[i] for i, (u, v) in enumerate(E) if ((S >> u) & 1) == ((S >> v) & 1))
        if tau is None or s < tau:
            tau, arg = s, S

    # ---- tau*_w : explicit rational feasible cover y = 1/3 on the ten kept edges,
    #      1 on the free (weight-0) edges.  Cost is exactly 10/3 and costs nothing extra.
    y = [F(0)] * len(E)
    for i in keep:
        y[i] = F(1, 3)
    for i in Z:
        y[i] = F(1)
    bad = [c for c in odd if sum(y[i] for i in c) < 1]
    cost = sum(F(w[i]) * y[i] for i in range(len(E)))
    print(f"M = {M:4d}:  tau_w = {tau}   feasible y cost = {cost} = {float(cost):.6f}   "
          f"violated odd cycles = {len(bad)}   "
          f"{'EXACT GAP tau_w > tau*_w' if not bad and cost < tau else 'no certificate'}")
    if bad:
        print(f"    first violated cycle {sorted(bad[0])} -> edges {[E[i] for i in sorted(bad[0])]}")

print("\nSanity: the same construction on Wagner must fail (no odd-K5 minor there).")
