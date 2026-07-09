import Erdos23Delta0.Ell5CSReduction

/-!
# Small Hall obstructions for the ell=5 support problem

This module records the next small T7 step after `geodesics_union_ge_six`:
once every row has support size at least four and every two distinct rows have
combined support at least six, there is no Hall obstruction of size at most six.
-/

namespace Erdos23Delta0
namespace Ell5HallSmall

open Finset

/-- If each row has size at least four and every two distinct rows have union
size at least six, then Hall expansion holds for all sets of at most six rows.

The `≤ 5` part is `Ell5CSReduction.hall_le_five`.  For size exactly six, a
violating set would have total support of size at most five, contradicting the
two-row union lower bound. -/
theorem hall_le_six
    {α β : Type*} [DecidableEq α] [DecidableEq β] (Erow : α → Finset β)
    (h4 : ∀ e, 4 ≤ (Erow e).card)
    (hpair6 : ∀ e f, e ≠ f → 6 ≤ (Erow e ∪ Erow f).card)
    (S : Finset α) (hS : S.card ≤ 6) :
    S.card ≤ (S.biUnion Erow).card := by
  by_cases hsmall : S.card ≤ 5
  · exact Ell5CSReduction.hall_le_five Erow h4
      (fun e f hne => le_trans (by norm_num) (hpair6 e f hne)) S hsmall
  have h6 : S.card = 6 := by omega
  by_contra hnot
  push_neg at hnot
  have hU_lt_six : (S.biUnion Erow).card < 6 := by omega
  have hSpos : 0 < S.card := by omega
  obtain ⟨e, he⟩ := Finset.card_pos.mp hSpos
  have herase : (S.erase e).card = 5 := by
    rw [Finset.card_erase_of_mem he]
    omega
  have herase_pos : 0 < (S.erase e).card := by omega
  obtain ⟨f, hfErase⟩ := Finset.card_pos.mp herase_pos
  have hf_ne : f ≠ e := (Finset.mem_erase.mp hfErase).1
  have hf : f ∈ S := (Finset.mem_erase.mp hfErase).2
  have hsub : Erow e ∪ Erow f ⊆ S.biUnion Erow :=
    Finset.union_subset (Finset.subset_biUnion_of_mem Erow he)
      (Finset.subset_biUnion_of_mem Erow hf)
  have hpair_le : (Erow e ∪ Erow f).card ≤ (S.biUnion Erow).card :=
    Finset.card_le_card hsub
  have hpair_ge : 6 ≤ (Erow e ∪ Erow f).card :=
    hpair6 e f (Ne.symm hf_ne)
  omega

/-- Minimal-obstruction wrapper for the handoff's T7 base case. -/
theorem no_minimal_violator_le_six
    {α β : Type*} [DecidableEq α] [DecidableEq β] (Erow : α → Finset β)
    (h4 : ∀ e, 4 ≤ (Erow e).card)
    (hpair6 : ∀ e f, e ≠ f → 6 ≤ (Erow e ∪ Erow f).card)
    (S : Finset α) (hS : S.card ≤ 6)
    (hlt : (S.biUnion Erow).card < S.card) :
    False := by
  have h := hall_le_six Erow h4 hpair6 S hS
  omega

/-- At most five injectively labelled four-subsets can live inside a five-set. -/
theorem card_le_five_of_four_subsets_of_five
    {α β : Type*} [DecidableEq α] [DecidableEq β] (Erow : α → Finset β)
    (S : Finset α) (U : Finset β)
    (hU : U.card = 5)
    (hsub : ∀ e ∈ S, Erow e ⊆ U)
    (hcard : ∀ e ∈ S, (Erow e).card = 4)
    (hinj : Set.InjOn Erow S) :
    S.card ≤ 5 := by
  have himage_subset : S.image Erow ⊆ U.powersetCard 4 := by
    intro A hA
    rw [Finset.mem_image] at hA
    obtain ⟨e, he, rfl⟩ := hA
    rw [Finset.mem_powersetCard]
    exact ⟨hsub e he, hcard e he⟩
  calc
    S.card = (S.image Erow).card := (Finset.card_image_of_injOn hinj).symm
    _ ≤ (U.powersetCard 4).card := Finset.card_le_card himage_subset
    _ = Nat.choose U.card 4 := Finset.card_powersetCard 4 U
    _ = 5 := by rw [hU]; norm_num

/-- The handoff's intended T7 `m=6` counting form.  A minimal Hall obstruction
with six rows has total support of size five and every row contained in that
support.  If T6 has ruled out five-edge supports, each row is a four-subset of
that five-set; injectivity of row supports then gives at most five rows. -/
theorem no_minimal_violator_card_six_of_no_card_five
    {α β : Type*} [DecidableEq α] [DecidableEq β] (Erow : α → Finset β)
    (S : Finset α)
    (hS : S.card = 6)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (h4 : ∀ e ∈ S, 4 ≤ (Erow e).card)
    (hnot5 : ∀ e ∈ S, (Erow e).card ≠ 5)
    (hinj : Set.InjOn Erow S) :
    False := by
  obtain ⟨hcard, hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hlt hmin
  let U : Finset β := S.biUnion Erow
  have hU : U.card = 5 := by
    dsimp [U]
    omega
  have hsub : ∀ e ∈ S, Erow e ⊆ U := by
    intro e he
    dsimp [U]
    have heraseSub : (S.erase e).biUnion Erow ⊆ S.biUnion Erow := by
      intro x hx
      rw [Finset.mem_biUnion] at hx ⊢
      obtain ⟨a, ha, hax⟩ := hx
      exact ⟨a, Finset.mem_of_mem_erase ha, hax⟩
    exact subset_trans (hnoPrivate e he) heraseSub
  have hrow4 : ∀ e ∈ S, (Erow e).card = 4 := by
    intro e he
    have hle : (Erow e).card ≤ U.card := Finset.card_le_card (hsub e he)
    have hge : 4 ≤ (Erow e).card := h4 e he
    have hne : (Erow e).card ≠ 5 := hnot5 e he
    omega
  have hle5 := card_le_five_of_four_subsets_of_five Erow S U hU hsub hrow4 hinj
  omega
#print axioms hall_le_six
#print axioms no_minimal_violator_le_six
#print axioms card_le_five_of_four_subsets_of_five
#print axioms no_minimal_violator_card_six_of_no_card_five

end Ell5HallSmall
end Erdos23Delta0
