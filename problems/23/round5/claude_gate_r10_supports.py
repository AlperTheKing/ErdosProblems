"""ROOT-AGENT GATE (Claude): Codex's R10 support reduction for the Gamma_11 frontier lemma.

Codex's exact falsifier certificate reports no strict rational counterexample to
`25 * ARCBOUND_Gamma_11(x) <= (sum x)^2` with cleared denominator q <= 50, plus a structural
reduction that is the load-bearing part of the claim:

  * of the 2^11 - 1 = 2047 nonempty supports, 1474 have an ARC containing no monochromatic support
    edge, hence ARCBOUND = 0 and no falsifier;
  * the remaining 573 form 38 orbits under D_22 = Aut(Gamma_11);
  * their 33 INCLUSION-MINIMAL members are exactly the 33 induced C5s of Gamma_11;
  * those 33 pentagons form THREE D_22 orbits, represented by {0,1,4,5,8}, {0,1,4,6,8}, {0,2,4,6,8}.

Consequence: any surviving falsifier must contain one of those three pentagons up to a dihedral
automorphism. That is what makes the remaining search finite and targeted, so I re-derive all of it
from my own construction. Integers only.
"""
from itertools import combinations


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def arc_cuts(n):
    seen = {}
    for s in range(n):
        for L in range(1, n):
            S = frozenset((s + t) % n for t in range(L))
            key = min(tuple(sorted(S)), tuple(sorted(set(range(n)) - S)))
            seen[key] = S
    return [frozenset()] + list(seen.values())


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
arcs = arc_cuts(n)
print(f"Gamma_11: |E| = {len(E)}, arc cuts = {len(arcs)}, nonempty supports = {(1 << n) - 1}")

# ---- 1. supports for which SOME arc has no monochromatic support edge
zero, live = [], []
for m in range(1, 1 << n):
    S = {v for v in range(n) if (m >> v) & 1}
    dead = False
    for T in arcs:
        if not any(u in S and v in S and ((u in T) == (v in T)) for (u, v) in E):
            dead = True
            break
    (zero if dead else live).append(frozenset(S))
print(f"  supports with an arc carrying no monochromatic support edge (ARCBOUND = 0): {len(zero)}"
      f"   [Codex: 1474 -> {'MATCH' if len(zero) == 1474 else 'MISMATCH'}]")
print(f"  surviving supports: {len(live)}   [Codex: 573 -> "
      f"{'MATCH' if len(live) == 573 else 'MISMATCH'}]")

# ---- 2. D_22 orbits
def rot(S, k):
    return frozenset((v + k) % n for v in S)


def ref(S):
    return frozenset((-v) % n for v in S)


def orbit(S):
    out = set()
    for k in range(n):
        out.add(rot(S, k))
        out.add(rot(ref(S), k))
    return frozenset(out)


seen, orbs = set(), []
for S in live:
    if S in seen:
        continue
    o = orbit(S)
    seen |= o
    orbs.append(o)
print(f"  D_22 orbits among the survivors: {len(orbs)}   [Codex: 38 -> "
      f"{'MATCH' if len(orbs) == 38 else 'MISMATCH'}]")

# ---- 3. inclusion-minimal survivors
liveset = set(live)
minimal = [S for S in live if not any(T < S for T in liveset)]
print(f"  inclusion-minimal survivors: {len(minimal)}   [Codex: 33 -> "
      f"{'MATCH' if len(minimal) == 33 else 'MISMATCH'}]")

pent = {frozenset(T) for T in combinations(range(n), 5)
        if all(len(A[v] & set(T)) == 2 for v in T)}
print(f"  induced C5s of Gamma_11: {len(pent)};  minimal survivors == induced C5s: "
      f"{set(minimal) == pent}")

# ---- 4. the three orbits of pentagons
seen, porbs = set(), []
for S in sorted(pent, key=sorted):
    if S in seen:
        continue
    o = orbit(S)
    seen |= o
    porbs.append((sorted(S), len(o)))
print(f"  D_22 orbits of induced C5s: {len(porbs)}   [Codex: 3 -> "
      f"{'MATCH' if len(porbs) == 3 else 'MISMATCH'}]")
for rep, sz in porbs:
    print(f"    representative {rep}, orbit size {sz}")
claimed = [{0, 1, 4, 5, 8}, {0, 1, 4, 6, 8}, {0, 2, 4, 6, 8}]
ok = all(any(frozenset(c) in orbit(frozenset(rep)) for rep, _ in porbs) for c in claimed)
print(f"  Codex's three representatives lie in my three orbits, one each: {ok}")
print(f"  orbit sizes sum to the pentagon count: {sum(s for _, s in porbs) == len(pent)}")
