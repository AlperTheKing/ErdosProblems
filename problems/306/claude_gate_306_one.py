"""ROOT-AGENT GATE (Claude): independently verify the representation of 1 found by the CSP search.

The search (tools/claude_erdos306_csp.py) returned a 58-term candidate for the Erdos 306 base case:
1 as a sum of distinct 1/(pq) with p, q distinct primes. A certificate is worth exactly its
verification, so this re-checks it from scratch, in exact rational arithmetic, with its own
factorisation routine -- nothing imported from the search.

Checks:
  1. every denominator is a product of exactly TWO DISTINCT primes (omega = Omega = 2, squarefree);
  2. all denominators are distinct;
  3. all are > 1 and the list is sortable into the strictly increasing form the statement requires;
  4. the sum of reciprocals is EXACTLY 1 as a rational.
"""
from fractions import Fraction as F

DEN = [6, 10, 14, 22, 26, 34, 38, 46, 58, 62, 15, 21, 33, 39, 51, 57, 69, 93, 111,
       35, 55, 65, 85, 95, 115, 145, 155, 77, 91, 119, 133, 161, 203, 217, 259,
       143, 187, 209, 253, 341, 451, 221, 247, 299, 403, 481, 533, 629, 437, 551,
       589, 779, 713, 851, 943, 899, 1147, 1517]


def factor(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


print(f"candidate: {len(DEN)} denominators")

bad = []
for n in DEN:
    f = factor(n)
    if len(f) != 2 or any(e != 1 for e in f.values()):
        bad.append((n, f))
print(f"(1) every denominator is a product of two DISTINCT primes: {not bad}"
      + (f"   offenders {bad[:3]}" if bad else ""))

dist = len(set(DEN)) == len(DEN)
print(f"(2) all denominators distinct: {dist}   ({len(set(DEN))} unique of {len(DEN)})")

srt = sorted(DEN)
print(f"(3) all > 1 and strictly increasing when sorted: "
      f"{all(x > 1 for x in DEN) and all(srt[i] < srt[i+1] for i in range(len(srt)-1))}")

total = sum(F(1, n) for n in DEN)
print(f"(4) sum of reciprocals = {total}   equals 1 exactly: {total == 1}")

primes = sorted({p for n in DEN for p in factor(n)})
print(f"\nprimes used: {primes}")
print(f"largest denominator: {max(DEN)},  largest prime: {max(primes)}")

# the local congruence predicted by the reduction, re-checked here
print("\nlocal congruence at each prime (sum of inverse neighbours == 0 mod p):")
adj = {p: [] for p in primes}
for n in DEN:
    p, q = sorted(factor(n))
    adj[p].append(q)
    adj[q].append(p)
allok = True
for p in primes:
    s = sum(pow(q, -1, p) for q in adj[p]) % p
    if s != 0:
        allok = False
    print(f"   p = {p:3d}: degree {len(adj[p]):2d}, sum of inverses mod p = {s}")
print(f"congruence holds at every prime: {allok}")

print(f"\nVERDICT: 1 IS representable as a sum of distinct 1/(pq): "
      f"{(not bad) and dist and total == 1}")
