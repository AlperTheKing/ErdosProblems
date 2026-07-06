/-
Seed3 door-type classifier — the STRUCTURAL, N-uniform combinatorial core of Seed3 ClassifierComplete
(GPT-Pro MAIN Verdict, 2026-07-07; Claude-verified spec). A "door graph" is three door edges (ℕ×ℕ pairs,
bipartite: `.1` = left/V0-side endpoint, `.2` = right/V4-side endpoint). Two edges SHARE a vertex iff they
have the same left endpoint or the same right endpoint. For a valid (pairwise-distinct, bipartite) door
graph the four door types P4 / K13 / P2uE / 3E are exactly the four sharing-counts of the three edge-pairs:
  0 shares → 3E (matching 3K2) ; 1 → P2uE (P3 + disjoint edge) ; 2 → P4 (path) ; 3 → K13 (star).
(Triangle K3 — the would-be fifth type — is impossible in a bipartite graph, and 3-shares with distinct
edges forces a common vertex, i.e. the star; see SEED3_COMPLETENESS_GPTPRO.md build spec.)

This module proves the door-type partition is EXHAUSTIVE, UNIQUE, and each type is INHABITED — a sound,
NON-VACUOUS, N-uniform structural theorem (no census, no bounded-N enumeration). Honest build.
-/
import Mathlib

namespace Erdos23Delta0
namespace Seed3Door

/-- The four Seed3 door types. -/
inductive DoorType
  | threeE
  | p2uE
  | p4
  | k13
deriving DecidableEq, Repr

/-- Two door edges share a vertex: same left endpoint (`.1`) or same right endpoint (`.2`).
    Bipartite convention: left endpoints compare only to left, right only to right. -/
def share (e f : ℕ × ℕ) : Prop := e.1 = f.1 ∨ e.2 = f.2

instance (e f : ℕ × ℕ) : Decidable (share e f) := by unfold share; infer_instance

/-- Structural door-type predicate by the sharing pattern of the three edges: the type is determined by
    HOW MANY of the three edge-pairs share a vertex (0/1/2/3). For a valid door graph this is the
    P4/K13/P2uE/3E classification. -/
def HasType (e1 e2 e3 : ℕ × ℕ) : DoorType → Prop
  | .threeE => ¬ share e1 e2 ∧ ¬ share e1 e3 ∧ ¬ share e2 e3
  | .p2uE   => (share e1 e2 ∧ ¬ share e1 e3 ∧ ¬ share e2 e3)
             ∨ (¬ share e1 e2 ∧ share e1 e3 ∧ ¬ share e2 e3)
             ∨ (¬ share e1 e2 ∧ ¬ share e1 e3 ∧ share e2 e3)
  | .p4     => (share e1 e2 ∧ share e1 e3 ∧ ¬ share e2 e3)
             ∨ (share e1 e2 ∧ ¬ share e1 e3 ∧ share e2 e3)
             ∨ (¬ share e1 e2 ∧ share e1 e3 ∧ share e2 e3)
  | .k13    => share e1 e2 ∧ share e1 e3 ∧ share e2 e3

/-- EXHAUSTIVENESS: every triple of door edges realizes one of the four door types. -/
theorem hasType_exhaustive (e1 e2 e3 : ℕ × ℕ) :
    ∃ ty, HasType e1 e2 e3 ty := by
  by_cases h12 : share e1 e2 <;> by_cases h13 : share e1 e3 <;> by_cases h23 : share e2 e3
  · exact ⟨.k13, h12, h13, h23⟩
  · exact ⟨.p4, Or.inl ⟨h12, h13, h23⟩⟩
  · exact ⟨.p4, Or.inr (Or.inl ⟨h12, h13, h23⟩)⟩
  · exact ⟨.p2uE, Or.inl ⟨h12, h13, h23⟩⟩
  · exact ⟨.p4, Or.inr (Or.inr ⟨h12, h13, h23⟩)⟩
  · exact ⟨.p2uE, Or.inr (Or.inl ⟨h12, h13, h23⟩)⟩
  · exact ⟨.p2uE, Or.inr (Or.inr ⟨h12, h13, h23⟩)⟩
  · exact ⟨.threeE, h12, h13, h23⟩

/-- UNIQUENESS: the door type of a triple is well-defined (mutually exclusive types). -/
theorem hasType_unique (e1 e2 e3 : ℕ × ℕ) (ty ty' : DoorType)
    (h : HasType e1 e2 e3 ty) (h' : HasType e1 e2 e3 ty') : ty = ty' := by
  by_cases h12 : share e1 e2 <;> by_cases h13 : share e1 e3 <;> by_cases h23 : share e2 e3 <;>
    cases ty <;> cases ty' <;> simp_all [HasType]

/-- NON-VACUITY: each of the four door types is realized by an actual door graph. -/
theorem hasType_threeE_inhabited : HasType (0, 0) (1, 1) (2, 2) .threeE := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [share]

theorem hasType_p2uE_inhabited : HasType (0, 0) (0, 1) (2, 2) .p2uE := by
  refine Or.inl ⟨?_, ?_, ?_⟩ <;> simp [share]

theorem hasType_p4_inhabited : HasType (0, 0) (0, 1) (2, 0) .p4 := by
  refine Or.inl ⟨?_, ?_, ?_⟩ <;> simp [share]

theorem hasType_k13_inhabited : HasType (0, 0) (0, 1) (0, 2) .k13 := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [share]

/-- Pairwise-distinct door edges (the nodup hypothesis of a valid door graph). -/
def Nodup3 (e1 e2 e3 : ℕ × ℕ) : Prop := e1 ≠ e2 ∧ e1 ≠ e3 ∧ e2 ≠ e3

/-- NO FIFTH DOOR TYPE (falsifier guard, per MAIN): a K13-type door graph of pairwise-distinct edges is
    a genuine STAR — the three edges share a common left endpoint or a common right endpoint. The
    would-be "triangle" fifth type cannot occur, because three pairwise-sharing distinct edges that do
    not meet in a common vertex would force two edges to coincide. -/
theorem k13_star (e1 e2 e3 : ℕ × ℕ) (hnd : Nodup3 e1 e2 e3) (h : HasType e1 e2 e3 .k13) :
    (e1.1 = e2.1 ∧ e2.1 = e3.1) ∨ (e1.2 = e2.2 ∧ e2.2 = e3.2) := by
  obtain ⟨h12, h13, h23⟩ := h
  obtain ⟨hne12, hne13, _hne23⟩ := hnd
  unfold share at h12 h13 h23
  rcases h12 with hL12 | hR12
  · rcases h13 with hL13 | hR13
    · exact Or.inl ⟨hL12, by omega⟩
    · rcases h23 with hL23 | hR23
      · exact Or.inl ⟨hL12, hL23⟩
      · exact absurd (Prod.ext_iff.mpr ⟨hL12, by omega⟩) hne12
  · rcases h13 with hL13 | hR13
    · rcases h23 with hL23 | hR23
      · exact absurd (Prod.ext_iff.mpr ⟨by omega, hR12⟩) hne12
      · exact Or.inr ⟨hR12, by omega⟩
    · exact Or.inr ⟨hR12, by omega⟩

/-- Computable door-type classifier (the decision procedure): the door type as a TOTAL function of the
    three edges, branching on the finite symbolic data (the sharing pattern). This is the checker form
    MAIN's Seed3 spec requires. -/
def classifyDoor (e1 e2 e3 : ℕ × ℕ) : DoorType :=
  if share e1 e2 then
    if share e1 e3 then
      if share e2 e3 then .k13 else .p4
    else
      if share e2 e3 then .p4 else .p2uE
  else
    if share e1 e3 then
      if share e2 e3 then .p4 else .p2uE
    else
      if share e2 e3 then .p2uE else .threeE

/-- SOUNDNESS of the computable classifier: it always returns the structural door type of the triple. -/
theorem hasType_classifyDoor (e1 e2 e3 : ℕ × ℕ) : HasType e1 e2 e3 (classifyDoor e1 e2 e3) := by
  unfold classifyDoor
  split_ifs <;> simp only [HasType] <;> tauto

/-- The computable classifier agrees with the structural predicate: `HasType` holds iff the classifier
    outputs that type (combines soundness + uniqueness). -/
theorem hasType_iff_classifyDoor (e1 e2 e3 : ℕ × ℕ) (ty : DoorType) :
    HasType e1 e2 e3 ty ↔ classifyDoor e1 e2 e3 = ty := by
  constructor
  · intro h; exact (hasType_unique e1 e2 e3 ty (classifyDoor e1 e2 e3) h (hasType_classifyDoor e1 e2 e3)).symm
  · intro h; rw [← h]; exact hasType_classifyDoor e1 e2 e3

end Seed3Door
end Erdos23Delta0
