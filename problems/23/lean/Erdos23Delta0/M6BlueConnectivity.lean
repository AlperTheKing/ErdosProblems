import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.MaxCutVertexIneq
import Erdos23Delta0.MaxCutSelection

/-!
# M6: every maximum cut is blue-connected on its bad pairs (2026-07-08)

GPT-Pro's M6 design (archive `M6_GOODCUT_PROVIDER_GPTPRO.md` §1.1), compiled at the `SimpleGraph` level: if a
bad (monochromatic) edge's endpoints lay in different components of the blue (cut-edge) graph, flipping the blue
component `U` of one endpoint would change the cut by `|δ_M(U)| − |δ_B(U)| ≥ 1 − 0 > 0` — an improving flip,
contradicting maximality (`MaxCutVertexIneq.not_isMaxCut_of_improving_flip`). The two structural facts are
`deltaB_blueComponent_empty` (no cut edge leaves a blue component) and `badEdge_mem_deltaM_of_not_reachable`.

Consequence `maxCut_badEdge_blueReachable`: the `bConnected` field of the M6 `GoodCutData` provider is FREE for
every maximum cut — no per-component surgery needed at selection time. `exists_maxCut_argmin_bconnected` then
packages the full selection: a Γ-minimal (any `ℕ`-functional) maximum cut that is blue-connected on all its bad
pairs exists. No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace M6BlueConnectivity

open MaxCutVertexIneq Distances

variable {V : Type*} [Fintype V] [DecidableEq V]

open Classical in
/-- The blue-reachability component of `u` under the cut `s`, as a `Finset`. -/
noncomputable def blueComponent (G : SimpleGraph V) (s : V → Bool) (u : V) : Finset V :=
  Finset.univ.filter fun x => (Distances.blueGraph G ⟨s⟩).Reachable u x

theorem mem_blueComponent_iff {G : SimpleGraph V} {s : V → Bool} {u x : V} :
    x ∈ blueComponent G s u ↔ (Distances.blueGraph G ⟨s⟩).Reachable u x := by
  classical
  unfold blueComponent
  rw [Finset.mem_filter]
  simp only [Finset.mem_univ, true_and]

theorem self_mem_blueComponent (G : SimpleGraph V) (s : V → Bool) (u : V) :
    u ∈ blueComponent G s u :=
  mem_blueComponent_iff.mpr (SimpleGraph.Reachable.refl u)

/-- **No cut edge leaves a blue component:** `δ_B(blueComponent u) = ∅`. -/
theorem deltaB_blueComponent_empty (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (u : V) :
    deltaB G s (blueComponent G s u) = ∅ := by
  classical
  rw [Finset.eq_empty_iff_forall_notMem]
  intro c hc
  revert hc
  induction c using Sym2.ind with
  | _ x y =>
    intro hc
    unfold deltaB at hc
    rw [Finset.mem_filter] at hc
    obtain ⟨hcE, hcond⟩ := hc
    rw [Bool.and_eq_true] at hcond
    obtain ⟨hcut, hbd⟩ := hcond
    have hadj : G.Adj x y := by
      have h := SimpleGraph.mem_edgeFinset.mp hcE
      rwa [SimpleGraph.mem_edgeSet] at h
    have hsxy : s x ≠ s y := by
      simpa [edgeCut, edgeBool, Sym2.lift_mk, decide_eq_true_eq] using hcut
    have hblue : (Distances.blueGraph G ⟨s⟩).Adj x y := ⟨hadj, hsxy⟩
    have hne : memBool (blueComponent G s u) x ≠ memBool (blueComponent G s u) y := by
      simpa [edgeBoundary, edgeBool, Sym2.lift_mk, decide_eq_true_eq] using hbd
    by_cases hx : x ∈ blueComponent G s u
    · have hy : y ∉ blueComponent G s u := by
        intro hy
        exact hne (by simp [memBool, hx, hy])
      exact hy (mem_blueComponent_iff.mpr
        ((mem_blueComponent_iff.mp hx).trans hblue.reachable))
    · have hy : y ∈ blueComponent G s u := by
        by_contra hy
        exact hne (by simp [memBool, hx, hy])
      exact hx (mem_blueComponent_iff.mpr
        ((mem_blueComponent_iff.mp hy).trans hblue.symm.reachable))

/-- A bad edge whose far endpoint is blue-unreachable lies in `δ_M` of the blue component. -/
theorem badEdge_mem_deltaM_of_not_reachable (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) {u v : V} (hadj : G.Adj u v) (hmono : s u = s v)
    (hnr : ¬ (Distances.blueGraph G ⟨s⟩).Reachable u v) :
    s(u, v) ∈ deltaM G s (blueComponent G s u) := by
  classical
  unfold deltaM
  rw [Finset.mem_filter]
  refine ⟨G.mem_edgeFinset.mpr hadj, ?_⟩
  have hcut : edgeCut s s(u, v) = false := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hmono]
  have hu : u ∈ blueComponent G s u := self_mem_blueComponent G s u
  have hv : v ∉ blueComponent G s u := fun hv => hnr (mem_blueComponent_iff.mp hv)
  have hbd : edgeBoundary (blueComponent G s u) s(u, v) = true := by
    simp only [edgeBoundary, edgeBool, Sym2.lift_mk, decide_eq_true_eq, memBool]
    simp [hu, hv]
  rw [hcut, hbd]
  rfl

/-- **Every maximum cut is blue-connected on its bad pairs.** -/
theorem maxCut_badEdge_blueReachable (G : SimpleGraph V) [Fintype G.edgeSet]
    {s : V → Bool} (hmax : IsMaxCut G s) {u v : V}
    (hadj : G.Adj u v) (hmono : s u = s v) :
    (Distances.blueGraph G ⟨s⟩).Reachable u v := by
  by_contra hnr
  have h1 : s(u, v) ∈ deltaM G s (blueComponent G s u) :=
    badEdge_mem_deltaM_of_not_reachable G s hadj hmono hnr
  have h2 : deltaB G s (blueComponent G s u) = ∅ :=
    deltaB_blueComponent_empty G s u
  have hlt : (deltaB G s (blueComponent G s u)).card
      < (deltaM G s (blueComponent G s u)).card := by
    rw [h2]
    simpa using Finset.card_pos.mpr ⟨_, h1⟩
  exact not_isMaxCut_of_improving_flip G s _ hlt hmax

/-- **M6 selection, fully packaged:** a maximum cut minimizing any `ℕ`-functional `g` (e.g. Γ) exists, and it is
    automatically blue-connected on all its bad pairs. -/
theorem exists_maxCut_argmin_bconnected (G : SimpleGraph V) [Fintype G.edgeSet]
    (g : (V → Bool) → ℕ) :
    ∃ s, IsMaxCut G s
      ∧ (∀ u v : V, G.Adj u v → s u = s v → (Distances.blueGraph G ⟨s⟩).Reachable u v)
      ∧ ∀ s', IsMaxCut G s' → g s ≤ g s' := by
  obtain ⟨s, hmax, _, hmin⟩ :=
    MaxCutSelection.exists_maxCut_argmin G (fun _ => True) g
      (by obtain ⟨s, hs⟩ := MaxCutSelection.exists_maxCut G; exact ⟨s, hs, trivial⟩)
  exact ⟨s, hmax, fun u v hadj hmono => maxCut_badEdge_blueReachable G hmax hadj hmono,
    fun s' h1 => hmin s' h1 trivial⟩


end M6BlueConnectivity
end Erdos23Delta0
