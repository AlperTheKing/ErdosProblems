"""ROOT-AGENT GATE: exact bip of the Higman-Sims graph, built from scratch.

Third of the strongly-regular claims left unverified when the Round-1 verifier agents quota-failed
(F5/F8 asserted bip(Higman-Sims) = 350). This settles it in both directions without relying on
those reports, and without any external graph library: the graph is constructed from the extended
binary Golay code.

Chain:
  1. build the extended binary Golay code [24,12,8] as [I_12 | B] with B the quadratic-residue
     matrix on {inf} u Z_11, and VERIFY it by its weight distribution (1, 759, 2576, 759, 1);
  2. take the 759 octads, keep those containing two fixed coordinates, strip those coordinates:
     this must give 77 blocks of size 6 on 22 points, and it is VERIFIED to be a Steiner system
     S(3,6,22) by checking that every one of the C(22,3) = 1540 triples lies in exactly one block;
  3. build Higman-Sims on 1 + 22 + 77 = 100 vertices: the special vertex joined to all 22 points,
     point p joined to block B iff p in B, blocks joined iff disjoint. VERIFY 22-regular, 1100
     edges, triangle-free, and the strongly-regular identity A^2 + 6A - 16I = 6J entrywise in
     exact integers, which pins the spectrum to 22 and the roots of x^2 + 6x - 16, i.e. 2 and -8;
  4. LOWER bound: maxcut <= (n/4)(d - lambda_min) = (100/4)(22+8) = 750, so bip >= 1100 - 750 = 350;
  5. UPPER bound: exhibit a bipartition with exactly 750 crossing edges, recounted independently.
Together: bip = 350 exactly.
"""

import random
from itertools import combinations
from fractions import Fraction

def golay24():
    """Extended binary Golay code, built as the cyclic [23,12,7] Golay code extended by an
    overall parity bit. g(x) = x^11 + x^9 + x^7 + x^6 + x^5 + x + 1 generates the cyclic code;
    codewords are the 4096 products m(x) g(x) mod (x^23 - 1)."""
    g = 0
    for e in (11, 9, 7, 6, 5, 1, 0):
        g |= 1 << e

    def mulmod(a, b):
        r = 0
        for i in range(12):
            if (a >> i) & 1:
                r ^= b << i
        # reduce mod x^23 - 1: fold bit k>=23 onto bit k-23
        while r >> 23:
            hi = r >> 23
            r = (r & ((1 << 23) - 1)) ^ hi
        return r

    code = []
    for m in range(1 << 12):
        c = mulmod(m, g)
        if bin(c).count("1") % 2:           # overall parity bit at position 23
            c |= 1 << 23
        code.append(c)
    return code


def weight_distribution(code):
    d = {}
    for w in code:
        k = bin(w).count("1")
        d[k] = d.get(k, 0) + 1
    return dict(sorted(d.items()))


print("=" * 74)
print("1. extended binary Golay code")
print("=" * 74)
code = golay24()
wd = weight_distribution(code)
print(f"   codewords: {len(code)}   weight distribution: {wd}")
expected = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
good = (wd == expected)
print(f"   matches the Golay weight distribution: {good}")
assert good, "Golay construction failed"

octads = [w for w in code if bin(w).count("1") == 8]
print(f"   octads: {len(octads)}   (expect 759)")

print()
print("=" * 74)
print("2. contract twice to S(3,6,22)")
print("=" * 74)
P, Q = 22, 23                                   # the two coordinates we fix
both = [w for w in octads if (w >> P) & 1 and (w >> Q) & 1]
blocks = []
for w in both:
    pts = frozenset(i for i in range(22) if (w >> i) & 1)
    blocks.append(pts)
print(f"   blocks: {len(blocks)}   (expect 77)   sizes: {sorted({len(b) for b in blocks})}  (expect [6])")
triple_count = {}
for b in blocks:
    for t in combinations(sorted(b), 3):
        triple_count[t] = triple_count.get(t, 0) + 1
all_triples = list(combinations(range(22), 3))
covered_once = all(triple_count.get(t, 0) == 1 for t in all_triples)
print(f"   every one of the {len(all_triples)} triples lies in exactly one block: {covered_once}")
assert len(blocks) == 77 and covered_once, "S(3,6,22) check failed"

print()
print("=" * 74)
print("3. build Higman-Sims and verify it")
print("=" * 74)
n = 100
adj = [0] * n
SPECIAL = 0
PT = lambda p: 1 + p
BL = lambda b: 23 + b


def link(a, b):
    adj[a] |= 1 << b
    adj[b] |= 1 << a


for p in range(22):
    link(SPECIAL, PT(p))
for bi, b in enumerate(blocks):
    for p in b:
        link(PT(p), BL(bi))
for i in range(77):
    for j in range(i + 1, 77):
        if not (blocks[i] & blocks[j]):
            link(BL(i), BL(j))

degs = sorted(bin(a).count("1") for a in adj)
E = [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]
tri_free = all(not (adj[u] & adj[v]) for (u, v) in E)
print(f"   vertices {n}, edges {len(E)} (expect 1100), degrees {degs[0]}..{degs[-1]} (expect 22,22)")
print(f"   triangle-free: {tri_free}")

ok = True
for u in range(n):
    for v in range(n):
        a2 = bin(adj[u] & adj[v]).count("1")
        a_uv = (adj[u] >> v) & 1
        want = (22 if u == v else 0) + 0 * a_uv + 6 * (1 - (1 if u == v else 0) - a_uv)
        if a2 != want:
            ok = False
print(f"   SRG identity A^2 = 22I + 6(J - I - A) holds exactly: {ok}")
print("   => spectrum 22 and the roots of x^2 + 6x - 16 = 0, i.e. 2 and -8; lambda_min = -8")
assert tri_free and ok and len(E) == 1100 and degs[0] == degs[-1] == 22

bound = Fraction(n, 4) * (22 + 8)
print()
print("=" * 74)
print("4/5. bounds")
print("=" * 74)
print(f"   maxcut <= (n/4)(d - lambda_min) = {bound}   =>   bip >= {len(E)} - {bound} = {len(E) - bound}")

rnd = random.Random(20260725)
FULL = (1 << n) - 1
best, bestS = 0, 0
for restart in range(600):
    S = rnd.getrandbits(n)
    improved = True
    while improved:
        improved = False
        order = list(range(n))
        rnd.shuffle(order)
        for v in order:
            inS = (S >> v) & 1
            nin = bin(adj[v] & S).count("1")
            nout = bin(adj[v] & ~S & FULL).count("1")
            gain = (nin - nout) if inS else (nout - nin)
            if gain > 0:
                S ^= (1 << v)
                improved = True
    val = sum(1 for (u, v) in E if ((S >> u) & 1) != ((S >> v) & 1))
    if val > best:
        best, bestS = val, S
        if best >= int(bound):
            break

recount = sum(1 for (u, v) in E if ((bestS >> u) & 1) != ((bestS >> v) & 1))
side = bin(bestS).count("1")
print(f"   best cut found {best}, independent recount {recount}, parts {side}/{n - side}")
print(f"   bip <= {len(E)} - {recount} = {len(E) - recount}")

print()
print("=" * 74)
if recount == int(bound):
    b = len(E) - recount
    print(f"   RESULT: maxcut(Higman-Sims) = {recount}, bip = {b}")
    print(f"   claim bip = 350 : {'CONFIRMED' if b == 350 else 'REFUTED'}")
    print(f"   ratio bip/N^2 = {Fraction(b, n*n)} = {float(Fraction(b, n*n)):.6f}  vs 1/25 = 0.040000")
else:
    print(f"   bounds not met: bip >= {len(E) - bound} and bip <= {len(E) - recount}; search fell short")
print("=" * 74)
