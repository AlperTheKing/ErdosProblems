import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
# Active-scoped Hall reduction to owner shores

Availability of an active collision or endpoint-hit demand depends only on
its owner.  Hence every deficient demand shore can be saturated by owners
without changing its source neighborhood.  This reduces the corrected Hall
frontier to a finite set of vertex-shore inequalities.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall

attribute [local instance] Classical.propDecidable

noncomputable def scopedOwnerDemandSet {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (Demand G c omega) :=
  Finset.univ.filter fun d => demandOwner d ∈ A

noncomputable def scopedOwnerSourceSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  Finset.univ.filter fun s =>
    ∃ d ∈ scopedOwnerDemandSet (G := G) (c := c) (omega := omega) A,
      Available G c d s

noncomputable def ScopedOwnerHallCondition (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (Fin G.n),
    (scopedOwnerDemandSet (G := G) (c := c) (omega := omega) A).card ≤
      (scopedOwnerSourceSet G c omega A).card

noncomputable def scopedDemandOwners {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (D : Finset (Demand G c omega)) : Finset (Fin G.n) :=
  D.image demandOwner

theorem mem_scopedDemandOwners_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {D : Finset (Demand G c omega)}
    {owner : Fin G.n} :
    owner ∈ scopedDemandOwners D ↔
      ∃ d ∈ D, demandOwner d = owner := by
  simp [scopedDemandOwners]

theorem available_iff_of_demandOwner_eq
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {d e : Demand G c omega}
    (howner : demandOwner d = demandOwner e) (s : FreeHalf G omega) :
    Available G c d s ↔ Available G c e s := by
  simp only [Available, EligibleOwner, howner]

theorem scopedDemand_subset_ownerSaturation
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (D : Finset (Demand G c omega)) :
    D ⊆ scopedOwnerDemandSet (G := G) (c := c) (omega := omega)
      (scopedDemandOwners D) := by
  intro d hd
  simp only [scopedOwnerDemandSet, Finset.mem_filter, Finset.mem_univ,
    true_and]
  exact mem_scopedDemandOwners_iff.mpr ⟨d, hd, rfl⟩

theorem scopedOwnerSourceSet_demandOwners
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (D : Finset (Demand G c omega)) :
    scopedOwnerSourceSet G c omega (scopedDemandOwners D) =
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ D, Available G c d s) := by
  ext s
  simp only [scopedOwnerSourceSet, Finset.mem_filter, Finset.mem_univ,
    true_and]
  constructor
  · rintro ⟨d, hd, havailable⟩
    have howner : demandOwner d ∈ scopedDemandOwners D := by
      simpa only [scopedOwnerDemandSet, Finset.mem_filter, Finset.mem_univ,
        true_and] using hd
    rcases mem_scopedDemandOwners_iff.mp howner with ⟨e, he, heowner⟩
    exact ⟨e, he,
      (available_iff_of_demandOwner_eq heowner.symm s).mp havailable⟩
  · rintro ⟨d, hd, havailable⟩
    exact ⟨d, scopedDemand_subset_ownerSaturation D hd, havailable⟩

theorem scopedOwnerHallCondition_of_hallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (hHall : HallCondition G c omega) :
    ScopedOwnerHallCondition G c omega := by
  intro A
  simpa only [scopedOwnerSourceSet] using
    hHall (scopedOwnerDemandSet (G := G) (c := c) (omega := omega) A)

theorem hallCondition_of_scopedOwnerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (hHall : ScopedOwnerHallCondition G c omega) :
    HallCondition G c omega := by
  intro D
  calc
    D.card ≤
        (scopedOwnerDemandSet (G := G) (c := c) (omega := omega)
          (scopedDemandOwners D)).card :=
      Finset.card_le_card (scopedDemand_subset_ownerSaturation D)
    _ ≤ (scopedOwnerSourceSet G c omega (scopedDemandOwners D)).card :=
      hHall (scopedDemandOwners D)
    _ = (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ D, Available G c d s).card := by
      exact congrArg Finset.card (scopedOwnerSourceSet_demandOwners G c omega D)

theorem hallCondition_iff_scopedOwnerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    HallCondition G c omega ↔ ScopedOwnerHallCondition G c omega := by
  exact ⟨scopedOwnerHallCondition_of_hallCondition G c omega,
    hallCondition_of_scopedOwnerHallCondition G c omega⟩

theorem matching_nonempty_iff_scopedOwnerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Nonempty (Matching G c omega) ↔ ScopedOwnerHallCondition G c omega := by
  rw [matching_nonempty_iff_hall,
    hallCondition_iff_scopedOwnerHallCondition]

theorem matching_failure_iff_exists_scopedOwner_defect
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    (¬Nonempty (Matching G c omega)) ↔
      ∃ A : Finset (Fin G.n),
        (scopedOwnerSourceSet G c omega A).card <
          (scopedOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card := by
  rw [matching_nonempty_iff_scopedOwnerHallCondition]
  simp only [ScopedOwnerHallCondition, not_forall, not_le]

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
