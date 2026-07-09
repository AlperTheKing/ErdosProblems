import Mathlib
import Erdos23Delta0.Ell5CSReduction
import Erdos23Delta0.PathRigidity

/-!
# ell=5 atom base case: closing `|S| ≤ 5` for concrete geodesic-carrying atoms (2026-07-08)

Ties together the two graph facts proved separately — `h4` (a length-4 geodesic has ≥ 4 support edges) and the
rigidity `hpair` (`PathRigidity.edges_determine_badedge`: equal supports ⟹ equal bad edge) — into the `|S| ≤ 5`
base case of `Ell5SupportExpansion`, for an `Ell5Atom` (a bad edge packaged with a shortest length-4 blue geodesic).

An `Ell5Atom` is identified by its bad edge `s(u, v)`; on a set `S` of atoms with distinct bad edges, distinct atoms
have distinct supports (rigidity), so `Ell5CSReduction.pair_union_ge_five` gives `|P_e ∪ P_f| ≥ 5`, and an S-local form
of `hall_le_five` yields `|S| ≤ |E_short(S)|`. Axiom-clean; the abstract `Ell5CSReduction.hall_le_five` had a *global*
`hpair`, so we prove `hall_le_five_local` (S-restricted hypotheses) here — its proof mirrors the abstract one.
-/

namespace Erdos23Delta0
namespace Ell5AtomBase

open SimpleGraph Finset

variable {V : Type*} {G : SimpleGraph V}

/-- **S-local `|S| ≤ 5` Hall bound.** Same as `Ell5CSReduction.hall_le_five` but the size and pair hypotheses are
    only required for atoms *in* `S` (which is all the proof uses). -/
theorem hall_le_five_local {α β : Type*} [DecidableEq β] (Erow : α → Finset β) (S : Finset α)
    (h4 : ∀ e ∈ S, 4 ≤ (Erow e).card)
    (hpair : ∀ e ∈ S, ∀ f ∈ S, e ≠ f → 5 ≤ (Erow e ∪ Erow f).card)
    (hS : S.card ≤ 5) :
    S.card ≤ (S.biUnion Erow).card := by
  rcases Finset.eq_empty_or_nonempty S with h | ⟨e, he⟩
  · simp [h]
  · by_cases h2 : ∃ f ∈ S, f ≠ e
    · obtain ⟨f, hf, hfe⟩ := h2
      have hunion : (Erow e ∪ Erow f) ⊆ S.biUnion Erow :=
        Finset.union_subset (Finset.subset_biUnion_of_mem Erow he)
          (Finset.subset_biUnion_of_mem Erow hf)
      calc S.card ≤ 5 := hS
        _ ≤ (Erow e ∪ Erow f).card := hpair e he f hf (Ne.symm hfe)
        _ ≤ (S.biUnion Erow).card := Finset.card_le_card hunion
    · push_neg at h2
      have hcard1 : S.card ≤ 1 :=
        Finset.card_le_one.mpr (fun a ha b hb => by rw [h2 a ha, h2 b hb])
      have h4e : 4 ≤ (S.biUnion Erow).card :=
        le_trans (h4 e he) (Finset.card_le_card (Finset.subset_biUnion_of_mem Erow he))
      omega

/-- An ell=5 atom: a bad edge `s(u,v)` packaged with a shortest blue geodesic of length 4 (a `Path`). -/
structure Ell5Atom (G : SimpleGraph V) where
  u : V
  v : V
  geo : G.Walk u v
  isPath : geo.IsPath
  len4 : geo.length = 4

variable [DecidableEq V]

/-- The shortest-geodesic cut-edge support of the atom. -/
def Ell5Atom.support (a : Ell5Atom G) : Finset (Sym2 V) := a.geo.edges.toFinset

theorem Ell5Atom.support_card (a : Ell5Atom G) : a.support.card = 4 :=
  Ell5CSReduction.geodesic_len4_card_edges a.geo a.isPath a.len4

theorem Ell5Atom.four_le_support (a : Ell5Atom G) : 4 ≤ a.support.card := by
  rw [a.support_card]

theorem Ell5Atom.not_nil (a : Ell5Atom G) : ¬ a.geo.Nil := by
  rw [Walk.nil_iff_length_eq, a.len4]; decide

theorem Ell5Atom.uv_ne (a : Ell5Atom G) : a.u ≠ a.v := by
  intro h
  have h04 : (0 : ℕ) = 4 :=
    a.isPath.getVert_injOn (by simp [a.len4]) (by simp [a.len4]) (by
      rw [Walk.getVert_zero, show (4 : ℕ) = a.geo.length from a.len4.symm, Walk.getVert_length]
      exact h)
  norm_num at h04

/-- **Rigidity at atom level:** equal supports force equal bad edges. -/
theorem Ell5Atom.badEdge_eq_of_support_eq {a b : Ell5Atom G} (h : a.support = b.support) :
    s(a.u, a.v) = s(b.u, b.v) :=
  PathRigidity.edges_determine_badedge a.isPath b.isPath a.not_nil a.uv_ne h

/-- **`hpair` at atom level:** atoms with distinct bad edges have union support `≥ 5`. -/
theorem Ell5Atom.pair_union {a b : Ell5Atom G} (hbad : s(a.u, a.v) ≠ s(b.u, b.v)) :
    5 ≤ (a.support ∪ b.support).card :=
  Ell5CSReduction.pair_union_ge_five a.four_le_support b.four_le_support
    (fun h => hbad (Ell5Atom.badEdge_eq_of_support_eq h))

/-- **The `|S| ≤ 5` base case of `Ell5SupportExpansion`, at the concrete blue-geodesic level.** For a finset `S` of
    ell=5 atoms whose bad edges are distinct (`hInj`: two atoms in `S` with the same bad edge are equal) and with
    `|S| ≤ 5`, the support-expansion bound holds: `|S| ≤ |E_short(S)|`. Both graph facts are discharged —
    `four_le_support` (h4) and `pair_union` via rigidity (hpair). -/
theorem ell5_base_case (S : Finset (Ell5Atom G))
    (hInj : ∀ a ∈ S, ∀ b ∈ S, s(a.u, a.v) = s(b.u, b.v) → a = b)
    (hS : S.card ≤ 5) :
    S.card ≤ (S.biUnion Ell5Atom.support).card := by
  refine hall_le_five_local Ell5Atom.support S (fun a _ => a.four_le_support) ?_ hS
  intro a ha b hb hab
  exact Ell5Atom.pair_union (fun hbad => hab (hInj a ha b hb hbad))


end Ell5AtomBase
end Erdos23Delta0
