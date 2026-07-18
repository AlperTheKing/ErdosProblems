import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Circulant

/-! Direct `C5`-blow-up total-domination transfer prototype. -/

namespace WOWII314.BlowupTest

open SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α} [DecidableRel G.Adj]

/-- A graph whose adjacency is pulled back from `C5` along a surjective bag map. -/
structure IsC5Blowup (G : SimpleGraph α) [DecidableRel G.Adj]
    (bag : α → Fin 5) : Prop where
  surjective : Function.Surjective bag
  adj_iff : ∀ u v, G.Adj u v ↔ (cycleGraph 5).Adj (bag u) (bag v)

lemma blowup_totalDominatingSet_iff
    {bag : α → Fin 5} (hB : IsC5Blowup G bag) (S : Finset α) :
    IsTotalDominatingSet G S ↔
      IsTotalDominatingSet (cycleGraph 5) (S.image bag) := by
  constructor
  · intro hS i
    obtain ⟨u, hu⟩ := hB.surjective i
    obtain ⟨v, hvS, huv⟩ := hS u
    refine ⟨bag v, Finset.mem_image.mpr ⟨v, hvS, rfl⟩, ?_⟩
    rw [← hu]
    exact (hB.adj_iff u v).mp huv
  · intro hSupport u
    obtain ⟨j, hjSupport, huj⟩ := hSupport (bag u)
    obtain ⟨v, hvS, hvj⟩ := Finset.mem_image.mp hjSupport
    refine ⟨v, hvS, ?_⟩
    apply (hB.adj_iff u v).mpr
    simpa [hvj] using huj

lemma blowup_bag_injOn_of_minimal
    {bag : α → Fin 5} (hB : IsC5Blowup G bag) {S : Finset α}
    (hS : IsMinimalTotalDominatingSet G S) : Set.InjOn bag S := by
  intro u huS v hvS huv
  by_contra huv_ne
  have hErase : IsTotalDominatingSet G (S.erase u) := by
    intro z
    obtain ⟨w, hwS, hzw⟩ := hS.1 z
    by_cases hwu : w = u
    · subst w
      refine ⟨v, Finset.mem_erase.mpr ⟨(fun hvu => huv_ne hvu.symm), hvS⟩, ?_⟩
      apply (hB.adj_iff z v).mpr
      have hzbag : (cycleGraph 5).Adj (bag z) (bag u) :=
        (hB.adj_iff z u).mp hzw
      simpa [huv] using hzbag
    · exact ⟨w, Finset.mem_erase.mpr ⟨hwu, hwS⟩, hzw⟩
  exact hS.2 (S.erase u) (Finset.erase_ssubset huS) hErase

lemma blowup_support_minimal
    {bag : α → Fin 5} (hB : IsC5Blowup G bag) {S : Finset α}
    (hS : IsMinimalTotalDominatingSet G S) :
    IsMinimalTotalDominatingSet (cycleGraph 5) (S.image bag) := by
  constructor
  · exact (blowup_totalDominatingSet_iff hB S).mp hS.1
  · intro T hTproper hTtds
    let R : Finset α := S.filter fun v => bag v ∈ T
    have hRsubset : R ⊆ S := by
      intro v hvR
      exact (Finset.mem_filter.mp hvR).1
    have hImage : R.image bag = T := by
      ext i
      constructor
      · intro hi
        obtain ⟨v, hvR, rfl⟩ := Finset.mem_image.mp hi
        exact (Finset.mem_filter.mp hvR).2
      · intro hiT
        have hTsubset : T ⊆ S.image bag :=
          (Finset.ssubset_iff_subset_ne.mp hTproper).1
        obtain ⟨v, hvS, hvbag⟩ := Finset.mem_image.mp (hTsubset hiT)
        refine Finset.mem_image.mpr ⟨v, ?_, hvbag⟩
        exact Finset.mem_filter.mpr ⟨hvS, by simpa [hvbag] using hiT⟩
    have hRtds : IsTotalDominatingSet G R := by
      apply (blowup_totalDominatingSet_iff hB R).mpr
      rw [hImage]
      exact hTtds
    have hRne : R ≠ S := by
      intro hRS
      have hTne : T ≠ S.image bag :=
        (Finset.ssubset_iff_subset_ne.mp hTproper).2
      apply hTne
      calc
        T = R.image bag := hImage.symm
        _ = S.image bag := congrArg (fun U : Finset α => U.image bag) hRS
    have hRproper : R ⊂ S :=
      Finset.ssubset_iff_subset_ne.mpr ⟨hRsubset, hRne⟩
    exact hS.2 R hRproper hRtds

lemma cycleGraph_five_minimal_tds_card (S : Finset (Fin 5))
    (hS : IsMinimalTotalDominatingSet (cycleGraph 5) S) : S.card = 3 := by
  revert S
  unfold IsMinimalTotalDominatingSet IsTotalDominatingSet
  decide

/-- Every minimal TDS in a nonempty `C5` blow-up has cardinality three. -/
lemma blowup_minimal_tds_card_eq_three
    {bag : α → Fin 5} (hB : IsC5Blowup G bag) {S : Finset α}
    (hS : IsMinimalTotalDominatingSet G S) : S.card = 3 := by
  have hInj : Set.InjOn bag S := blowup_bag_injOn_of_minimal hB hS
  have hImageCard : (S.image bag).card = S.card :=
    Finset.card_image_iff.mpr hInj
  calc
    S.card = (S.image bag).card := hImageCard.symm
    _ = 3 := cycleGraph_five_minimal_tds_card _ (blowup_support_minimal hB hS)

end WOWII314.BlowupTest
