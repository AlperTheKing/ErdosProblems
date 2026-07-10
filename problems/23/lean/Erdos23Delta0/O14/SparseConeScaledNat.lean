import Erdos23Delta0.O14.SparseConeMatrix

namespace Erdos23Delta0
namespace O14
namespace SparseConeScaledNat

structure Term where
  weightId : Nat
  coeff : Int
  deriving Repr

structure Row where
  scalePred : Nat
  target : Int
  terms : List Term
  deriving Repr

def rowScale (row : Row) : Nat := row.scalePred + 1

def weightAt (weights : Array Nat) (weightId : Nat) : Nat :=
  (weights[weightId]?).getD 0

def scaledWeightedSum (weights : Array Nat) : List Term -> Int
  | [] => 0
  | term :: terms =>
      (weightAt weights term.weightId : Int) * term.coeff +
        scaledWeightedSum weights terms

def scaledResidual (weights : Array Nat) (row : Row) : Int :=
  row.target - scaledWeightedSum weights row.terms

def checkRow (weights : Array Nat) (row : Row) : Bool :=
  decide (0 <= scaledResidual weights row)

def checkRows (weights : Array Nat) : List Row -> Bool
  | [] => true
  | row :: rows => checkRow weights row && checkRows weights rows

def weightRat (denom : Nat) (weights : Array Nat) (weightId : Nat) : Rat :=
  (weightAt weights weightId : Rat) / (denom : Rat)

def coeffRat (row : Row) (term : Term) : Rat :=
  (term.coeff : Rat) / (rowScale row : Rat)

def targetRat (denom : Nat) (row : Row) : Rat :=
  (row.target : Rat) / ((denom : Rat) * (rowScale row : Rat))

def weightedSumRat (denom : Nat) (weights : Array Nat) (row : Row) : List Term -> Rat
  | [] => 0
  | term :: terms =>
      weightRat denom weights term.weightId * coeffRat row term +
        weightedSumRat denom weights row terms

def residualRat (denom : Nat) (weights : Array Nat) (row : Row) : Rat :=
  targetRat denom row - weightedSumRat denom weights row row.terms

theorem weightedSumRat_eq_scaled
    {denom : Nat} {weights : Array Nat} {row : Row}
    (hdenom : 0 < denom) :
    weightedSumRat denom weights row row.terms =
      (scaledWeightedSum weights row.terms : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  have hdenomRat : (denom : Rat) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hdenom)
  have hscale : 0 < rowScale row := by simp [rowScale]
  have hscaleRat : (rowScale row : Rat) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt hscale)
  induction row.terms with
  | nil => simp [weightedSumRat, scaledWeightedSum]
  | cons term terms ih =>
      simp only [weightedSumRat, scaledWeightedSum]
      rw [ih]
      simp only [weightRat, coeffRat]
      field_simp [hdenomRat, hscaleRat]
      norm_cast

theorem residualRat_eq_scaled
    {denom : Nat} {weights : Array Nat} {row : Row}
    (hdenom : 0 < denom) :
    residualRat denom weights row =
      (scaledResidual weights row : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  rw [residualRat, targetRat, weightedSumRat_eq_scaled hdenom]
  simp only [scaledResidual, Int.cast_sub]
  ring

theorem residualRat_nonneg_of_checkRow
    {denom : Nat} {weights : Array Nat} {row : Row}
    (hdenom : 0 < denom)
    (hcheck : checkRow weights row = true) :
    0 <= residualRat denom weights row := by
  have hresidual : 0 <= scaledResidual weights row := by
    simpa [checkRow] using hcheck
  rw [residualRat_eq_scaled hdenom]
  apply div_nonneg
  · exact_mod_cast hresidual
  · positivity

theorem residualRat_nonneg_of_scaled
    {denom : Nat} {weights : Array Nat} {row : Row}
    (hdenom : 0 < denom)
    (hresidual : 0 <= scaledResidual weights row) :
    0 <= residualRat denom weights row := by
  rw [residualRat_eq_scaled hdenom]
  apply div_nonneg
  · exact_mod_cast hresidual
  · positivity

theorem checkRows_eq_true_iff
    (weights : Array Nat) (rows : List Row) :
    checkRows weights rows = true <->
      ∀ row ∈ rows, checkRow weights row = true := by
  induction rows with
  | nil => simp [checkRows]
  | cons row rows ih =>
      simp [checkRows, ih]

theorem residualRat_nonneg_of_checkRows
    {denom : Nat} {weights : Array Nat} {rows : List Row}
    (hdenom : 0 < denom)
    (hcheck : checkRows weights rows = true)
    {row : Row} (hrow : row ∈ rows) :
    0 <= residualRat denom weights row := by
  apply residualRat_nonneg_of_checkRow hdenom
  exact (checkRows_eq_true_iff weights rows).mp hcheck row hrow

end SparseConeScaledNat
end O14
end Erdos23Delta0
