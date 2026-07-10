import Erdos23Delta0.Ell5BlockSingleton

/-!
# Finite inactive-component block checker

This module reflects exactly the finite hypotheses of
`certificate_of_blockSingleton_boundaryDoors`. It accepts explicit graph,
cut, core, selected-atom, support, off-support, block-label, Door, and
capacity data. It does not assert that any graph admits an accepted input.
-/

namespace Erdos23Delta0
namespace InactiveComponentBlockChecker

open Finset MaxCutVertexIneq
open Ell5BlockSingleton Ell5FullBankInterface

variable {V Block : Type*}
variable [Fintype V] [DecidableEq V]
variable [Fintype Block] [DecidableEq Block]

local instance blocksApartDecidable (block : V → Block) (e : Sym2 V) :
    Decidable (BlocksApart block e) := by
  unfold BlocksApart
  infer_instance

local instance sameBlockDecidable (block : V → Block) (e : Sym2 V) :
    Decidable (SameBlock block e) := by
  unfold SameBlock
  infer_instance

/-- Boolean universal quantification over exactly the entries of a finset. -/
def finsetAll {α : Type*} [DecidableEq α]
    (s : Finset α) (P : α → Prop) [DecidablePred P] : Bool :=
  decide (∀ x : {x // x ∈ s}, P x)

theorem finsetAll_eq_true_iff {α : Type*} [DecidableEq α]
    (s : Finset α) (P : α → Prop) [DecidablePred P] :
    finsetAll s P = true ↔ ∀ x ∈ s, P x := by
  simp [finsetAll]

/-- Explicit finite cut, core, edge classes, block labels, and Door data. -/
structure Candidate (V Block : Type*) [Fintype V] [DecidableEq V]
    [Fintype Block] [DecidableEq Block] where
  cut : V → Bool
  core : Finset V
  selectedAtoms : Finset (Sym2 V)
  support : Finset (Sym2 V)
  offSupport : Finset (Sym2 V)
  blockLabel : V → Block
  legal : Sym2 V → Sym2 V → Bool
  capacity : Sym2 V → ℚ

variable (G : SimpleGraph V) [DecidableRel G.Adj]
variable (D : Candidate V Block)

local instance graphEdgeSetFintype : Fintype G.edgeSet :=
  G.fintypeEdgeSet

/-- Exactly the bounded hypotheses consumed by the block-singleton
boundary-Door certificate constructor. -/
def Candidate.Valid : Prop :=
  (∀ e ∈ D.selectedAtoms,
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = false ∧
      e ∈ D.core.sym2 ∧ BlocksApart D.blockLabel e) ∧
  (∀ e ∈ D.support,
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = true) ∧
  (∀ e ∈ D.offSupport,
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = true ∧
      (edgeBoundary D.core e = true ∨
        (e ∈ D.core.sym2 ∧ SameBlock D.blockLabel e))) ∧
  (∀ e ∈ D.offSupport, edgeBoundary D.core e = true → D.legal e e = true) ∧
  (∀ e ∈ D.offSupport,
    edgeBoundary D.core e = true → (1 / 2 : ℚ) ≤ D.capacity e) ∧
  (∀ e ∈ D.offSupport, 0 ≤ D.capacity e)

/-- Boolean checker for all block-singleton certificate obligations. -/
def check : Bool :=
  finsetAll D.selectedAtoms (fun e =>
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = false ∧
      e ∈ D.core.sym2 ∧ BlocksApart D.blockLabel e) &&
  (finsetAll D.support (fun e =>
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = true) &&
  (finsetAll D.offSupport (fun e =>
    e ∈ G.edgeFinset ∧ edgeCut D.cut e = true ∧
      (edgeBoundary D.core e = true ∨
        (e ∈ D.core.sym2 ∧ SameBlock D.blockLabel e))) &&
  (finsetAll D.offSupport (fun e =>
    edgeBoundary D.core e = true → D.legal e e = true) &&
  (finsetAll D.offSupport (fun e =>
    edgeBoundary D.core e = true → (1 / 2 : ℚ) ≤ D.capacity e) &&
  finsetAll D.offSupport (fun e => 0 ≤ D.capacity e)))))

theorem check_eq_true_iff : check G D = true ↔ D.Valid G := by
  simp [check, Candidate.Valid, finsetAll_eq_true_iff]

/-- Checker soundness: an accepted finite input constructs the existing
full-bank relaxed-cover certificate, using no graph-side existence premise. -/
noncomputable def certificate_of_check (hcheck : check G D = true) :
    FullBankRelaxedCoverCert
      D.selectedAtoms D.support D.offSupport D.offSupport Finset.univ
      (fun b => deltaM G D.cut (blockSet D.core D.blockLabel b))
      (fun b => deltaB G D.cut (blockSet D.core D.blockLabel b))
      (fun c j => D.legal c j = true) D.capacity := by
  rcases (check_eq_true_iff G D).1 hcheck with
    ⟨hselected, hsupport, hoffSupport, hlegal, hhalf, hnonneg⟩
  exact certificate_of_blockSingleton_boundaryDoors
    G D.cut D.core D.blockLabel
    D.selectedAtoms D.support D.offSupport
    (fun c j => D.legal c j = true) D.capacity
    hnonneg hselected hsupport hoffSupport hlegal hhalf

#print axioms certificate_of_check

end InactiveComponentBlockChecker
end Erdos23Delta0
