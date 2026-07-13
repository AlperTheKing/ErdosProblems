import Erdos23Delta0.Gamma.CommonBlueExtendedMatching

namespace Erdos23Delta0
namespace Gamma
namespace CommonBlueExtendedMatching

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

noncomputable section

def microOwnerSet
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (A : Finset (MicroDemand G c omega)) : Finset (Fin G.n) :=
  A.image microDemandOwner

def microOwnerShore
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (W : Finset (Fin G.n)) : Finset (MicroDemand G c omega) :=
  Finset.univ.filter fun d => microDemandOwner d ∈ W

def MicroOwnerHallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ W : Finset (Fin G.n),
    (microOwnerShore G c omega W).card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ microOwnerShore G c omega W,
          MicroAvailable G c d s).card

theorem microAvailable_congr_owner
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {d e : MicroDemand G c omega} {s : FreeHalf G omega}
    (h : microDemandOwner d = microDemandOwner e) :
    MicroAvailable G c d s ↔ MicroAvailable G c e s := by
  simp only [MicroAvailable]
  rw [h]

theorem microHallCondition_iff_ownerHallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    MicroHallCondition G c omega ↔ MicroOwnerHallCondition G c omega := by
  constructor
  · intro h W
    exact h (microOwnerShore G c omega W)
  · intro h A
    let W := microOwnerSet A
    have hsubset : A ⊆ microOwnerShore G c omega W := by
      intro d hd
      simp only [microOwnerShore, Finset.mem_filter, Finset.mem_univ, true_and]
      exact Finset.mem_image.mpr ⟨d, hd, rfl⟩
    have hneighbors :
        (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ microOwnerShore G c omega W,
            MicroAvailable G c d s) =
        (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ A, MicroAvailable G c d s) := by
      ext s
      simp only [Finset.mem_filter, Finset.mem_univ, true_and]
      constructor
      · rintro ⟨d, hd, havail⟩
        simp only [microOwnerShore, Finset.mem_filter, Finset.mem_univ,
          true_and] at hd
        rcases Finset.mem_image.mp hd with ⟨e, heA, heq⟩
        refine ⟨e, heA, ?_⟩
        exact (microAvailable_congr_owner heq.symm).mp havail
      · rintro ⟨d, hdA, havail⟩
        refine ⟨d, ?_, havail⟩
        simp only [microOwnerShore, Finset.mem_filter, Finset.mem_univ,
          true_and]
        exact Finset.mem_image.mpr ⟨d, hdA, rfl⟩
    calc
      A.card ≤ (microOwnerShore G c omega W).card :=
        Finset.card_le_card hsubset
      _ ≤ (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ microOwnerShore G c omega W,
            MicroAvailable G c d s).card := h W
      _ = (Finset.univ.filter fun s : FreeHalf G omega =>
          ∃ d ∈ A, MicroAvailable G c d s).card := by rw [hneighbors]

#print axioms microAvailable_congr_owner
#print axioms microHallCondition_iff_ownerHallCondition

end
end CommonBlueExtendedMatching
end Gamma
end Erdos23Delta0
