"""Gate for GPT-Pro's S7 x=1 six-face reduction (sibling thread, 2026-07-03).

Checks EXACTLY (sympy rational + Fraction probes):
  (X1)  Phi on x=1 equals 2N^2 + 75S - C_A*q - C_B*y*v   (m = q+yv, N = S+1+y+q)
  (Ry)  R_y := eY*dPhi/dy = 4eYN - v(50eY+75B)
  (Rv)  dPhi/dv at fixed q = -C_B*y
  (I1)  Xi := eYZ*Phi = Z*y*R_y + eY*(Z*(2N(N-2y)+75S) - q(50Z+75A))
  (ID)  (D+T)Z - DA = DY(e-1) + eT(Y-D) + d(fR(D+T) - D(R+f))  [Case-1 identity]
  (FL)  2D^2 - 22D + 96 = 2(D-11/2)^2 + 71/2  and > 0
  (RB)  probe: C_A*q <= 125D + 75T on feasible points (ratio bound)
  (XDy) probe: R_y >= 0 & feasible & x=1  ==>  Phi > 0
"""
from fractions import Fraction as F
import random
import sympy as sp

a, b, c, d, e, f, x, y, u, v = sp.symbols('a b c d e f x y u v', positive=True)
q = sp.Symbol('q', positive=True)

Y = a*c + b*f + c*f
Z = e*Y + d*f*(b + c)
A = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
B = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a + b + c + d + e + f
m_full = x*u + x*v + y*v
N_full = a + b + c + d + e + f + x + y + u + v
Phi_full = 2*(N_full**2 - 25*m_full) - 75*(x*(u + v)*A/Z + y*v*B/(e*Y) - S)

ok = {}

sub_x1 = {x: 1, u: q - v}
N1 = S + 1 + y + q
CA = 50 + 75*A/Z
CB = 50 + 75*B/(e*Y)
Phi1 = 2*N1**2 + 75*S - CA*q - CB*y*v
ok['X1_Phi_form'] = sp.simplify(sp.together(Phi_full.subs(sub_x1) - Phi1)) == 0

Ry_claim = 4*e*Y*N1 - v*(50*e*Y + 75*B)
ok['Ry'] = sp.simplify(sp.expand(e*Y*sp.diff(Phi1, y)) - Ry_claim) == 0

ok['Rv'] = sp.simplify(sp.diff(Phi1, v) + CB*y) == 0

Xi = sp.expand(e*Y*Z*Phi1)
rem = Z*(2*N1*(N1 - 2*y) + 75*S) - q*(50*Z + 75*A)
ok['I1_split'] = sp.simplify(Xi - sp.expand(Z*y*Ry_claim + e*Y*rem)) == 0

R_ = b + c
T_ = a + b + c + f
D_ = d + e
lhs = (D_ + T_)*Z - D_*A
rhs = D_*Y*(e - 1) + e*T_*(Y - D_) + d*(f*R_*(D_ + T_) - D_*(R_ + f))
ok['ID_case1'] = sp.simplify(sp.expand(lhs - rhs)) == 0

Dn = sp.Symbol('Dn')
ok['FL_floor'] = sp.simplify(2*Dn**2 - 22*Dn + 96 - (2*(Dn - sp.Rational(11, 2))**2 + sp.Rational(71, 2))) == 0

# probes on x=1 feasible points
def feas(pt):
    va = {a: pt[0], b: pt[1], c: pt[2], d: pt[3], e: pt[4], f: pt[5],
          y: pt[6], v: pt[7], q: pt[8]}
    if va[q] - va[v] < 1:
        return None
    mm = va[q] + va[y]*va[v]
    Yv = va[a]*va[c] + va[b]*va[f] + va[c]*va[f]
    s = [va[e] - va[v], va[d] + va[e] - va[q], va[b] + va[c] - 1 - va[y],
         Yv - mm,
         va[a]*va[e] + va[b]*va[f] + va[c]*va[f] - mm,
         va[a]*va[c] + va[d]*va[f] + va[e]*va[f] - mm,
         va[a]*va[e] + va[d]*va[f] + va[e]*va[f] - mm]
    if any(si < 0 for si in s):
        return None
    return va

random.seed(31)
probes = 0
violRB = 0
violXDy = 0
while probes < 400:
    pt = [F(random.randint(1, 8)) + F(random.randint(0, 4), 5) for _ in range(9)]
    va = feas(pt)
    if va is None:
        continue
    probes += 1
    Tv = va[a] + va[b] + va[c] + va[f]
    Dv = va[d] + va[e]
    CAv = CA.subs(va)
    if CAv*va[q] > 125*Dv + 75*Tv:
        violRB += 1
    Phv = Phi1.subs(va)
    Ryv = Ry_claim.subs(va)
    if Ryv >= 0 and Phv <= 0:
        violXDy += 1
ok['RB_probe'] = (probes == 400 and violRB == 0)
ok['XDy_probe'] = (probes == 400 and violXDy == 0)

print("=" * 50)
for k, s_ in ok.items():
    print(f"{k}: {'PASS' if s_ else 'FAIL'}")
print("=" * 50)
print("VERDICT:", "ALL-PASS" if all(ok.values()) else "FAIL")
