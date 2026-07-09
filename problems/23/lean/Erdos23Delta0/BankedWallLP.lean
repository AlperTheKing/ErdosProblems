import Mathlib

/-!
# The banked wall LP core (2026-07-09)

Bookkeeping layer of the WALL ATTACK design (`WALL_ATTACK_R1_GPTPRO.md` §§2-3), compiled with FULL proofs.
The wall (`Ell5FullBankRelaxedCover_globalPackage_exists`) is reduced to killing every strict Farkas dual of a
finite rational banked LP; this module supplies the abstract LP surface and the two soundness theorems:

* `noStrictDual_of_dualSqueeze` — a dual squeeze (nonneg combination of D1 cut inequalities whose port
  coefficients are legally routed to bank sinks within capacity) refutes `StrictGap` for that dual. This is
  the exact point where the BANKED form matters: the only right-hand capacity is `cap`, and at the extractor
  level those sinks are door/vertexSlack/c5Base/prune ONLY (no η field exists anywhere in this module).
* `noStrictDual_of_primal` — the easy Farkas direction (a feasible primal cover refutes every strict dual),
  obtained by viewing the primal as the trivial all-cuts-allowed squeeze (`DualSqueeze.ofPrimal`).

`DualSqueeze` is parameterized by an arbitrary `Allowed : Cut → Prop` restriction so the wall proof can
restrict to singleton / quotient-closed / bank-rooted-closure cuts without this module knowing about them.
Sink kind/source-ID labels, Bool `decide` checkers, and the obstruction extractor attach at the SPEC-1 ledger
level (Codex lane) — deliberately not here, so this module depends on nothing but Mathlib.
No forbidden proof placeholders; axiom-probe expected
`⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace Wall

open scoped BigOperators

/-- A banked wall LP instance. `Cut` is a ROUTED cut atom (two equal vertex shores with different legal
routing profiles may be distinct `Cut` values). No η, local η, or cage η occurs anywhere. -/
structure BankedWallLP where
  Cut : Type
  Atom : Type
  Short : Type
  Port : Type
  Sink : Type
  cutFintype : Fintype Cut
  atomFintype : Fintype Atom
  shortFintype : Fintype Short
  portFintype : Fintype Port
  sinkFintype : Fintype Sink
  /-- Cut `X` separates atom/row `a` (usually 0 or 1). -/
  cov : Cut → Atom → ℚ
  /-- Cut `X` uses in-support short edge `f` (usually 0 or 1). -/
  useShort : Cut → Short → ℚ
  /-- Cut `X` produces off-support load at port `p`. -/
  cutPort : Cut → Port → ℚ
  /-- Legal routing arc from off-support port to bank sink. -/
  legal : Port → Sink → Prop
  legalDecidable : ∀ p s, Decidable (legal p s)
  /-- Bank capacity (door/vertexSlack/c5Base/prune only, labelled at the extractor level). -/
  cap : Sink → ℚ

attribute [instance] BankedWallLP.cutFintype BankedWallLP.atomFintype BankedWallLP.shortFintype
  BankedWallLP.portFintype BankedWallLP.sinkFintype

variable {I : BankedWallLP}

/-- Primal feasibility: a relaxed banked cut cover (weights `lam`, port-to-sink routing `q`). -/
structure Primal (I : BankedWallLP) where
  lam : I.Cut → ℚ
  q : I.Port → I.Sink → ℚ
  lam_nonneg : ∀ X, 0 ≤ lam X
  q_nonneg : ∀ p s, 0 ≤ q p s
  q_legal : ∀ p s, q p s ≠ 0 → I.legal p s
  coverage : ∀ a : I.Atom, 1 ≤ ∑ X : I.Cut, lam X * I.cov X a
  shortCongestion : ∀ f : I.Short, (∑ X : I.Cut, lam X * I.useShort X f) ≤ 1
  portRouted : ∀ p : I.Port, (∑ X : I.Cut, lam X * I.cutPort X p) ≤ ∑ s : I.Sink, q p s
  sinkCapacity : ∀ s : I.Sink, (∑ p : I.Port, q p s) ≤ I.cap s

/-- Dual variables (the exact projected Farkas dual of the banked LP). -/
structure Dual (I : BankedWallLP) where
  alpha : I.Atom → ℚ
  beta : I.Short → ℚ
  gamma : I.Port → ℚ
  delta : I.Sink → ℚ

/-- α-mass a cut collects. -/
def cutAlpha (d : Dual I) (X : I.Cut) : ℚ := ∑ a : I.Atom, I.cov X a * d.alpha a

/-- β-cost a cut pays on in-support short edges. -/
def cutBeta (d : Dual I) (X : I.Cut) : ℚ := ∑ f : I.Short, I.useShort X f * d.beta f

/-- γ-cost a cut pays on off-support ports. -/
def cutGamma (d : Dual I) (X : I.Cut) : ℚ := ∑ p : I.Port, I.cutPort X p * d.gamma p

def totalAlpha (d : Dual I) : ℚ := ∑ a : I.Atom, d.alpha a

def totalBeta (d : Dual I) : ℚ := ∑ f : I.Short, d.beta f

def totalDeltaCap (d : Dual I) : ℚ := ∑ s : I.Sink, I.cap s * d.delta s

/-- A checked banked dual: nonnegativity + D1 (every routed cut inequality) + D2 (legal routing arcs). -/
structure Dual.Checked (d : Dual I) : Prop where
  alpha_nonneg : ∀ a : I.Atom, 0 ≤ d.alpha a
  beta_nonneg : ∀ f : I.Short, 0 ≤ d.beta f
  gamma_nonneg : ∀ p : I.Port, 0 ≤ d.gamma p
  delta_nonneg : ∀ s : I.Sink, 0 ≤ d.delta s
  cap_nonneg : ∀ s : I.Sink, 0 ≤ I.cap s
  d1 : ∀ X : I.Cut, cutAlpha d X ≤ cutBeta d X + cutGamma d X
  d2 : ∀ p s, I.legal p s → d.gamma p ≤ d.delta s

/-- A strict dual witness (would refute the primal cover; the wall = no checked dual is strict). -/
def Dual.StrictGap (d : Dual I) : Prop := totalBeta d + totalDeltaCap d < totalAlpha d

/-- A dual squeeze: a nonnegative combination (`theta`, supported on `Allowed` cuts) of D1 inequalities that
dominates the dual's total α-mass, keeps in-support short-edge coefficients within the unit capacities, and
legally routes the generated port coefficients (`rho`) to bank sinks within capacity. It is NOT a primal
cover: it dominates only this particular dual's α, not every atom uniformly. -/
structure DualSqueeze (I : BankedWallLP) (Allowed : I.Cut → Prop) (d : Dual I) where
  theta : I.Cut → ℚ
  rho : I.Port → I.Sink → ℚ
  theta_nonneg : ∀ X, 0 ≤ theta X
  theta_allowed : ∀ X, theta X ≠ 0 → Allowed X
  rho_nonneg : ∀ p s, 0 ≤ rho p s
  rho_legal : ∀ p s, rho p s ≠ 0 → I.legal p s
  alpha_dominated : totalAlpha d ≤ ∑ X : I.Cut, theta X * cutAlpha d X
  short_coeff : ∀ f : I.Short, (∑ X : I.Cut, theta X * I.useShort X f) ≤ 1
  port_coeff_routed : ∀ p : I.Port, (∑ X : I.Cut, theta X * I.cutPort X p) ≤ ∑ s : I.Sink, rho p s
  sink_coeff : ∀ s : I.Sink, (∑ p : I.Port, rho p s) ≤ I.cap s

/-- **The central bookkeeping theorem**: a dual squeeze refutes the strict gap of a checked dual.
Chain: totalα ≤ Σθ·cutα ≤ Σθ·(cutβ+cutγ); the β-part rearranges to Σ_f (Σθ·use)·β ≤ Σβ = totalβ; the γ-part
rearranges to Σ_p (Σθ·port)·γ ≤ Σ_p (Σ_s ρ)·γ ≤ Σ_s (Σ_p ρ)·δ ≤ Σ_s cap·δ = totalδcap, using D2 on legal
arcs. Hence totalα ≤ totalβ + totalδcap, contradicting `StrictGap`. -/
theorem noStrictDual_of_dualSqueeze {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.Checked) (Z : DualSqueeze I Allowed d) : ¬ d.StrictGap := by
  intro hstrict
  -- D1 under the nonnegative combination
  have h2 : (∑ X : I.Cut, Z.theta X * cutAlpha d X)
      ≤ ∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X) :=
    Finset.sum_le_sum fun X _ => mul_le_mul_of_nonneg_left (hd.d1 X) (Z.theta_nonneg X)
  have h3 : (∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X))
      = (∑ X : I.Cut, Z.theta X * cutBeta d X) + ∑ X : I.Cut, Z.theta X * cutGamma d X := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun X _ => mul_add _ _ _
  -- β side
  have hswapb : (∑ X : I.Cut, Z.theta X * cutBeta d X)
      = ∑ f : I.Short, (∑ X : I.Cut, Z.theta X * I.useShort X f) * d.beta f := by
    simp only [cutBeta, Finset.mul_sum, Finset.sum_mul, mul_assoc]
    rw [Finset.sum_comm]
  have hbeta : (∑ X : I.Cut, Z.theta X * cutBeta d X) ≤ totalBeta d := by
    rw [hswapb]
    refine Finset.sum_le_sum fun f _ => ?_
    calc (∑ X : I.Cut, Z.theta X * I.useShort X f) * d.beta f
        ≤ 1 * d.beta f := mul_le_mul_of_nonneg_right (Z.short_coeff f) (hd.beta_nonneg f)
      _ = d.beta f := one_mul _
  -- γ side
  have hswapg : (∑ X : I.Cut, Z.theta X * cutGamma d X)
      = ∑ p : I.Port, (∑ X : I.Cut, Z.theta X * I.cutPort X p) * d.gamma p := by
    simp only [cutGamma, Finset.mul_sum, Finset.sum_mul, mul_assoc]
    rw [Finset.sum_comm]
  have hgamma : (∑ X : I.Cut, Z.theta X * cutGamma d X) ≤ totalDeltaCap d := by
    rw [hswapg]
    calc (∑ p : I.Port, (∑ X : I.Cut, Z.theta X * I.cutPort X p) * d.gamma p)
        ≤ ∑ p : I.Port, (∑ s : I.Sink, Z.rho p s) * d.gamma p :=
          Finset.sum_le_sum fun p _ =>
            mul_le_mul_of_nonneg_right (Z.port_coeff_routed p) (hd.gamma_nonneg p)
      _ = ∑ p : I.Port, ∑ s : I.Sink, Z.rho p s * d.gamma p := by simp only [Finset.sum_mul]
      _ ≤ ∑ p : I.Port, ∑ s : I.Sink, Z.rho p s * d.delta s := by
          refine Finset.sum_le_sum fun p _ => Finset.sum_le_sum fun s _ => ?_
          by_cases h : Z.rho p s = 0
          · simp [h]
          · exact mul_le_mul_of_nonneg_left (hd.d2 p s (Z.rho_legal p s h)) (Z.rho_nonneg p s)
      _ = ∑ s : I.Sink, (∑ p : I.Port, Z.rho p s) * d.delta s := by
          simp only [Finset.sum_mul]
          rw [Finset.sum_comm]
      _ ≤ totalDeltaCap d :=
          Finset.sum_le_sum fun s _ =>
            mul_le_mul_of_nonneg_right (Z.sink_coeff s) (hd.delta_nonneg s)
  -- combine
  have hfinal : totalAlpha d ≤ totalBeta d + totalDeltaCap d :=
    calc totalAlpha d
        ≤ ∑ X : I.Cut, Z.theta X * cutAlpha d X := Z.alpha_dominated
      _ ≤ ∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X) := h2
      _ = (∑ X : I.Cut, Z.theta X * cutBeta d X) + ∑ X : I.Cut, Z.theta X * cutGamma d X := h3
      _ ≤ totalBeta d + totalDeltaCap d := add_le_add hbeta hgamma
  exact absurd hstrict (not_lt.mpr hfinal)

/-- A feasible primal IS the trivial squeeze (all cuts allowed): coverage + α ≥ 0 gives α-domination. -/
def DualSqueeze.ofPrimal {d : Dual I} (hd : d.Checked) (P : Primal I) :
    DualSqueeze I (fun _ => True) d where
  theta := P.lam
  rho := P.q
  theta_nonneg := P.lam_nonneg
  theta_allowed := fun _ _ => trivial
  rho_nonneg := P.q_nonneg
  rho_legal := P.q_legal
  alpha_dominated := by
    have h0 : totalAlpha d ≤ ∑ a : I.Atom, (∑ X : I.Cut, P.lam X * I.cov X a) * d.alpha a := by
      unfold totalAlpha
      refine Finset.sum_le_sum fun a _ => ?_
      calc d.alpha a = 1 * d.alpha a := (one_mul _).symm
        _ ≤ (∑ X : I.Cut, P.lam X * I.cov X a) * d.alpha a :=
            mul_le_mul_of_nonneg_right (P.coverage a) (hd.alpha_nonneg a)
    have h1 : (∑ a : I.Atom, (∑ X : I.Cut, P.lam X * I.cov X a) * d.alpha a)
        = ∑ X : I.Cut, P.lam X * cutAlpha d X := by
      simp only [cutAlpha, Finset.mul_sum, Finset.sum_mul, mul_assoc]
      rw [Finset.sum_comm]
    exact h0.trans (le_of_eq h1)
  short_coeff := P.shortCongestion
  port_coeff_routed := P.portRouted
  sink_coeff := P.sinkCapacity

/-- **Easy Farkas direction**: a feasible primal banked cover refutes every strict checked dual. This is the
exact-side theorem behind the falsifier format: a `WallFalsifier` (checked dual + StrictGap) on a config with
a verified cover would be an outright contradiction. -/
theorem noStrictDual_of_primal {d : Dual I} (hd : d.Checked) (P : Primal I) : ¬ d.StrictGap :=
  noStrictDual_of_dualSqueeze hd (DualSqueeze.ofPrimal hd P)

end Wall
end Erdos23Delta0
