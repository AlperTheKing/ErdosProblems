import Erdos23Delta0.O14.SparseConeMatrix

namespace Erdos23Delta0
namespace O14
namespace SparseConePacked

structure Term where
  weightId : Nat
  coeff : Rat
  deriving Repr

structure Row where
  target : Rat
  terms : List Term
  deriving Repr

def weightAt (weights : Array Rat) (weightId : Nat) : Rat :=
  (weights[weightId]?).getD 0

def weightedSum (weights : Array Rat) (row : Row) : Rat :=
  row.terms.foldl
    (fun total term => total + weightAt weights term.weightId * term.coeff)
    0

def residual (weights : Array Rat) (row : Row) : Rat :=
  row.target - weightedSum weights row

def checkRow (weights : Array Rat) (row : Row) : Bool :=
  decide (0 <= residual weights row)

def checkRows (weights : Array Rat) (rows : List Row) : Bool :=
  rows.all (checkRow weights)

theorem checkRow_eq_true_iff (weights : Array Rat) (row : Row) :
    checkRow weights row = true <-> 0 <= residual weights row := by
  simp [checkRow]

theorem residual_nonneg_of_checkRow
    (weights : Array Rat) (row : Row)
    (hcheck : checkRow weights row = true) :
    0 <= residual weights row :=
  (checkRow_eq_true_iff weights row).mp hcheck

theorem residual_nonneg_of_checkRows
    (weights : Array Rat) (rows : List Row)
    (hcheck : checkRows weights rows = true)
    {row : Row} (hrow : row ∈ rows) :
    0 <= residual weights row := by
  rw [checkRows, List.all_eq_true] at hcheck
  exact residual_nonneg_of_checkRow weights row (hcheck row hrow)

end SparseConePacked
end O14
end Erdos23Delta0
