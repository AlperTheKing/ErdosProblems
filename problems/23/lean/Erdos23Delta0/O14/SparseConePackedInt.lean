import Erdos23Delta0.O14.ConeEvalBridge

/-!
# Packed integer source-matrix rows

This kernel stores every sparse matrix term once.  Generated rows use a
balanced `TermTree`, so ordinary kernel reduction checks one row at a time
without constructing the long left-associated sums used by the earlier
direct-integer pilot.

The soundness lemmas clear two positive denominators: the common solution
denominator and a row-local coefficient denominator.  A successful integer
check therefore supplies the exact rational base coefficient consumed by
`ConeEvalBridge.coreODLGoal_of_coneEval`.
-/

namespace Erdos23Delta0
namespace O14
namespace SparseConePackedInt

open PolyCert
open ODLFull
open ConeEvalBridge

/-- One nonzero source-matrix entry after clearing its row denominator. -/
structure Term where
  weightId : Nat
  coeff : Int

/-- A balanced serialization of sparse terms. -/
inductive TermTree where
  | empty
  | leaf (term : Term)
  | node (left right : TermTree)

/-- One denominator-cleared source-matrix row. -/
structure Row where
  scalePred : Nat
  target : Int
  terms : TermTree

/-- A row together with its Bernstein monomial metadata. -/
structure NFRow where
  row : Row
  factor : Nat
  pows : List (Prod Var Nat)

def rowScale (row : Row) : Nat := row.scalePred + 1

/-- A generated balanced dictionary; leftSize makes lookup logarithmic. -/
inductive WeightTree where
  | empty
  | leaf (value : Nat)
  | node (leftSize : Nat) (left right : WeightTree)

def WeightTree.get : WeightTree -> Nat -> Nat
  | .empty, _ => 0
  | .leaf value, index => if index = 0 then value else 0
  | .node leftSize left right, index =>
      if index < leftSize then left.get index
      else right.get (index - leftSize)

def weightAt (weights : WeightTree) (weightId : Nat) : Nat :=
  weights.get weightId

def Term.evalInt (weights : WeightTree) (term : Term) : Int :=
  (weightAt weights term.weightId : Int) * term.coeff

def TermTree.evalInt (weights : WeightTree) : TermTree -> Int
  | .empty => 0
  | .leaf term => term.evalInt weights
  | .node left right => left.evalInt weights + right.evalInt weights

def TermTree.all (p : Term -> Bool) : TermTree -> Bool
  | .empty => true
  | .leaf term => p term
  | .node left right => left.all p && right.all p

def scaledResidual (weights : WeightTree) (row : Row) : Int :=
  row.target - row.terms.evalInt weights

def termValid (weightCount : Nat) (term : Term) : Bool :=
  decide (term.weightId < weightCount)

/-- The generated proof is deliberately row-local: `by decide` or `rfl`. -/
def checkRow (weightCount : Nat) (weights : WeightTree) (row : Row) : Bool :=
  row.terms.all (termValid weightCount) && decide (0 <= scaledResidual weights row)

def checkRows (weightCount : Nat) (weights : WeightTree) (rows : List NFRow) : Bool :=
  rows.all (fun item => checkRow weightCount weights item.row)

def weightRat (denom : Nat) (weights : WeightTree) (weightId : Nat) : Rat :=
  (weightAt weights weightId : Rat) / (denom : Rat)

def coeffRat (row : Row) (term : Term) : Rat :=
  (term.coeff : Rat) / (rowScale row : Rat)

def Term.evalRat
    (denom : Nat) (weights : WeightTree) (row : Row) (term : Term) : Rat :=
  weightRat denom weights term.weightId * coeffRat row term

def TermTree.evalRat
    (denom : Nat) (weights : WeightTree) (row : Row) : TermTree -> Rat
  | .empty => 0
  | .leaf term => term.evalRat denom weights row
  | .node left right =>
      left.evalRat denom weights row + right.evalRat denom weights row

def targetRat (denom : Nat) (row : Row) : Rat :=
  (row.target : Rat) / ((denom : Rat) * (rowScale row : Rat))

def residualRat (denom : Nat) (weights : WeightTree) (row : Row) : Rat :=
  targetRat denom row - row.terms.evalRat denom weights row

def NFRow.mono (denom : Nat) (weights : WeightTree) (item : NFRow) : Mono :=
  { coeff := (item.factor : Rat) * residualRat denom weights item.row
    pows := item.pows }

def base (denom : Nat) (weights : WeightTree) (rows : List NFRow) : NF :=
  rows.map (NFRow.mono denom weights)

theorem scaledResidual_nonneg_of_checkRow
    {weightCount : Nat} {weights : WeightTree} {row : Row}
    (hcheck : checkRow weightCount weights row = true) :
    0 <= scaledResidual weights row := by
  simp only [checkRow, Bool.and_eq_true, decide_eq_true_eq] at hcheck
  exact hcheck.2

theorem term_evalRat_eq_evalInt_div
    {denom : Nat} {weights : WeightTree} {row : Row}
    (hdenom : 0 < denom) (term : Term) :
    term.evalRat denom weights row =
      (term.evalInt weights : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  have hdenomRat : Not ((denom : Rat) = 0) := by
    exact_mod_cast Nat.ne_of_gt hdenom
  have hscale : 0 < rowScale row := by simp [rowScale]
  have hscaleRat : Not ((rowScale row : Rat) = 0) := by
    exact_mod_cast Nat.ne_of_gt hscale
  simp only [Term.evalRat, Term.evalInt, weightRat, coeffRat]
  field_simp [hdenomRat, hscaleRat]
  norm_cast

theorem termTree_evalRat_eq_evalInt_div
    {denom : Nat} {weights : WeightTree} {row : Row}
    (hdenom : 0 < denom) (tree : TermTree) :
    tree.evalRat denom weights row =
      (tree.evalInt weights : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  induction tree with
  | empty => simp [TermTree.evalRat, TermTree.evalInt]
  | leaf term => exact term_evalRat_eq_evalInt_div hdenom term
  | node left right ihLeft ihRight =>
      simp only [TermTree.evalRat, TermTree.evalInt]
      rw [ihLeft, ihRight]
      push_cast
      ring

theorem residualRat_eq_scaled
    {denom : Nat} {weights : WeightTree} {row : Row}
    (hdenom : 0 < denom) :
    residualRat denom weights row =
      (scaledResidual weights row : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  rw [residualRat, targetRat, termTree_evalRat_eq_evalInt_div hdenom]
  simp only [scaledResidual, Int.cast_sub]
  ring

theorem residualRat_nonneg_of_checkRow
    {denom weightCount : Nat} {weights : WeightTree} {row : Row}
    (hdenom : 0 < denom)
    (hcheck : checkRow weightCount weights row = true) :
    0 <= residualRat denom weights row := by
  rw [residualRat_eq_scaled hdenom]
  apply div_nonneg
  . exact_mod_cast scaledResidual_nonneg_of_checkRow hcheck
  . positivity

theorem nfRow_coeff_nonneg_of_checkRow
    {denom weightCount : Nat} {weights : WeightTree} {item : NFRow}
    (hdenom : 0 < denom)
    (hcheck : checkRow weightCount weights item.row = true) :
    0 <= (item.mono denom weights).coeff := by
  simp only [NFRow.mono]
  exact mul_nonneg (by positivity)
    (residualRat_nonneg_of_checkRow hdenom hcheck)

theorem base_allCoeffNonneg_of_checkRows
    {denom weightCount : Nat} {weights : WeightTree} {rows : List NFRow}
    (hdenom : 0 < denom)
    (hcheck : checkRows weightCount weights rows = true) :
    (base denom weights rows).allCoeffNonneg = true := by
  induction rows with
  | nil => rfl
  | cons item rows ih =>
      simp only [checkRows, List.all_cons, Bool.and_eq_true] at hcheck
      simp only [base, List.map_cons, NF.allCoeffNonneg, List.all_cons,
        Bool.and_eq_true, decide_eq_true_eq]
      constructor
      . exact nfRow_coeff_nonneg_of_checkRow hdenom hcheck.1
      . exact ih hcheck.2

theorem list_all_append_true {alpha : Type} (p : alpha -> Bool) :
    forall left right : List alpha,
      left.all p = true -> right.all p = true -> (left ++ right).all p = true
  | [], right, _, hright => by simpa using hright
  | item :: left, right, hleft, hright => by
      simp only [List.all_cons, Bool.and_eq_true] at hleft
      change (p item && (left ++ right).all p) = true
      rw [hleft.1, list_all_append_true p left right hleft.2 hright]
      rfl

theorem allCoeffNonneg_append
    (left right : NF)
    (hleft : left.allCoeffNonneg = true)
    (hright : right.allCoeffNonneg = true) :
    (left ++ right).allCoeffNonneg = true := by
  unfold NF.allCoeffNonneg at hleft hright
  unfold NF.allCoeffNonneg
  exact list_all_append_true _ left right hleft hright

theorem allCoeffNonneg_flatten :
    forall chunks : List NF,
      chunks.all NF.allCoeffNonneg = true ->
        NF.allCoeffNonneg chunks.flatten = true
  | [], _ => by rfl
  | chunk :: chunks, hcheck => by
      simp only [List.all_cons, Bool.and_eq_true] at hcheck
      simp only [List.flatten_cons]
      exact allCoeffNonneg_append chunk chunks.flatten hcheck.1
        (allCoeffNonneg_flatten chunks hcheck.2)

theorem all_allCoeffNonneg_flatten :
    forall chunks : List (List NF),
      chunks.all (fun rows => rows.all NF.allCoeffNonneg) = true ->
        chunks.flatten.all NF.allCoeffNonneg = true
  | [], _ => by rfl
  | chunk :: chunks, hcheck => by
      simp only [List.all_cons, Bool.and_eq_true] at hcheck
      simp only [List.flatten_cons]
      exact list_all_append_true NF.allCoeffNonneg chunk chunks.flatten hcheck.1
        (all_allCoeffNonneg_flatten chunks hcheck.2)

/-- Direct adapter from packed row checks to the production ConeEval API. -/
theorem coreODLGoal_of_packedRows
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rowDB : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rowDB Q)
    (denom weightCount : Nat) (weights : WeightTree) (packedRows : List NFRow)
    (target : NF) (mults slacks : List NF) (env : Var -> Rat)
    (hdenom : 0 < denom)
    (hrows : checkRows weightCount weights packedRows = true)
    (hvars : forall v, 0 <= env v)
    (hmults : mults.all NF.allCoeffNonneg = true)
    (hslacks : forall s, s ∈ slacks -> 0 <= NF.eval env s)
    (hidEval :
      NF.eval env target =
        NF.eval env (comboNF (base denom weights packedRows) mults slacks))
    (htarget : NF.eval env target = coreDefect core) :
    CoreODLGoal G c rowDB Q core := by
  exact coreODLGoal_of_coneEval core target (base denom weights packedRows)
    mults slacks env hvars
    (base_allCoeffNonneg_of_checkRows hdenom hrows)
    hmults hslacks hidEval htarget

end SparseConePackedInt
end O14
end Erdos23Delta0
