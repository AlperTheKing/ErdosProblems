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

/-! ### Resolution trace + refutation soundness -/

/-- A resolution step: resolve the clauses at indices `lhs`, `rhs` (into the growing list) on `pivot`. -/
structure Step where
  lhs : Nat
  rhs : Nat
  pivot : Literal
deriving Repr

/-- The resolvent produced by a step against the current clause list (`[]` if an index is out of range). -/
def stepResolvent (cs : List Clause) (s : Step) : Clause :=
  match cs[s.lhs]?, cs[s.rhs]? with
  | some C, some D => resolvent C D s.pivot
  | _, _ => []

/-- A step is valid against the current list: both indices in range, `pivot ∈ lhs`, `compl pivot ∈ rhs`. -/
def checkStep (cs : List Clause) (s : Step) : Bool :=
  match cs[s.lhs]?, cs[s.rhs]? with
  | some C, some D => decide (s.pivot ∈ C) && decide (compl s.pivot ∈ D)
  | _, _ => false

/-- Derived clause list after processing all steps (each appends its resolvent). -/
def derivedFrom : List Clause → List Step → List Clause
  | cs, [] => cs
  | cs, s :: rest => derivedFrom (cs ++ [stepResolvent cs s]) rest

/-- The trace is valid iff every step is valid against the list at that point. -/
def validFrom : List Clause → List Step → Bool
  | _, [] => true
  | cs, s :: rest => checkStep cs s && validFrom (cs ++ [stepResolvent cs s]) rest

/-- A clause is a logical CONSEQUENCE of the base: every satisfying assignment satisfies it. -/
def Consequence (base : List Clause) (C : Clause) : Prop :=
  ∀ a : Assignment, Sat a base → Clause.sat a C

/-- Membership from an in-range `[i]?` lookup. -/
private theorem clause_mem_of_getElem? {l : List Clause} {i : Nat} {C : Clause}
    (h : l[i]? = some C) : C ∈ l := by
  obtain ⟨hlt, rfl⟩ := List.getElem?_eq_some_iff.mp h
  exact List.getElem_mem hlt

/-- A valid step of consequences yields a consequence (uses `resolvent_sat`; needs only index validity). -/
theorem step_consequence (base cs : List Clause) (s : Step)
    (hcs : ∀ C ∈ cs, Consequence base C) (hstep : checkStep cs s = true) :
    Consequence base (stepResolvent cs s) := by
  unfold checkStep at hstep
  unfold stepResolvent
  cases hL : cs[s.lhs]? with
  | none => rw [hL] at hstep; simp at hstep
  | some C =>
    cases hR : cs[s.rhs]? with
    | none => rw [hL, hR] at hstep; simp at hstep
    | some D =>
      intro a hsat
      exact resolvent_sat a C D s.pivot
        (hcs C (clause_mem_of_getElem? hL) a hsat) (hcs D (clause_mem_of_getElem? hR) a hsat)

/-- INVARIANT: a valid trace over consequences keeps every derived clause a consequence. -/
theorem derivedFrom_consequence (base : List Clause) :
    ∀ (steps : List Step) (cs : List Clause),
      (∀ C ∈ cs, Consequence base C) → validFrom cs steps = true →
      (∀ C ∈ derivedFrom cs steps, Consequence base C) := by
  intro steps
  induction steps with
  | nil => intro cs hcs _ C hC; simpa [derivedFrom] using hcs C hC
  | cons s rest ih =>
      intro cs hcs hvalid
      rw [validFrom] at hvalid
      obtain ⟨hstep, hrest⟩ := (Bool.and_eq_true _ _).mp hvalid
      have hres : Consequence base (stepResolvent cs s) := step_consequence base cs s hcs hstep
      have hcs' : ∀ C ∈ cs ++ [stepResolvent cs s], Consequence base C := by
        intro C hC
        rcases List.mem_append.mp hC with h | h
        · exact hcs C h
        · rw [List.mem_singleton.mp h]; exact hres
      rw [derivedFrom]
      exact ih (cs ++ [stepResolvent cs s]) hcs' hrest

/-- The resolution-refutation certificate: a valid trace deriving the empty clause. -/
def checkCSPResolutionCert (base : List Clause) (steps : List Step) : Bool :=
  validFrom base steps && decide (([] : Clause) ∈ derivedFrom base steps)

/-- SOUNDNESS: a passing resolution refutation certifies the base CSP is unsatisfiable — i.e. the
    C5-labeling has no satisfying assignment, so the terminal block is NOT C5-extendable. -/
theorem checkCSPResolutionCert_sound (base : List Clause) (steps : List Step)
    (h : checkCSPResolutionCert base steps = true) : NoSat base := by
  unfold checkCSPResolutionCert at h
  obtain ⟨hvalid, hmem⟩ := (Bool.and_eq_true _ _).mp h
  have hemp : ([] : Clause) ∈ derivedFrom base steps := of_decide_eq_true hmem
  have hall : ∀ C ∈ derivedFrom base steps, Consequence base C :=
    derivedFrom_consequence base steps base (fun C hC a hsat => hsat C hC) hvalid
  intro a hsat
  exact nil_not_sat a (hall [] hemp a hsat)

end CSPResolution
end Erdos23Delta0
