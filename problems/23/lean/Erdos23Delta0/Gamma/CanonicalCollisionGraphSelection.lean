import Erdos23Delta0.Gamma.CanonicalCollisionProgress
import Erdos23Delta0.Gamma.CollisionDefectGraphAdapter

/-!
# Canonical graph collision selector

This file specializes the generic two-stage finite selector to literal row
choices.  Its deterministic secondary score is the explicit mixed-radix tuple
rank used by the exact certificate emitters.  It proves that existence of any
zero-defect tuple is equivalent to totality at the canonical tuple.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionGraphSelection

open MinimumDemandRowSelection
open CanonicalCollisionHall
open CheckedCollisionDefectTrade
open CheckedCollisionLexTrade
open CanonicalCollisionLexSelection
open CanonicalCollisionProgress
open CollisionDefectGraphAdapter

/-- Prefix product of the row-family sizes before coordinate `i`. -/
def rowRadixPrefix (bads : List CertGraph.BadEdgeData) (i : Nat) : Nat :=
  ((bads.take i).map fun bad => bad.rows.length).prod

/-- Explicit little-endian mixed-radix rank
`sum_i rowIndex_i * product_{j<i} rowCount_j`. -/
def rowCode (bads : List CertGraph.BadEdgeData) :
    RowChoice bads → Nat :=
  fun omega => ∑ i : Fin bads.length,
    (omega i).1 * rowRadixPrefix bads i.1

/-- A separate finite equivalence gives an injective audit code independent
of the mixed-radix arithmetic.  The live selector uses `rowCode`; every lex
trade carries and checks its strict `rowCode` inequality explicitly. -/
noncomputable def finiteAuditCode (bads : List CertGraph.BadEdgeData) :
    RowChoice bads → Nat :=
  fun omega => (Fintype.equivFin (RowChoice bads) omega).1

theorem finiteAuditCode_injective (bads : List CertGraph.BadEdgeData) :
    Function.Injective (finiteAuditCode bads) := by
  intro omega eta h
  apply (Fintype.equivFin (RowChoice bads)).injective
  exact Fin.ext h

/-- The honest canonical row tuple for collision matching. -/
noncomputable def canonicalChoice
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads) : RowChoice bads := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice hrows⟩
  exact canonicalState (defectData G c bads R) (rowCode bads)

theorem canonicalChoice_lexMinimal
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads) :
    LexMinimal (defectData G c bads R) (rowCode bads)
      (canonicalChoice G c bads R hrows) := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice hrows⟩
  exact canonicalState_lexMinimal (defectData G c bads R) (rowCode bads)

/-- If any row tuple has zero defect, the canonical tuple has zero defect. -/
theorem canonicalChoice_defect_eq_zero_of_exists
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads)
    (hexists : ∃ omega : RowChoice bads,
      (defectData G c bads R).collisionDefect omega = 0) :
    (defectData G c bads R).collisionDefect
      (canonicalChoice G c bads R hrows) = 0 := by
  obtain ⟨omega, homega⟩ := hexists
  have hle := (canonicalChoice_lexMinimal G c bads R hrows).1 omega
  exact Nat.eq_zero_of_le_zero (homega ▸ hle)

/-- Graph-specialized progress predicate with row-choice nonemptiness supplied
by the checked complete-row database. -/
def GraphProgressAtCanonical
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads)
    (stateRealized : RowChoice bads → Prop)
    (ChangeWitness : Type*)
    (simultaneousRowChangeRealized :
      RowChoice bads → RowChoice bads → ChangeWitness → Prop) : Prop :=
  let _ : Nonempty (RowChoice bads) := ⟨defaultChoice hrows⟩
  ProgressAtCanonical (defectData G c bads R)
      (rowCode bads) stateRealized ChangeWitness
      simultaneousRowChangeRealized

/-- Any graph-checked progress producer at the canonical tuple gives a total
coherent collision assignment there. -/
theorem canonicalChoice_total_of_progress
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads)
    {stateRealized : RowChoice bads → Prop}
    {ChangeWitness : Type*}
    {simultaneousRowChangeRealized :
      RowChoice bads → RowChoice bads → ChangeWitness → Prop}
    (hprogress : GraphProgressAtCanonical G c bads R hrows
      stateRealized ChangeWitness simultaneousRowChangeRealized) :
    Nonempty (TotalCoherentAssignment G c R
      (canonicalChoice G c bads R hrows)) := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice hrows⟩
  have hp : ProgressAtCanonical (defectData G c bads R)
      (rowCode bads) stateRealized ChangeWitness
      simultaneousRowChangeRealized := by
    simpa [GraphProgressAtCanonical] using hprogress
  apply (collisionDefect_eq_zero_iff_total G c R
    (canonicalChoice G c bads R hrows)).mp
  exact canonical_defect_eq_zero_of_progress hp

/-- Feasibility is exactly total coherent assignment at the canonical tuple.
The graph hypotheses remain explicit and are not packaged as certificate
fields. -/
theorem feasibility_iff_canonical_total
    (G : CertGraph.GraphData) (c : CertGraph.CutData)
    (bads : List CertGraph.BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads)
    (hrows : RowsNonempty bads) :
    NoCommonBlueCollisionFeasibility G c bads R ↔
      (CertGraph.TriangleFree G → CertGraph.IsMaxCut G c →
        CertGraph.BConnected G c →
        CompleteShortestRowDB G c bads →
          Nonempty (TotalCoherentAssignment G c R
            (canonicalChoice G c bads R hrows))) := by
  constructor
  · intro hfeasible htri hmax hconnected hdb
    have hexists : ∃ omega : RowChoice bads,
        (defectData G c bads R).collisionDefect omega = 0 :=
      exists_zero_collisionDefect_of_feasibility G c bads R hfeasible
        htri hmax hconnected hdb
    exact (collisionDefect_eq_zero_iff_total G c R
      (canonicalChoice G c bads R hrows)).mp
        (canonicalChoice_defect_eq_zero_of_exists G c bads R hrows hexists)
  · intro hcanonical htri hmax hconnected hdb
    exact ⟨canonicalChoice G c bads R hrows,
      hcanonical htri hmax hconnected hdb⟩

#print axioms finiteAuditCode_injective
#print axioms canonicalChoice_lexMinimal
#print axioms canonicalChoice_defect_eq_zero_of_exists
#print axioms canonicalChoice_total_of_progress
#print axioms feasibility_iff_canonical_total

end CanonicalCollisionGraphSelection
end Gamma
end Erdos23Delta0
