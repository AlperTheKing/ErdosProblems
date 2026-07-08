import Mathlib
import Erdos23Delta0.MaxCutVertexIneq
import Erdos23Delta0.RelaxedCutCover

/-!
# Relaxed cut-cover: graph instantiation (2026-07-08)

Wires the abstract soundness of `RelaxedCutCover` to the real graph objects of `MaxCutVertexIneq`: rows are bad
(monochromatic) edges, `sep k := δ_M(U_k)`, `dB k := δ_B(U_k)`, and the per-cut hypothesis `hmcap` is discharged by
the compiled maximum-cut vertex inequality `deltaM_card_le_deltaB_card`. The off-support edge set is
`cutEdges \ F`. Result: `graph_defect_bound` — for ANY weighted family of vertex sets over a MAXIMUM cut, with row
coverage ≥ 1 and in-support congestion ≤ 1, the Hall defect `|S| − |F|` is bounded by the external load, with NO
remaining graph hypotheses. `badEdge_mem_deltaM` is the membership helper for building coverage certificates.
No `sorry`/`admit`/`native_decide`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace RelaxedCoverGraphBridge

open Finset MaxCutVertexIneq RelaxedCutCover

variable {V : Type*} [Fintype V] [DecidableEq V]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- All cut (bichromatic) edges of the cut `s`. -/
def cutEdges (s : V → Bool) : Finset (Sym2 V) :=
  G.edgeFinset.filter fun e => edgeCut s e = true

/-- Every boundary cut edge is a cut edge. -/
theorem deltaB_subset_cutEdges (s : V → Bool) (U : Finset V) :
    deltaB G s U ⊆ cutEdges G s := by
  intro e he
  unfold deltaB at he
  unfold cutEdges
  rw [Finset.mem_filter] at he ⊢
  refine ⟨he.1, ?_⟩
  have h := he.2
  cases hcut : edgeCut s e with
  | false => rw [hcut] at h; simp at h
  | true => rfl

/-- **Coverage helper.** A monochromatic graph edge `s(u,v)` with exactly one endpoint in `U`
    (as booleans: `memBool U u ≠ memBool U v`) lies in `δ_M(U)`. -/
theorem badEdge_mem_deltaM (s : V → Bool) {u v : V} (hadj : G.Adj u v) (hmono : s u = s v)
    (U : Finset V) (hsep : memBool U u ≠ memBool U v) :
    s(u, v) ∈ deltaM G s U := by
  unfold deltaM
  rw [Finset.mem_filter]
  refine ⟨G.mem_edgeFinset.mpr hadj, ?_⟩
  have hcut : edgeCut s s(u, v) = false := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hmono]
  have hbd : edgeBoundary U s(u, v) = true := by
    simp only [edgeBoundary, edgeBool, Sym2.lift_mk, decide_eq_true_iff]
    exact hsep
  rw [hcut, hbd]
  rfl

/-- **Graph-level relaxed cut-cover defect bound** (no remaining graph hypotheses). For a MAXIMUM cut `s`, any
    finite weighted family of vertex sets `(K, Ufam, λ)` with nonnegative weights, row coverage ≥ 1 on `S` (via
    `δ_M`), and in-support congestion ≤ 1 on `F ⊆ cutEdges` (via `δ_B`) bounds the Hall defect by the external
    load on the off-support cut edges: `|S| ≤ |F| + Σ_{c ∈ cutEdges \ F} load(c)`. -/
theorem graph_defect_bound {ι : Type*}
    (s : V → Bool) (hmax : IsMaxCut G s)
    (S F : Finset (Sym2 V)) (hF : F ⊆ cutEdges G s)
    (K : Finset ι) (Ufam : ι → Finset V) (lam : ι → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ deltaM G s (Ufam k) then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ deltaB G s (Ufam k) then lam k else 0) ≤ 1) :
    (S.card : ℚ) ≤ (F.card : ℚ)
      + ∑ c ∈ cutEdges G s \ F, load K lam (fun k => deltaB G s (Ufam k)) c := by
  refine relaxed_cutcover_defect_bound S F (cutEdges G s \ F) Finset.disjoint_sdiff K lam
    (fun k => deltaM G s (Ufam k)) (fun k => deltaB G s (Ufam k)) hlam ?_ ?_ hcov hcong
  · intro k _
    rw [Finset.union_sdiff_of_subset hF]
    exact deltaB_subset_cutEdges G s (Ufam k)
  · intro k _
    exact_mod_cast deltaM_card_le_deltaB_card G s (Ufam k) hmax

/-- **Graph-level bank absorption.** If additionally `25 ×` the external load is within the bank `B`, then
    `25|S| ≤ 25|F| + B` — the full-bank Hall inequality at the graph level, from a certificate. -/
theorem graph_hall_absorbed {ι : Type*}
    (s : V → Bool) (hmax : IsMaxCut G s)
    (S F : Finset (Sym2 V)) (hF : F ⊆ cutEdges G s)
    (K : Finset ι) (Ufam : ι → Finset V) (lam : ι → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ deltaM G s (Ufam k) then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ deltaB G s (Ufam k) then lam k else 0) ≤ 1)
    (B : ℚ)
    (hbank : 25 * (∑ c ∈ cutEdges G s \ F, load K lam (fun k => deltaB G s (Ufam k)) c) ≤ B) :
    25 * (S.card : ℚ) ≤ 25 * (F.card : ℚ) + B := by
  have h := graph_defect_bound G s hmax S F hF K Ufam lam hlam hcov hcong
  linarith

end Graph

#print axioms deltaB_subset_cutEdges
#print axioms badEdge_mem_deltaM
#print axioms graph_defect_bound
#print axioms graph_hall_absorbed

end RelaxedCoverGraphBridge
end Erdos23Delta0
