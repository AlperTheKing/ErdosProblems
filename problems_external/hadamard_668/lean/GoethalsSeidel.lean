import FormalConjectures.Wikipedia.Hadamard
import Mathlib.LinearAlgebra.Matrix.Circulant
import Mathlib.LinearAlgebra.Matrix.Permutation

/-!
# Goethals--Seidel bridge for order 668

This file contains only generic, certificate-independent lemmas.  In
particular, the conversion from orthogonality to `Hadamard.IsHadamard` is
proved directly and does not use the unfinished equivalence theorem in the
upstream conjecture file.
-/

namespace Hadamard

/-- The completed direction of the upstream equivalence needed by a concrete
Goethals--Seidel certificate. -/
theorem isHadamard_of_isHadamard' {n : ℕ} {M : Matrix (Fin n) (Fin n) ℝ}
    (hM : IsHadamard' M) : IsHadamard M := by
  rcases hM with ⟨hentries, horth⟩
  refine ⟨hentries, ?_⟩
  have hdet : (M.transpose * M).det = n ^ (n : ℝ) := by
    have hscalar : Matrix.diagonal (fun _ : Fin n ↦ (n : ℝ)) =
        (n : Matrix (Fin n) (Fin n) ℝ) := by
      rfl
    rw [horth, ← hscalar]
    norm_num
  simp only [Matrix.det_mul, Matrix.det_transpose] at hdet
  rw [← Real.sqrt_mul_self_eq_abs M.det, hdet]
  have hsqrt : √(↑n ^ (n : ℝ)) = (↑n ^ (n : ℝ)) ^ ((1 : ℝ) / 2) := by
    rw [Real.rpow_div_two_eq_sqrt]
    · simp only [Real.rpow_natCast, Real.rpow_one]
    · simp only [Real.rpow_natCast, Nat.cast_nonneg, pow_nonneg]
  rw [hsqrt]
  simp
  refine ((fun {x y z} hx hy hz ↦ (Real.eq_rpow_inv hx hy hz).mpr) ?_ ?_ ?_ ?_).symm
  · exact Real.rpow_nonneg (Nat.cast_nonneg' n) _
  · simp only [Nat.cast_nonneg, pow_nonneg]
  · norm_num
  · rw [← Real.rpow_mul <| Nat.cast_nonneg' n]
    norm_num

namespace GoethalsSeidel

variable {R : Type*} {κ ι : Type*}

/-- Interpret a matrix of square blocks as one matrix on the product index. -/
def flattenBlocks (M : Matrix κ κ (Matrix ι ι R)) :
    Matrix (κ × ι) (κ × ι) R :=
  fun row column ↦ M row.1 column.1 row.2 column.2

@[simp]
theorem flattenBlocks_apply (M : Matrix κ κ (Matrix ι ι R))
    (row column : κ × ι) :
    flattenBlocks M row column = M row.1 column.1 row.2 column.2 :=
  rfl

/-- Transpose both the outer block matrix and every inner block. -/
def blockTranspose (M : Matrix κ κ (Matrix ι ι R)) :
    Matrix κ κ (Matrix ι ι R) :=
  fun row column ↦ (M column row).transpose

@[simp]
theorem flattenBlocks_transpose (M : Matrix κ κ (Matrix ι ι R)) :
    (flattenBlocks M).transpose = flattenBlocks (blockTranspose M) := by
  rfl

@[simp]
theorem flattenBlocks_mul [Fintype κ] [Fintype ι]
    [NonUnitalNonAssocSemiring R]
    (M N : Matrix κ κ (Matrix ι ι R)) :
    flattenBlocks (M * N) = flattenBlocks M * flattenBlocks N := by
  ext ⟨blockRow, row⟩ ⟨blockColumn, column⟩
  simp only [flattenBlocks_apply, Matrix.mul_apply, Fintype.sum_prod_type]
  simp_rw [Matrix.sum_apply, Matrix.mul_apply]

/-- A diagonal matrix at block level, used as the target of the generic
orthogonality calculation. -/
def blockDiagonal [DecidableEq κ] [Zero R] (D : Matrix ι ι R) :
    Matrix κ κ (Matrix ι ι R) :=
  Matrix.diagonal fun _ ↦ D

@[simp]
theorem blockDiagonal_apply [DecidableEq κ] [Zero R] (D : Matrix ι ι R)
    (row column : κ) :
    blockDiagonal D row column = if row = column then D else 0 := by
  rw [blockDiagonal, Matrix.diagonal_apply]

@[simp]
theorem flattenBlocks_scalarDiagonal [DecidableEq κ] [DecidableEq ι] [Zero R]
    (value : R) :
    flattenBlocks (blockDiagonal (κ := κ) (Matrix.diagonal fun _ : ι ↦ value)) =
      Matrix.diagonal (fun _ : κ × ι ↦ value) := by
  ext ⟨blockRow, row⟩ ⟨blockColumn, column⟩
  simp only [flattenBlocks_apply, blockDiagonal_apply, Matrix.diagonal_apply]
  by_cases hBlock : blockRow = blockColumn
  · subst blockColumn
    by_cases hEntry : row = column
    · subst column
      simp
    · simp [hEntry, Prod.ext_iff]
  · have hProduct : (blockRow, row) ≠ (blockColumn, column) :=
      fun equality ↦ hBlock (congrArg Prod.fst equality)
    simp [hBlock, hProduct]

/-- The quaternionic four-block sign pattern underlying the
Goethals--Seidel construction. -/
def quaternionBlocks [Neg R] (A B C D : Matrix ι ι R) :
    Matrix (Fin 4) (Fin 4) (Matrix ι ι R) :=
  !![A, B, C, D;
     -B, A, -D, C;
     -C, D, A, -B;
     -D, -C, B, A]

/-- Pairwise amicability is the exact cancellation condition for the
quaternionic four-block array. -/
structure PairwiseAmicable [Fintype ι] [NonUnitalNonAssocSemiring R]
    (A B C D : Matrix ι ι R) : Prop where
  ab : A.transpose * B = B.transpose * A
  ac : A.transpose * C = C.transpose * A
  ad : A.transpose * D = D.transpose * A
  bc : B.transpose * C = C.transpose * B
  bd : B.transpose * D = D.transpose * B
  cd : C.transpose * D = D.transpose * C

/-- The sum of the four block Gram matrices. -/
def gramSum [Fintype ι] [NonUnitalNonAssocSemiring R]
    (A B C D : Matrix ι ι R) : Matrix ι ι R :=
  A.transpose * A + B.transpose * B + C.transpose * C + D.transpose * D

/-- Generic four-block orthogonality before flattening.  This is the algebraic
cancellation core used by Goethals--Seidel after its reversal identities have
been discharged. -/
theorem quaternionBlocks_transpose_mul [Fintype ι] [DecidableEq ι] [CommRing R]
    (A B C D : Matrix ι ι R) (h : PairwiseAmicable A B C D) :
    blockTranspose (quaternionBlocks A B C D) * quaternionBlocks A B C D =
      blockDiagonal (gramSum A B C D) := by
  apply Matrix.ext
  intro i j
  fin_cases i <;> fin_cases j <;> rw [Matrix.mul_apply] <;>
    simp [quaternionBlocks, blockTranspose, blockDiagonal, gramSum,
      Fin.sum_univ_succ, h.ab, h.ac, h.ad, h.bc, h.bd, h.cd] <;> abel

/-- Flattened form of `quaternionBlocks_transpose_mul`. -/
theorem flatten_quaternionBlocks_transpose_mul [Fintype ι] [DecidableEq ι]
    [CommRing R] (A B C D : Matrix ι ι R) (h : PairwiseAmicable A B C D) :
    (flattenBlocks (quaternionBlocks A B C D)).transpose *
        flattenBlocks (quaternionBlocks A B C D) =
      flattenBlocks (blockDiagonal (gramSum A B C D)) := by
  rw [flattenBlocks_transpose, ← flattenBlocks_mul,
    quaternionBlocks_transpose_mul A B C D h]

/-- If the four block Gram matrices sum to a scalar diagonal, the flattened
four-block array is exactly orthogonal. -/
theorem flatten_quaternionBlocks_orthogonal [Fintype ι] [DecidableEq ι]
    [CommRing R] (A B C D : Matrix ι ι R) (h : PairwiseAmicable A B C D)
    (value : R)
    (hgram : gramSum A B C D = Matrix.diagonal (fun _ : ι ↦ value)) :
    (flattenBlocks (quaternionBlocks A B C D)).transpose *
        flattenBlocks (quaternionBlocks A B C D) =
      Matrix.diagonal (fun _ : Fin 4 × ι ↦ value) := by
  rw [flatten_quaternionBlocks_transpose_mul A B C D h, hgram,
    flattenBlocks_scalarDiagonal]

/-- The permutation matrix for negation of the cyclic `Fin n` index. -/
def reversalMatrix (n : ℕ) (R : Type*) [Zero R] [One R] :
    Matrix (Fin n) (Fin n) R :=
  (Equiv.neg (Fin n)).toPEquiv.toMatrix

@[simp]
theorem reversalMatrix_transpose (n : ℕ) [Zero R] [One R] :
    (reversalMatrix n R).transpose = reversalMatrix n R := by
  unfold reversalMatrix
  rw [← PEquiv.toMatrix_symm]
  congr 1

@[simp]
theorem reversalMatrix_mul_self (n : ℕ) [NonAssocSemiring R] :
    reversalMatrix n R * reversalMatrix n R = 1 := by
  change (Equiv.neg (Fin n)).permMatrix R * (Equiv.neg (Fin n)).permMatrix R = 1
  rw [← Matrix.permMatrix_mul]
  have hneg : Equiv.neg (Fin n) * Equiv.neg (Fin n) = 1 := by
    ext i
    simp
  rw [hneg, Matrix.permMatrix_one]

/-- Reversal moves through a circulant by transposing it. -/
theorem reversalMatrix_mul_circulant {n : ℕ} [CommRing R] (v : Fin n → R) :
    reversalMatrix n R * Matrix.circulant v =
      (Matrix.circulant v).transpose * reversalMatrix n R := by
  cases n with
  | zero => exact Subsingleton.elim _ _
  | succ n =>
      ext i j
      simp [reversalMatrix, PEquiv.toMatrix_toPEquiv_mul,
        PEquiv.mul_toMatrix_toPEquiv, Matrix.circulant_apply]
      apply congrArg v
      abel

/-- The companion form with reversal on the right. -/
theorem circulant_mul_reversalMatrix {n : ℕ} [CommRing R] (v : Fin n → R) :
    Matrix.circulant v * reversalMatrix n R =
      reversalMatrix n R * (Matrix.circulant v).transpose := by
  cases n with
  | zero => exact Subsingleton.elim _ _
  | succ n =>
      ext i j
      simp [reversalMatrix, PEquiv.toMatrix_toPEquiv_mul,
        PEquiv.mul_toMatrix_toPEquiv, Matrix.circulant_apply]
      apply congrArg v
      abel

/-- Reversal sandwiches a circulant to its transpose. -/
theorem reversalMatrix_circulant_reversalMatrix {n : ℕ} [CommRing R]
    (v : Fin n → R) :
    reversalMatrix n R * (Matrix.circulant v * reversalMatrix n R) =
      (Matrix.circulant v).transpose := by
  rw [← Matrix.mul_assoc, reversalMatrix_mul_circulant, Matrix.mul_assoc,
    reversalMatrix_mul_self, Matrix.mul_one]

/-- Product rule for two reversed circulant blocks. -/
theorem circulantReversal_mul_circulantReversal {n : ℕ} [CommRing R]
    (v w : Fin n → R) :
    (Matrix.circulant v * reversalMatrix n R) *
        (Matrix.circulant w * reversalMatrix n R) =
      Matrix.circulant v * (Matrix.circulant w).transpose := by
  rw [Matrix.mul_assoc, reversalMatrix_circulant_reversalMatrix]

/-- Product rule for a reversed circulant followed by a circulant. -/
theorem circulantReversal_mul_circulant {n : ℕ} [CommRing R]
    (v w : Fin n → R) :
    (Matrix.circulant v * reversalMatrix n R) * Matrix.circulant w =
      (Matrix.circulant v * (Matrix.circulant w).transpose) * reversalMatrix n R := by
  rw [Matrix.mul_assoc, reversalMatrix_mul_circulant, ← Matrix.mul_assoc]

/-- Standard Goethals--Seidel block array for four cyclic sequences. -/
def goethalsSeidelBlocks {n : ℕ} [Ring R]
    (a b c d : Fin n → R) : Matrix (Fin 4) (Fin 4) (Matrix (Fin n) (Fin n) R) :=
  let A := Matrix.circulant a
  let B := Matrix.circulant b
  let C := Matrix.circulant c
  let D := Matrix.circulant d
  let J := reversalMatrix n R
  !![A, B * J, C * J, D * J;
     -(B * J), A, -(D.transpose * J), C.transpose * J;
     -(C * J), D.transpose * J, A, -(B.transpose * J);
     -(D * J), -(C.transpose * J), B.transpose * J, A]

/-- The un-reindexed matrix on `Fin 4 × Fin n`; a final equivalence transports
this to `Fin (4*n)` once the certificate is inserted. -/
def goethalsSeidelMatrix {n : ℕ} [Ring R] (a b c d : Fin n → R) :
    Matrix (Fin 4 × Fin n) (Fin 4 × Fin n) R :=
  flattenBlocks (goethalsSeidelBlocks a b c d)

end GoethalsSeidel
end Hadamard
