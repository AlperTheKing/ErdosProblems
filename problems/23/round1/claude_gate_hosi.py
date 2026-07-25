"""ROOT-AGENT GATE: exact bip of the Hoffman-Singleton graph.

Round-1 families F5 and F8 both claimed bip(Hoffman-Singleton) = 50 (and bip(Higman-Sims) = 350,
bip(Gewirtz) = 84, bip(Clebsch) = 8). No verifier agent ever ran on any of them (session quota),
so all are unaccepted claims. This settles the Hoffman-Singleton one, exactly and in both
directions, with no reliance on those reports.

Strategy. HoSi is srg(50, 7, 0, 1): 50 vertices, 7-regular, triangle-free (lambda = 0), 175 edges,
eigenvalues 7, 2, -3.
  LOWER bound on bip: for a d-regular graph on n vertices the Delorme-Poljak / Hoffman-type bound
  gives maxcut <= (n/4)(d - lambda_min). Verified here from the SRG identity
      A^2 + A - 6I = J
  in EXACT integer matrix arithmetic, which pins the eigenvalues to 7 and the roots of
  x^2 + x - 6 = 0, i.e. 2 and -3, hence lambda_min = -3 and maxcut <= (50/4)(7+3) = 125,
  hence bip >= 175 - 125 = 50.
  UPPER bound on bip: exhibit an explicit bipartition with 125 crossing edges, counted exactly.
Together these give bip = 50 exactly.

Construction (standard): five pentagons P_0..P_4 and five pentagrams Q_0..Q_4, each on vertices
0..4; in P_i join j to j+-1 (mod 5); in Q_k join j to j+-2 (mod 5); join P_i[j] to Q_k[i*k + j mod 5].
"""

import random
from fractions import Fraction


def hoffman_singleton():
    """returns n, adjacency as list of int bitmasks, and an index map for readability"""
    idx = {}
    c = 0
    for i in range(5):
        for j in range(5):
            idx[('P', i, j)] = c; c += 1
    for k in range(5):
        for j in range(5):
            idx[('Q', k, j)] = c; c += 1
    n = c
    adj = [0] * n

    def link(a, b):
        adj[a] |= 1 << b
        adj[b] |= 1 << a

    for i in range(5):
        for j in range(5):
            link(idx[('P', i, j)], idx[('P', i, (j + 1) % 5)])
    for k in range(5):
        for j in range(5):
            link(idx[('Q', k, j)], idx[('Q', k, (j + 2) % 5)])
    for i in range(5):
        for k in range(5):
            for j in range(5):
                link(idx[('P', i, j)], idx[('Q', k, (i * k + j) % 5)])
    return n, adj


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def is_triangle_free(n, adj):
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1 and (adj[u] & adj[v]):
                return False
    return True


def matmul_bool_to_int(n, adj):
    """A^2 as an integer matrix, exactly"""
    A2 = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            A2[u][v] = bin(adj[u] & adj[v]).count("1")
    return A2


def cut_value(adj, S, n):
    c = 0
    for u in range(n):
        if (S >> u) & 1:
            c += bin(adj[u] & ~S & ((1 << n) - 1)).count("1")
    return c


n, adj = hoffman_singleton()
E = edges_of(n, adj)
degs = sorted(bin(a).count("1") for a in adj)

print("=" * 72)
print("Hoffman-Singleton: construction checks")
print("=" * 72)
print(f"   vertices      : {n}                       (expect 50)")
print(f"   edges         : {len(E)}                      (expect 175)")
print(f"   degrees       : min {degs[0]}, max {degs[-1]}          (expect 7, 7)")
print(f"   triangle-free : {is_triangle_free(n, adj)}")

# exact SRG identity A^2 + A - 6I = J, i.e. A^2 = 6I - A + J
A2 = matmul_bool_to_int(n, adj)
ok = True
for u in range(n):
    for v in range(n):
        a_uv = (adj[u] >> v) & 1
        want = (6 if u == v else 0) - a_uv + 1
        if A2[u][v] != want:
            ok = False
print(f"   SRG identity A^2 + A - 6I = J holds exactly: {ok}")
print("   => spectrum is 7 and the roots of x^2 + x - 6 = 0, i.e. 2 and -3; lambda_min = -3")

bound = Fraction(n, 4) * (7 + 3)
print()
print("=" * 72)
print("Lower bound on bip via the regular-graph maximum-cut bound")
print("=" * 72)
print(f"   maxcut <= (n/4)(d - lambda_min) = ({n}/4)(7+3) = {bound}")
print(f"   hence bip >= |E| - {bound} = {len(E)} - {bound} = {len(E) - bound}")

print()
print("=" * 72)
print("Upper bound on bip: search for an explicit cut of size 125, then count it exactly")
print("=" * 72)
rnd = random.Random(20260725)
best = 0
best_S = 0
FULL = (1 << n) - 1
for restart in range(400):
    S = rnd.getrandbits(n)
    improved = True
    while improved:
        improved = False
        order = list(range(n))
        rnd.shuffle(order)
        for v in order:
            inS = (S >> v) & 1
            nb_in = bin(adj[v] & S).count("1")
            nb_out = bin(adj[v] & ~S & FULL).count("1")
            # moving v flips its contribution
            gain = (nb_in - nb_out) if inS else (nb_out - nb_in)
            if gain > 0:
                S ^= (1 << v)
                improved = True
    val = cut_value(adj, S, n)
    if val > best:
        best, best_S = val, S
        if best >= int(bound):
            break

# exact independent recount of the best cut
recount = 0
for (u, v) in E:
    if ((best_S >> u) & 1) != ((best_S >> v) & 1):
        recount += 1
side = bin(best_S).count("1")
print(f"   best cut found      : {best}   (independent recount over the edge list: {recount})")
print(f"   parts               : {side} / {n - side}")
print(f"   bip <= |E| - cut    = {len(E)} - {recount} = {len(E) - recount}")

print()
print("=" * 72)
if recount == int(bound):
    print(f"   RESULT: maxcut(HoSi) = {recount} exactly, bip(HoSi) = {len(E) - recount}")
    print(f"   claim bip = 50 : {'CONFIRMED' if len(E) - recount == 50 else 'REFUTED'}")
else:
    print(f"   RESULT: bound gives bip >= {len(E) - bound}; best explicit cut gives bip <= {len(E) - recount}")
    print(f"   gap not closed by this search (need a cut of {int(bound)}).")
print(f"   ratio bip/N^2 = {Fraction(len(E) - recount, n * n)} = {float(Fraction(len(E)-recount, n*n)):.6f}   vs 1/25 = 0.040000")
print("=" * 72)
