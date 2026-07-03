"""Gate for the S7 residual-fiber convexity reduction (user-relayed authoritative text).

Checks EXACTLY (sympy):
  (F14) phi(y) = 2(N0+lam*y)^2 + 75S - C_A*M_j + v(C_A-C_B)*y  equals Phi on the fiber
        x(y) = (M_j - v y)/q, for j = 4,5,6,7
  (F15) phi' = 4 lam (N0 + lam y) + v(C_A - C_B)
  (F16) window: x>=1 <-> y <= (M_j-q)/v ; s3>=0 <-> y <= (R - M_j/q)/lam
  (F21) y* solves phi'=0
  (F22/F23) phi* vertex value + cleared form 8 lam^2 phi*
  (C41) s3=0 corner: x = (M_j-vR)/u, y = (qR-M_j)/u solve x+y=R, xq+yv=M_j (u=q-v)
  (C51) s1=0 spec: v=e,q=u+e -> x=(M_j-eR)/u, y=((u+e)R-M_j)/u; s2=d-u
  (C61) u=1 spec: x=M_j-vR, y=(1+v)R-M_j
  (C71) v=1 spec: x=(M_j-R)/u, y=((u+1)R-M_j)/u
"""
import sympy as sp

a, b, c, d, e, f, x, y, u, v = sp.symbols('a b c d e f x y u v', positive=True)
q, yy = sp.symbols('q yy', positive=True)

Y = a*c + b*f + c*f
Z = e*Y + d*f*(b + c)
A = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
B = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a + b + c + d + e + f
R = b + c
CA = 50 + 75*A/Z
CB = 50 + 75*B/(e*Y)
Ms = {4: Y, 5: a*e + b*f + c*f, 6: a*c + d*f + e*f, 7: a*e + d*f + e*f}

ok = {}

lam = 1 - v/q
for j, Mj in Ms.items():
    xf = (Mj - v*yy)/q
    N0 = S + q + Mj/q
    Nf = S + q + xf + yy
    Phi_fiber = 2*Nf**2 + 75*S - CA*xf*q - CB*yy*v
    phi_claim = 2*(N0 + lam*yy)**2 + 75*S - CA*Mj + v*(CA - CB)*yy
    ok[f'F14_j{j}'] = sp.simplify(sp.expand(sp.together(Phi_fiber - phi_claim))) == 0
    if j == 4:
        dphi = sp.diff(phi_claim, yy)
        dphi_claim = 4*lam*(N0 + lam*yy) + v*(CA - CB)
        ok['F15'] = sp.simplify(sp.expand(sp.together(dphi - dphi_claim))) == 0
        ystar = sp.solve(sp.Eq(dphi_claim, 0), yy)
        ystar_claim = -(4*lam*N0 + v*(CA - CB))/(4*lam**2)
        ok['F21'] = len(ystar) == 1 and sp.simplify(sp.together(ystar[0] - ystar_claim)) == 0
        phistar_claim = 2*N0**2 + 75*S - CA*Mj - (4*lam*N0 + v*(CA - CB))**2/(8*lam**2)
        ok['F22'] = sp.simplify(sp.expand(sp.together(phi_claim.subs(yy, ystar_claim) - phistar_claim))) == 0
        cleared = 16*lam**2*N0**2 + 600*lam**2*S - 8*lam**2*CA*Mj - (4*lam*N0 + v*(CA - CB))**2
        ok['F23'] = sp.simplify(sp.expand(sp.together(8*lam**2*phistar_claim - cleared))) == 0
        # window bounds
        ok['F16_x'] = sp.simplify(sp.together((xf - 1) - (v/q)*((Mj - q)/v - yy))) == 0
        s3f = R - xf - yy
        ok['F16_s3'] = sp.simplify(sp.together(s3f - lam*((R - Mj/q)/lam - yy))) == 0

# corner substitutions (u = q - v)
xc = (Ms[4] - v*R)/u
yc = ((u + v)*R - Ms[4])/u
ok['C41'] = (sp.simplify(sp.expand(xc + yc - R)) == 0 and
             sp.simplify(sp.expand(xc*(u + v) + yc*v - Ms[4])) == 0)
# s1=0: v=e, q=u+e
xe = (Ms[4] - e*R)/u
ye = ((u + e)*R - Ms[4])/u
ok['C51'] = (sp.simplify(sp.expand(xe + ye - R)) == 0 and
             sp.simplify(sp.expand(xe*(u + e) + ye*e - Ms[4])) == 0)
# u=1: q=1+v
x1 = Ms[4] - v*R
y1 = (1 + v)*R - Ms[4]
ok['C61'] = (sp.simplify(sp.expand(x1 + y1 - R)) == 0 and
             sp.simplify(sp.expand(x1*(1 + v) + y1*v - Ms[4])) == 0)
# v=1: q=u+1
xv = (Ms[4] - R)/u
yv_ = ((u + 1)*R - Ms[4])/u
ok['C71'] = (sp.simplify(sp.expand(xv + yv_ - R)) == 0 and
             sp.simplify(sp.expand(xv*(u + 1) + yv_*1 - Ms[4])) == 0)

print("=" * 50)
for k, s_ in ok.items():
    print(f"{k}: {'PASS' if s_ else 'FAIL'}")
print("=" * 50)
print("VERDICT:", "ALL-PASS" if all(ok.values()) else "FAIL")
