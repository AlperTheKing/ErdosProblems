"""Erdos #23, family F4: the k-vertex deletion step on the extremal family C5[n].

Induced subgraphs of C5[n] on 5n-k vertices are exactly C5[a] with 0<=a_i<=n and
sum a_i = 5n-k, and bip(C5[a]) = min_i a_i a_{i+1} (Lemma A).  Hence the cheapest
k-vertex deletion costs
    cost(n,k) = n^2 - max{ min_i (n-d_i)(n-d_{i+1}) : d>=0, sum d_i = k }
and the induction budget for deleting k vertices out of N=5n is
    budget(n,k) = (N^2-(N-k)^2)/25 = k(10n-k)/25.
The step closes iff cost <= budget.  Exact integer / Fraction arithmetic.
"""
from fractions import Fraction
from itertools import product

def value(n, k):
    """max over deficits d>=0, sum d = k, of min_i (n-d_i)(n-d_{i+1}), d_i<=n."""
    best = -1
    for d in product(range(min(k, n)+1), repeat=4):
        s = sum(d)
        if s > k or k - s > n:
            continue
        dd = list(d) + [k - s]
        m = min((n-dd[i])*(n-dd[(i+1) % 5]) for i in range(5))
        if m > best:
            best = m
    return best

def formula(n, k):
    q, r = divmod(k, 5)
    if n - q - 1 < 0:
        return None
    if r == 0:
        return (n-q)**2
    if r in (1, 2):
        return (n-q)*(n-q-1)
    return (n-q-1)**2

bad = []
closes = {}
for n in range(1, 13):
    for k in range(1, 5*n+1):
        v = value(n, k)
        f = formula(n, k)
        if f is not None and v != f:
            bad.append((n, k, v, f))
        cost = n*n - v
        budget = Fraction(k*(10*n-k), 25)
        ok = cost <= budget
        closes.setdefault(n, []).append((k, ok, cost, budget))
print("formula mismatches:", bad)
for n in range(1, 13):
    ks = [k for (k, ok, c, b) in closes[n] if ok]
    print(f"n={n:2d} N={5*n:3d}: k with cost<=budget: {ks}"
          f"   (all multiples of 5? {all(k % 5 == 0 for k in ks)};"
          f" all multiples of 5 present? {sorted(ks)==list(range(5,5*n+1,5))})")
# equality check for k=5s
for n in range(1, 13):
    for s in range(1, n+1):
        k = 5*s
        assert n*n - value(n, k) == Fraction(k*(10*n-k), 25) == 2*n*s - s*s
print("k=5s: cost == budget == 2ns-s^2 verified for n<=12, all s<=n")
