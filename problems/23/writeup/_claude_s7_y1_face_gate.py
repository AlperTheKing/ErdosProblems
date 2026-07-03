"""Gate for GPT-Pro's S7 y=1 six-face reduction (sibling thread, 2026-07-03).

Checks EXACTLY (sympy, rational):
  (I1)  Phi on y=1 equals 2N^2 + 75S - C_A*x*q - C_B*v  (from the S7 definition)
  (I3)  R_x := Z*dPhi/dx = 4ZN - q(50Z+75A)   [cleared x-derivative]
  (I4)  R_q := Z*dPhi/dq = 4ZN - x(50Z+75A)   [cleared q-derivative, u=q-v param]
  (I5)  Xi := eYZ*Phi = eY*x*R_x + Z*L_x, L_x = eY(2N(N-2x)+75S) - (50eY+75B)v
  (I8)  Xi = eY*q*R_q + Z*L_q,             L_q = eY(2N(N-2q)+75S) - (50eY+75B)v
  (B)   B = Y + e*T with T=a+b+c+f
  (F)   floor arithmetic: 2(T+D+q+2)(T+2)+25D-75 >= 95 at T=4,D=2,q=2
  (S)   random feasible integer probes: Dx/Dq statements hold (R_x>=0 -> Phi>0)
"""
from fractions import Fraction as F
import random
import sympy as sp

a, b, c, d, e, f, x, y, u, v = sp.symbols('a b c d e f x y u v', positive=True)

m = x*u + x*v + y*v
N = a + b + c + d + e + f + x + y + u + v
Y = a*c + b*f + c*f
Z = e*Y + d*f*(b + c)
A = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
B = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a + b + c + d + e + f
Phi = 2*(N**2 - 25*m) - 75*(x*(u + v)*A/Z + y*v*B/(e*Y) - S)

ok = {}

# --- restrict to y=1, parametrize u = q - v ---
q = sp.Symbol('q', positive=True)
sub_y1 = {y: 1, u: q - v}
Phi1 = sp.together(Phi.subs(sub_y1))
CA = 50 + 75*A/Z
CB = 50 + 75*B/(e*Y)
Phi1_claim = 2*(S + 1 + x + q)**2 + 75*S - CA*x*q - CB*v
ok['I1_Phi_y1_form'] = sp.simplify(sp.expand(sp.together(Phi.subs(sub_y1) - Phi1_claim))) == 0

N1 = S + 1 + x + q
Rx_claim = 4*Z*N1 - q*(50*Z + 75*A)
Rx_true = sp.expand(Z*sp.diff(Phi1_claim, x))
ok['I3_Rx'] = sp.simplify(Rx_true - Rx_claim) == 0

Rq_claim = 4*Z*N1 - x*(50*Z + 75*A)
Rq_true = sp.expand(Z*sp.diff(Phi1_claim, q))
ok['I4_Rq'] = sp.simplify(Rq_true - Rq_claim) == 0

Xi = sp.expand(e*Y*Z*Phi1_claim)
Lx = e*Y*(2*N1*(N1 - 2*x) + 75*S) - (50*e*Y + 75*B)*v
ok['I5_Xi_split_x'] = sp.simplify(Xi - sp.expand(e*Y*x*Rx_claim + Z*Lx)) == 0

Lq = e*Y*(2*N1*(N1 - 2*q) + 75*S) - (50*e*Y + 75*B)*v
ok['I8_Xi_split_q'] = sp.simplify(Xi - sp.expand(e*Y*q*Rq_claim + Z*Lq)) == 0

T = a + b + c + f
ok['B_eq_Y_plus_eT'] = sp.simplify(B - (Y + e*T)) == 0

Tn, Dn, qn = sp.symbols('Tn Dn qn')
floor = 2*(Tn + Dn + qn + 2)*(Tn + 2) + 25*Dn - 75
ok['F_floor_95'] = floor.subs({Tn: 4, Dn: 2, qn: 2}) == 95

# --- (S) probe Dx/Dq on random S7-feasible y=1 rational points ---
def feasible(pt):
    va = {a: pt[0], b: pt[1], c: pt[2], d: pt[3], e: pt[4], f: pt[5],
          x: pt[6], v: pt[7], q: pt[8]}
    if va[q] - va[v] < 1:  # u >= 1
        return None
    mm = va[x]*va[q] + va[v]
    Yv = va[a]*va[c] + va[b]*va[f] + va[c]*va[f]
    s = [va[e] - va[v], va[d] + va[e] - va[q], va[b] + va[c] - va[x] - 1,
         Yv - mm,
         va[a]*va[e] + va[b]*va[f] + va[c]*va[f] - mm,
         va[a]*va[c] + va[d]*va[f] + va[e]*va[f] - mm,
         va[a]*va[e] + va[d]*va[f] + va[e]*va[f] - mm]
    if any(si < 0 for si in s):
        return None
    return va

random.seed(23)
probes = 0
viol = 0
while probes < 400:
    pt = [F(random.randint(1, 8)) + F(random.randint(0, 4), 5) for _ in range(9)]
    va = feasible(pt)
    if va is None:
        continue
    probes += 1
    Phv = Phi1_claim.subs(va)
    Rxv = Rx_claim.subs(va)
    Rqv = Rq_claim.subs(va)
    # Dx: R_x >= 0 and feasible ==> Phi > 0 ; contrapositive check
    if Rxv >= 0 and Phv <= 0:
        viol += 1
    if Rqv >= 0 and Phv <= 0:
        viol += 1
ok['S_probe_DxDq'] = (probes == 400 and viol == 0)

print("=" * 50)
for k, s in ok.items():
    print(f"{k}: {'PASS' if s else 'FAIL'}")
print("=" * 50)
print("VERDICT:", "ALL-PASS" if all(ok.values()) else "FAIL")
