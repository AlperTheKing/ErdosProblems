import Mathlib
import Erdos23Delta0.CertGraph

/-!
# The row partition core (2026-07-09)

SPEC 2 of the critical wiring specs (`WIRING_SPECS_GPTPRO.md`), fixing the architecture audit's MISSING-SPEC 2.
**The key correction: EQODL1 membership is a COMPONENT-level equal-length condition — a row of length 5 inside
a mixed component is Branch-B.** The wrong definition (`IsEQODL1Row i := rowEll i = 5`) would leak mixed-component
length-5 rows out of the partition; the correct one routes them to Branch-B, whose machinery is component-scoped.

The K2-component table is data (`compOfRow`), so the provider gets a decidable dispatch; its semantic soundness
against the graph-level row-connectivity relation is a separate checked obligation (parameterized here as `R`
until the concrete relation is wired). Compiled here: the class definitions, the anti-bug theorem
(`nonEQ_L5_row_is_BranchB`), the exhaustive coverage theorem (`rowCoverage`: every row is in EXACTLY one class),
the long-row guardrail, and the no-third-class theorem. All pure finite case analysis.
No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace RowPartitionCore

open CertGraph

abbrev RowIdx (rows : RowDB) := Fin rows.rowList.length

def rowAt (rows : RowDB) (i : RowIdx rows) : RowCert :=
  rows.rowList.get i

/-- Row length as the vertex count of the recorded geodesic (ell = path length + 1 = |verts|). -/
def rowEll (rows : RowDB) (i : RowIdx rows) : Nat :=
  (rowAt rows i).verts.length

/-- The K2/B-component dispatch table: pure data, so the provider can branch decidably. -/
structure K2ComponentData (rows : RowDB) where
  componentCount : Nat
  compOfRow : RowIdx rows → Fin componentCount

namespace K2ComponentData

variable {rows : RowDB} (D : K2ComponentData rows)

/-- Semantic soundness against a row-connectivity relation `R` (to be instantiated with the graph-level
    `RowsK2Connected` used by BOTH branches — the partition is unsound if the branches disagree on it). -/
def SoundFor (R : RowIdx rows → RowIdx rows → Prop) : Prop :=
  ∀ i j : RowIdx rows, D.compOfRow i = D.compOfRow j ↔ R i j

def sameComponent (i j : RowIdx rows) : Prop :=
  D.compOfRow i = D.compOfRow j

/-- EQ = the WHOLE K2 component is equal-length L=5 (never merely "this row has length 5"). -/
def ComponentAllL5 (c : Fin D.componentCount) : Prop :=
  ∀ i : RowIdx rows, D.compOfRow i = c → rowEll rows i = 5

def ComponentBranchB (c : Fin D.componentCount) : Prop :=
  ¬ D.ComponentAllL5 c

def IsEQODL1Row (i : RowIdx rows) : Prop :=
  D.ComponentAllL5 (D.compOfRow i)

/-- Branch-B intentionally owns mixed components WHOLESALE, including their length-5 rows. -/
def IsBranchBRow (i : RowIdx rows) : Prop :=
  D.ComponentBranchB (D.compOfRow i)

/-- Diagnostic only; provably uninhabited (`noOtherGreenLeafRows`). -/
def IsOtherGreenLeafRow (i : RowIdx rows) : Prop :=
  ¬ D.IsEQODL1Row i ∧ ¬ D.IsBranchBRow i

/-- **The anti-bug theorem:** a length-5 row in a MIXED component is Branch-B. -/
theorem nonEQ_L5_row_is_BranchB (i : RowIdx rows)
    (hmixed : ∃ j : RowIdx rows, D.sameComponent i j ∧ rowEll rows j ≠ 5) :
    D.IsBranchBRow i := by
  rcases hmixed with ⟨j, hcomp, hjne⟩
  intro hall
  exact hjne (hall j hcomp.symm)

/-- Guardrail: with the triangle-free minimum length in hand, a Branch-B component genuinely contains a row
    of length `> 5` (not merely `≠ 5`). -/
theorem BranchB_component_contains_long_row
    (hMinLen : ∀ i : RowIdx rows, 5 ≤ rowEll rows i)
    (i : RowIdx rows) (hB : D.IsBranchBRow i) :
    ∃ j : RowIdx rows, D.sameComponent i j ∧ 5 < rowEll rows j := by
  classical
  unfold IsBranchBRow ComponentBranchB ComponentAllL5 at hB
  push_neg at hB
  obtain ⟨j, hjcomp, hjne⟩ := hB
  exact ⟨j, hjcomp.symm, lt_of_le_of_ne (hMinLen j) (Ne.symm hjne)⟩

end K2ComponentData

/-- Exactly one of two propositions holds. -/
def ExactlyOne (P Q : Prop) : Prop :=
  (P ∧ ¬ Q) ∨ (Q ∧ ¬ P)

/-- **Exhaustive row coverage:** every row is in EXACTLY one class. Pure case split — no graph input. -/
theorem rowCoverage {rows : RowDB} (D : K2ComponentData rows) :
    ∀ i : RowIdx rows, ExactlyOne (D.IsEQODL1Row i) (D.IsBranchBRow i) := by
  intro i
  classical
  by_cases hP : D.ComponentAllL5 (D.compOfRow i)
  · exact Or.inl ⟨hP, fun hB => hB hP⟩
  · exact Or.inr ⟨hP, fun hEQ => hP hEQ⟩

/-- There is no third class. -/
theorem noOtherGreenLeafRows {rows : RowDB} (D : K2ComponentData rows) :
    ∀ i : RowIdx rows, ¬ D.IsOtherGreenLeafRow i := by
  intro i h
  exact h.2 h.1


end RowPartitionCore
end Erdos23Delta0
