import Mathlib

/-!
# Distance-four footprint count interface

This file isolates the tiny Lean interface needed for the m=7,8 footprint
certificate: if a minimal Hall obstruction projects injectively into the
unordered vertex pairs at distance exactly four in its connected footprint F,
and an external exact certificate proves D4(F) ≤ |E(F)| - 1, then the usual
minimal-obstruction equation |S| = |E(F)| + 1 is impossible.
-/

namespace Erdos23Delta0
namespace Ell5FootprintCount

open SimpleGraph Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Unordered vertex pairs at graph-distance exactly four. -/
noncomputable def distance4Pairs (F : SimpleGraph V) : Finset (Sym2 V) :=
  Finset.univ.filter fun e => ∃ a b : V, e = s(a,b) ∧ F.dist a b = 4

@[simp] theorem mem_distance4Pairs {F : SimpleGraph V} {e : Sym2 V} :
    e ∈ distance4Pairs F ↔ ∃ a b : V, e = s(a,b) ∧ F.dist a b = 4 := by
  classical
  simp [distance4Pairs]

/-- Generic certificate interface for the `m≤8` footprint step.  The external
checker supplies `hD4`; the graph-to-obstruction reduction supplies `hmap`,
`hinj`, and `hS`. -/
theorem no_minimal_violator_of_distance4_count_bound
    {ι : Type*} [DecidableEq ι] (F : SimpleGraph V) [DecidableRel F.Adj]
    (S : Finset ι) (pair : ι → Sym2 V)
    (hD4 : (distance4Pairs F).card ≤ F.edgeFinset.card - 1)
    (hS : S.card = F.edgeFinset.card + 1)
    (hmap : ∀ a ∈ S, pair a ∈ distance4Pairs F)
    (hinj : Set.InjOn pair S) :
    False := by
  have himage_subset : S.image pair ⊆ distance4Pairs F := by
    intro e he
    rw [Finset.mem_image] at he
    obtain ⟨a, ha, rfl⟩ := he
    exact hmap a ha
  have hle : S.card ≤ F.edgeFinset.card - 1 := by
    calc
      S.card = (S.image pair).card := (Finset.card_image_of_injOn hinj).symm
      _ ≤ (distance4Pairs F).card := Finset.card_le_card himage_subset
      _ ≤ F.edgeFinset.card - 1 := hD4
  omega

/-- Endpoint-map convenience wrapper for the same certificate interface. -/
theorem no_minimal_violator_of_distance4_count_bound_endpoints
    {ι : Type*} [DecidableEq ι] (F : SimpleGraph V) [DecidableRel F.Adj]
    (S : Finset ι) (x y : ι → V)
    (hD4 : (distance4Pairs F).card ≤ F.edgeFinset.card - 1)
    (hS : S.card = F.edgeFinset.card + 1)
    (hdist : ∀ a ∈ S, F.dist (x a) (y a) = 4)
    (hinj : Set.InjOn (fun a => s(x a, y a)) S) :
    False := by
  exact no_minimal_violator_of_distance4_count_bound F S (fun a => s(x a, y a))
    hD4 hS (fun a ha => mem_distance4Pairs.mpr ⟨x a, y a, rfl, hdist a ha⟩) hinj

#print axioms distance4Pairs
#print axioms no_minimal_violator_of_distance4_count_bound
#print axioms no_minimal_violator_of_distance4_count_bound_endpoints

end Ell5FootprintCount
end Erdos23Delta0