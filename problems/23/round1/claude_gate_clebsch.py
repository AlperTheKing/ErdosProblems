"""ROOT-AGENT GATE: exact bip of the Clebsch graph, by EXHAUSTIVE maximum cut.

Second of the unverified strongly-regular claims from the quota-killed Round-1 workflows
(F5/F8 claimed bip(Clebsch) = 8). The Clebsch graph is srg(16, 5, 0, 2): 16 vertices, 5-regular,
triangle-free, 40 edges, spectrum 5, 1, -3. At n = 16 the maximum cut can be computed by brute
force over all 2^15 bipartitions, so no heuristic and no spectral bound is needed -- this is a
complete exact determination.

The spectral bound is computed anyway, as a cross-check of the brute force:
maxcut <= (n/4)(d - lambda_min) = (16/4)(5+3) = 32, so bip >= 40 - 32 = 8.

Construction: vertices are the 16 elements of GF(2)^4; u ~ v iff u + v has weight 1 or 4
(the "folded 5-cube"); this is the standard halved/folded description of the Clebsch graph.
"""

from fractions import Fraction


def clebsch():
    n = 16
    adj = [0] * n
    for u in range(16):
        for v in range(u + 1, 16):
            w = bin(u ^ v).count("1")
            if w == 1 or w == 4:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return n, adj


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def is_triangle_free(n, adj):
    return all(not (adj[u] & adj[v])
               for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1)


def maxcut_exhaustive(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best, bestS = cut, S
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best, bestS = cut, S
    return best, bestS


n, adj = clebsch()
E = edges_of(n, adj)
degs = sorted(bin(a).count("1") for a in adj)
print("=" * 72)
print("Clebsch graph: construction checks")
print("=" * 72)
print(f"   vertices {n} (expect 16), edges {len(E)} (expect 40), "
      f"degrees {degs[0]}..{degs[-1]} (expect 5,5)")
print(f"   triangle-free : {is_triangle_free(n, adj)}")

# exact SRG identity for srg(16,5,0,2): A^2 = 5I + 0*A + 2(J - I - A) = 3I - 2A + 2J
ok = True
for u in range(n):
    for v in range(n):
        a2 = bin(adj[u] & adj[v]).count("1")
        a_uv = (adj[u] >> v) & 1
        want = (3 if u == v else 0) - 2 * a_uv + 2
        if a2 != want:
            ok = False
print(f"   SRG identity A^2 + 2A - 3I = 2J holds exactly: {ok}")
print("   => spectrum 5 and the roots of x^2 + 2x - 3 = 0, i.e. 1 and -3; lambda_min = -3")

bound = Fraction(n, 4) * (5 + 3)
print(f"   spectral bound: maxcut <= {bound}, so bip >= {len(E)} - {bound} = {len(E) - bound}")

mc, S = maxcut_exhaustive(n, adj)
recount = sum(1 for (u, v) in E if ((S >> u) & 1) != ((S >> v) & 1))
print()
print("=" * 72)
print("EXHAUSTIVE maximum cut over all 2^15 bipartitions")
print("=" * 72)
print(f"   maxcut = {mc}   (independent recount of the optimal cut over the edge list: {recount})")
print(f"   parts  = {bin(S).count('1')} / {n - bin(S).count('1')}")
print(f"   bip(Clebsch) = {len(E)} - {mc} = {len(E) - mc}")
print(f"   claim bip = 8 : {'CONFIRMED' if len(E) - mc == 8 else 'REFUTED'}")
print(f"   spectral lower bound matched exactly: {len(E) - mc == len(E) - bound}")
print(f"   ratio bip/N^2 = {Fraction(len(E) - mc, n * n)} = {float(Fraction(len(E)-mc, n*n)):.6f}  vs 1/25 = 0.040000")
print("=" * 72)
