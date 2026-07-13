"""Gate (40) membership-recursion census — INDEPENDENT algorithm, cross-validates
the truncated-closure generator. DP ascending: n in G iff n in {2,3} or n+1 = a*b
with a != b, a,b >= 2, both already in G (well-founded: a,b <= (n+1)/2 < n for n >= 3).
Divisors of n+1 enumerated from an SPF sieve factorization (no trial division).
Cross-check: exact set equality (count + SHA-256 of the sorted membership bitmap)
against the worklist closure at the same B.
"""
import bisect, sys, hashlib

B = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6

# --- algorithm 1: membership recursion DP with SPF sieve ---
N = B + 2
spf = list(range(N))
i = 2
while i * i < N:
    if spf[i] == i:
        for j in range(i * i, N, i):
            if spf[j] == j:
                spf[j] = i
    i += 1

def divisors(m):
    ds = [1]
    while m > 1:
        p = spf[m]; e = 0
        while m % p == 0:
            m //= p; e += 1
        ds = [d * p**k for d in ds for k in range(e + 1)]
    return ds

g = bytearray(B + 1)
g[2] = g[3] = 1
for n in range(4, B + 1):
    m = n + 1
    for a in divisors(m):
        if a < 2: continue
        b = m // a
        if a != b and b >= 2 and g[a] and g[b]:
            g[n] = 1
            break

cnt_dp = sum(g)
sha_dp = hashlib.sha256(bytes(g)).hexdigest()

# --- algorithm 2: proven truncated worklist closure ---
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

g2 = bytearray(B + 1)
for x in inset: g2[x] = 1
cnt_cl = sum(g2)
sha_cl = hashlib.sha256(bytes(g2)).hexdigest()

print(f"B={B}")
print(f"membership-recursion DP: |G|={cnt_dp}  bitmap SHA-256={sha_dp}")
print(f"truncated closure:       |G|={cnt_cl}  bitmap SHA-256={sha_cl}")
print("EXACT MATCH" if sha_dp == sha_cl else "MISMATCH — first diffs: " +
      str([n for n in range(2, B + 1) if g[n] != g2[n]][:10]))
d = 10
while d <= B:
    print(f"  A({d}) = {sum(g[:d+1])}")
    d *= 10
print("script SHA-256:", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
