import Erdos23Delta0.RowPartitionCore

/-!
# Provider-facing row partition

This is the provider-facing half of `WIRING_SPECS_GPTPRO.md` Spec 2.

The important guardrail is preserved here: EQODL1 is a whole-component
condition (`ComponentAllL5`), not the predicate `rowEll = 5` on a single row.
Mixed K2-components are routed wholesale to Branch-B, including any length-5
rows they contain.  For that reason this module produces the final row GERSH
bound directly, rather than trying to squeeze the component-scoped Branch-B
provider through the older length-only `Delta0Inputs.branchB` field.
-/

namespace Erdos23Delta0
namespace Rows
namespace RowPartition

open CertGraph
open RowPartitionCore

/-- The two provider classes used by the final dispatch table. -/
inductive RowClass where
  | eqodl1
  | branchB
deriving DecidableEq, Repr

/-- A component-level EQODL1 provider.  It supplies Branch-A bundles for every
row in a component known to be all length 5. -/
structure EQODL1ComponentCert (G : GraphData) (c : CutData) (rows : RowDB)
    (D : K2ComponentData rows) (comp : Fin D.componentCount) : Prop where
  bundle :
    ∀ i : RowIdx rows, D.compOfRow i = comp →
      BranchACertBundle G c rows (rowAt rows i)

/-- A component-scoped Branch-B provider.  It is intentionally stated as the
final row GERSH bound for every row in a mixed component, including length-5
rows.  This is the anti-leak guardrail from the spec. -/
structure BranchBComponentCert (G : GraphData) (c : CutData) (rows : RowDB)
    (D : K2ComponentData rows) (comp : Fin D.componentCount) : Prop where
  gersh :
    ∀ i : RowIdx rows, D.compOfRow i = comp →
      RowGershBound G c rows (rowAt rows i)

/-- Provider-facing dispatch data.  The generated/checker layer supplies a
class for each K2 component and component-level certificates for the selected
class. -/
structure ODLFullRowPartitionView
    (G : GraphData) (c : CutData) (rows : RowDB) where
  k2 : K2ComponentData rows
  classOf : Fin k2.componentCount → RowClass
  eqCert :
    ∀ comp : Fin k2.componentCount, classOf comp = RowClass.eqodl1 →
      EQODL1ComponentCert G c rows k2 comp
  branchCert :
    ∀ comp : Fin k2.componentCount, classOf comp = RowClass.branchB →
      BranchBComponentCert G c rows k2 comp

namespace ODLFullRowPartitionView

variable {G : GraphData} {c : CutData} {rows : RowDB}

/-- Semantic checker obligations for the dispatch table.  `R` is the concrete
row-connectivity relation shared by both branches. -/
structure Checked (P : ODLFullRowPartitionView G c rows)
    (R : RowIdx rows → RowIdx rows → Prop) : Prop where
  k2Sound : P.k2.SoundFor R
  class_eqodl1 :
    ∀ comp : Fin P.k2.componentCount,
      P.classOf comp = RowClass.eqodl1 ↔ P.k2.ComponentAllL5 comp
  class_branchB :
    ∀ comp : Fin P.k2.componentCount,
      P.classOf comp = RowClass.branchB ↔ P.k2.ComponentBranchB comp

/-- Component all-L5 rows are dispatched to EQODL1. -/
theorem class_eqodl1_of_allL5
    {P : ODLFullRowPartitionView G c rows}
    {R : RowIdx rows → RowIdx rows → Prop}
    (h : P.Checked R) (comp : Fin P.k2.componentCount)
    (hall : P.k2.ComponentAllL5 comp) :
    P.classOf comp = RowClass.eqodl1 :=
  (h.class_eqodl1 comp).2 hall

/-- Mixed components are dispatched to Branch-B. -/
theorem class_branchB_of_mixed
    {P : ODLFullRowPartitionView G c rows}
    {R : RowIdx rows → RowIdx rows → Prop}
    (h : P.Checked R) (comp : Fin P.k2.componentCount)
    (hmix : P.k2.ComponentBranchB comp) :
    P.classOf comp = RowClass.branchB :=
  (h.class_branchB comp).2 hmix

/-- Row-indexed dispatch to the final GERSH bound.  This is the key theorem:
it uses component membership, not row length, to choose the provider. -/
theorem rowGersh_of_partition
    {P : ODLFullRowPartitionView G c rows}
    {R : RowIdx rows → RowIdx rows → Prop}
    (h : P.Checked R) (i : RowIdx rows) :
    RowGershBound G c rows (rowAt rows i) := by
  classical
  have hcov := RowPartitionCore.rowCoverage P.k2 i
  rcases hcov with hEQ | hB
  · have hclass : P.classOf (P.k2.compOfRow i) = RowClass.eqodl1 :=
      class_eqodl1_of_allL5 h (P.k2.compOfRow i) hEQ.1
    exact gersh_L5_of_branchA_inputs ((P.eqCert (P.k2.compOfRow i) hclass).bundle i rfl).inputs
  · have hclass : P.classOf (P.k2.compOfRow i) = RowClass.branchB :=
      class_branchB_of_mixed h (P.k2.compOfRow i) hB.1
    exact (P.branchCert (P.k2.compOfRow i) hclass).gersh i rfl

private theorem exists_get_of_mem {l : List RowCert} {Q : RowCert}
    (hQ : Q ∈ l) :
    ∃ i : Fin l.length, l.get i = Q := by
  induction l with
  | nil =>
      simp at hQ
  | cons R Rs ih =>
      simp at hQ
      rcases hQ with hQR | hQR
      · refine ⟨⟨0, by simp⟩, ?_⟩
        simp [hQR]
      · rcases ih hQR with ⟨i, hi⟩
        refine ⟨⟨i.val + 1, by simp [i.isLt]⟩, ?_⟩
        exact hi

private theorem exists_rowIdx_of_mem {rows : RowDB} {Q : RowCert}
    (hQ : RowInDB rows Q) :
    ∃ i : RowIdx rows, rowAt rows i = Q := by
  unfold RowInDB at hQ
  simpa [RowIdx, rowAt] using exists_get_of_mem (l := rows.rowList) hQ

/-- Value-level `RowInDB` form consumed by `GammaBetaFacts`. -/
theorem allRowsGersh_of_partition
    {P : ODLFullRowPartitionView G c rows}
    {R : RowIdx rows → RowIdx rows → Prop}
    (h : P.Checked R) :
    ∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q := by
  intro Q hQ
  rcases exists_rowIdx_of_mem hQ with ⟨i, hi⟩
  simpa [hi] using rowGersh_of_partition (P := P) h i

/-- Direct δ=0 graph-data route from a checked component partition.  This is
the replacement for the old length-only `Delta0Inputs` dispatch. -/
theorem beta_bound_of_partitioned_provider
    {P : ODLFullRowPartitionView G c rows}
    {R : RowIdx rows → RowIdx rows → Prop}
    (hGood : GoodCutData G c rows) (h : P.Checked R) :
    hGood.gammaBeta.betaVal ≤ (G.n : ℚ) ^ 2 / 25 := by
  have hAllRows : ∀ Q : RowCert, RowInDB rows Q →
      RowGershBound G c rows Q :=
    allRowsGersh_of_partition (P := P) h
  have hGammaUpper : hGood.gammaBeta.gammaVal ≤ (G.n : ℚ) ^ 2 :=
    hGood.gammaBeta.gammaUpper_of_all_rows_gersh hAllRows
  exact beta_bound_of_gamma hGood.gammaBeta hGammaUpper


end ODLFullRowPartitionView

end RowPartition
end Rows
end Erdos23Delta0
