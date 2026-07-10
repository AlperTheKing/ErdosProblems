import Erdos23Delta0.PositiveCapacityCornerSplit
import Erdos23Delta0.DisjointPetalHalfSqueeze

/-!
# Positive-capacity split or half-layer reduction

This module packages the exact surviving wall dichotomy.

* If no primitive/positive-bank coupling component meets both corner seeds,
  `PositiveCapacityCornerSplit` gives a proper closed split.  Shared
  zero-capacity sinks are harmless.
* If such a harmful component exists, the only remaining extractor obligation
  is to emit a disjoint-petal positive-alpha TwoCover.  The compiled
  half-layer theorem then refutes the strict dual.

The module deliberately does not claim the real extractor supplies the second
branch.  It isolates that statement as the sole hypothesis `mixedToHalf`.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open DisjointPetalHalfSqueeze

variable {V : Type*} [DecidableEq V]
variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- Concrete half-layer output required from one harmful mixed component. -/
structure PositiveMixedHalfLayerWitness
    (V : Type*) [DecidableEq V] (I : BankedWallLP) (d : Dual I) where
  q : Nat
  walls : Fin q → I.Cut
  route : DisjointPetalRouteData (V := V) I walls
  twoCover : ∀ a : I.Atom, 0 < d.alpha a →
    ∑ i : Fin q, I.cov (walls i) a = 2

/-- Exact real-extractor obligation left after capacity-sensitive splitting. -/
def HarmfulMixedComponentProducesHalfLayer
    (V : Type*) [DecidableEq V]
    (I : BankedWallLP) (d : Dual I)
    (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port) : Prop :=
  ¬NoMixedPositiveCapacityComponent I primitive parent seedL seedR →
    Nonempty (PositiveMixedHalfLayerWitness V I d)

/-- The narrowed dichotomy: either a proper closed bank split exists, or the
checked dual is non-strict.  All remaining geometric content is precisely the
`mixedToHalf` implication. -/
theorem properSplit_or_noStrictGap_of_positiveCapacityDichotomy
    (L : I.Port → ℚ) (d : Dual I) (hd : d.Checked)
    (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port)
    (hseedLne : seedL.Nonempty) (hseedRne : seedR.Nonempty)
    (hseedL : seedL ⊆ parent) (hseedR : seedR ⊆ parent)
    (hblocks : PrimitiveBlockClosureExactOn Q primitive parent)
    (mixedToHalf : HarmfulMixedComponentProducesHalfLayer
      V I d primitive parent seedL seedR) :
    Nonempty (ProperClosedBankSplit Q L parent) ∨ ¬d.StrictGap := by
  classical
  by_cases hNMC :
      NoMixedPositiveCapacityComponent I primitive parent seedL seedR
  · exact Or.inl ⟨properClosedBankSplitOfNoMixedPositiveCapacityComponent
      L primitive parent seedL seedR hseedLne hseedRne hseedL hseedR
      hNMC hblocks hd.cap_nonneg⟩
  · rcases mixedToHalf hNMC with ⟨H⟩
    exact Or.inr
      (noStrictDual_of_disjointPetalTwoCover d hd H.walls H.twoCover H.route)

#print axioms properSplit_or_noStrictGap_of_positiveCapacityDichotomy

end ClosedShore
end Wall
end Erdos23Delta0
