/-
Erdős #23 δ=0 — L1: ordered-dart flip calculus (first load-bearing file).
Per LEAN_BRANCHB_BLUEPRINT_GPTPRO.md: darts, obadCount, boundary counts, the
ℤ-valued flip identity, and maxCut ⟹ σ(S) ≥ 0. Everything downstream
(packet exchange, ν_K, Bank-L) consumes these.
-/

import Mathlib

namespace Erdos23Delta0
namespace DartsCalc

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A two-sided cut (independent of the graph). -/
structure Cut (V : Type*) where
  side : V → Bool

/-- Flip the side of every vertex in `S`. -/
def flip (c : Cut V) (S : Finset V) : Cut V :=
  ⟨fun v => if v ∈ S then !(c.side v) else c.side v⟩

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Ordered adjacent pairs. Each unordered edge appears twice. -/
def darts : Finset (V × V) :=
  Finset.univ.filter (fun p : V × V => G.Adj p.1 p.2)

/-- Ordered bad (monochromatic) dart count: twice the bad-edge count. -/
def obadCount (c : Cut V) : ℕ :=
  ((darts G).filter (fun p => c.side p.1 = c.side p.2)).card

/-- A dart crosses `S` iff exactly one endpoint lies in `S`. -/
def crosses (S : Finset V) (p : V × V) : Prop :=
  ¬((p.1 ∈ S) ↔ (p.2 ∈ S))

instance (S : Finset V) : DecidablePred (crosses S) := fun _ => by
  unfold crosses; infer_instance

/-- Ordered blue darts on the boundary of `S`. -/
def oBoundaryBlue (c : Cut V) (S : Finset V) : ℕ :=
  ((darts G).filter (fun p => crosses S p ∧ ¬(c.side p.1 = c.side p.2))).card

/-- Ordered bad darts on the boundary of `S`. -/
def oBoundaryBad (c : Cut V) (S : Finset V) : ℕ :=
  ((darts G).filter (fun p => crosses S p ∧ c.side p.1 = c.side p.2)).card

omit [Fintype V] in
theorem flip_side (c : Cut V) (S : Finset V) (v : V) :
    (flip c S).side v = if v ∈ S then !(c.side v) else c.side v := rfl

omit [Fintype V] in
/-- Crossing darts toggle badness under the flip. -/
theorem flip_bad_iff_of_crosses (c : Cut V) (S : Finset V) {p : V × V}
    (h : crosses S p) :
    ((flip c S).side p.1 = (flip c S).side p.2) ↔ ¬(c.side p.1 = c.side p.2) := by
  unfold crosses at h
  by_cases h1 : p.1 ∈ S <;> by_cases h2 : p.2 ∈ S <;>
    simp [h1, h2] at h ⊢ <;>
    first
      | (cases hb1 : c.side p.1 <;> cases hb2 : c.side p.2 <;>
          simp [flip, h1, h2, hb1, hb2])

omit [Fintype V] in
/-- Non-crossing darts keep their badness under the flip. -/
theorem flip_bad_iff_of_not_crosses (c : Cut V) (S : Finset V) {p : V × V}
    (h : ¬crosses S p) :
    ((flip c S).side p.1 = (flip c S).side p.2) ↔ (c.side p.1 = c.side p.2) := by
  unfold crosses at h
  rw [not_not] at h
  by_cases h1 : p.1 ∈ S <;> by_cases h2 : p.2 ∈ S <;>
    simp [h1, h2] at h ⊢ <;>
    (cases hb1 : c.side p.1 <;> cases hb2 : c.side p.2 <;>
      simp [flip, h1, h2, hb1, hb2])

/-- Split the flipped bad count by the crossing predicate. -/
theorem obadCount_flip_split (c : Cut V) (S : Finset V) :
    obadCount G (flip c S) = oBoundaryBlue G c S +
      ((darts G).filter
        (fun p => ¬crosses S p ∧ c.side p.1 = c.side p.2)).card := by
  unfold obadCount oBoundaryBlue
  conv_lhs => rw [← Finset.card_filter_add_card_filter_not (fun p => crosses S p)]
  congr 1
  · rw [Finset.filter_filter]
    refine congrArg Finset.card (Finset.filter_congr ?_)
    intro p _
    constructor
    · rintro ⟨hb, hc⟩
      exact ⟨hc, (flip_bad_iff_of_crosses c S hc).mp hb⟩
    · rintro ⟨hc, hb⟩
      exact ⟨(flip_bad_iff_of_crosses c S hc).mpr hb, hc⟩
  · rw [Finset.filter_filter]
    refine congrArg Finset.card (Finset.filter_congr ?_)
    intro p _
    constructor
    · rintro ⟨hb, hc⟩
      exact ⟨hc, (flip_bad_iff_of_not_crosses c S hc).mp hb⟩
    · rintro ⟨hc, hb⟩
      exact ⟨(flip_bad_iff_of_not_crosses c S hc).mpr hb, hc⟩

/-- Split the original bad count by the crossing predicate. -/
theorem obadCount_split (c : Cut V) (S : Finset V) :
    obadCount G c = oBoundaryBad G c S +
      ((darts G).filter
        (fun p => ¬crosses S p ∧ c.side p.1 = c.side p.2)).card := by
  unfold obadCount oBoundaryBad
  conv_lhs => rw [← Finset.card_filter_add_card_filter_not (fun p => crosses S p)]
  congr 1
  · rw [Finset.filter_filter]
    refine congrArg Finset.card (Finset.filter_congr ?_)
    intro p _
    exact ⟨fun ⟨hb, hc⟩ => ⟨hc, hb⟩, fun ⟨hc, hb⟩ => ⟨hb, hc⟩⟩
  · rw [Finset.filter_filter]
    refine congrArg Finset.card (Finset.filter_congr ?_)
    intro p _
    exact ⟨fun ⟨hb, hc⟩ => ⟨hc, hb⟩, fun ⟨hc, hb⟩ => ⟨hb, hc⟩⟩

/-- THE FLIP IDENTITY (ℤ-valued): flipping S trades boundary-bad for boundary-blue. -/
theorem flip_obadCount_eq (c : Cut V) (S : Finset V) :
    (obadCount G (flip c S) : ℤ) - obadCount G c =
      (oBoundaryBlue G c S : ℤ) - oBoundaryBad G c S := by
  have h1 := obadCount_flip_split G c S
  have h2 := obadCount_split G c S
  omega

/-- Max-cut ⟹ every switch has σ(S) ≥ 0 (doubled, ordered form). -/
theorem maxCut_sigma_nonneg (c : Cut V) (S : Finset V)
    (hmax : ∀ c' : Cut V, obadCount G c ≤ obadCount G c') :
    0 ≤ (oBoundaryBlue G c S : ℤ) - oBoundaryBad G c S := by
  have hle := hmax (flip c S)
  have hid := flip_obadCount_eq G c S
  omega

end DartsCalc
end Erdos23Delta0
