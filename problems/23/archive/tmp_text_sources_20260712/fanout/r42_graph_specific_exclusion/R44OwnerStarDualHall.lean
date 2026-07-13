import Erdos23Delta0.Ell5MinimalCircuitDualHall

/-!
# Dual-Hall pressure on the two t=4 owner stars

In a minimal defect-one circuit every nonempty support set touches one more
atom than its cardinality.  Hence the eight support edges incident with two
rotating owners cannot be touched only by the eight bad edges incident with
those owners: at least one additional bad atom uses an owner-star edge.
-/

namespace Erdos23Delta0
namespace Gamma
namespace R44OwnerStarDualHall

open Finset
open Ell5MinimalCircuitDualHall

variable {Atom Edge : Type*} [DecidableEq Atom] [DecidableEq Edge]

/-- A support subset `W` of size `k`, already touched by a named `k`-atom
family, has an additional incident atom in a minimal defect-one circuit. -/
theorem exists_incidentAtom_outside_named
    (Erow : Atom -> Finset Edge) (S : Finset Atom)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : forall T, T ⊂ S -> T.card <= (T.biUnion Erow).card)
    (W : Finset Edge) (hWne : W.Nonempty)
    (hWU : W ⊆ S.biUnion Erow)
    (named : Finset Atom)
    (hnamedSub : named ⊆ incidentAtoms Erow S W)
    (hnamedCard : named.card = W.card) :
    exists a, a ∈ incidentAtoms Erow S W ∧ a ∉ named := by
  have hstrict := card_add_one_le_incidentAtoms
    Erow S hlt hmin W hWne hWU
  by_contra hnone
  have hIncSub : incidentAtoms Erow S W ⊆ named := by
    intro a ha
    by_contra han
    exact hnone ⟨a, ha, han⟩
  have hEq : incidentAtoms Erow S W = named :=
    Finset.Subset.antisymm hIncSub hnamedSub
  rw [hEq, hnamedCard] at hstrict
  omega

/-- Specialization to the t=4 two-owner star union: eight named incident
bad atoms cannot account for all atoms using the eight owner-star edges. -/
theorem t4_two_owner_stars_have_external_atom
    (Erow : Atom -> Finset Edge) (S : Finset Atom)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : forall T, T ⊂ S -> T.card <= (T.biUnion Erow).card)
    (ownerStarEdges : Finset Edge)
    (hstarCard : ownerStarEdges.card = 8)
    (hstarSub : ownerStarEdges ⊆ S.biUnion Erow)
    (ownerBadAtoms : Finset Atom)
    (hownerCard : ownerBadAtoms.card = 8)
    (hownerSub : ownerBadAtoms ⊆
      incidentAtoms Erow S ownerStarEdges) :
    exists a, a ∈ incidentAtoms Erow S ownerStarEdges ∧
      a ∉ ownerBadAtoms := by
  have hne : ownerStarEdges.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro hempty
    rw [hempty] at hstarCard
    simp at hstarCard
  exact exists_incidentAtom_outside_named Erow S hlt hmin
    ownerStarEdges hne hstarSub ownerBadAtoms hownerSub
    (hownerCard.trans hstarCard.symm)

#print axioms exists_incidentAtom_outside_named
#print axioms t4_two_owner_stars_have_external_atom

end R44OwnerStarDualHall
end Gamma
end Erdos23Delta0
