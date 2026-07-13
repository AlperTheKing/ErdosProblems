# Exact arithmetic for the insertion-chain (amortization) analysis on C5 blow-up prefixes.
# Units: U and budgets in edges; N^2/25 potential. All Fractions/ints.
from fractions import Fraction as F

print("== (a) prefix (t,t,t,t,j): pentagram U = (3t^2+2tj)/5 <= (4t+j)^2/25, equality iff j=t ==")
ok = eq_only_at_j_eq_t = True
for t in range(1, 61):
    for j in range(0, t + 1):
        lhs = 5*(3*t*t + 2*t*j)          # 25 * U_pentagram
        rhs = (4*t + j)**2               # 25 * potential
        assert lhs <= rhs
        assert (lhs == rhs) == (j == t)  # identity rhs-lhs = (t-j)^2
        assert rhs - lhs == (t - j)**2
print("verified t<=60: 25*U_pent = (4t+j)^2 - (t-j)^2  (tight iff balanced)")

print("\n== (b) prefix (j+1,j+1,j,j,j), n=5j+2: pentagram EXCEEDS n^2/25 by exactly 1/25 ==")
for j in range(0, 101):
    U25 = 5*((j+1)*(j+1) + (j+1)*j + j*j + j*j + j*(j+1))  # 25*U_pent = 5*sum n_k n_{k+1}
    n = 5*j + 2
    assert U25 - n*n == 1
print("verified j<=100: 25*U_pent - n^2 = 1  (pentagram alone cannot carry the n^2/25 potential)")

print("\n== (c) same prefix: 2-atom cut embedding U = min_k m_k = j^2 <= n^2/25 with slack (20j+4)/25 ==")
for j in range(0, 101):
    n = 5*j + 2
    assert (5*j+2)**2 - 25*j*j == 20*j + 4
print("verified: cut embedding fits with slack (20j+4)/25 -> embeddings must MORPH (cut <-> pentagram)")

print("\n== (d) cut-only induction dies at rebalancing: step (j+1,j+1,j+1,j+1,j)->(j+1)^5 ==")
for j in range(0, 101):
    dbeta = (j+1)**2 - j*(j+1)           # = j+1
    n_before = 5*j + 4
    budget25 = 2*n_before + 1            # 25 * ((n+1)^2 - n^2)/25
    assert 25*dbeta > budget25           # 25(j+1) > 10j+9  <=> 15j+16 > 0
print("verified j<=100: integral beta jump (j+1) exceeds per-step budget (10j+9)/25 -- lumpiness")

print("\n== (e) balanced-step pentagram insertion is 1/25 under budget ==")
for j in range(1, 101):
    cost25 = 5*(2*j)                     # 25 * (2j/5): degree 2j at w=1/5
    budget25 = 10*j + 1                  # 25 * ((5j+1)^2-(5j)^2)/25
    assert budget25 - cost25 == 1
print("verified: inserting into balanced prefix costs (10j)/25 vs budget (10j+1)/25 -- slack exactly 1/25")

print("\n== (f) And(4)=C11(1,4) winding-4 circulant embedding: exact U ==")
# position of vertex v: angle (2*4*v/11)*pi -> a_v = F(8v,11) mod 2
from fractions import Fraction
def th(a, b):
    d = abs(a - b) % 2
    return min(d, 2 - d)
n = 11
edges = set()
for v in range(n):
    for c in (1, 4):
        edges.add((min(v, (v+c) % n), max(v, (v+c) % n)))
ang = [F(8*v, 11) % 2 for v in range(n)]
U = sum(1 - th(ang[u], ang[v]) for u, v in edges)
print(f"And(4) winding-4: U = {U} ; bound N^2/25 = {F(121,25)} ; U <= bound: {U <= F(121,25)} ; beta = 4 (brute, see verify_all)")
assert U == 4
print("=> the winding embedding certifies beta(And(4)[t]) <= 4t^2 = (100/121) N^2/25 for ALL t, matching brute force")

print("\n== (g) banked amortization closes EXACTLY at full balance ==")
# prefix (t,t,t,t,t-1): 25*U_pent = (5t-1)^2 - 1  (bank = 1/25 under potential)
# completing vertex: cost 2t/5 = 10t/25 vs budget (10t-1)/25 (overdraft 1/25)
# total: U(C5[t]) = t^2 = N^2/25 exactly.
for t in range(1, 201):
    U25_prefix = (5*t - 1)**2 - 1
    assert U25_prefix == 5*(3*t*t + 2*t*(t-1))          # consistency with (a)
    total25 = U25_prefix + 5*(2*t)                       # + 25*(2t/5) insertion at w=1/5
    assert total25 == 25*t*t                             # == (5t)^2 = N^2 exactly
print("verified t<=200: bank(1/25) + overdraft(1/25) cancel; chain lands EXACTLY on N^2/25 (zero slack)")

print("\n== (h) And(4)[t] insertion-cost equilibrium fits budget for all t>=1 ==")
# class-j vertex: neighbors 2t at w=3/11 (steps +-1) and 2t at w=1/11 (steps +-4): cost = 8t/11
# budget (2N-1)/25, N=11t:  8t/11 <= (22t-1)/25  <=>  42t >= 11
for t in range(1, 201):
    assert 25*8*t*11 <= 11*11*(22*t - 1) or True  # (placeholder guard, real check below)
    assert 200*t <= 11*(22*t - 1)
print("verified t<=200: 8t/11 <= (22t-1)/25 -- non-extremal families sit strictly inside the budget")
