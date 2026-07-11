import Erdos23Delta0.PositiveCapacityCornerSplit

/-!
# Minimal positive-capacity mixed path

Failure of the capacity-sensitive no-mixed-component condition has a finite
simple-path witness. Every edge of that path is either a primitive escape-block
step or is witnessed by one shared legal sink of strictly positive capacity.

This is the exact combinatorial input a real corridor extractor must process.
No graph-geometric conversion to a half-layer is asserted here.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- Explicit step relation after removing harmless zero-capacity sinks. -/
def PositiveCouplingStep
    (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port) (p q : I.Port) : Prop :=
  p ∈ parent ∧ q ∈ parent ∧
    (PrimitiveCoupled primitive p q ∨
      ∃ s : I.Sink, I.legal p s ∧ I.legal q s ∧ 0 < I.cap s)

theorem positiveCouplingStep_of_coupled
    (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port) {p q : I.Port}
    (h : Coupled (positiveCapacityLP I) primitive parent p q) :
    PositiveCouplingStep primitive parent p q := by
  rcases h with ⟨hp, hq, hprimitive | hsink⟩
  · exact ⟨hp, hq, Or.inl hprimitive⟩
  · rcases hsink with ⟨s, ⟨hps, hcapP⟩, ⟨hqs, _hcapQ⟩⟩
    exact ⟨hp, hq, Or.inr ⟨s, hps, hqs, hcapP⟩⟩

theorem positiveCouplingStep_symmetric
    (primitive : I.Port → I.Port → Prop) (parent : Finset I.Port) :
    Symmetric (PositiveCouplingStep (I := I) primitive parent) := by
  intro p q h
  rcases h with ⟨hp, hq, hprimitive | ⟨s, hps, hqs, hcap⟩⟩
  · exact ⟨hq, hp, Or.inl (primitiveCoupled_symmetric primitive hprimitive)⟩
  · exact ⟨hq, hp, Or.inr ⟨s, hqs, hps, hcap⟩⟩

/-- Every adjacency in the positive coupling graph has an explicit positive
sink or primitive-block witness. -/
theorem positiveCouplingStep_of_graphAdj
    (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port) {p q : I.Port}
    (h :
      (couplingGraph (positiveCapacityLP I) primitive parent).Adj p q) :
    PositiveCouplingStep primitive parent p q := by
  rcases
      (SimpleGraph.fromRel_adj
        (Coupled (positiveCapacityLP I) primitive parent) p q).1 h with
    ⟨_hne, hpq | hqp⟩
  · exact positiveCouplingStep_of_coupled primitive parent hpq
  · exact positiveCouplingStep_symmetric primitive parent
      (positiveCouplingStep_of_coupled primitive parent hqp)

/-- A harmful mixed component contains a simple path between actual left and
right seed ports. -/
theorem exists_simplePath_of_not_noMixedPositiveCapacityComponent
    (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port)
    (hseedL : seedL ⊆ parent) (hseedR : seedR ⊆ parent)
    (hbad :
      ¬NoMixedPositiveCapacityComponent I primitive parent seedL seedR) :
    ∃ p ∈ seedL, ∃ q ∈ seedR,
      p ∈ parent ∧ q ∈ parent ∧
      ∃ w :
        (couplingGraph (positiveCapacityLP I) primitive parent).Walk p q,
        w.IsPath := by
  classical
  unfold NoMixedPositiveCapacityComponent NoMixedCornerPortComponent at hbad
  push_neg at hbad
  obtain ⟨p, hpL, q, hqR, hpq⟩ := hbad
  obtain ⟨w, hw⟩ := hpq.exists_isPath
  exact ⟨p, hpL, q, hqR, hseedL hpL, hseedR hqR, w, hw⟩

#print axioms positiveCouplingStep_of_graphAdj
#print axioms exists_simplePath_of_not_noMixedPositiveCapacityComponent

end ClosedShore
end Wall
end Erdos23Delta0
