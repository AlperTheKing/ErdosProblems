import Erdos23Delta0.O14.SparseConeMatrix

namespace Erdos23Delta0
namespace O14
namespace SparseConeScaled

structure Term where
  weightId : Nat
  coeff : Int
  deriving Repr

structure Row where
  scale : Nat
  target : Int
  terms : List Term
  deriving Repr

def weightAt (weights : Array Int) (weightId : Nat) : Int :=
  (weights[weightId]?).getD 0

def scaledWeightedSum (weights : Array Int) : List Term -> Int
  | [] => 0
  | term :: terms =>
      weightAt weights term.weightId * term.coeff + scaledWeightedSum weights terms

def scaledResidual (weights : Array Int) (row : Row) : Int :=
  row.target - scaledWeightedSum weights row.terms

def termValid (weights : Array Int) (term : Term) : Bool :=
  decide (term.weightId < weights.size)

def checkRow (weights : Array Int) (row : Row) : Bool :=
  decide (0 < row.scale) &&
    row.terms.all (termValid weights) &&
    decide (0 <= scaledResidual weights row)

def checkRows (weights : Array Int) (rows : List Row) : Bool :=
  rows.all (checkRow weights)

def checkWeights (denom : Nat) (weights : Array Int) : Bool :=
  decide (0 < denom) && weights.all (fun weight => decide (0 <= weight))

def weightRat (denom : Nat) (weights : Array Int) (weightId : Nat) : Rat :=
  (weightAt weights weightId : Rat) / (denom : Rat)

def coeffRat (row : Row) (term : Term) : Rat :=
  (term.coeff : Rat) / (row.scale : Rat)

def targetRat (denom : Nat) (row : Row) : Rat :=
  (row.target : Rat) / ((denom : Rat) * (row.scale : Rat))

def weightedSumRat (denom : Nat) (weights : Array Int) (row : Row) : List Term -> Rat
  | [] => 0
  | term :: terms =>
      weightRat denom weights term.weightId * coeffRat row term +
        weightedSumRat denom weights row terms

def residualRat (denom : Nat) (weights : Array Int) (row : Row) : Rat :=
  targetRat denom row - weightedSumRat denom weights row row.terms

theorem weightedSumRat_eq_scaled
    {denom : Nat} {weights : Array Int} {row : Row}
    (hdenom : 0 < denom) (hscale : 0 < row.scale) :
    weightedSumRat denom weights row row.terms =
      (scaledWeightedSum weights row.terms : Rat) /
        ((denom : Rat) * (row.scale : Rat)) := by
  have hdenomRat : (denom : Rat) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hdenom)
  have hscaleRat : (row.scale : Rat) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hscale)
  induction row.terms with
  | nil => simp [weightedSumRat, scaledWeightedSum]
  | cons term terms ih =>
      simp only [weightedSumRat, scaledWeightedSum]
      rw [ih]
      simp only [weightRat, coeffRat]
      field_simp [hdenomRat, hscaleRat]
      norm_cast

theorem residualRat_eq_scaled
    {denom : Nat} {weights : Array Int} {row : Row}
    (hdenom : 0 < denom) (hscale : 0 < row.scale) :
    residualRat denom weights row =
      (scaledResidual weights row : Rat) /
        ((denom : Rat) * (row.scale : Rat)) := by
  rw [residualRat, targetRat, weightedSumRat_eq_scaled hdenom hscale]
  simp only [scaledResidual, Int.cast_sub]
  ring

theorem rowFacts_of_checkRow
    {weights : Array Int} {row : Row}
    (hcheck : checkRow weights row = true) :
    0 < row.scale ∧
      (∀ term ∈ row.terms, term.weightId < weights.size) ∧
      0 <= scaledResidual weights row := by
  simp [checkRow, termValid, List.all_eq_true] at hcheck
  exact ⟨hcheck.1.1, hcheck.1.2, hcheck.2⟩

theorem residualRat_nonneg_of_checkRow
    {denom : Nat} {weights : Array Int} {row : Row}
    (hdenom : 0 < denom)
    (hcheck : checkRow weights row = true) :
    0 <= residualRat denom weights row := by
  obtain ⟨hscale, _hids, hresidual⟩ := rowFacts_of_checkRow hcheck
  rw [residualRat_eq_scaled hdenom hscale]
  apply div_nonneg
  · exact_mod_cast hresidual
  · positivity

theorem weightFacts_of_checkWeights
    {denom : Nat} {weights : Array Int}
    (hcheck : checkWeights denom weights = true) :
    0 < denom ∧ ∀ index : Fin weights.size, 0 <= weights[index] := by
  simp [checkWeights, Array.all_eq_true] at hcheck
  refine ⟨hcheck.1, ?_⟩
  intro index
  exact hcheck.2 index.1 index.2

end SparseConeScaled
end O14
end Erdos23Delta0
