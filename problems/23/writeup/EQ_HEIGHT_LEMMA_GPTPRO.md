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

## ADDENDUM 3 (2026-07-03): CERT-2 INFEASIBILITY DIAGNOSIS + CHARTED BERNSTEIN-HANDELMAN PLAN
Codex ground truth: LP-1 shifted-coeff infeasible deg<=5-6; LP-2 small products infeasible.
GPT-Pro diagnosis: (a) shifted-coefficient nonnegativity on the x-orthant is MUCH stronger
than cone positivity — wrong basis for a deg-11 17578-term target with seed equality.
(e) CHART REDUCTION (uses height lemma H(hw)=hH, eta(hw)=h^2 eta + CERT-1 eta>=1): any
cone counterexample normalizes to one of TEN charts w_k = 1, w_i >= 1 (min-coordinate
chart; F_j homogeneous). So FIRST: per-chart semialgebraic falsifier search for
{F_1..F_7 >= 0, P_EQ < 0}; do NOT keep running global LPs.
(b) TARGETED CHARTED LP (the one run to do): per chart k, generators = homogenized
F_1,k..F_7,k PLUS the CERT-1 grouped generators (all cone-valid by CERT-1's proof):
G1 = UV-T, G2 = UZ-T, G3 = XY-T, G4 = VZ-XY, G5 = VZ-T, G6 = A^2-9T, G7 = B^2-4T,
G8 = eta25-25 (U=w0+w8, V=w4+w6, X=w1+w7, Y=w2+w9, Z=w3+w5, T=m+1, A=U+V+Z, B=X+Y);
multipliers = total-degree BERNSTEIN basis on the chart, deg B_0 <= 11,
deg B_G <= 11 - deg G; seed-vanishing B_0(seed chart pt) = 0.
(c) Row-template split WRONG for CERT-2 (11 templates belong to M-certs); optional
per-door preconditioner I_EQ = I_19 + I_27 + I_79 only.
(d) ESCALATION if a chart counterexample appears: seven cuts -> FULL quotient max-cut
flip facets F_S(w) = delta_B^w(S) - delta_M^w(S) >= 0 (subsets mod complement/autom) ->
ONLY THEN gamma-switch facets nu_K(S) >= 0 (completed terminal shadows). A max-cut-
satisfying, gamma-min-satisfying counterexample would mean EQ branch redesign (not
expected per seed/blowup evidence).
VERDICT INTERPRETATION: all-chart certificate success = CERT-2 PROVEN.

## ADDENDUM 3b (authoritative fuller CERT-2 text, user-relayed): compactification + outcomes
Chart compactification: S = 1 + Sigma x_i, s = 1/S, z_i = x_i/S; simplex Delta_k
{s>=0, z>=0, s+Sigma z=1}; P-hat_k = s^11 P^(k)(z/s); F-hat_{j,k} = s^{d_j} F_j(z/s);
BankGen B-hat_k = eta25-hat - 25 s^2. Generator list (union of both reply versions):
F1..F7 + {UV-T, UZ-T, VZ-T, XY-T, VZ-XY, A^2-9T, B^2-4T, eta25-25} homogenized.
Seed-vanishing = Bernstein vertex coefficient c_{0,(11,0,..,0)} = 0.
ChartSOS fallback: + Z^T Q Z, Q PSD rational Gram/LDL, monomials deg<=5, SOS vanishing
at seed; if degree parity awkward multiply by (s+Sigma z=1) to formal degree 12 / SOS 6.
OUTCOMES: all-chart ChartCert success => CERT-2 PROVEN (heights via EQ height lemma);
ChartSOS success fine (Lean needs rational Gram backend); optimizer cex => escalate
(first version: full maxcut flip facets F_S(w) FIRST, then gamma-switch; second version
notes gamma-switch is the LIKELY missing one — test maxcut facets first anyway).

# ===== CERT-2 VERDICT: RETIRED, replaced by EQ-ODL1 (main thread, 2026-07-04) =====
STRATEGIC DECISION: retire the old c = 2/3 CERT-2 from the critical path. The 2/3
inequality I_EQ <= N - (2/3)... is a sharp strengthening TIGHT AT THE SEED — that
tightness is exactly what made every chart/SOS certificate hard (boundary
certificate with the wrong basis: 2x2 atoms leave thousands of uncovered negative
rows, split atoms worsen numerics, generic PSD too wide, no falsifier).
BRANCH-A ONLY NEEDS c = 1:   EQ-ODL1:  I_EQ <= N + eta.
HEIGHT PROPAGATION (verified my side): H(w) = I_EQ(w) - N(w) is 1-homogeneous,
eta 2-homogeneous; CERT-1 gives eta25 >= 25 i.e. eta >= 1 > 0; so for h >= 1:
H(hw) = h H(w) <= h eta(w) <= h^2 eta(w) = eta(hw). Passive AM extends to all
passive EQ extensions (attachments add no bad doors). So c = 1 at height 1
suffices for the whole EQ branch. The c = 1 target has POSITIVE SEED GAP
(adds (1/3) D_EQ eta25 >= 25 D_EQ /3 vs the 2/3 form) — no seed-vanishing
constraint, much easier certificate.
NEW LEDGER ENTRY (replaces EQ-CERT2): EQ-ODL1 with certificate target
    P_EQ^(1) = D_EQ [ eta25 - 25 (I_EQ - N) ] >= 0   (up to the fixed clearing)
RUNG 1 (run before any further SOS): shifted cone LP
    P_EQ^(1) = P_0 + sum_{j=1..7} F_j P_j + B_0 P_B + sum_l G_l P_l
  generators: seven-cut inequalities F_j; CERT-1 bank generator B_0 = eta25 - 25;
  CERT-1 grouped generators UVT, UZT, XYT, VZXY, VZT, U_A, U_B.
  All multipliers shifted-coefficient-nonnegative in w_i = 1 + x_i, x_i >= 0.
  Degree caps: P_EQ^(1) deg 11; P_0 deg 11; linear-F_j multipliers deg 10;
  quadratic-F_j deg 9; B_0 multiplier deg 9; quadratic G_l deg 9.
  NO seed-vanishing constraint.
  ABORT rung 1 only if: LP infeasible with CERT-1 generators through the caps AND
  a falsifier search on the c = 1 target stays clean.
RUNG 2: (chart/KKT split of the c=1 target — details in thread if rung 1 aborts.)
RUNG 3: targeted low-rank SOS ONLY for failed c=1 charts: P_k^(1) = B_{0,k} +
  sum_G B_{G,k} + Z_k^T Q_k Z_k, keep constant monomial, no seed-zero constraint,
  small Z_k from the negative-coefficient support (deg 4, then 5). Abort if fails
  + falsifier clean + uncovered rows large => GENERATOR REDESIGN (full max-cut
  facets F_S of the EQ quotient), NOT larger PSD.
OLD 2/3 ChartSOS: keep as OPTIONAL strengthening, off critical path. All prior
2x2/PSD artifacts remain as evidence of the sharp-boundary diagnosis.


# ===== EQ-ODL1 RUNG-2 SPEC: height-normalized KKT/dominance chart split (main, 2026-07-04) =====
DECISION: drop the monolithic shifted cone; use height normalization + CERT-1
equality geometry + dominance charts + separate equality-stratum certificate.
TARGET: P_EQ1 = D_EQ [eta25 - 25(I_EQ - N)] >= 0.
1 HEIGHT CHARTS: min_i w_i = 1 (EQ height lemma) => 10 charts H_k (w_k = 1,
  w_i = 1 + x_i, x_i >= 0); compactify S = 1 + sum x_i, s = 1/S, z_i = x_i/S:
  s, z_i >= 0, s + sum z_i = 1; chart target P_k = s^11 P_EQ1^(k)(z/s) (deg 11).
2 TRUE MINIMUM at the all-ones seed: eta25 = 25, I_EQ - N = 2/3, bracket = 25/3,
  D_EQ = w5 w6 A B C = 45 => P_EQ1(seed) = 375. Active there: all x_i = 0, all
  F_j = 0, B0 = 0, all grouped generators = 0. NO seed-vanishing condition.
3 GENERATORS (15): F1..F7 + G1 = UV-T, G2 = UZ-T, G3 = XY-T, G4 = VZ-XY,
  G5 = VZ-T, G6 = U_A = A^2-9T, G7 = U_B = B^2-4T, G8 = B0 = eta25-25, where
  U = w0+w8, V = w4+w6, X = w1+w7, Y = w2+w9, Z = w3+w5, T = m+1, A = U+V+Z,
  B = X+Y (EQ grouping). Homogenize all to degree 2 on the chart simplex (3.1).
4 EQUALITY STRATUM = seed ray w0..w4 = 1, w5..w9 = t >= 1: eta25 = 25;
  I_EQ - N = (t+1)(3t+2)/((t+2)(t^2+3t+1)); D_EQ = t^5 (t+2)^2 (t^2+3t+1);
  P_EQ1(t) = 25 t^6 (t+2)(t^2+2t+2) >= 375, certified by t = 1+u coefficientwise
  nonnegativity. MY GATE (sympy exact): chain identities TRUE; shifted coeffs
  [25,325,1850,6050,12500,16900,14950,8350,2675,0] all >= 0. EQUALITY-STRATUM
  CERTIFICATE PROVEN (Codex to digit-verify the I_EQ - N seed-ray input formula
  against the EQ seed data).
5 DOMINANCE CHARTS D_{k,a}: G_a-hom >= G_b-hom for all b (deltas Delta_{a,b,k} >= 0
  as extra generators). COMPLETENESS: all generators zero => equality stratum;
  else the max generator's chart applies.
6 BAND SPLIT (recommended): B_near = 2s-1 >= 0, B_inf = 1-2s >= 0 (covers simplex).
7 PER-CHART CERT (k, a, beta): P_k = P_0 + sum_G G-hom P_G + sum_b Delta P_{a,b}
  + B_beta P_beta; multipliers Bernstein-positive on the simplex; caps: P_0 <= 11,
  P_G <= 9, P_{a,b} <= 9, P_beta <= 10. No seed-vanishing.
8 CHART COUNT: 10 x 15 x 2 = 300 + equality stratum. Expected: k in {5..9}
  easier (seed ray only at t=1); infinity-band charts often close with P_0 +
  leading homogeneous multipliers; hard charts = finite-band a in {G8, G6, G7};
  linear-cut-dominated charts easy once deltas included.
9 TRIVIALITY DETECTION (order): (i) Bernstein interval lower bound of P_k alone
  (all coeffs >= 0 => closed); (ii) band-only certificate P_0 + B_beta P_beta;
  (iii) full dominance LP (7.1).
10 KKT reading: minimum on the CERT-1 equality stratum; dominance chart picks a
  largest active generator; KKT surfaces = height/coordinate bounds, s = 0,
  s = 1/2 band, generator-equality surfaces, equality stratum. No symbolic KKT.
11 ABORT RUNG-2 only if ALL: 300 charts infeasible/timeout at caps; equality
  stratum verified; per-chart falsifier clean; failed-chart dual rays point at
  missing full max-cut facets.
12 FALLBACK: generator redesign — add EQ quotient max-cut facets F_S (all proper
  subsets mod complement/automorphism) to the SAME chart machinery.


# ===== RUNG-2 INFINITY-BAND CORRECTION (main thread, 2026-07-04) =====
VERDICT: Codex's s ZZEQ 0-face infeasibility refuted ONLY a strict face-truncation,
NOT the spec. The old degree-2 lift s^(2-d) H_G KILLS linear generators on the
s = 0 face (d = 1 gives a factor s). CORRECT LIFT:
    G# := H_G * Lambda^(2-d),   Lambda := s + sum z_i,
where H_G = s^(deg G) G(z/s). On the simplex Lambda = 1 so G# = H_G as a FUNCTION,
but the s = 0 face of G# retains the leading homogeneous part (Lambda(0,z) = 1 on
the face). Dominance deltas: Delta#_{a,b} = G#_a - G#_b.
CORRECT INF-BAND CERT: Phat_k = P0 + sum_G G# P_G + sum_b Delta# P_{a,b} +
B_inf P_inf, B_inf = 1 - 2s, Bernstein-positive multipliers, caps 11/9/9/10.
The s = 0 FaceCert is an OPTIONAL subcertificate (asymptotic boundary only); it
certifies the band only when paired with a radial-monotonicity certificate.
B_inf MUST carry its multiplier (only local inequality expressing distance from
the near boundary); deg-10 as used.
SKIP CRITERION (no unconditional skip): an infinity chart is covered iff a
certified derivative condition holds on [0,1/2] x Delta for
Ptilde(s,u) = Phat(s, (1-s)u):
  (i) -d/ds Ptilde >= 0 AND the near-band cert covers s = 1/2; or
  (ii) +d/ds Ptilde >= 0 AND the s = 0 FaceCert covers the face.
HARD-ROW PRIORITY: (k, a, inf) with a in {B0, U_A, U_B} first (the observed hard
k=0/B0/inf belongs here), then quadratic-cut dominance charts (F5-F7), then
linear-cut charts, then near-band. Do not budget all 300 equally.
CODEX PATCH STEPS: (1) replace s^(2-d) H_G by H_G Lambda^(2-d); (2) deltas from
G#; (3) keep FULL G# forms (never s=0-face-only); (4) keep B_inf with deg <= 10
multiplier; (5) run the corrected full InfCert per chart; optionally attempt the
radial-monotonicity skip certificates where cheap.


# ===== EXACT-REPLAY: FLOOR-BUFFER RATIONALIZATION (main thread, 2026-07-04) =====
VERDICT: high-height LP vertices are EXPECTED (Bernstein/Handelman cone of a
degree-11 target, many near-dependent columns, near the equality stratum: vertex
denominators = determinants of large ill-conditioned subsystems). The CONE
CERTIFICATE does not need huge coefficients — reconstructing vertices was the
mistake. Use an INTERIOR point with margin, then floor-round.
METHOD:
 1 Inequality form: certificate p = b + A lambda, lambda >= 0, b >= 0 (b = base).
 2 Row sensitivity n_i^- = sum_j max(0, -A_ij); n^- = 0 rows are safe under
   downward rounding.
 3 BufferLP two-stage: Stage 1 maximize theta s.t. A lambda + theta n^- <= p,
   lambda >= 0. Stage 2 (interior, NOT vertex): theta_0 = theta_max/2; minimize
   sum c_j lambda_j s.t. A lambda + theta_0 n^- <= p, with c_j = 1 or
   1 + log(1 + ||A_col_j||_1). NEVER lexicographic-to-vertex.
 4 Safe floor: Q integer with 1/Q < theta*/4 (practically: theta ~ 1e-3 =>
   Q = 2^14 or 1e5 => 14-17 BIT denominators); lambda_j^(Q) =
   floor(Q max(0, lambda_j^num - eps_sol))/Q, eps_sol ~ 1e-8/solver tolerance.
   Guarantee: r_i^(Q) >= n_i^-(theta* - 1/Q) >= 0 buffered rows; safe rows only
   improve.
 5 EXACT VERIFY: b = p - A lambda^(Q) in exact rationals; all b_i >= 0 => emit
   ConeCert {target = p, base = b, mults = lambda^(Q), slacks = columns}; checkEq
   contract UNCHANGED (slack absorbed into base).
 6 RepairLP fallback: violation set V = {i : b_i < 0} small => column-restricted
   repair (columns with a negative entry on V): A_rep mu + theta n_rep^- <= b,
   floor-round mu, lambda_final = lambda^(Q) + mu^(Q), re-verify. V large =>
   insufficient true margin: rerun BufferLP w/ better objective/larger support.
CONSEQUENCE: replaces ALL vertex/basis-extraction work across the 300 charts;
expected certificate denominators ~15 bits, not thousands.


# ===== RADIAL MONOTONICITY ANALYSIS + SKIP PROTOCOL (main thread, 2026-07-04) =====
FORMULA: on chart k, Ptilde(s,u) = sum_{d=0}^{11} s^(11-d) (1-s)^d P_{k,d}(u)
(homogeneous decomposition of the shifted target); per-term derivative
d/ds [s^(11-d)(1-s)^d P_d] = s^(10-d)(1-s)^(d-1)((11-d) - 11 s) P_d for 0<d<11;
endpoints d=0: 11 s^10 P_0; d=11: -11(1-s)^10 P_11.
ASYMPTOTIC TEST (2.2): decreasing near s=0 iff 11 P_{k,11}(u) - P_{k,10}(u) >= 0
on the simplex (leading positivity alone is NOT enough). If P_top vanishes on a
face use the first nonzero coefficient of the s-expansion.
SKIPS: decreasing cert (-d/ds Ptilde >= 0 on [0,1/2] x Delta) => inf band covered
by near-band s=1/2. Increasing cert => covered by s=0 FaceCert. Neither => no
skip. PARTIAL: monotone on [0,s0] (s0 = 1/8 or 1/4) => residual band [s0,1/2]
only, with generators s-s0 >= 0 and 1/2-s >= 0.
DERIVATIVE CERT FORM: M_k^{+-} = P_0 + sum G^rad P_G + sum Delta^rad P_{a,b} +
B_inf P_inf; G^rad(s,u) = G#(s,(1-s)u); multipliers Bernstein-positive on
[0,1/2] x Delta (substitute sigma = 2s in [0,1]); caps 10/8/8/9 => ~60-75% of the
main chart LP size.
CHART RANKING (seed ray w0..4=1, w5..9=t lives in charts k=0..4): most likely
monotone k=5,6,7,8,9 (seed ray only at t=1); then k=3,4; then k=1,2; k=0 LAST.
Within k: B0, U_A, U_B, F5-F7, then linear dominants. WARNING: k=0/B0-dominant
may not be globally monotone (seed-ray infinity direction + bank-distance
generator near-cancel) — expect at best sub-band skip there.
SWEEP PROTOCOL (before any cert attempt): build M^- and M^+ exactly; sample
s in {0, 1/32, 1/16, 3/32, 1/8, 3/16, 1/4, 3/8, 1/2}, u in {vertices, edge
midpoints, 2/3/4-support barycenters, rational Dirichlet den 16 and 32}; keep
only dominance-satisfying points; sign test both; both signs negative somewhere
=> NO skip attempt; one-signed with margin => attempt that skip cert; near-zero
=> exact boundary polynomials at s=0, 1/2; global fail => sub-band sweep
[0,1/8], [0,1/4]. Cases: A decreasing pass => near-band covers; B increasing =>
FaceCert covers; C sub-band => partial skip + residual band; D none => full
corrected InfCert.

