import Erdos23Delta0.O14.SparseConeScaledNat

namespace Erdos23Delta0
namespace O14
namespace SparseConeScaledFun

open SparseConeScaledNat (Term Row rowScale)

def scaledWeightedSum (weight : Nat -> Nat) : List Term -> Int
  | [] => 0
  | term :: terms =>
      (weight term.weightId : Int) * term.coeff + scaledWeightedSum weight terms

def scaledResidual (weight : Nat -> Nat) (row : Row) : Int :=
  row.target - scaledWeightedSum weight row.terms

def weightRat (denom : Nat) (weight : Nat -> Nat) (weightId : Nat) : Rat :=
  (weight weightId : Rat) / (denom : Rat)

def coeffRat (row : Row) (term : Term) : Rat :=
  (term.coeff : Rat) / (rowScale row : Rat)

def targetRat (denom : Nat) (row : Row) : Rat :=
  (row.target : Rat) / ((denom : Rat) * (rowScale row : Rat))

def weightedSumRat (denom : Nat) (weight : Nat -> Nat) (row : Row) : List Term -> Rat
  | [] => 0
  | term :: terms =>
      weightRat denom weight term.weightId * coeffRat row term +
        weightedSumRat denom weight row terms

def residualRat (denom : Nat) (weight : Nat -> Nat) (row : Row) : Rat :=
  targetRat denom row - weightedSumRat denom weight row row.terms

theorem weightedSumRat_eq_scaled
    {denom : Nat} {weight : Nat -> Nat} {row : Row}
    (hdenom : 0 < denom) :
    weightedSumRat denom weight row row.terms =
      (scaledWeightedSum weight row.terms : Rat) /
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
    {denom : Nat} {weight : Nat -> Nat} {row : Row}
    (hdenom : 0 < denom) :
    residualRat denom weight row =
      (scaledResidual weight row : Rat) /
        ((denom : Rat) * (rowScale row : Rat)) := by
  rw [residualRat, targetRat, weightedSumRat_eq_scaled hdenom]
  simp only [scaledResidual, Int.cast_sub]
  ring

theorem residualRat_nonneg_of_scaled
    {denom : Nat} {weight : Nat -> Nat} {row : Row}
    (hdenom : 0 < denom)
    (hresidual : 0 <= scaledResidual weight row) :
    0 <= residualRat denom weight row := by
  rw [residualRat_eq_scaled hdenom]
  apply div_nonneg
  · exact_mod_cast hresidual
  · positivity

end SparseConeScaledFun
end O14
end Erdos23Delta0
