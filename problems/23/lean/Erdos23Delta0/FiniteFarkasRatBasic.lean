import Mathlib

/-!
# Finite rational Farkas: basic interfaces

The theorem-level exact-rational interface used by the banked wall LP.  This
module contains only the two alternatives and weak duality.  The constructive
Fourier-Motzkin existence direction is isolated in `FiniteFarkasRatElim`.
-/

namespace Erdos23Delta0
namespace FiniteFarkasRat

open scoped BigOperators

variable {Row Var : Type*} [Fintype Row] [Fintype Var]

/-- A nonnegative solution of the finite rational system `A x <= b`. -/
structure Feasible (A : Row -> Var -> ℚ) (b : Row -> ℚ) where
  x : Var -> ℚ
  x_nonneg : forall j, 0 <= x j
  row_le : forall i, (Finset.univ.sum fun j => A i j * x j) <= b i

/-- A nonnegative Farkas multiplier: `y^T A >= 0` and `y^T b < 0`. -/
structure Certificate (A : Row -> Var -> ℚ) (b : Row -> ℚ) where
  y : Row -> ℚ
  y_nonneg : forall i, 0 <= y i
  column_nonneg : forall j, 0 <= Finset.univ.sum fun i => y i * A i j
  rhs_neg : (Finset.univ.sum fun i => y i * b i) < 0

/-- Weak duality for the nonnegative finite inequality system. -/
theorem Certificate.refutes_feasible
    {A : Row -> Var -> ℚ} {b : Row -> ℚ}
    (C : Certificate A b) : Not (Nonempty (Feasible A b)) := by
  rintro ⟨P⟩
  have hnonneg :
      0 <= Finset.univ.sum fun j =>
        (Finset.univ.sum fun i => C.y i * A i j) * P.x j := by
    exact Finset.sum_nonneg fun j _ =>
      mul_nonneg (C.column_nonneg j) (P.x_nonneg j)
  have hswap :
      (Finset.univ.sum fun j =>
          (Finset.univ.sum fun i => C.y i * A i j) * P.x j)
        = Finset.univ.sum fun i =>
            C.y i * (Finset.univ.sum fun j => A i j * P.x j) := by
    simp only [Finset.sum_mul, Finset.mul_sum, mul_assoc]
    rw [Finset.sum_comm]
  have hrows :
      (Finset.univ.sum fun i =>
          C.y i * (Finset.univ.sum fun j => A i j * P.x j))
        <= Finset.univ.sum fun i => C.y i * b i := by
    exact Finset.sum_le_sum fun i _ =>
      mul_le_mul_of_nonneg_left (P.row_le i) (C.y_nonneg i)
  have hzero : 0 <= Finset.univ.sum fun i => C.y i * b i := by
    exact hnonneg.trans (by simpa only [hswap] using hrows)
  exact (not_lt_of_ge hzero) C.rhs_neg

/-- Equivalent weak-duality orientation. -/
theorem Feasible.no_certificate
    {A : Row -> Var -> ℚ} {b : Row -> ℚ}
    (P : Feasible A b) : Not (Nonempty (Certificate A b)) := by
  rintro ⟨C⟩
  exact C.refutes_feasible ⟨P⟩

end FiniteFarkasRat
end Erdos23Delta0
