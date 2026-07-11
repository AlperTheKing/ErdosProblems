import Erdos23Delta0.Gamma.CommonBlueExtendedMatching

/-!
# Bank-scale common-blue Hall reduction to owner shores

Every micro-demand owned by the same vertex has the same source
neighborhood.  Consequently any deficient demand shore remains deficient
after saturation by its owner fibers.  The universal bank-scale Hall frontier
therefore reduces exactly to vertex-shore inequalities.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CommonBlueExtendedMatching

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

attribute [local instance] Classical.propDecidable

noncomputable def microOwnerDemandSet
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (Fin G.n)) : Finset (MicroDemand G c omega) :=
  Finset.univ.filter fun d => microDemandOwner d ∈ A

noncomputable def microOwnerSourceSet
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (A : Finset (Fin G.n)) : Finset (FreeHalf G omega) :=
  Finset.univ.filter fun s =>
    ∃ d ∈ microOwnerDemandSet (G := G) (c := c) (omega := omega) A,
      MicroAvailable G c d s

noncomputable def MicroOwnerHallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (Fin G.n),
    (microOwnerDemandSet (G := G) (c := c) (omega := omega) A).card ≤
      (microOwnerSourceSet G c omega A).card

noncomputable def microDemandOwners
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (D : Finset (MicroDemand G c omega)) : Finset (Fin G.n) :=
  D.image microDemandOwner

theorem mem_microDemandOwners_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {D : Finset (MicroDemand G c omega)}
    {owner : Fin G.n} :
    owner ∈ microDemandOwners D ↔
      ∃ d ∈ D, microDemandOwner d = owner := by
  simp [microDemandOwners]

theorem microAvailable_iff_of_owner_eq
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {d e : MicroDemand G c omega}
    (howner : microDemandOwner d = microDemandOwner e)
    (s : FreeHalf G omega) :
    MicroAvailable G c d s ↔ MicroAvailable G c e s := by
  simp only [MicroAvailable, howner]

theorem microDemand_subset_ownerSaturation
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (D : Finset (MicroDemand G c omega)) :
    D ⊆ microOwnerDemandSet (G := G) (c := c) (omega := omega)
      (microDemandOwners D) := by
  intro d hd
  simp only [microOwnerDemandSet, Finset.mem_filter, Finset.mem_univ,
    true_and]
  exact mem_microDemandOwners_iff.mpr ⟨d, hd, rfl⟩

theorem microOwnerSourceSet_demandOwners
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (D : Finset (MicroDemand G c omega)) :
    microOwnerSourceSet G c omega (microDemandOwners D) =
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ D, MicroAvailable G c d s) := by
  ext s
  simp only [microOwnerSourceSet, Finset.mem_filter, Finset.mem_univ,
    true_and]
  constructor
  · rintro ⟨d, hd, havailable⟩
    have howner : microDemandOwner d ∈ microDemandOwners D := by
      simpa only [microOwnerDemandSet, Finset.mem_filter, Finset.mem_univ,
        true_and] using hd
    rcases mem_microDemandOwners_iff.mp howner with ⟨e, he, heowner⟩
    exact ⟨e, he,
      (microAvailable_iff_of_owner_eq heowner.symm s).mp havailable⟩
  · rintro ⟨d, hd, havailable⟩
    exact ⟨d, microDemand_subset_ownerSaturation D hd, havailable⟩

theorem microOwnerHallCondition_of_hallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (hHall : MicroHallCondition G c omega) :
    MicroOwnerHallCondition G c omega := by
  intro A
  simpa only [microOwnerSourceSet] using
    hHall (microOwnerDemandSet (G := G) (c := c) (omega := omega) A)

theorem microHallCondition_of_ownerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (hHall : MicroOwnerHallCondition G c omega) :
    MicroHallCondition G c omega := by
  intro D
  calc
    D.card ≤
        (microOwnerDemandSet (G := G) (c := c) (omega := omega)
          (microDemandOwners D)).card :=
      Finset.card_le_card (microDemand_subset_ownerSaturation D)
    _ ≤ (microOwnerSourceSet G c omega (microDemandOwners D)).card :=
      hHall (microDemandOwners D)
    _ = (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ D, MicroAvailable G c d s).card := by
      exact congrArg Finset.card
        (microOwnerSourceSet_demandOwners G c omega D)

theorem microHallCondition_iff_ownerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    MicroHallCondition G c omega ↔
      MicroOwnerHallCondition G c omega := by
  exact ⟨microOwnerHallCondition_of_hallCondition G c omega,
    microHallCondition_of_ownerHallCondition G c omega⟩

theorem microMatching_nonempty_iff_ownerHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Nonempty (MicroMatching G c omega) ↔
      MicroOwnerHallCondition G c omega := by
  rw [microMatching_nonempty_iff_hall,
    microHallCondition_iff_ownerHallCondition]

theorem microMatching_failure_iff_exists_ownerDefect
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    (¬Nonempty (MicroMatching G c omega)) ↔
      ∃ A : Finset (Fin G.n),
        (microOwnerSourceSet G c omega A).card <
          (microOwnerDemandSet
            (G := G) (c := c) (omega := omega) A).card := by
  rw [microMatching_nonempty_iff_ownerHallCondition]
  simp only [MicroOwnerHallCondition, not_forall, not_le]

end CommonBlueExtendedMatching
end Gamma
end Erdos23Delta0
