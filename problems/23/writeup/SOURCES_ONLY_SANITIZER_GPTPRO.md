# Sources-only defect protocol: source-nullspace sanitizer + escalation ladder (GPT-Pro, MAIN, 2026-07-05)

Source: MAIN thread reply (9571c raw, fully extracted). Faithful structured transcription.

## Classification (source-only decision rule, §7)
b = p − Aλ ≥ 0 everywhere; λ_j < 0 only on a small set C−; |λ−| ≤ 1e-8 after normalization.

## Route 1 (FIRST): source-nullspace sanitizer (§1-3)
Identity-preserving representation fix; residual UNTOUCHED.
- Dominance chart with dominant G_a; for every other generator G_b and every multiplier
  basis element m, EXACT null relation (N): m·G_b + m·Δ_{a,b} − m·G_a = 0
  (columns A_{b,m}, D_{b,m}, A_{a,m}; may ADD absent columns at 0 within the degree cap).
- Per-monomial free rational t_{b,m}; update λ'_{a,m} = λ_{a,m} − Σ_b t; λ'_{b,m} += t;
  λ'_{Δab,m} += t. Solve tiny per-monomial EXACT feasibility λ' ≥ 0 (SN). Objective
  optional: min Σ|t| via t = t+ − t−. Pure Fraction; no float LP.
- Negative column cases: m·G_b (b≠a): positive t. m·Δ_{a,b}: same relation, positive t.
  m·G_a: NEGATIVE t in some relation — needs same-monomial donor mass in a pair
  (m·G_b, m·Δ_{a,b}); block feasibility decides automatically.
- Soundness (§1.4, §8): the added combination is identically zero → target identity,
  residual base, and all residual rows unchanged; final cert is an ORDINARY ConeCert
  (checker never sees the moves). Optional SourceSanitizeLog for debugging; Lean ignores.

## Route 2 (if sanitizer infeasible — ANTICIPATED case, §4)
Infeasibility means: an offending column is outside the dominance-delta dictionary
(e.g. a band generator column), or same-monomial donors insufficient. Then:
- §4.1: ZERO the unresolved negative columns; compute exact b⁰ = p − Aλ⁰;
  H := {i : b⁰_i < 0} (k8/G5 scale: ~14 rows).
- §4.2: NONNEGATIVE additive repair: solve exactly b⁰ − Aμ ≥ 0, μ ≥ 0 with row generation:
  R0 = H ∪ T ∪ D; T = {0 ≤ b⁰_i ≤ 2^-40(1+|p_i|)} cap 256; D = {b⁰_i ≤ 2^-34(1+|p_i|),
  touched by a repair column} cap 512; repair columns J = {j : ∃h∈H, A_hj < 0} ranked by
  score_h(j) = (−A_hj)/(1+Σ_{R0} max(0,A_ij)), TOP 1024 per hard row; objective
  min Σ (1+‖A_j‖_{1,R0}) μ_j; apply full-row; add worst 64 new negatives; MAX 3 rounds.

## Route 3 (both fail, §5): face-split around the dominant generator
G_a# = 0 face (P_face ≥ 0 by ConeCert on remaining constraints) + lift P = P_face + G_a#·M
with M ≥ 0 on the full dominant near region. Exact and sound; NOT a weak certificate.

## FORBIDDEN-first (§6)
- No fresh basis from scratch (reintroduces degeneracy/height).
- No signed active-face repair first (changes residuals, spreads damage — it is for
  residual-negative cases).
- Never declare a negative source "essential" before Routes 1+2 both fail.

## Invocation block (§9, k8/G5; same protocol for k7/G3-class with dominant G3)
mode=source_nullspace_sanitizer; dominant=G5; negative_sources=exact list from checker;
relations: for every b≠G5 and every multiplier monomial m: Gen_b(m)+Delta_G5_b(m)−Gen_G5(m)=0;
solve_per_monomial=true; arithmetic=Fraction; objective=min Σ|t|.
if success: emit sanitized ConeCert. else: zero unresolved negatives; additive_repair
(hard_rows=residual negatives after zeroing, top_gain 1024, tight cap 256, damage cap 512,
rowgen 3). if still fail: route=G_a_face_split.
