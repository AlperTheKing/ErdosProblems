import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Circulant

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

/-- Kernel-checked finite classification: every minimal TDS of `C5` has size three. -/
lemma cycleGraph_five_minimal_tds_card (S : Finset (Fin 5))
    (hS : IsMinimalTotalDominatingSet (cycleGraph 5) S) : S.card = 3 := by
  revert S
  decide

end WOWII314.TDSCandidates
