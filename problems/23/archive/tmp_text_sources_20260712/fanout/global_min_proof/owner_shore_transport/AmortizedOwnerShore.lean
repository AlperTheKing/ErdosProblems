import Erdos23Delta0.Gamma.ActiveScopedVariationReduction

/-!
An endpoint lemma for the surviving owner-shore route.  It deliberately says
nothing about a single-coordinate descent: a coordinated trade may pass through
higher-score intermediate choices.  Transport is used only to prove the net
collision inequality, while persistent-component monotonicity proves the net
HitNeed inequality.
-/

namespace Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

open CertGraph MinimumDemandRowSelection

/-- The exact two-bank endpoint principle for an arbitrary simultaneous trade. -/
theorem scopedObligationScore_lt_of_amortized_banks
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega eta : RowChoice bads)
    (hcollision :
      (scopedCollisionScore G c eta : Int) <
        (scopedCollisionScore G c omega : Int))
    (hhitNeed : scopedHitNeedScore G c eta ≤ scopedHitNeedScore G c omega) :
    scopedObligationScore G c eta < scopedObligationScore G c omega := by
  rw [scopedObligationScore_eq_parts, scopedObligationScore_eq_parts]
  have hhitNeedInt :
      (scopedHitNeedScore G c eta : Int) ≤
        (scopedHitNeedScore G c omega : Int) := by
    exact_mod_cast hhitNeed
  exact_mod_cast add_lt_add_of_lt_of_le hcollision hhitNeedInt

/-- Quantitative version: a positive owner-shore collision credit dominates
all nonpersistent-component activation cost; persistent components contribute
no positive HitNeed variation. -/
theorem scopedObligationScore_lt_of_transport_credit
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega eta : RowChoice bads) (credit activationCost : Nat)
    (hcredit : activationCost < credit)
    (hcollision :
      scopedCollisionScore G c eta + credit ≤
        scopedCollisionScore G c omega + activationCost)
    (hhitNeed : scopedHitNeedScore G c eta ≤ scopedHitNeedScore G c omega) :
    scopedObligationScore G c eta < scopedObligationScore G c omega := by
  apply scopedObligationScore_lt_of_amortized_banks G c omega eta
  · have hwithCost :
        scopedCollisionScore G c eta + activationCost <
          scopedCollisionScore G c omega + activationCost :=
      lt_of_lt_of_le
        (Nat.add_lt_add_left hcredit (scopedCollisionScore G c eta))
        hcollision
    exact_mod_cast Nat.lt_of_add_lt_add_right hwithCost
  · exact hhitNeed

#print axioms scopedObligationScore_lt_of_amortized_banks
#print axioms scopedObligationScore_lt_of_transport_credit

end Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
