import Mathlib

/-!
# Maximum-cut vertex inequality (machine-checked, 2026-07-08)

For a MAXIMUM cut `s` of a finite `SimpleGraph`, flipping any vertex set `U` cannot increase the cut, whence the
capacity inequality `|δ_M(U)| ≤ |δ_B(U)|` (boundary bad/monochromatic edges ≤ boundary cut edges). This is the graph
fact that discharges the hypothesis `hmaxcut` of `Erdos23Delta0.Ell5CSReduction.c5book_support_expansion` and is the
capacity lemma of the Erdős #23 gap#1 ell=5 expansion route.

Route (GPT-Pro-designed, Claude-verified): a pure Boolean counting identity `bcount_xor_add_bcount_and` (proven by
`Finset.induction`) + the per-edge crossing-flip fact `edgeCut_flip` (via `Sym2.lift`) give the cardinal identity
`cutVal(flip U) + |δ_B(U)| = cutVal + |δ_M(U)|`; maximality + `omega` then give the inequality. No proof gaps.
-/

namespace Erdos23Delta0
namespace MaxCutVertexIneq

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Boolean xor, written as a decidable inequality of booleans. -/
def bxor (a b : Bool) : Bool := decide (a ≠ b)

/-- Count elements of a finset satisfying a boolean predicate. -/
def bcount {α : Type*} (s : Finset α) (p : α → Bool) : Nat :=
  (s.filter fun x => p x = true).card

/-- Pure boolean counting identity: over any finite set, the boundary-toggle of `c` across `b` conserves the total,
    swapping the `c ∧ b` count for the `¬c ∧ b` count. Proven by writing each `bcount` as a sum of indicators and
    reducing to the pointwise 4-case Bool identity. -/
theorem bcount_xor_add_bcount_and {α : Type*} [DecidableEq α]
    (s : Finset α) (c b : α → Bool) :
    bcount s (fun x => bxor (c x) (b x)) + bcount s (fun x => c x && b x)
      = bcount s c + bcount s (fun x => (! c x) && b x) := by
  classical
  have h : ∀ x, (if bxor (c x) (b x) = true then (1 : ℕ) else 0) + (if (c x && b x) = true then 1 else 0)
              = (if c x = true then 1 else 0) + (if ((! c x) && b x) = true then 1 else 0) := by
    intro x; cases hc : c x <;> cases hb : b x <;> simp [bxor, hc, hb]
  simp only [bcount, Finset.card_filter]
  trans (∑ x ∈ s, ((if bxor (c x) (b x) = true then (1 : ℕ) else 0) + (if (c x && b x) = true then 1 else 0)))
  · exact (Finset.sum_add_distrib).symm
  · rw [Finset.sum_congr rfl (fun x _ => h x), Finset.sum_add_distrib]

/-- Induced symmetric edge boolean: true exactly when the two endpoints have different values. -/
def edgeBool (f : V → Bool) : Sym2 V → Bool :=
  Sym2.lift ⟨fun u v => decide (f u ≠ f v), by
    intro u v
    cases hu : f u <;> cases hv : f v <;> simp [hu, hv]⟩

/-- Flip a cut `s` on a vertex set `U`. -/
def flipCut (s : V → Bool) (U : Finset V) : V → Bool :=
  fun v => if v ∈ U then ! s v else s v

/-- Boolean membership in a finset. -/
def memBool (U : Finset V) : V → Bool := fun v => decide (v ∈ U)

/-- An edge crosses the cut `s` if its endpoints have different `s`-values. -/
def edgeCut (s : V → Bool) : Sym2 V → Bool := edgeBool s

/-- An edge crosses the vertex boundary of `U` if it has exactly one endpoint in `U`. -/
def edgeBoundary (U : Finset V) : Sym2 V → Bool := edgeBool (memBool U)

/-- Pointwise flip identity for unordered edges: an edge is cut after flipping `U` iff exactly one of
    "was already cut" / "crosses the boundary of `U`" held before. -/
theorem edgeCut_flip (s : V → Bool) (U : Finset V) (e : Sym2 V) :
    edgeCut (flipCut s U) e = bxor (edgeCut s e) (edgeBoundary U e) := by
  classical
  refine Sym2.inductionOn e ?_
  intro u v
  by_cases huU : u ∈ U <;> by_cases hvU : v ∈ U <;>
    cases hsu : s u <;> cases hsv : s v <;>
    simp [edgeCut, edgeBoundary, edgeBool, flipCut, memBool, bxor,
      huU, hvU, hsu, hsv, Sym2.lift_mk]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- The value of a cut: number of graph edges crossing `s`. -/
def cutVal (s : V → Bool) : Nat := bcount G.edgeFinset (edgeCut s)

/-- Boundary cut edges of `U`: graph edges crossing `U` and crossing the cut `s`. -/
def deltaB (s : V → Bool) (U : Finset V) : Finset (Sym2 V) :=
  G.edgeFinset.filter fun e => (edgeCut s e && edgeBoundary U e) = true

/-- Boundary monochromatic/bad edges of `U`: graph edges crossing `U` but not crossing `s`. -/
def deltaM (s : V → Bool) (U : Finset V) : Finset (Sym2 V) :=
  G.edgeFinset.filter fun e => ((! edgeCut s e) && edgeBoundary U e) = true

/-- Main cardinal identity: only edges crossing the vertex boundary of `U` toggle their cut-status. -/
theorem cutVal_flip_add_deltaB_card (s : V → Bool) (U : Finset V) :
    cutVal G (flipCut s U) + (deltaB G s U).card = cutVal G s + (deltaM G s U).card := by
  classical
  have hflip : cutVal G (flipCut s U)
      = bcount G.edgeFinset (fun e => bxor (edgeCut s e) (edgeBoundary U e)) := by
    unfold cutVal
    congr 1
    funext e
    exact edgeCut_flip s U e
  rw [hflip]
  have hkey := bcount_xor_add_bcount_and G.edgeFinset (edgeCut s) (edgeBoundary U)
  simpa [cutVal, deltaB, deltaM, bcount] using hkey

/-- `s` is a maximum cut. -/
def IsMaxCut (s : V → Bool) : Prop := ∀ s' : V → Bool, cutVal G s' ≤ cutVal G s

/-- **Maximum-cut vertex inequality.** For a maximum cut `s` and every vertex set `U`, the number of boundary bad
    (monochromatic) edges is at most the number of boundary cut edges. -/
theorem deltaM_card_le_deltaB_card (s : V → Bool) (U : Finset V) (hmax : IsMaxCut G s) :
    (deltaM G s U).card ≤ (deltaB G s U).card := by
  classical
  have hle : cutVal G (flipCut s U) ≤ cutVal G s := hmax (flipCut s U)
  have hid := cutVal_flip_add_deltaB_card G s U
  omega

/-- **Improving flip refutes maximality** (contrapositive of the vertex inequality). If some vertex set `U` has strictly
    more boundary bad edges than boundary cut edges — `|δ_B(U)| < |δ_M(U)|`, an improving flip — then `s` is NOT a
    maximum cut. This is the maximality lever for the gap#1 escaping-atom argument: an escaping atom that produces such a
    `U` cannot occur at a maximum cut, so at a max cut the balanced-neutral lens has no escaping atom (its escape closure
    is proper), and `NeutralLensLedger.no_ledgerSep_in_minNeg` then closes it. (Pending: the graph lemma
    "escaping atom ⟹ ∃ such `U`".) -/
theorem not_isMaxCut_of_improving_flip (s : V → Bool) (U : Finset V)
    (h : (deltaB G s U).card < (deltaM G s U).card) : ¬ IsMaxCut G s := by
  intro hmax
  have := deltaM_card_le_deltaB_card G s U hmax
  omega

end Graph


end MaxCutVertexIneq
end Erdos23Delta0
