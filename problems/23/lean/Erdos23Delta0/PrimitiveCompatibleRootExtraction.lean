import Erdos23Delta0.NoMixedCornerPortComponent

/-!
# Unique-root extraction from primitive-compatible legal components

`PrimitiveBlockClosureExactOn` says that primitive-block-saturated subsets of
one parent shore are exactly the closed port sets.  It does not, by itself,
say that a legal-incidence component is primitive-block-saturated; the exact
two-port counterexample in
`PositiveCouplingConnectedNotRootCounterexample.lean` shows that omission is
real.

This module records the repaired implication.  If every block of a given
legal-component partition is primitive-block-saturated, then each block is a
closed shore.  Deficiency additivity supplies a positive block, and minimality
of the parent closed deficiency forces that block to be the whole parent.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open PortHall

variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- Compatibility needed between the primitive closure relation and one
legal-incidence component partition. -/
def LegalComponentsPrimitiveCompatible
    (primitive : I.Port → I.Port → Prop) (parent : Finset I.Port)
    (D : LegalComponentPartition I parent) : Prop :=
  ∀ k : D.K, PrimitiveBlockSaturatedIn primitive parent (D.ports k)

/-- A minimal closed deficient shore has a unique legal root whenever its
legal-component blocks are primitive-compatible. -/
theorem minimalClosedDeficient_has_unique_root_of_primitiveCompatible
    (L : I.Port → ℚ) (primitive : I.Port → I.Port → Prop)
    (parent : Finset I.Port)
    (hMin : MinimalClosedDeficient Q L parent)
    (hblocks : PrimitiveBlockClosureExactOn Q primitive parent)
    (D : LegalComponentPartition I parent)
    (hcompat : LegalComponentsPrimitiveCompatible primitive parent D) :
    Fintype.card D.K = 1 := by
  obtain ⟨_hParentClosed, hParentDeficient, hMinimal⟩ := hMin
  have hsum : deficiencyQ I L parent =
      ∑ k : D.K, deficiencyQ I L (D.ports k) :=
    deficiencyQ_eq_sum_components L D
  have hex : ∃ k : D.K, 0 < deficiencyQ I L (D.ports k) := by
    by_contra h
    push_neg at h
    have hle : deficiencyQ I L parent ≤ 0 := by
      rw [hsum]
      exact Finset.sum_nonpos fun k _ => h k
    exact absurd hParentDeficient (not_lt.mpr hle)
  obtain ⟨k, hk⟩ := hex
  have hkClosed : ClosedPortSet Q (D.ports k) :=
    (hblocks (D.ports k) (D.ports_subset k)).2 (hcompat k)
  have huniq : ∀ l : D.K, l = k := by
    intro l
    by_contra hlk
    obtain ⟨x, hxl⟩ := D.nonempty_ports l
    have hxParent : x ∈ parent := D.ports_subset l hxl
    have hxNotK : x ∉ D.ports k := by
      have hdisj := D.ports_pairwise_disjoint l k hlk
      exact fun hxk => (Finset.disjoint_left.mp hdisj hxl) hxk
    have hkProper : D.ports k ⊂ parent :=
      (Finset.ssubset_iff_of_subset (D.ports_subset k)).mpr
        ⟨x, hxParent, hxNotK⟩
    have hle : deficiencyQ I L (D.ports k) ≤ 0 :=
      hMinimal (D.ports k) hkClosed hkProper
    exact absurd hk (not_lt.mpr hle)
  exact Fintype.card_eq_one_iff.mpr ⟨k, huniq⟩

#print axioms minimalClosedDeficient_has_unique_root_of_primitiveCompatible

end ClosedShore
end Wall
end Erdos23Delta0
