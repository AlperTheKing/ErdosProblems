from math import gcd, isqrt, lcm, prod

d = 105_525
base = [(0,2),(0,3),(1,4),(5,6),(7,12)]
children = [(d*r, d*q) for r,q in base]

# Exact full-common-period check of equality with 0 (mod d).
P = lcm(*(m for a,m in children))
assert P == 1_266_300 == 12*d
for x in range(P):
    in_parent = (x % d == 0)
    in_children = any((x-a) % m == 0 for a,m in children)
    assert in_parent == in_children

# Distinct child half-moduli, and avoidance of the prescribed finite set [1,138600].
E = [m for a,m in children]
assert len(E) == len(set(E))
assert min(E) > 138_600

# Exact integer primality test (no floating point, no probable-prime test).
def is_prime_exact(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    k = 3
    while k <= isqrt(n):
        if n % k == 0:
            return False
        k += 2
    return True

assert is_prime_exact(2*d+1)
assert all(is_prime_exact(2*e+1) for e in E)

# Pocklington certificates, included as an independent compact check.
factorizations = {
    211_051: {2:1,3:2,5:2,7:1,67:1},
    422_101: {2:2,3:2,5:2,7:1,67:1},
    633_151: {2:1,3:3,5:2,7:1,67:1},
    844_201: {2:3,3:2,5:2,7:1,67:1},
  1_266_301: {2:2,3:3,5:2,7:1,67:1},
  2_532_601: {2:3,3:3,5:2,7:1,67:1},
}
witnesses = {
    211_051: 3,
    422_101: 23,
    633_151: 12,
    844_201: 13,
  1_266_301: 6,
  2_532_601: 19,
}
assert is_prime_exact(67)
for N, fac in factorizations.items():
    assert prod(q**a for q,a in fac.items()) == N-1
    w = witnesses[N]
    assert pow(w,N-1,N) == 1
    for q in fac:
        assert gcd(pow(w,(N-1)//q,N)-1,N) == 1

print('verified', children, P)

