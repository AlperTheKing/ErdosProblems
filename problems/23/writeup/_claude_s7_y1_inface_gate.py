"""Gate for REPLY 8 y=1/x=1 in-face fiber reductions (user-relayed authoritative).

Checks EXACTLY (sympy):
  (YF/YQ) phi_j^Y(v) = 2(N0 - v/q)^2 + 75S - C_A M_j + v(C_A - C_B) equals Phi on the
          fiber x(v) = (M_j - v)/q, y=1, for j=4..7
  (YD)    (phi)' = -4N/q + 75(A/Z - B/(eY))
  (Y9)    at STAT (A/Z - B/(eY) = 4N/(75q)):
          xq A/Z + v B/(eY) = M_j/e + M_j T/Y + 4Nx/75
  (Y10)   Phi_STAT = 2N^2 - 4Nx - 50M_j - 75M_j/e + 75D + 75T(Y-M_j)/Y
  (YC)    YCOR subs: v = M_j-(R-1)q, u = Rq-M_j solve x=R-1, xq+v=M_j, u=q-v
  (YX)    YXCOR subs: x=y=1 -> m=u+2v=M_j, q=M_j-v, u=M_j-2v
  (XD)    x=1 fiber: phi_j^X(y) = 2(S+1+q+y)^2 + 75S - C_A q - C_B(M_j-q),
          derivative 4(S+1+q+y) > 0 (no STAT window)
"""
import sympy as sp

a, b, c, d, e, f, x, y, u, v = sp.symbols('a b c d e f x y u v', positive=True)
q, vv, yy = sp.symbols('q vv yy', positive=True)

Y = a*c + b*f + c*f
Z = e*Y + d*f*(b + c)
A = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
B = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a + b + c + d + e + f
R = b + c
D = d + e
T = a + b + c + f
CA = 50 + 75*A/Z
CB = 50 + 75*B/(e*Y)
m_full = x*u + x*v + y*v
N_full = a + b + c + d + e + f + x + y + u + v
Phi_full = 2*(N_full**2 - 25*m_full) - 75*(x*(u + v)*A/Z + y*v*B/(e*Y) - S)
Ms = {4: Y, 5: a*e + b*f + c*f, 6: a*c + d*f + e*f, 7: a*e + d*f + e*f}

ok = {}

for j, Mj in Ms.items():
    xf = (Mj - vv)/q
    sub = {y: 1, x: xf, u: q - vv, v: vv}
    N0 = S + 1 + q + Mj/q
    phi_claim = 2*(N0 - vv/q)**2 + 75*S - CA*Mj + vv*(CA - CB)
    ok[f'YQ_j{j}'] = sp.simplify(sp.expand(sp.together(Phi_full.subs(sub) - phi_claim))) == 0
    if j == 4:
        Nv = N0 - vv/q
        dphi = sp.diff(phi_claim, vv)
        dphi_claim = -4*Nv/q + 75*(A/Z - B/(e*Y))
        ok['YD'] = sp.simplify(sp.expand(sp.together(dphi - dphi_claim))) == 0

# (Y9)/(Y10): impose STAT relation symbolically via substitution of A/Z
# STAT: A/Z = B/(eY) + 4N/(75q). Treat N as the fiber value with x free (x = (Mj-v)/q).
AZ = sp.Symbol('AZ', positive=True)  # stands for A/Z
for j, Mj in Ms.items():
    xs = (Mj - vv)/q
    Ns = S + 1 + xs + q
    stat_AZ = B/(e*Y) + 4*Ns/(75*q)
    lhs = xs*q*AZ + vv*B/(e*Y)
    lhs_at_stat = lhs.subs(AZ, stat_AZ)
    rhs9 = Mj/e + Mj*T/Y + 4*Ns*xs/75
    ok[f'Y9_j{j}'] = sp.simplify(sp.expand(sp.together(lhs_at_stat - rhs9 - (Mj*B/(e*Y) - Mj/e - Mj*T/Y)))) == 0 \
        if False else sp.simplify(sp.expand(sp.together(lhs_at_stat - (Mj*B/(e*Y) + 4*Ns*xs/75)))) == 0
    # B = Y + eT  =>  Mj B/(eY) = Mj/e + Mj T/Y
    ok[f'Y9b_j{j}'] = sp.simplify(sp.expand(sp.together(Mj*B/(e*Y) - (Mj/e + Mj*T/Y)))) == 0
    Phi_stat = 2*(Ns**2 - 25*Mj) - 75*(lhs_at_stat - S)
    Y10 = 2*Ns**2 - 4*Ns*xs - 50*Mj - 75*Mj/e + 75*D + 75*T*(Y - Mj)/Y
    ok[f'Y10_j{j}'] = sp.simplify(sp.expand(sp.together(Phi_stat - Y10))) == 0

# YCOR substitutions
for j, Mj in Ms.items():
    vc = Mj - (R - 1)*q
    uc = R*q - Mj
    ok[f'YC_j{j}'] = (sp.simplify(sp.expand((R - 1)*q + vc - Mj)) == 0 and
                      sp.simplify(sp.expand(uc + vc - q)) == 0)

# YXCOR substitutions: x=y=1: m = q + v = u + 2v; q = Mj - v, u = Mj - 2v
mj = sp.Symbol('mj', positive=True)
qx = mj - vv
ux = mj - 2*vv
ok['YX_subs'] = (sp.simplify(sp.expand(qx + vv - mj)) == 0 and
                 sp.simplify(sp.expand(ux + vv - qx)) == 0)

# x=1 fiber: v(y) = (Mj-q)/y, u = q - v; phi^X and derivative
for j, Mj in Ms.items():
    vf = (Mj - q)/yy
    subX = {x: 1, v: vf, u: q - vf, y: yy}
    phiX_claim = 2*(S + 1 + q + yy)**2 + 75*S - CA*q - CB*(Mj - q)
    ok[f'XQ_j{j}'] = sp.simplify(sp.expand(sp.together(Phi_full.subs(subX) - phiX_claim))) == 0
    if j == 4:
        ok['XD'] = sp.simplify(sp.diff(phiX_claim, yy) - 4*(S + 1 + q + yy)) == 0

print("=" * 50)
for k, s_ in ok.items():
    print(f"{k}: {'PASS' if s_ else 'FAIL'}")
print("=" * 50)
print("VERDICT:", "ALL-PASS" if all(ok.values()) else "FAIL")
