import Erdos23Delta0.BankedWallLP

/-!
# Restricted-D1 wall squeeze

`BankedWallLP.noStrictDual_of_dualSqueeze` assumes D1 for every routed cut.
The wall W3 route restricts D1 to the allowed family
`singleton ∪ quotientClosed ∪ bankRootedClosure`.  This module records the
same bookkeeping theorem with D1 required only on that allowed family, using
the existing `DualSqueeze.theta_allowed` support condition.
-/

namespace Erdos23Delta0
namespace Wall

open scoped BigOperators

variable {I : BankedWallLP}

/-- A checked dual relative to a restricted cut family.  This is the same dual
as `Dual.Checked`, except D1 is required only for allowed cuts. -/
structure Dual.RestrictedChecked (Allowed : I.Cut → Prop) (d : Dual I) : Prop where
  alpha_nonneg : ∀ a : I.Atom, 0 ≤ d.alpha a
  beta_nonneg : ∀ f : I.Short, 0 ≤ d.beta f
  gamma_nonneg : ∀ p : I.Port, 0 ≤ d.gamma p
  delta_nonneg : ∀ s : I.Sink, 0 ≤ d.delta s
  cap_nonneg : ∀ s : I.Sink, 0 ≤ I.cap s
  d1_allowed : ∀ X : I.Cut, Allowed X → cutAlpha d X ≤ cutBeta d X + cutGamma d X
  d2 : ∀ p s, I.legal p s → d.gamma p ≤ d.delta s

/-- The all-cut checker implies the restricted checker for any `Allowed`. -/
theorem Dual.Checked.restrict {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.Checked) : d.RestrictedChecked Allowed where
  alpha_nonneg := hd.alpha_nonneg
  beta_nonneg := hd.beta_nonneg
  gamma_nonneg := hd.gamma_nonneg
  delta_nonneg := hd.delta_nonneg
  cap_nonneg := hd.cap_nonneg
  d1_allowed := fun X _ => hd.d1 X
  d2 := hd.d2

/-- Restricted-D1 version of `noStrictDual_of_dualSqueeze`.  Only cuts with
nonzero squeeze weight need D1, and `DualSqueeze.theta_allowed` supplies that
membership. -/
theorem noStrictDual_of_restrictedDualSqueeze
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.RestrictedChecked Allowed) (Z : DualSqueeze I Allowed d) :
    ¬ d.StrictGap := by
  intro hstrict
  have h2 : (∑ X : I.Cut, Z.theta X * cutAlpha d X)
      ≤ ∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X) := by
    refine Finset.sum_le_sum fun X _ => ?_
    by_cases htheta : Z.theta X = 0
    · simp [htheta]
    · exact mul_le_mul_of_nonneg_left
        (hd.d1_allowed X (Z.theta_allowed X htheta)) (Z.theta_nonneg X)
  have h3 : (∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X))
      = (∑ X : I.Cut, Z.theta X * cutBeta d X) + ∑ X : I.Cut, Z.theta X * cutGamma d X := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun X _ => mul_add _ _ _
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
      _ = ∑ p : I.Port, ∑ s : I.Sink, Z.rho p s * d.gamma p := by
          simp only [Finset.sum_mul]
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
  have hfinal : totalAlpha d ≤ totalBeta d + totalDeltaCap d :=
    calc totalAlpha d
        ≤ ∑ X : I.Cut, Z.theta X * cutAlpha d X := Z.alpha_dominated
      _ ≤ ∑ X : I.Cut, Z.theta X * (cutBeta d X + cutGamma d X) := h2
      _ = (∑ X : I.Cut, Z.theta X * cutBeta d X) + ∑ X : I.Cut, Z.theta X * cutGamma d X := h3
      _ ≤ totalBeta d + totalDeltaCap d := add_le_add hbeta hgamma
  exact absurd hstrict (not_lt.mpr hfinal)

/-- Existing all-cut squeeze theorem as a corollary of the restricted one. -/
theorem noStrictDual_of_dualSqueeze_via_restricted
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.Checked) (Z : DualSqueeze I Allowed d) : ¬ d.StrictGap :=
  noStrictDual_of_restrictedDualSqueeze hd.restrict Z

end Wall
end Erdos23Delta0
