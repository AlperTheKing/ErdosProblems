import Mathlib

/-!
# The first forced overlap in the t = 4, k = 2 window

Two rotating owners contribute disjoint four-edge support stars.  Their four
distinct bad endpoints contribute four final support edges each, all external
to both owners.  If the complete support union has at most fifteen edges, the
two final-edge families cannot be disjoint.
-/

namespace Erdos23Delta0
namespace Gamma
namespace R44K2TailOverlap

structure K2TailIncidence (Edge : Type*) [DecidableEq Edge] where
  support : Finset Edge
  atV : Finset Edge
  atM : Finset Edge
  tailV : Finset Edge
  tailM : Finset Edge
  atV_subset : atV ⊆ support
  atM_subset : atM ⊆ support
  tailV_subset : tailV ⊆ support
  tailM_subset : tailM ⊆ support
  disjointVM : Disjoint atV atM
  disjointV_tailV : Disjoint atV tailV
  disjointV_tailM : Disjoint atV tailM
  disjointM_tailV : Disjoint atM tailV
  disjointM_tailM : Disjoint atM tailM
  four_le_atV : 4 ≤ atV.card
  four_le_atM : 4 ≤ atM.card
  four_le_tailV : 4 ≤ tailV.card
  four_le_tailM : 4 ≤ tailM.card

namespace K2TailIncidence

variable {Edge : Type*} [DecidableEq Edge]

private theorem disjoint_union_left
    {a b c : Finset Edge} (hac : Disjoint a c) (hbc : Disjoint b c) :
    Disjoint (a ∪ b) c := by
  rw [Finset.disjoint_left]
  intro e he hec
  rcases Finset.mem_union.mp he with hea | heb
  · exact (Finset.disjoint_left.mp hac) hea hec
  · exact (Finset.disjoint_left.mp hbc) heb hec

private theorem incident_disjoint_tailUnion (F : K2TailIncidence Edge) :
    Disjoint (F.atV ∪ F.atM) (F.tailV ∪ F.tailM) := by
  rw [Finset.disjoint_left]
  intro e heIncident heTail
  rcases Finset.mem_union.mp heIncident with heV | heM
  · rcases Finset.mem_union.mp heTail with heTV | heTM
    · exact (Finset.disjoint_left.mp F.disjointV_tailV) heV heTV
    · exact (Finset.disjoint_left.mp F.disjointV_tailM) heV heTM
  · rcases Finset.mem_union.mp heTail with heTV | heTM
    · exact (Finset.disjoint_left.mp F.disjointM_tailV) heM heTV
    · exact (Finset.disjoint_left.mp F.disjointM_tailM) heM heTM

/-- If the two tail families were disjoint, the support union would have at
least sixteen edges. -/
theorem sixteen_le_support_card_of_disjoint_tails
    (F : K2TailIncidence Edge) (hTail : Disjoint F.tailV F.tailM) :
    16 ≤ F.support.card := by
  have hsub : (F.atV ∪ F.atM) ∪ (F.tailV ∪ F.tailM) ⊆ F.support := by
    intro e he
    simp only [Finset.mem_union] at he
    rcases he with (heV | heM) | heTV | heTM
    · exact F.atV_subset heV
    · exact F.atM_subset heM
    · exact F.tailV_subset heTV
    · exact F.tailM_subset heTM
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint F.incident_disjoint_tailUnion,
    Finset.card_union_of_disjoint F.disjointVM,
    Finset.card_union_of_disjoint hTail] at hcard
  have hV := F.four_le_atV
  have hM := F.four_le_atM
  have hTV := F.four_le_tailV
  have hTM := F.four_le_tailM
  omega

/-- A fifteen-edge t=4 support union forces a common final support edge. -/
theorem exists_common_tail_of_support_card_le_fifteen
    (F : K2TailIncidence Edge) (hcap : F.support.card ≤ 15) :
    ∃ e, e ∈ F.tailV ∧ e ∈ F.tailM := by
  by_contra hnone
  have hdisjoint : Disjoint F.tailV F.tailM := by
    rw [Finset.disjoint_left]
    intro e heV heM
    exact hnone ⟨e, heV, heM⟩
  have := F.sixteen_le_support_card_of_disjoint_tails hdisjoint
  omega

#print axioms sixteen_le_support_card_of_disjoint_tails
#print axioms exists_common_tail_of_support_card_le_fifteen

end K2TailIncidence
end R44K2TailOverlap
end Gamma
end Erdos23Delta0
