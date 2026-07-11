import Erdos23Delta0.Gamma.CollisionOwnerHallReduction

/-!
# Collision owner-source load reduction

The owner-saturated source neighborhood splits according to whether the first
source coordinate lies in the owner shore.  Outside the shore, same-owner
cancellation is impossible, so every available source is witnessed by a row
companion.  This gives an exact scalar owner-Hall inequality with separate
same-owner and companion-only loads.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionHall

open CertGraph
open MinimumDemandRowSelection

/-- The part of the actual owner-source neighborhood whose first coordinate
lies in the owner shore. -/
def sameOwnerSourceSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  (ownerSourceSet G c (omega := omega) A).filter fun s => s.sourceX ∈ A

/-- The part of the actual owner-source neighborhood whose first coordinate
lies outside the owner shore. -/
def companionOnlySourceSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  (ownerSourceSet G c (omega := omega) A).filter fun s => s.sourceX ∉ A

@[simp] theorem mem_sameOwnerSourceSet_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega} :
    s ∈ sameOwnerSourceSet G c (omega := omega) A ↔
      s ∈ ownerSourceSet G c (omega := omega) A ∧ s.sourceX ∈ A := by
  simp [sameOwnerSourceSet]

/-- Every source in the same-owner side of the partition is unreserved. -/
theorem sameOwnerSource_unreserved
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega}
    (hs : s ∈ sameOwnerSourceSet G c (omega := omega) A) :
    ¬Reserved G c omega s := by
  have hsource := (mem_sameOwnerSourceSet_iff.mp hs).1
  simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
    true_and] at hsource
  rcases hsource with ⟨d, _hd, havailable⟩
  exact havailable.2

/-- Outside the owner shore, availability is exactly unreserved
row-companion availability to a collision demand owned in the shore. -/
theorem mem_companionOnlySourceSet_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {A : Finset (Fin G.n)}
    {s : FreeHalf G omega} :
    s ∈ companionOnlySourceSet G c (omega := omega) A ↔
      s.sourceX ∉ A ∧
      ¬Reserved G c omega s ∧
      ∃ d ∈ ownerDemandSet (G := G) (omega := omega) A,
        RowCompanion G c d s := by
  constructor
  · intro hs
    have hparts :
        s ∈ ownerSourceSet G c (omega := omega) A ∧ s.sourceX ∉ A := by
      simpa [companionOnlySourceSet] using hs
    have hsource := hparts.1
    simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
      true_and] at hsource
    rcases hsource with ⟨d, hd, havailable⟩
    have hunreserved : ¬Reserved G c omega s := havailable.2
    have heligible := havailable.1
    unfold Eligible at heligible
    have hcompanion : RowCompanion G c d s := by
      rcases heligible with hsame | hcompanion
      · have howner : d.owner ∈ A := by
          simpa only [ownerDemandSet, Finset.mem_filter, Finset.mem_univ,
            true_and] using hd
        unfold SameOwner at hsame
        exact False.elim (hparts.2 (by simpa [hsame] using howner))
      · exact hcompanion
    exact ⟨hparts.2, hunreserved, d, hd, hcompanion⟩
  · rintro ⟨houtside, hunreserved, d, hd, hcompanion⟩
    simp only [companionOnlySourceSet, Finset.mem_filter]
    refine ⟨?_, houtside⟩
    simp only [ownerSourceSet, Finset.mem_filter, Finset.mem_univ,
      true_and]
    exact ⟨d, hd, ⟨Or.inr hcompanion, hunreserved⟩⟩

/-- The two source buckets are disjoint. -/
theorem sameOwnerSourceSet_disjoint_companionOnlySourceSet
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    Disjoint (sameOwnerSourceSet G c (omega := omega) A)
      (companionOnlySourceSet G c (omega := omega) A) := by
  rw [Finset.disjoint_left]
  intro s hsame hcompanion
  exact (mem_companionOnlySourceSet_iff.mp hcompanion).1
    (mem_sameOwnerSourceSet_iff.mp hsame).2

/-- The two source buckets exhaust the owner-source neighborhood. -/
theorem sameOwnerSourceSet_union_companionOnlySourceSet
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    sameOwnerSourceSet G c (omega := omega) A ∪
        companionOnlySourceSet G c (omega := omega) A =
      ownerSourceSet G c (omega := omega) A := by
  ext s
  by_cases hs : s.sourceX ∈ A <;>
    simp [sameOwnerSourceSet, companionOnlySourceSet, hs]

/-- Cardinal form of the exact source partition. -/
theorem ownerSourceSet_card_eq_sameOwner_add_companionOnly
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    (ownerSourceSet G c (omega := omega) A).card =
      (sameOwnerSourceSet G c (omega := omega) A).card +
        (companionOnlySourceSet G c (omega := omega) A).card := by
  calc
    (ownerSourceSet G c (omega := omega) A).card =
        (sameOwnerSourceSet G c (omega := omega) A ∪
          companionOnlySourceSet G c (omega := omega) A).card :=
      congrArg Finset.card
        (sameOwnerSourceSet_union_companionOnlySourceSet G c A).symm
    _ = (sameOwnerSourceSet G c (omega := omega) A).card +
        (companionOnlySourceSet G c (omega := omega) A).card :=
      Finset.card_union_of_disjoint
        (sameOwnerSourceSet_disjoint_companionOnlySourceSet G c A)

/-- Scalar same-owner-side source load. -/
def sameOwnerUnits (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Nat :=
  (sameOwnerSourceSet G c (omega := omega) A).card

/-- Scalar companion-only source load. -/
def companionOnlyUnits (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Nat :=
  (companionOnlySourceSet G c (omega := omega) A).card

theorem ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (A : Finset (Fin G.n)) :
    ownerSourceUnits G c (omega := omega) A =
      sameOwnerUnits G c (omega := omega) A +
        companionOnlyUnits G c (omega := omega) A := by
  exact ownerSourceSet_card_eq_sameOwner_add_companionOnly G c A

/-- Owner Hall is exactly demand load bounded by the two disjoint source
loads for every owner shore. -/
theorem ownerHallCondition_iff_ownerLoadUnits
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} :
    OwnerHallCondition G c omega ↔
      ∀ A : Finset (Fin G.n),
        ownerDemandUnits (G := G) omega A ≤
          sameOwnerUnits G c (omega := omega) A +
            companionOnlyUnits G c (omega := omega) A := by
  rw [ownerHallCondition_iff_ownerUnits]
  constructor
  · intro h A
    rw [← ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits]
    exact h A
  · intro h A
    rw [ownerSourceUnits_eq_sameOwnerUnits_add_companionOnlyUnits]
    exact h A

#print axioms mem_companionOnlySourceSet_iff
#print axioms sameOwnerSourceSet_union_companionOnlySourceSet
#print axioms ownerSourceSet_card_eq_sameOwner_add_companionOnly
#print axioms ownerHallCondition_iff_ownerLoadUnits

end CanonicalCollisionHall
end Gamma
end Erdos23Delta0
