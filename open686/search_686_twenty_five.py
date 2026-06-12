import math
from math import prod

# Erdos686 twenty_five search
# Exact integer arithmetic only. For fixed k,n, P_k(m) is strictly increasing, so m is located by binary search.


def P(k, x):
    r = 1
    for i in range(1, k + 1):
        r *= x + i
    return r


def find_m_for(k, n):
    target = 25 * P(k, n)
    lo = n + k
    plo = P(k, lo)
    if plo > target:
        return None
    if plo == target:
        return lo
    # asymptotic m ~= 25^(1/k) n; use it only as a starting upper bound, then double exactly.
    alpha = math.exp(math.log(25.0) / k)
    guess = int(alpha * (n + 1) + k + 8)
    hi = max(lo + 1, guess)
    while P(k, hi) < target:
        hi = hi * 2 + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        val = P(k, mid)
        if val < target:
            lo = mid
        else:
            hi = mid
    return hi if P(k, hi) == target else None


def pell_k2():
    # X^2 - 25Y^2 = -24 => (X - 5Y)(X + 5Y) = -24.
    sols = []
    for a in range(-24, 25):
        if a == 0 or (-24) % a != 0:
            continue
        b = -24 // a
        # a = X - 5Y, b = X + 5Y
        if (a + b) % 2 != 0:
            continue
        if (b - a) % 10 != 0:
            continue
        X = (a + b) // 2
        Y = (b - a) // 10
        if X > 0 and Y > 0 and X % 2 == 1 and Y % 2 == 1:
            if X * X - 25 * Y * Y == -24:
                m = (X - 3) // 2
                n = (Y - 3) // 2
                if n >= 0 and m >= n + 2 and (m + 1) * (m + 2) == 25 * (n + 1) * (n + 2):
                    sols.append((n, m, X, Y, a, b))
    return sols

print('Pell k=2 solutions:', pell_k2(), flush=True)

# Initial exact scan as requested. Split into phases so progress is visible and the run can be extended.
# A simple lower-bound test P_k(n+k) <= 25 P_k(n) filters impossible n before binary search.

def scan(k_max, n_max, log_every_k=1):
    checked = 0
    filtered = 0
    for k in range(2, k_max + 1):
        hits_k = 0
        for n in range(0, n_max + 1):
            checked += 1
            # exact lower-bound filter; if even m=n+k is too large, no admissible m exists.
            if P(k, n + k) > 25 * P(k, n):
                filtered += 1
                continue
            m = find_m_for(k, n)
            if m is not None:
                print('HIT', k, n, m, P(k, m), 25 * P(k, n), flush=True)
                return k, n, m
        if k % log_every_k == 0:
            print(f'completed k={k} up to n={n_max} checked={checked} filtered={filtered}', flush=True)
    return None

# First do the exact initial range but with adaptive product calls. This may still be substantial.
hit = scan(100, 1_000_000, 1)
print('initial_hit', hit, flush=True)

if hit is None:
    # Deeper exact scan for k=3..30 as requested, larger n, still binary search.
    hit = scan(30, 10_000_000, 1)
    print('deep_3_30_hit', hit, flush=True)
