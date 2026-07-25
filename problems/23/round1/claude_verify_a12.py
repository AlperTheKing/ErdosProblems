"""Independent verification (own graph6 decoder, own maxcut) of the N=12 finding.

Checks, all in exact integer arithmetic:
  1. the claimed extremal graph is triangle-free, has the stated edge count,
     and bip = 5 by exhaustive maxcut;
  2. the best C5 blow-up on 12 vertices has bip = 4, i.e. the extremal graph
     at N = 12 is NOT a C5 blow-up;
  3. the vertex-deletion induction step fails on C5[n]:
     bip(C5[n]) - bip(C5[n] - v) = n, against a budget of (2N-1)/25 = (10n-1)/25.
"""

from itertools import combinations, product


def g6_decode(s):
    """graph6 -> (n, set of edges). Independent of the C++ decoder."""
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for byte in b[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    edges = set()
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.add((i, j))
            idx += 1
    return n, edges


def is_triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    for i, j in edges:
        if adj[i] & adj[j]:
            return False
    return True


def maxcut_bruteforce(n, edges):
    """Exhaustive over all 2^(n-1) bipartitions, exact."""
    elist = list(edges)
    best = 0
    for mask in range(1 << (n - 1)):
        S = mask << 1 | 1  # vertex 0 always in S
        c = 0
        for i, j in elist:
            if ((S >> i) & 1) != ((S >> j) & 1):
                c += 1
        if c > best:
            best = c
    return best


def bip(n, edges):
    return len(edges) - maxcut_bruteforce(n, edges)


def blowup_C5(parts):
    """C5 blow-up with the given five part sizes (cyclically adjacent parts joined)."""
    n = sum(parts)
    start = []
    acc = 0
    for p in parts:
        start.append(acc)
        acc += p
    edges = set()
    for k in range(5):
        l = (k + 1) % 5
        for a in range(start[k], start[k] + parts[k]):
            for b in range(start[l], start[l] + parts[l]):
                edges.add((min(a, b), max(a, b)))
    return n, edges


print("=" * 62)
print("1. claimed extremal graph at N=12")
G6 = "K?ABBBwerwBw"
n, E = g6_decode(G6)
tf = is_triangle_free(n, E)
mc = maxcut_bruteforce(n, E)
print(f"   g6={G6}  n={n}  |E|={len(E)}  triangle-free={tf}  maxcut={mc}  bip={len(E)-mc}")
assert n == 12 and tf, "decode/triangle-free check failed"
a12 = len(E) - mc
print(f"   bound N^2/25 = 144/25 = 5.76  ->  bip={a12} <= 5.76 : {a12 * 25 <= 144}")

print("=" * 62)
print("2. best C5 blow-up on 12 vertices (exhaustive over part vectors)")
best_bu, best_parts = -1, None
seen = set()
for parts in product(range(1, 9), repeat=5):
    if sum(parts) != 12:
        continue
    # canonical up to rotation/reflection, to avoid redundant work
    rots = [tuple(parts[i:] + parts[:i]) for i in range(5)]
    rots += [tuple(reversed(r)) for r in rots]
    canon = min(rots)
    if canon in seen:
        continue
    seen.add(canon)
    nn, EE = blowup_C5(list(parts))
    b = bip(nn, EE)
    if b > best_bu:
        best_bu, best_parts = b, parts
print(f"   distinct part vectors: {len(seen)}")
print(f"   best blow-up bip = {best_bu}  at parts {best_parts}")
print(f"   a(12) from the census = {a12}")
print(f"   VERDICT: extremal graph at N=12 is a C5 blow-up? {a12 == best_bu}")

print("=" * 62)
print("3. vertex-deletion induction step on C5[n]")
print("   n | N  | bip(C5[n]) | max_v bip(C5[n]-v) | drop | budget (2N-1)/25 | step holds?")
for k in (1, 2, 3):
    nn, EE = blowup_C5([k] * 5)
    N = nn
    b_full = bip(nn, EE)
    # delete one vertex (all vertices equivalent by symmetry, but check all anyway)
    best_after = -1
    for v in range(nn):
        keep = [u for u in range(nn) if u != v]
        relab = {u: i for i, u in enumerate(keep)}
        E2 = {(min(relab[i], relab[j]), max(relab[i], relab[j]))
              for (i, j) in EE if i != v and j != v}
        bb = bip(nn - 1, E2)
        best_after = max(best_after, bb)
    drop = b_full - best_after
    budget_num, budget_den = 2 * N - 1, 25
    holds = drop * budget_den <= budget_num
    print(f"   {k} | {N:2d} |     {b_full:2d}     |         {best_after:2d}         |  {drop:2d}  |"
          f"      {budget_num}/{budget_den} = {budget_num/budget_den:.2f}      | {holds}")
print("   => the naive step bip(G) - bip(G-v) <= (2N-1)/25 FAILS on the extremal family itself.")
print("=" * 62)
