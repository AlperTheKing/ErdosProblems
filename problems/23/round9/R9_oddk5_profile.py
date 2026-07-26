"""R9: the exact 1-terminal profile of C5 and the 1-sum optimisation.

RETRACTION of my own first guess.  I first claimed
    f(u) = max{ psi(C5,x) : x_v = u, sum x = 1 } = min(u,(1-u)/4)*(1-u)/4 ,
which assumes the four remaining weights are equal.  The exhaustive rational grid in
R9_oddk5_sums.py FALSIFIED it at u = 1/12 (grid max 1/40 = 0.025 > 11/576 = 0.0191).
The correct profile is asymmetric: with the C5 written v,a,b,c,d and a = d = p, b = c = q,
    psi = min(u p, p q, q^2);  for u <= 1/5 the binding pair is u p = q^2 with p = q^2/u,
    2q^2/u + 2q = 1-u  =>  q = (sqrt(2u-u^2) - u)/2 ,  f(u) = q^2 ,
and for u >= 1/5 the four are equal, f(u) = ((1-u)/4)^2.  f(1/5) = 1/25 is the maximum.
Note f is irrational at rational u, so no rational grid can attain it -- that is exactly
why the grid maxima sit just below.
"""
from fractions import Fraction as F
from math import sqrt

def f(u):
    if u <= 0.2:
        q = (sqrt(2*u - u*u) - u) / 2
        return q*q
    return ((1-u)/4)**2

def grid_max(u, D):
    """exhaustive rational maximum with denominator D, for comparison"""
    from fractions import Fraction as FF
    best = FF(0); rem = D - int(u*D)
    if abs(u*D - int(u*D)) > 1e-9: return None
    U = FF(int(u*D), D)
    for a in range(rem+1):
        for b in range(rem-a+1):
            for c in range(rem-a-b+1):
                d = rem-a-b-c
                y = [U, FF(a,D), FF(b,D), FF(c,D), FF(d,D)]
                v = min(y[i]*y[(i+1)%5] for i in range(5))
                if v > best: best = v
    return best

print("u        f(u) (closed form)      exhaustive grid D=60      grid <= f ?")
for k in range(0, 13):
    u = k/12
    g = grid_max(u, 60)
    print(f"{u:8.4f} {f(u):.8f}   {float(g) if g is not None else '-':>16}   "
          f"{'OK' if (g is None or float(g) <= f(u)+1e-12) else '*** VIOLATION ***'}")
print()
print("max of f on [0,1] :", max((f(i/2000), i/2000) for i in range(2001)), " (1/25 = 0.04)")
print()
print("1-sum of two pentagons at a vertex of weight z (s,t = the two side totals, s+t=1+z):")
best = (0, None)
NN = 400
for zi in range(NN+1):
    z = zi/NN
    for si in range(NN+1):
        s = z + (1+z-2*z)*si/NN            # s ranges over [z, 1]
        t = 1+z-s
        if t < z - 1e-12 or s <= 0 or t <= 0: continue
        val = s*s*f(z/s) + t*t*f(z/t)
        if val > best[0]: best = (val, (z, s, t))
print("  continuous maximum found:", best, "   1/25 =", 1/25)
