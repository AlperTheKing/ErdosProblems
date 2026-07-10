import Erdos23Delta0.ODLFull

/-!
# Sparse source-matrix cone certificates

This is the compact replacement kernel for expanded O14 `ConePairs` payloads.
It works at the exact source-LP coefficient level.  A template supplies the
semantic meaning of its target, basis rows, and source columns once.  A slot
then supplies only nonnegative rational weights/residuals and exact scalar row
equations.

No generated chart payload is imported here.
-/

namespace Erdos23Delta0
namespace O14
namespace SparseConeMatrix

open scoped BigOperators
open ODLFull

/-- Semantic chart template for one finite source LP. -/
structure Template (Row Col Env : Type*) [Fintype Row] [Fintype Col] where
  targetCoeff : Row -> ℚ
  columnCoeff : Col -> Row -> ℚ
  basisValue : Env -> Row -> ℚ
  targetValue : Env -> ℚ
  columnValue : Env -> Col -> ℚ
  target_semantics : forall env,
    targetValue env = Finset.univ.sum fun r => targetCoeff r * basisValue env r
  column_semantics : forall env c,
    columnValue env c =
      Finset.univ.sum fun r => columnCoeff c r * basisValue env r

/-- Solution-specific data.  In generated code `weight` and `residual` are
sparse tables, while `row_eq` is checked in small scalar shards. -/
structure Solution
    {Row Col Env : Type*} [Fintype Row] [Fintype Col]
    (T : Template Row Col Env) where
  weight : Col -> ℚ
  residual : Row -> ℚ
  weight_nonneg : forall c, 0 <= weight c
  residual_nonneg : forall r, 0 <= residual r
  row_eq : forall r,
    T.targetCoeff r = residual r +
      Finset.univ.sum fun c => weight c * T.columnCoeff c r

namespace Solution

variable {Row Col Env : Type*} [Fintype Row] [Fintype Col]
variable {T : Template Row Col Env}

/-- Weighted source-matrix coefficient in one row. -/
def weightedCoeff (T : Template Row Col Env) (weight : Col -> ℚ) (r : Row) : ℚ :=
  Finset.univ.sum fun c => weight c * T.columnCoeff c r

/-- Canonical residual.  Generated payloads need not store or prove the row
equation separately: it follows by construction from this definition. -/
def canonicalResidual (T : Template Row Col Env) (weight : Col -> ℚ) (r : Row) : ℚ :=
  T.targetCoeff r - weightedCoeff T weight r

theorem targetCoeff_eq_canonicalResidual_add
    (T : Template Row Col Env) (weight : Col -> ℚ) (r : Row) :
    T.targetCoeff r = canonicalResidual T weight r +
      Finset.univ.sum fun c => weight c * T.columnCoeff c r := by
  unfold canonicalResidual weightedCoeff
  ring

/-- Build a sparse solution from weights once the canonical residuals have
been checked nonnegative. -/
def ofWeights
    (T : Template Row Col Env) (weight : Col -> ℚ)
    (hweight : forall c, 0 <= weight c)
    (hresidual : forall r, 0 <= canonicalResidual T weight r) :
    Solution T where
  weight := weight
  residual := canonicalResidual T weight
  weight_nonneg := hweight
  residual_nonneg := hresidual
  row_eq := targetCoeff_eq_canonicalResidual_add T weight

/-- Exact finite-sum identity behind sparse source-matrix certificates. -/
theorem targetValue_eq_residual_add_columns
    (S : Solution T) (env : Env) :
    T.targetValue env =
      (Finset.univ.sum fun r => S.residual r * T.basisValue env r) +
        Finset.univ.sum fun c => S.weight c * T.columnValue env c := by
  rw [T.target_semantics env]
  calc
    (Finset.univ.sum fun r => T.targetCoeff r * T.basisValue env r) =
        Finset.univ.sum fun r =>
          (S.residual r + Finset.univ.sum fun c =>
            S.weight c * T.columnCoeff c r) * T.basisValue env r := by
      apply Finset.sum_congr rfl
      intro r _
      rw [S.row_eq r]
    _ = (Finset.univ.sum fun r => S.residual r * T.basisValue env r) +
        Finset.univ.sum fun r =>
          (Finset.univ.sum fun c => S.weight c * T.columnCoeff c r) *
            T.basisValue env r := by
      simp only [add_mul, Finset.sum_add_distrib]
    _ = (Finset.univ.sum fun r => S.residual r * T.basisValue env r) +
        Finset.univ.sum fun c => S.weight c *
          (Finset.univ.sum fun r => T.columnCoeff c r * T.basisValue env r) := by
      congr 1
      simp only [Finset.sum_mul, Finset.mul_sum, mul_assoc]
      rw [Finset.sum_comm]
    _ = (Finset.univ.sum fun r => S.residual r * T.basisValue env r) +
        Finset.univ.sum fun c => S.weight c * T.columnValue env c := by
      apply congrArg
      apply Finset.sum_congr rfl
      intro c _
      rw [T.column_semantics env c]

/-- Nonnegative basis values and nonnegative source-column values imply a
nonnegative target. -/
theorem targetValue_nonneg
    (S : Solution T) (env : Env)
    (hbasis : forall r, 0 <= T.basisValue env r)
    (hcolumn : forall c, 0 <= T.columnValue env c) :
    0 <= T.targetValue env := by
  rw [S.targetValue_eq_residual_add_columns env]
  exact add_nonneg
    (Finset.sum_nonneg fun r _ => mul_nonneg (S.residual_nonneg r) (hbasis r))
    (Finset.sum_nonneg fun c _ => mul_nonneg (S.weight_nonneg c) (hcolumn c))

/-- Adapter to the existing ODL consumer.  The instance-specific semantic
layer only has to identify the template target with `coreDefect`. -/
theorem coreODLGoal
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}
    (core : ODLCoreData G c rows Q)
    (S : Solution T) (env : Env)
    (hbasis : forall r, 0 <= T.basisValue env r)
    (hcolumn : forall col, 0 <= T.columnValue env col)
    (htarget : T.targetValue env = coreDefect core) :
    CoreODLGoal G c rows Q core := by
  have h := S.targetValue_nonneg env hbasis hcolumn
  rw [htarget] at h
  exact CoreODLGoal_of_defect_nonneg core h

end Solution

end SparseConeMatrix
end O14
end Erdos23Delta0
