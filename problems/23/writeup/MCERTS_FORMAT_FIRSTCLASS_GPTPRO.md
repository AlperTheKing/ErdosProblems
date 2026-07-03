# M-Certs: Format + First Signature Class (GPT-Pro, 2026-07-03) — Branch A / A2 / AM

## (M-cert) format, one (signature τ, row R) pair — EQ seed
Bad doors M_EQ = {19,27,79}; active row Q* = (7,5,8,6,9); weights w_0..w_9 > 0; attachment
weight z ≥ 0. Monotonicity defect Θ_{τ,R}(w,z) = E_Q*(w) − (I_R^τ(w,z) − N(w) − z)
= z + I_Q*(w) − I_R^τ(w,z)  [attachment weakly decreases the excess].
  (M-cert)  D_{τ,R}·Θ_{τ,R}(w,z) = P⁰_{τ,R} + Σ_{j=1..7} F_j·P_{τ,R,j} + E_Q*(w)·P_{τ,R,8}
with D > 0 product of row denominators; after shift w_i = 1+x_i, z = y: ALL P ∈ Z≥0[x,y].
Seven EQ cone inequalities (explicit): F1 = w5−w9, F2 = w6−w7, F3 = w3+w5−w2−w9,
F4 = w4+w6−w1−w7, F5 = w0w6+w3w8+w5w8−m, F6 = w0w5+w3w8+w5w8−m, F7 = w0w6+w4w8+w6w8−m
[m = w1w9+w2w7+w7w9]. Valid on the overfull seed branch (F_j ≥ 0, E_Q* ≥ 0).

## First class τ_0 = (V2; L={3,5}, R={4,6}) — TRUE TWIN of bag 8 (simplest of 27)
N(8) = {3,5,4,6}: the attachment is exactly a twin of bag 8 ⟹ no new row types after twin
contraction. NO multipliers needed (α=0, F_j=0, E_Q*=0):
  (Pj)  P_j(w,z) = D_0(w,z)·[ z + I_Q*(w) − I_{R_j}(w0..w7, w8+z, w9) ]  for j = 0..10
  (Coeff+)  P_j ∈ Z≥0[w_0..w_9, z]  — pure coefficient positivity, STRONGER than shifted.
Denominators: A(t) = w0w6+(w4+w6)t, B(t) = w0w5+(w3+w5)t,
C(t) = w0w5w6 + t(w3w4+w3w6+w4w5+w5w6); A0/B0/C0 at t=w8, Az/Bz/Cz at t=w8+z;
D_0 = w5w6·A0B0C0·AzBzCz.
11 EQ row types (COMPLETE, recovered from thread 2026-07-03): R0=(1,5,0,6,9), R1=(1,5,8,4,9),
R2=(1,5,8,6,9), R3=(7,5,0,6,2), R4=(7,5,8,6,2), R5=(7,3,8,6,2), R6=(7,5,0,6,9),
R7=(7,5,8,4,9), R8=(7,5,8,6,9), R9=(7,3,8,4,9), R10=(7,3,8,6,9).
GPT-Pro also produced a downloadable verifier generator (link in thread) — but the spec above
suffices to implement directly: construct the 11 rational identities, clear D_0, assert no
negative coefficients; dump sparse monomial dicts for the engine.

## Template value + master cube (M5 tail)
The class exercises the full rational machinery (defect, denominator clearing, row updates,
coefficient positivity) with zero multipliers; remaining 26 classes = same pipeline plus
multiplier search. Uniformity conjecture: signature-parameterized master certificate over the
V2 master cube (λ_3+λ_5+λ_4+λ_6 = 1 parametrization) — one certificate family covering all
signatures; plausible but unproven.

## Obligations
Codex: implement the τ_0 verifier (11 identities, exact sympy/Fraction), then grind classes
2..27 with the (M-cert) multiplier LP. Claude: exact-audit every identity. GPT-Pro: master
cube uniformity after τ_0 lands.
