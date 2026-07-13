"""Route R-A empirical gate: for n ≡ 8 (mod 9), n <= B, is n+1 = a*b with a != b,
a,b in G (any residue — G1 forces factors of 9m to include multiples of 3 anyway
when both are in G? NO: a*b ≡ 0 mod 9 with a,b in G ⊆ {0,2 mod 3} allows a≡0,b≡0
(both mult of 3) OR one ≡ 0 mod 9 times ≡ 2... 2 mod 3 * 0 mod 3 = 0 mod 3 but
0 mod 9 needs the 0-mod-3 factor divisible by 9 or both by 3. We test the honest
predicate: exists factorization with BOTH in G, a != b).
Also reports the same for n ≡ 5 (mod 9) (n+1 ≡ 6 mod 9) and the exceptional lists.
Exact; G computed by the proven G0 truncated closure.
"""
import bisect, sys, hashlib

B = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
pool = [2, 3]; inset = {2, 3}; work = [2, 3]
while work:
    x = work.pop()
    lim = (B + 1) // x
    idx = bisect.bisect_right(pool, lim)
    for y in pool[:idx]:
        if y == x: continue
        z = x * y - 1
        if z <= B and z not in inset:
            inset.add(z); bisect.insort(pool, z); work.append(z)

def covered(n):
    """n+1 = a*b, a<b (a != b), both in G. a ranges over divisors <= sqrt(n+1)."""
    m = n + 1
    a = 2
    while a * a <= m:
        if m % a == 0:
            b = m // a
            if a != b and a in inset and b in inset:
                return True
        a += 1
    return False

for cls in (8, 5):
    exc = []
    total = 0
    n = cls
    while n <= B:
        if n >= 2:
            total += 1
            if not covered(n):
                exc.append(n)
        n += 9
    print(f"class {cls} mod 9, n <= {B}: total {total}, uncovered {len(exc)} "
          f"({len(exc)/total:.4f})")
    print(f"  largest uncovered: {exc[-1] if exc else None}")
    print(f"  uncovered <= 2000: {[e for e in exc if e <= 2000]}")
    per = {}
    d = 10
    while d <= B:
        lo = d // 10
        per[d] = sum(1 for e in exc if lo < e <= d)
        d *= 10
    print(f"  uncovered per decade: {per}")
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
