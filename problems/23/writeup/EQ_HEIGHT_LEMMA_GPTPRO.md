# EQ Height Lemma — corrected h-monotonicity (GPT-Pro, 2026-07-03) — Branch A / A2

Status: RAW h-monotonicity of I(Q)−N is FALSE (pure EQ h-blowup: N=10h, m=3h², η=h²,
I_EQ−N = (3/2)h — INCREASES). The correct statement is a HOMOGENEITY defect lemma; height
direction closes from the h=1 cone certificate alone.

## The lemma (corrected form)
F(w) = H(w) − (3/2)η(w), H = I_EQ − N, η = N²/25 − m, on the seven-cut cone F1..F7 ≥ 0,
w_i = 1 + x_i, x_i ≥ 0.
  (2.1) I_EQ(hw) = h·I_EQ(w)  [every quotient summand total degree 1; e.g. w5·w1w9/A,
        B·w2w7(w0+w8), C·w7w9/A with deg B,A = 2, deg C = 3]
  (2.2) H(hw) = h·H(w);  (2.3) η(hw) = h²·η(w)
  (H)   F(hw) = h·F(w) − (3/2)·h(h−1)·η(w) ≤ 0  once F(w) ≤ 0, η(w) ≥ 0, h ≥ 1. ∎ (3 lines)
Normalized obstruction (I−N)/η = 3/(2h) at pure blowups — decreasing; calibrated equality at
h=1: I−N = (3/2)η EXACTLY (seed: I−N = 3/2, η = 1).

## All-height closure (§7)
Any in-hypothesis EQ weighted blowup W: h = min_i W_i, w̃ = W/h (min-normalized, w̃_i ≥ 1);
seven-cut inequalities homogeneous (F1..F4 deg 1, F5..F7 deg 2) so remain valid; h=1
certificates H(w̃) ≤ (3/2)η(w̃), η(w̃) ≥ 0 ⟹ H(W) = hH(w̃) ≤ (3/2)hη(w̃) = (3/2)η(W)/h ≤
(3/2)η(W). Stronger by factor 1/h.

## h=1 machine obligations (the seven-cut symbolic program targets)
  (EQ-ODL)  I_EQ(w) − N(w) ≤ (3/2)·η(w)   on the cone   [(4.1): D_EQ-cleared, P0 + Σ Pj·Fj
            form with P ∈ Z≥0[x0..x9]]
  (EQ-bank) η(w) ≥ 0                       on the cone   [(4.2), same certificate shape]

## Hypothesis usage (§5)
Height lemma: only the fixed weighted quotient. Triangle-freeness: upstream (quotient validity,
row families = listed shortest paths). Max cut: the seven inequalities. Gamma-min: upstream
seed reduction (rules out non-EQ/SIB overfull cores). Class uniformity: ESSENTIAL for
homogeneity (rows scale h³, bad multiplicities h², per-vertex loads h — Claude to verify
symbolically).

## ✔ INTERFACE RESOLVED (Claude gate _gate_eq_constant_pin.py, 2026-07-03)
THE CONSTANT IS c = 2/3, NOT 3/2 (the sanitized "3 2" in the reply text was 2/3; exact gate
pinned it): EQ seed graph, every gamma-min cut, unique overfull row per component
(e.g. f=(7,9), Q=(7,5,8,6,9)): **I−N = 2/3, η = 1, ratio = 2/3 TIGHT**. All other rows
underfull. ODL c=1 HOLDS at the seed with slack 1/3. C5-RS holds every row (max sum 19/6 ≤
7/2, slack 1/3 — the familiar OHDX margin). The 2/3 is exactly the A1 proper-mask coefficient
(25/N + 2/3)η — constants line up across the assembly.
Blowup scaling VERIFIED EXACT (class-corner true max, full 3^10/4^10 enumeration):
h=2: m=12=3h², η=4=h²; h=3: m=27=3h², η=9=h² ✓ (2.2)/(2.3) homogeneity confirmed numerically.
CORRECTED height lemma: F(w) = H(w) − (2/3)η(w); F(hw) = hF(w) − (2/3)h(h−1)η(w).
h=1 MACHINE OBLIGATIONS (Codex symbolic program targets, now UNBLOCKED):
  (EQ-ODL)  I_EQ(w) − N(w) ≤ (2/3)·η(w)  on the seven-cut cone  [TIGHT at pure seed]
  (EQ-bank) η(w) ≥ 0                      on the same cone
⟹ all heights h ≥ 1: I−N ≤ (2/3)η/h... more precisely H(W) ≤ (2/3)η(W)/h ≤ (2/3)η(W) < η(W)
= ODL c=1 with room. EQ branch of A2 then rests on the two h=1 cone certificates + AM.

## ADDENDUM (2026-07-03): CERT-1 (EQ-bank) PROVEN ANALYTICALLY
eta25 = N^2 - 25m >= 25 on the seven-cut cone. PROOF (grouped variables): U=w0+w8, V=w4+w6,
X=w1+w7, Y=w2+w9, Z=w3+w5; N=U+V+X+Y+Z; T=m+1. Cone product bounds: UV >= T (F7 + w0w4>=1),
UZ >= T (F6 + w0w3>=1), XY >= T (w1w2>=1), VZ >= XY >= T (F3,F4). A=U+V+Z: A^2 >= 9T (QM +
three product bounds: A^2 >= 3((UV)+(UZ)+(VZ)) >= 9T); B=X+Y: B^2 = (X-Y)^2 + 4XY >= 4T.
A,B,T >= 0 ⟹ A >= 3 sqrt(T), B >= 2 sqrt(T) ⟹ N = A+B >= 5 sqrt(T) ⟹ N^2 >= 25T = 25(m+1)
⟹ eta25 >= 25. EQUALITY: forces F3=F4=F6=F7=0, w0w3=w0w4=w1w2=1, U=V=Z, X=Y ⟹ the seed
ray w0..w4=1, w5..w9=T0 exactly (matches Claude's ray computation: N=5(T0+1), m=T0^2+2T0,
N^2-25m=25). Polynomial verifier: degree-4 Positivstellensatz via multiplying the conic
implication by AB+6T (U_A = A^2-9T, U_B = B^2-4T auxiliary forms) — Codex to encode.
CERT-2 (EQ-ODL c=2/3): LP formulation in thread tail (read pending) — 'closes the EQ side
of ODL once Codex returns a rational solution to CERT-2's LP.'

## ADDENDUM 2 (2026-07-03): CERT-2 LP FORMULATION (for Codex rational solve)
I_EQ explicit via s5..s9 row-sum terms; positive denominator D_EQ = w5*w6*A*B*C (deg 9);
cleared numerator **P_EQ = D_EQ * (2*eta25 - 75*(I_EQ - N))** (deg 11; equivalent to
I_EQ-N <= (2/3)eta since eta25=25eta... note eta25 = N^2-25m = 25*eta). (LP-1) primary:
P_EQ = P0 + Sigma_j F_j*P_j, all shifted-coefficient-nonneg; deg P0 <= 11, deg P1..4 <= 10
(F1..F4 deg 1), deg P5..7 <= 9 (F5..F7 deg 2); SEED-EQUALITY: constant coeff of P0 = 0
(F_j(0)=0 handles the rest). (LP-2) fallback quadratic module: + Sigma F_i*F_j*P_ij with
deg-compatible bounds. Finite rational LP; clear denominators on solution.
