"""Erdos 424 — G0 truncated-closure census (Claude's independent bootstrap gate).

G0 LEMMA (proved here, used by the algorithm): for B >= 1, G ∩ [1,B] equals the
fixpoint of the truncated operator T_B(S) = S ∪ {xy-1 : x,y ∈ S, x≠y, xy-1 <= B}
starting from {2,3} ∩ [1,B]. Proof: any z ∈ G ∩ [1,B] has a finite generation
tree; each generating pair (x,y) satisfies xy = z+1 <= B+1 with x,y >= 2, so
x,y <= (B+1)/2 <= B, i.e. every ancestor lies in [1,B]. Hence the whole tree is
inside [1,B] and z is produced by the truncated iteration. Conversely the
truncated iteration only produces elements of G. QED (exact; no approximation).

Algorithm: worklist closure with sorted pool; for new x, scan y ascending while
x*y <= B+1. Exact integers only.
"""
import bisect, sys, hashlib

B = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
pool = [2, 3]
inset = {2, 3}
work = [2, 3]
while work:
    x = work.pop()
    lim = (B + 1) // x
    idx = bisect.bisect_right(pool, lim)
    for y in pool[:idx]:
        if y == x:
            continue
        z = x * y - 1
        if z <= B and z not in inset:
            inset.add(z)
            bisect.insort(pool, z)
            work.append(z)

g = sorted(inset)
print("B =", B)
print("|G cap [1,B]| =", len(g), " density =", len(g) / B)
print("first 25:", g[:25])
for c in (10**3, 10**4, 10**5, B):
    if c <= B:
        k = bisect.bisect_right(g, c)
        print(f"  count<= {c}: {k}  density {k/c:.6f}")
from collections import Counter
for m in (2, 3, 4, 6, 8, 12):
    cnt = Counter(z % m for z in g)
    print(f"mod {m}:", dict(sorted(cnt.items())))
h = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
print("script SHA-256:", h)
