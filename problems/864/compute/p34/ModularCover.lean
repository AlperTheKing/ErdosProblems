import Mathlib

namespace P34

theorem modular_cover_overlap
    {G : Type*} [Fintype G] [DecidableEq G] [AddCommGroup G]
    (sumset diffset : Finset G)
    (hcard : Fintype.card G < sumset.card + diffset.card)
    (g : G) :
    ∃ s ∈ sumset, ∃ d ∈ diffset, g = s + d := by
  classical
  let translate : Finset G := diffset.image (fun d => g - d)
  have htranslate : translate.card = diffset.card := by
    dsimp [translate]
    exact Finset.card_image_of_injective diffset sub_right_injective
  have hinter : (sumset ∩ translate).Nonempty := by
    apply Finset.inter_nonempty_of_card_lt_card_add_card
      (s := Finset.univ) (t := sumset) (u := translate)
    · exact Finset.subset_univ _
    · exact Finset.subset_univ _
    · simpa [htranslate] using hcard
  rcases hinter with ⟨s, hs⟩
  rcases Finset.mem_inter.mp hs with ⟨hsum, htranslated⟩
  rcases Finset.mem_image.mp htranslated with ⟨d, hdiff, hds⟩
  refine ⟨s, hsum, d, hdiff, ?_⟩
  rw [← hds]
  exact (sub_add_cancel g d).symm

end P34


