"""ROOT-AGENT GATE (Claude): does the PETERSEN graph carry an odd-K5 minor?

This decides a RETRACTION of my own. R3-C22 and the current GOAL accepted base (7) both assert that
what is proved unconditionally is "every triangle-free G with no odd-K5 minor has bip <= N^2/25,
covering C5, all C5 blow-ups, planar triangle-free, Wagner and PETERSEN". Round 9 says Petersen is in
the wrong list -- it HAS an odd-K5 minor -- and that round7/audit_Q5.md line 140 already flagged it.

Claimed minor: switch at the inner 5-set B. Spokes a_i b_i have exactly one endpoint switched, so
they flip odd -> even and can be contracted; outer edges a_i a_{i+1} have neither endpoint switched
and inner edges b_i b_{i+2} have both, so all ten stay ODD. Contracting the spokes, the branch sets
{a_i, b_i} are joined by outer edges for the pairs (i,i+1) and by inner edges for the pairs (i,i+2)
-- all ten pairs of K5, all odd.

Claimed gap weight: w = 1 on the ten outer/inner edges, w = 5 on the five spokes, giving
tau_w = 4 > 10/3 = tau*_w, a gap of exactly 6/5. The cover y = 1/3 on the ten non-spoke edges is
feasible because every odd cycle of Petersen uses an EVEN number of spokes and so carries at least 3
non-spoke edges.

Both are checked here from my own construction of Petersen. If they hold, the Petersen ceiling still
STANDS -- but on the round-7 exact SOS certificate Q4_cert_gpetersen_d1.pkl, NOT on Guenin -- and my
consequence statement must be retracted.
"""
from fractions import Fraction as F
from itertools import combinations


def petersen():
    """outer C5 a_i = i, inner pentagram b_i = 5+i, spokes a_i b_i"""
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, 5 + i) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner, outer, spokes, inner


n, E, outer, spokes, inner = petersen()
E = [tuple(sorted(e)) for e in E]
outer = [tuple(sorted(e)) for e in outer]
spokes = [tuple(sorted(e)) for e in spokes]
inner = [tuple(sorted(e)) for e in inner]
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
print(f"Petersen: |V| = {n}, |E| = {len(E)}, 3-regular = {all(len(a) == 3 for a in A)}, "
      f"triangle-free = {not any(A[u] & A[v] for u, v in E)}")

# ---- 1. the signed minor, done the same way as my And(4) gate
print("\n=== 1. the claimed odd-K5 minor ===")
branch = [{i, 5 + i} for i in range(5)]
switch = set(range(5, 10))                     # switch at the inner 5-set B


def sign_after(e):
    """all edges start ODD (sign 1); switching flips an edge iff exactly one endpoint is switched"""
    u, v = e
    return 1 ^ ((u in switch) ^ (v in switch))


for tag, grp in (("outer", outer), ("spokes", spokes), ("inner", inner)):
    print(f"  {tag:7s}: signs after switching = {sorted({sign_after(e) for e in grp})} "
          f"({'even, contractible' if all(sign_after(e) == 0 for e in grp) else 'odd, kept'})")

ok = True
pairs = {}
for i in range(5):
    for j in range(i + 1, 5):
        found = [e for e in E
                 if ((e[0] in branch[i] and e[1] in branch[j])
                     or (e[0] in branch[j] and e[1] in branch[i])) and sign_after(e) == 1]
        pairs[(i, j)] = found
        if not found:
            ok = False
for (i, j), f in sorted(pairs.items()):
    print(f"  pair ({i},{j}): odd connecting edges {f}")
print(f"  every branch set is connected and bipartite: "
      f"{all(len(b) == 2 and tuple(sorted(b)) in E for b in branch)}")
print(f"  VERDICT: Petersen HAS an odd-K5 minor: {ok}")

# ---- 2. the explicit gap weight
print("\n=== 2. the explicit finite gap weight ===")
w = {e: (5 if e in spokes else 1) for e in E}
tau = None
for m in range(1 << (n - 1)):
    S = (m << 1) | 1
    s = sum(w[e] for e in E if ((S >> e[0]) & 1) == ((S >> e[1]) & 1))
    if tau is None or s < tau:
        tau = s
odd = set()
for s0 in range(n):
    def dfs(u, seen, el):
        for v in sorted(A[u]):
            if v == s0 and len(seen) >= 3 and len(seen) % 2 == 1:
                odd.add(frozenset(el + [tuple(sorted((u, v)))]))
            elif v > s0 and v not in seen:
                dfs(v, seen | {v}, el + [tuple(sorted((u, v)))])
    dfs(s0, {s0}, [])
odd = sorted(odd, key=lambda c: (len(c), sorted(c)))
bylen = {}
for c in odd:
    bylen[len(c)] = bylen.get(len(c), 0) + 1
print(f"  odd cycles of Petersen: {len(odd)} by length {dict(sorted(bylen.items()))}")
evensp = all(sum(1 for e in c if e in spokes) % 2 == 0 for c in odd)
minnon = min(sum(1 for e in c if e not in spokes) for c in odd)
print(f"  every odd cycle uses an EVEN number of spokes: {evensp};  "
      f"min non-spoke edges on an odd cycle = {minnon}")
y = {e: (F(0) if e in spokes else F(1, 3)) for e in E}
bad = [c for c in odd if sum(y[e] for e in c) < 1]
cost = sum(F(w[e]) * y[e] for e in E)
print(f"  cover y = 1/3 on the ten non-spoke edges: violated odd cycles = {len(bad)}, "
      f"cost = {cost} = {float(cost):.5f}")
print(f"  tau_w = {tau} (exact integer min over all 512 cuts)")
print(f"  VERDICT: tau_w > tau*_w: {tau > cost}  gap = {F(tau) / cost} "
      f"-> Petersen is NOT weakly bipartite")

# ---- 3. so what still holds?
print("\n=== 3. consequence ===")
print("  Guenin's hypothesis FAILS on Petersen, so Theorem A + Guenin does NOT cover it.")
print("  The Petersen ceiling max_x psi = 1/25 still stands, but on the round-7 exact rational")
print("  Positivstellensatz certificate round7/Q4_cert_gpetersen_d1.pkl, which is independent of")
print("  Guenin. My R3-C22 consequence sentence and GOAL accepted base (7) must drop Petersen.")
