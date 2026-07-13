# Exact-rational proof that the Petersen SDP/spectral embedding (all edge cosines = -2/3)
# has GW-uncut mass U_spec = 15*(1 - arccos(-2/3)/pi) STRICTLY > 4 = N^2/25,
# although beta(Petersen) = 3 <= 4.
# Claim chain (all exact):
#   U_spec > 4  <=>  arccos(-2/3) < 11*pi/15  <=>  cos(11pi/15) < -2/3  <=>  cos(4pi/15) > 2/3.
#   c = cos(4pi/15) satisfies cos(5t) = cos(4pi/3) = -1/2 with cos5t = 16c^5-20c^3+5c
#   => p(c) = 0 where p(x) = 32x^5 - 40x^3 + 10x + 1.
#   p(-1/2) = 0, p = (2x+1) q,  q(x) = 16x^4 - 8x^3 - 16x^2 + 8x + 1.
#   Roots of q are exactly {cos(2pi/15), cos(4pi/15), cos(8pi/15), cos(14pi/15)} (4 distinct values,
#   each a root since cos != -1/2 there). Two are negative (args > pi/2); cos(2pi/15) > sqrt(3)/2 > 7/10.
#   q(2/3) > 0 > q(7/10)  =>  q has a root in (2/3, 7/10); the only root not excluded is cos(4pi/15).
#   Hence cos(4pi/15) in (2/3, 7/10)  =>  cos(4pi/15) > 2/3. QED.
from fractions import Fraction as F

def p(x): return 32*x**5 - 40*x**3 + 10*x + 1
def q(x): return 16*x**4 - 8*x**3 - 16*x**2 + 8*x + 1

# exact division check: p(x) == (2x+1) q(x)
import random
random.seed(1)
for _ in range(10):
    x = F(random.randrange(-100, 100), random.randrange(1, 50))
    assert p(x) == (2*x + 1)*q(x)
print("p(x) == (2x+1) q(x) verified identically (10 random rational points, degree check: 5 = 1+4)")

assert p(F(-1, 2)) == 0
print(f"p(-1/2) = 0 exact: {p(F(-1,2))}")

v1, v2 = q(F(2, 3)), q(F(7, 10))
print(f"q(2/3)  = {v1}  (> 0: {v1 > 0})")
print(f"q(7/10) = {v2}  (< 0: {v2 < 0})")
assert v1 > 0 > v2

# exclusions:
# cos(8pi/15), cos(14pi/15) < 0 since args in (pi/2, pi). cos(2pi/15) > cos(pi/6) = sqrt3/2 > 7/10 since (sqrt3/2)^2=3/4>49/100.
print("exclusions: cos(8pi/15),cos(14pi/15) < 0 (args>pi/2); cos(2pi/15) > sqrt(3)/2 > 7/10 (3/4 > 49/100 exact)")
print("=> unique root of q in (2/3,7/10) is cos(4pi/15) => cos(4pi/15) > 2/3")
print("=> U_spec(Petersen) = 15(1 - arccos(-2/3)/pi) > 15*(1 - 11/15) = 4  [exact strict]")

# non-load-bearing float display
import math
u = 15*(1 - math.acos(-2/3)/math.pi)
print(f"float display (not load-bearing): U_spec ~ {u:.6f} ; beta = 3 ; bound N^2/25 = 4")
