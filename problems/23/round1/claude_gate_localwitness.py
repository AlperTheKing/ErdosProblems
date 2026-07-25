"""ROOT-AGENT GATE: can LOCAL switching conditions alone certify bip <= N^2/25?

Round-1 family F2 exhibited a witness family and claimed the answer is NO. No verifier ran on it.
The witness: W_b = the blow-up of the path P4 with part sizes (b+1, b, b, b+1), together with the
particular bipartition  A = part1 u part4,  B = part2 u part3.

Under that bipartition the only monochromatic edges are those between parts 2 and 3, so
|M| = b^2, while N = 4b+2. For b >= 3 this gives 25|M| = 25b^2 > (4b+2)^2 = N^2, i.e. the cut sits
ABOVE the conjectured bound. The graph itself is bipartite (P4 is), so bip(W_b) = 0 and the
conjecture is of course not violated -- the point is entirely about what LOCAL conditions can see.

What is verified here, exactly:
  1. the arithmetic: N = 4b+2, |M| = b^2, and 25|M| > N^2 for every b >= 3;
  2. bip(W_b) = 0 (the graph is bipartite), so this cut is very far from maximum;
  3. THE POINT: the smallest k for which some switching set S with |S| = k has sigma(S) < 0.
     If that k grows like a constant fraction of N, then every local switching family whose sets
     are smaller than that fraction is satisfied by a cut carrying |M| > N^2/25, and therefore no
     such family can certify the conjecture.
sigma(S) = |edges of B leaving S| - |edges of M leaving S|; a maximum cut has sigma(S) >= 0 for all S.
"""

from itertools import combinations
from fractions import Fraction


def build_W(b):
    """P4 blow-up with parts (b+1, b, b, b+1); returns n, adj bitmasks, and the cut mask."""
    sizes = [b + 1, b, b, b + 1]
    start, acc = [], 0
    for s in sizes:
        start.append(acc); acc += s
    n = acc
    adj = [0] * n
    for k in range(3):                       # path edges 1-2, 2-3, 3-4
        for u in range(start[k], start[k] + sizes[k]):
            for v in range(start[k + 1], start[k + 1] + sizes[k + 1]):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    # cut: parts 1 and 4 on one side
    S = 0
    for u in range(start[0], start[0] + sizes[0]):
        S |= 1 << u
    for u in range(start[3], start[3] + sizes[3]):
        S |= 1 << u
    return n, adj, S, sizes, start


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def maxcut_exhaustive(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best = cut
    return best


def sigma_of(n, adj, cut, S):
    """sigma(S) for the fixed bipartition `cut` (bitmask of one side)"""
    sb = sm = 0
    for u in range(n):
        if not ((S >> u) & 1):
            continue
        out = adj[u] & ~S & ((1 << n) - 1)
        for v in range(n):
            if (out >> v) & 1:
                same = ((cut >> u) & 1) == ((cut >> v) & 1)
                if same:
                    sm += 1
                else:
                    sb += 1
    return sb - sm


print("=" * 78)
print("W_b = P4[b+1, b, b, b+1] with the cut  part1+part4 | part2+part3")
print("=" * 78)
print(f"{'b':>2} {'N':>4} {'|E|':>5} {'|M|':>5} {'N^2/25':>8} {'25|M|>N^2':>10} "
      f"{'bip(W_b)':>9} {'min |S| with sigma(S)<0':>24} {'as a fraction of N':>19}")
for b in range(2, 7):
    n, adj, cut, sizes, start = build_W(b)
    E = edges_of(n, adj)
    M = [(u, v) for (u, v) in E if ((cut >> u) & 1) == ((cut >> v) & 1)]
    violates = 25 * len(M) > n * n
    bip = len(E) - maxcut_exhaustive(n, adj) if n <= 24 else None
    # smallest k with some S of size k having sigma(S) < 0
    kmin = None
    for k in range(1, n + 1):
        found = False
        for T in combinations(range(n), k):
            S = 0
            for t in T:
                S |= 1 << t
            if sigma_of(n, adj, cut, S) < 0:
                found = True
                break
        if found:
            kmin = k
            break
        if k >= 8:            # keep the exhaustive search affordable
            kmin = f">{k}"
            break
    frac = (f"{kmin/n:.3f}" if isinstance(kmin, int) else f"{kmin}/{n}")
    print(f"{b:>2} {n:>4} {len(E):>5} {len(M):>5} {n*n/25:>8.2f} {str(violates):>10} "
          f"{str(bip):>9} {str(kmin):>24} {frac:>19}")

print()
print("=" * 78)
print("Reading of the table")
print("=" * 78)
print("""   For every b >= 3 the displayed cut carries 25|M| > N^2, i.e. it sits strictly above the
   conjectured bound, while bip(W_b) = 0 because the graph is bipartite. Whatever the exact
   threshold size turns out to be, the conclusion for the campaign is the same and is what
   matters: a cut that is NOT maximum can satisfy sigma(S) >= 0 on every small switching set
   while carrying far more than N^2/25 monochromatic edges. Local switch conditions therefore
   cannot, by themselves, force |M| <= N^2/25 -- they do not even distinguish this cut from a
   maximum one until the switching set is large.

   This bounds MY OWN general switch-star inequality too (section 3i): its switching sets are
   {v} u T with T inside the crossing star, hence of size at most 1 + d_B(v). On any graph where
   that is below the threshold, the whole family is satisfied by a cut with |M| > N^2/25, so no
   aggregation of switch-star inequalities alone can certify the conjecture. The family remains
   useful as a source of local structure (it forces the cut-tight vertices to induce a matching),
   but it is NOT a route to the bound on its own.""")
