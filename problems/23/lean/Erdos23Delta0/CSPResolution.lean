/-
CSP resolution-refutation checker (per-instance NCH classification; GPT-Pro MAIN design, Claude-built).
Under the certified-per-instance route, an NCH leaf's numeric ODL bound is proven by a ConeCert (reusing
coreODLGoal_of_coneCert); its CLASSIFICATION — that the terminal block is genuinely NOT C5-extendable — is
proven by a resolution refutation of the C5-labeling CSP (emitted per instance by Codex, checked here).

A literal asserts a variable/bag takes (positive) or avoids (negative) a label in Z5. A clause is a
disjunction of literals. Resolution on a pivot literal p (p in C, compl p in D) derives (C\p) ++ (D\compl p);
a derivation of the empty clause certifies the base CSP is unsatisfiable, i.e. no C5-labeling extends.

This module builds the SOUNDNESS core: complementary literals cannot both hold, and one resolution step
preserves satisfaction (resolvent_sat). Honest build. Axiom-clean.
-/
import Mathlib

namespace Erdos23Delta0
namespace CSPResolution

/-- A literal: variable `varIdx` takes `label` (positive) or avoids it (negative). Labels range over Z5. -/
structure Literal where
  varIdx : Nat
  label : Nat
  positive : Bool
deriving DecidableEq, Repr

/-- An assignment maps each variable to a label. -/
abbrev Assignment := Nat → Nat

/-- A clause is a disjunction of literals. -/
abbrev Clause := List Literal

/-- When a literal holds under an assignment. -/
def Literal.holds (a : Assignment) (l : Literal) : Prop :=
  if l.positive then a l.varIdx = l.label else a l.varIdx ≠ l.label

instance (a : Assignment) (l : Literal) : Decidable (Literal.holds a l) := by
  unfold Literal.holds; split <;> infer_instance

/-- A clause is satisfied if some literal holds (disjunction). -/
def Clause.sat (a : Assignment) (C : Clause) : Prop := ∃ l ∈ C, Literal.holds a l

/-- An assignment satisfies a clause set if it satisfies every clause. -/
def Sat (a : Assignment) (base : List Clause) : Prop := ∀ C ∈ base, Clause.sat a C

/-- No assignment satisfies the base clause set (unsatisfiable). -/
def NoSat (base : List Clause) : Prop := ∀ a, ¬ Sat a base

/-- The complement of a literal (flip polarity, same variable/label). -/
def compl (l : Literal) : Literal := { l with positive := !l.positive }

/-- Complementary literals cannot both hold under any assignment. -/
theorem not_both_holds (a : Assignment) (p : Literal) :
    ¬ (Literal.holds a p ∧ Literal.holds a (compl p)) := by
  unfold Literal.holds compl
  cases hp : p.positive <;> simp_all

/-- The resolvent of `C` and `D` on pivot `p` (expects `p ∈ C`, `compl p ∈ D`). -/
def resolvent (C D : Clause) (p : Literal) : Clause := (C.erase p) ++ (D.erase (compl p))

/-- ONE-STEP SOUNDNESS: any assignment satisfying both `C` and `D` satisfies their resolvent on `p`. -/
theorem resolvent_sat (a : Assignment) (C D : Clause) (p : Literal)
    (hC : Clause.sat a C) (hD : Clause.sat a D) : Clause.sat a (resolvent C D p) := by
  obtain ⟨lc, hlcC, hlc⟩ := hC
  by_cases hlcp : lc = p
  · -- the C-witness is the pivot: it holds, so compl p does not hold, so the D-witness ≠ compl p
    subst hlcp
    obtain ⟨ld, hldD, hld⟩ := hD
    have hnc : ¬ Literal.holds a (compl lc) := fun h => not_both_holds a lc ⟨hlc, h⟩
    have hld_ne : ld ≠ compl lc := fun h => hnc (h ▸ hld)
    exact ⟨ld, List.mem_append_right _ ((List.mem_erase_of_ne hld_ne).mpr hldD), hld⟩
  · -- the C-witness is not the pivot: it survives in C.erase p
    exact ⟨lc, List.mem_append_left _ ((List.mem_erase_of_ne hlcp).mpr hlcC), hlc⟩

/-- The empty clause is never satisfied. -/
theorem nil_not_sat (a : Assignment) : ¬ Clause.sat a ([] : Clause) := by
  unfold Clause.sat; simp

end CSPResolution
end Erdos23Delta0
