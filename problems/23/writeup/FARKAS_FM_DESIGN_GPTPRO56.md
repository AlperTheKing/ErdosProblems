# Finite rational Farkas — implementation design (GPT-5.6 Pro, 2026-07-09, RELAYED VERBATIM BY USER)

*Answers the finite-Farkas route question (lane 1): route (1) = constructive Fourier–Motzkin over ℚ; do NOT
pass through ℝ (ProperCone.map uses closure ⟹ extra finite-generation obligations; linarith's FM engine is a
meta-oracle, not an exported theorem).*

**[CLAUDE gate header:**
- λ-positivity check VERIFIED by hand: λ=0 in HomStrictDual forces Σβ + Σ cap·δ < 0 against β,δ,cap ≥ 0 —
  contradiction; so only `hcap` is needed, NOT alpha_nonneg. Sound.
- FM induction design sound: Row quantified AFTER n so the IH is polymorphic in the new ElimRow type;
  base n=0 correct; weight nonneg + head-cancellation are the two structural lemmas; feasibility lifting =
  one finite interval lemma (exists_between_finsets via Finset.max'/min'); certificate lifting = lift_dot
  (sum_comm + mul_sum + sum_mul). Augmentation rows encode x ≥ 0. All standard and checkable.
- PATH ADAPTATION (ours, not the reply's): implement under problems/23/lean/Erdos23Delta0/ as RatFM.lean,
  RatFarkas.lean, FullBankLPEncoding.lean, FullBankDualNormalization.lean, DualSqueezeAlternative.lean
  (NOT FormalConjectures/LinearProgramming/ — final PR placement decided at assembly).
- Encoding must align with the COMPILED BankedWallLP.DualSqueeze (theta over all cuts with Allowed-support ↔
  their AllowedCut subtype — equivalent; the dualSqueeze_iff_lpFeasible bridge carries it).
- Codex (5.6 Sol Ultra) = implementation owner per lane post 22:30Z; my gate unchanged.**]

---

## VERBATIM REPLY

# Decision: route (1), constructive Fourier–Motzkin over `ℚ`
Prove one generic finite rational alternative by eliminating **unrestricted** variables, then encode `x ≥ 0`
as additional inequality rows. Do not pass through `ℝ`.
The real-cone route is longer in Mathlib: `ProperCone.hyperplane_separation'` separates a point from a
`ProperCone`, but `ProperCone.map` is defined using the **closure** of the image. For a generated column
cone, that leaves a separate finite-generation/closedness proof before separation even applies. Afterward,
one still has to rationalize a real separator while preserving weak inequalities.
Do not treat the Fourier–Motzkin engine behind `linarith` as the theorem — it is a meta-level oracle.
No rational-transfer lemma is needed on this route.

## 1. Generic rational theorem and sign convention
Convention: b_i ≤ Σ_j A_ij x_j, x_j ≥ 0. Strict certificate: y ≥ 0, Σ_i y_i A_ij ≤ 0 ∀j, 0 < Σ_i y_i b_i.

```lean
namespace RatFarkas
def NonnegFeasible {Row Var} [Fintype Row] [Fintype Var] (A : Matrix Row Var ℚ) (b : Row → ℚ) : Prop :=
  ∃ x : Var → ℚ, (∀ j, 0 ≤ x j) ∧ ∀ i, b i ≤ ∑ j, A i j * x j
def StrictCertificate {Row Var} [Fintype Row] [Fintype Var] (A : Matrix Row Var ℚ) (b : Row → ℚ) : Prop :=
  ∃ y : Row → ℚ, (∀ i, 0 ≤ y i) ∧ (∀ j, ∑ i, y i * A i j ≤ 0) ∧ 0 < ∑ i, y i * b i
theorem strictCertificate_of_not_nonnegFeasible (A b) (h : ¬ NonnegFeasible A b) : StrictCertificate A b
theorem finite_rat_farkas (A b) : NonnegFeasible A b ↔ ¬ StrictCertificate A b
```
Easy direction = the standard finite-sum calculation (y·b ≤ y·Ax = Σ_j x_j(Σ_i y_i A_ij) ≤ 0). The only
substantial theorem is strictCertificate_of_not_nonnegFeasible.

## 2. Unrestricted-variable alternative first (namespace RatFM)
FreeFeasible (no sign restriction on x); FreeCertificate has column EQUALITY Σ_i y_i A_ij = 0.
```lean
theorem freeCertificate_of_not_freeFeasible :
    ∀ (n : ℕ) {Row} [Fintype Row] (A : Matrix Row (Fin n) ℚ) (b : Row → ℚ),
      ¬ FreeFeasible A b → FreeCertificate A b
```
**Quantifier order matters**: Row after n, so the IH instantiates at the new FM row type.
Base n = 0: FreeFeasible ⟺ ∀ i, b i ≤ 0; from negation take i₀ with 0 < b i₀; y := indicator i₀.

## 3. Exact FM elimination step
a i := A i 0; partition rows: HeadPos {0 < a}, HeadNeg {a < 0}, HeadZero {a = 0};
ElimRow := HeadZero ⊕ (HeadPos × HeadNeg). Weights: w_z = 1_{i=z}; w_{p,q}(i) = (−a_q)·1_{i=p} + a_p·1_{i=q}
(both coefficients strictly positive). Structural lemmas: weight_nonneg; weight_head_eq_zero
(Σ_i w_r(i)·A i 0 = 0). elimA r j := Σ_i w_r(i)·A i j.succ; elimB r := Σ_i w_r(i)·b i.
Only two directions needed: freeFeasible_of_elim (lift feasible tail) and freeCertificate_of_elim.

### 3.1 Feasibility lifting = one finite interval lemma
r_i := Σ_{j<n} A_{i,j+1} x_j; L_p := (b_p − r_p)/a_p; U_q := (r_q − b_q)/(−a_q). The (p,q) eliminated
inequality ⟺ L_p ≤ U_q (via div_le_iff₀ / le_div_iff₀ with a_p > 0, −a_q > 0).
```lean
lemma exists_between_finsets (L U : Finset ℚ) (hLU : ∀ l ∈ L, ∀ u ∈ U, l ≤ u) :
    ∃ t, (∀ l ∈ L, l ≤ t) ∧ ∀ u ∈ U, t ≤ u
-- L.Nonempty → L.max'; else U.Nonempty → U.min'; else 0.  (Finset.max'/le_max'/max'_le/min'/min'_le/le_min')
```
Apply to the images of L_p over HeadPos and U_q over HeadNeg; full vector := Fin.cons t x; split sums with
Fin.sum_univ_succ.

### 3.2 Certificate lifting = finite-sum interchange
y_i := Σ_r y'_r · w_r(i); one helper lift_dot: Σ_i (Σ_r y'_r w_r(i))·v i = Σ_r y'_r·(Σ_i w_r(i)·v i)
(sum_comm + mul_sum + sum_mul). Nonneg via sum_nonneg+mul_nonneg; head column zero by weight_head_eq_zero;
tail columns and objective transport exactly.

## 4. Nonneg variables via row augmentation
AugRow := Row ⊕ Fin n; augA (inr k) j := if j = k then 1 else 0; augB (inr _) := 0. Free feasibility of the
augmented system ⟺ original + x ≥ 0. A free certificate z splits y := z∘inl, s := z∘inr with
Σ_i y_i A_ij + s_j = 0 ⟹ Σ_i y_i A_ij ≤ 0 (s_j ≥ 0); objective unchanged. Arbitrary finite Var via
Fintype.equivFin + Equiv.sum_comp.

## 5. Exact FullBank LP encoding
```lean
abbrev AllowedCut := {X : Cut // Allowed X}
abbrev LegalArc := {a : Port × Sink // Legal a.1 a.2}
abbrev LPVar := AllowedCut ⊕ LegalArc
inductive LPRow | alpha | short (f : Short) | port (p : Port) | sink (s : Sink)
  deriving DecidableEq, Fintype
```
| Row r | b_r | A_{r,θ_X} | A_{r,ρ_{q,t}} |
|---|---|---|---|
| alpha | T := totalAlpha α | cutAlpha α X | 0 |
| short f | −1 | −useShort X f | 0 |
| port p | 0 | −cutPort X p | 1 if q=p else 0 |
| sink s | −cap s | 0 | −1 if t=s else 0 |

Bridge: dualSqueeze_iff_lpFeasible (mostly simp + Sum-splitting).

## 6. Generic certificate = homogeneous restricted dual
y decodes as λ := y.alpha, β := y∘short, γ := y∘port, δ := y∘sink. Cut column: λ·cutAlpha ≤ cutBeta+cutGamma;
arc column: γ_p ≤ δ_s; strict objective: Σβ + Σcap·δ < λ·T. HomStrictDual packages this;
lpCertificate_iff_homStrictDual is case-splitting on LPRow only (not another duality theorem).

## 7. Normalization incl λ = 0
```lean
lemma homStrictDual_lambda_pos (hcap : ∀ s, 0 ≤ cap s) (h : HomStrictDual ...) : 0 < λ
-- λ = 0 ⟹ Σβ + Σ cap·δ < 0 against β,δ,cap ≥ 0. Uses hcap, hβ, hδ; NOT γ≥0; NOT alpha_nonneg.
```
Then divide by λ: cutBeta_div/cutGamma_div (Finset.sum_div); D1 via le_div_iff₀; D2 via
div_le_div_iff_of_pos_right; strictness via div_lt_iff₀. homStrictDual_iff_restrictedStrictDual
(reverse: λ := 1). RestrictedStrictDual = the desired certificate (no λ).

## 8. Final theorem (no linear algebra in the assembly)
```lean
theorem dualSqueeze_iff_not_restrictedStrictDual (hcap : ∀ s, 0 ≤ cap s) :
    (∃ θ ρ, DualSqueeze α cap θ ρ) ↔ ¬ ∃ β γ δ, RestrictedStrictDual α cap β γ δ :=
  dualSqueeze_iff_lpFeasible.trans (finite_rat_farkas _ _) |>.trans (not_congr ...) ...
```

## 9. Module order (ADAPTED PATHS — see gate header)
RatFM.lean (FreeFeasible/FreeCertificate/freeCertificate_of_not_freeFeasible; keep FM internals private) →
RatFarkas.lean (NonnegFeasible/StrictCertificate/finite_rat_farkas) → FullBankLPEncoding.lean (LPRow/LPVar/
lpA/lpB/dualSqueeze_iff_lpFeasible/HomStrictDual/lpCertificate_iff_homStrictDual) →
FullBankDualNormalization.lean (RestrictedStrictDual/homStrictDual_lambda_pos/div lemmas/
homStrictDual_iff_restrictedStrictDual) → DualSqueezeAlternative.lean (final iff only).

## 10. Axiom gate
Exact over ℚ; classical but ordinary. #print axioms on freeCertificate_of_not_freeFeasible,
finite_rat_farkas, dualSqueeze_iff_not_restrictedStrictDual — expected ⊆ [propext, Classical.choice,
Quot.sound]. **The central implementation gate is freeFeasible_of_elim**; once exists_between_finsets is
isolated, everything else is finite-sum algebra or row/column decoding.
