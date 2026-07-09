import Mathlib
import Erdos23Delta0.CertGraph

/-!
# M6 selection at the GraphData level (2026-07-09)

Companion of `MaxCutSelection` (SimpleGraph level) for the certificate data model, per the architecture audit's
B1/B2 buildable-from-spec items: `CertGraph.IsMaxCut` is min-bad-count over valid cuts, so
* `badCount_eq_of_isMaxCut` — any two maximum cuts have the same bad count (pure antisymmetry; the audit's
  `badCount = edgeCount − cutVal` detour is unnecessary in this model);
* `exists_isMaxCut` — a maximum cut exists for every `GraphData` (ℕ-infimum over the nonempty bad-count image;
  the all-`false` cut witnesses validity);
* `exists_isMaxCut_argmin` — among maximum cuts one can select a minimizer of any `ℕ`-valued functional (the
  Γ-of-cut slot for `GammaMinimalConnected`, once the bridge supplies the concrete γ).
No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace M6DataSelection

open CertGraph

/-- Any two maximum cuts (min-bad-count form) have equal bad counts. -/
theorem badCount_eq_of_isMaxCut {G : GraphData} {c c' : CutData}
    (hc : IsMaxCut G c) (hc' : IsMaxCut G c') :
    badCount G c = badCount G c' :=
  Nat.le_antisymm (hc.min_bad c' hc'.valid) (hc'.min_bad c hc.valid)

/-- The all-`false` cut is valid for every `GraphData`. -/
theorem checkCut_allFalse (G : GraphData) :
    checkCut G ⟨List.replicate G.n false⟩ = true := by
  simp [checkCut]

/-- **A maximum cut exists** for every `GraphData` (ℕ-infimum of the bad-count image). -/
theorem exists_isMaxCut (G : GraphData) : ∃ c : CutData, IsMaxCut G c := by
  classical
  have hne : {k : ℕ | ∃ d : CutData, checkCut G d = true ∧ badCount G d = k}.Nonempty :=
    ⟨badCount G ⟨List.replicate G.n false⟩,
      ⟨⟨List.replicate G.n false⟩, checkCut_allFalse G, rfl⟩⟩
  obtain ⟨d, hd, hdk⟩ :
      ∃ d : CutData, checkCut G d = true ∧
        badCount G d = sInf {k : ℕ | ∃ d : CutData, checkCut G d = true ∧ badCount G d = k} :=
    Nat.sInf_mem hne
  refine ⟨d, ⟨hd, fun e he => ?_⟩⟩
  rw [hdk]
  exact Nat.sInf_le ⟨e, he, rfl⟩

/-- **Refined selection at the data level:** among maximum cuts, a minimizer of any `ℕ`-valued functional
    exists (instantiate `g` with the concrete Γ-of-cut once the bridge provides it). -/
theorem exists_isMaxCut_argmin (G : GraphData) (g : CutData → ℕ) :
    ∃ c : CutData, IsMaxCut G c ∧ ∀ c' : CutData, IsMaxCut G c' → g c ≤ g c' := by
  classical
  obtain ⟨c0, hc0⟩ := exists_isMaxCut G
  have hne : {k : ℕ | ∃ d : CutData, IsMaxCut G d ∧ g d = k}.Nonempty := ⟨g c0, c0, hc0, rfl⟩
  obtain ⟨d, hd, hdk⟩ :
      ∃ d : CutData, IsMaxCut G d ∧
        g d = sInf {k : ℕ | ∃ d : CutData, IsMaxCut G d ∧ g d = k} :=
    Nat.sInf_mem hne
  refine ⟨d, hd, fun e he => ?_⟩
  rw [hdk]
  exact Nat.sInf_le ⟨e, he, rfl⟩


end M6DataSelection
end Erdos23Delta0
