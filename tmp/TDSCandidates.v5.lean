import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Circulant
import Mathlib.Data.Finset.Max

/-!
# Total-domination branch lemmas for WOWII Conjecture 314

This scratch module contains direct-route prototypes for the chain-graph and
nonempty `C5`-blow-up branches. It does not alter the target conjecture.
-/

namespace WOWII314.TDSCandidates

open SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α} [DecidableRel G.Adj]

/-- Total domination is upward closed. -/
lemma IsTotalDominatingSet.mono {S T : Finset α}
    (hS : IsTotalDominatingSet G S) (hST : S ⊆ T) :
    IsTotalDominatingSet G T := by
  intro v
  obtain ⟨w, hwS, hvw⟩ := hS v
  exact ⟨w, hST hwS, hvw⟩

/-- A total-dominating subset of a minimal TDS is the whole minimal TDS. -/
lemma IsMinimalTotalDominatingSet.eq_of_subset {S T : Finset α}
    (hS : IsMinimalTotalDominatingSet G S)
    (hT : IsTotalDominatingSet G T) (hTS : T ⊆ S) : T = S := by
  by_contra hne
  exact hS.2 T (Finset.ssubset_iff_subset_ne.mpr ⟨hTS, hne⟩) hT

/-- A fixed-cardinality total-dominating core inside a minimal TDS fixes its cardinality. -/
lemma IsMinimalTotalDominatingSet.card_eq_of_core {S : Finset α} {k : ℕ}
    (hS : IsMinimalTotalDominatingSet G S)
    (hcore : ∃ T : Finset α, T ⊆ S ∧ IsTotalDominatingSet G T ∧ T.card = k) :
    S.card = k := by
  obtain ⟨T, hTS, hT, hcard⟩ := hcore
  have hEq : T = S :=
    WOWII314.TDSCandidates.IsMinimalTotalDominatingSet.eq_of_subset hS hT hTS
  simpa [hEq] using hcard

/-- A finite nonempty family linearly ordered by inclusion has a member containing all others. -/
lemma Finset.exists_member_containing_all
    {ι β : Type*} [DecidableEq ι] [DecidableEq β]
    (A : Finset ι) (F : ι → Finset β) (hA : A.Nonempty)
    (hchain : ∀ a ∈ A, ∀ b ∈ A, F a ⊆ F b ∨ F b ⊆ F a) :
    ∃ m ∈ A, ∀ a ∈ A, F a ⊆ F m := by
  obtain ⟨m, hmA, hm⟩ := Finset.exists_max_image A (fun a => (F a).card) hA
  refine ⟨m, hmA, ?_⟩
  intro a haA
  rcases hchain a haA m hmA with ham | hma
  · exact ham
  · have heq : F m = F a := Finset.eq_of_subset_of_card_le hma (hm a haA)
    simpa [heq]

/-- Data used from the chain-graph branch of the structural dichotomy. -/
structure IsChainBipartition (G : SimpleGraph α) [DecidableRel G.Adj]
    (X Y : Finset α) : Prop where
  left_nonempty : X.Nonempty
  right_nonempty : Y.Nonempty
  cover : ∀ v, v ∈ X ∨ v ∈ Y
  disjoint : Disjoint X Y
  cross : ∀ ⦃u v⦄, G.Adj u v →
    (u ∈ X ∧ v ∈ Y) ∨ (u ∈ Y ∧ v ∈ X)
  left_chain : ∀ ⦃u⦄, u ∈ X → ∀ ⦃v⦄, v ∈ X →
    G.neighborFinset u ⊆ G.neighborFinset v ∨
      G.neighborFinset v ⊆ G.neighborFinset u
  right_chain : ∀ ⦃u⦄, u ∈ Y → ∀ ⦃v⦄, v ∈ Y →
    G.neighborFinset u ⊆ G.neighborFinset v ∨
      G.neighborFinset v ⊆ G.neighborFinset u

/-- Every minimal TDS in a finite nontrivial chain graph has cardinality two. -/
lemma chain_minimal_tds_card_eq_two
    {X Y S : Finset α} (hXY : IsChainBipartition G X Y)
    (hS : IsMinimalTotalDominatingSet G S) : S.card = 2 := by
  have hSX : (S ∩ X).Nonempty := by
    obtain ⟨y, hyY⟩ := hXY.right_nonempty
    obtain ⟨w, hwS, hyw⟩ := hS.1 y
    have hwX : w ∈ X := by
      rcases hXY.cross hyw with h | h
      · exact False.elim (Finset.disjoint_left.mp hXY.disjoint h.1 hyY)
      · exact h.2
    exact ⟨w, Finset.mem_inter.mpr ⟨hwS, hwX⟩⟩
  have hSY : (S ∩ Y).Nonempty := by
    obtain ⟨x, hxX⟩ := hXY.left_nonempty
    obtain ⟨w, hwS, hxw⟩ := hS.1 x
    have hwY : w ∈ Y := by
      rcases hXY.cross hxw with h | h
      · exact h.2
      · exact False.elim (Finset.disjoint_left.mp hXY.disjoint hxX h.1)
    exact ⟨w, Finset.mem_inter.mpr ⟨hwS, hwY⟩⟩
  obtain ⟨x, hxSX, hxmax⟩ := Finset.exists_member_containing_all
    (S ∩ X) (fun v => G.neighborFinset v) hSX (by
      intro a ha b hb
      exact hXY.left_chain (Finset.mem_inter.mp ha).2 (Finset.mem_inter.mp hb).2)
  obtain ⟨y, hySY, hymax⟩ := Finset.exists_member_containing_all
    (S ∩ Y) (fun v => G.neighborFinset v) hSY (by
      intro a ha b hb
      exact hXY.right_chain (Finset.mem_inter.mp ha).2 (Finset.mem_inter.mp hb).2)
  have hxS : x ∈ S := (Finset.mem_inter.mp hxSX).1
  have hxX : x ∈ X := (Finset.mem_inter.mp hxSX).2
  have hyS : y ∈ S := (Finset.mem_inter.mp hySY).1
  have hyY : y ∈ Y := (Finset.mem_inter.mp hySY).2
  have hpair_tds : IsTotalDominatingSet G {x, y} := by
    intro v
    rcases hXY.cover v with hvX | hvY
    · obtain ⟨w, hwS, hvw⟩ := hS.1 v
      have hwY : w ∈ Y := by
        rcases hXY.cross hvw with h | h
        · exact h.2
        · exact False.elim (Finset.disjoint_left.mp hXY.disjoint hvX h.1)
      have hwSY : w ∈ S ∩ Y := Finset.mem_inter.mpr ⟨hwS, hwY⟩
      have hvNw : v ∈ G.neighborFinset w :=
        (G.mem_neighborFinset w v).mpr hvw.symm
      have hvNy : v ∈ G.neighborFinset y := hymax w hwSY hvNw
      exact ⟨y, by simp, ((G.mem_neighborFinset y v).mp hvNy).symm⟩
    · obtain ⟨w, hwS, hvw⟩ := hS.1 v
      have hwX : w ∈ X := by
        rcases hXY.cross hvw with h | h
        · exact False.elim (Finset.disjoint_left.mp hXY.disjoint h.1 hvY)
        · exact h.2
      have hwSX : w ∈ S ∩ X := Finset.mem_inter.mpr ⟨hwS, hwX⟩
      have hvNw : v ∈ G.neighborFinset w :=
        (G.mem_neighborFinset w v).mpr hvw.symm
      have hvNx : v ∈ G.neighborFinset x := hxmax w hwSX hvNw
      exact ⟨x, by simp, ((G.mem_neighborFinset x v).mp hvNx).symm⟩
  have hpair_subset : {x, y} ⊆ S := by
    intro z hz
    simp only [Finset.mem_insert, Finset.mem_singleton] at hz
    rcases hz with rfl | rfl
    · exact hxS
    · exact hyS
  have hEq : {x, y} = S :=
    WOWII314.TDSCandidates.IsMinimalTotalDominatingSet.eq_of_subset
      hS hpair_tds hpair_subset
  have hxy : x ≠ y := by
    intro h
    subst y
    exact Finset.disjoint_left.mp hXY.disjoint hxX hyY
  rw [← hEq]
  simp [hxy]

/-- Kernel-checked finite classification: every minimal TDS of `C5` has size three. -/
lemma cycleGraph_five_minimal_tds_card (S : Finset (Fin 5))
    (hS : IsMinimalTotalDominatingSet (cycleGraph 5) S) : S.card = 3 := by
  revert S
  unfold IsMinimalTotalDominatingSet IsTotalDominatingSet
  decide

end WOWII314.TDSCandidates
