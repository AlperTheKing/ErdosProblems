# Lean bridge for the order-668 Goethals--Seidel certificate

## Load-bearing theorem already targeted

`Hadamard.isHadamard_of_isHadamard'` proves directly, without invoking
`Hadamard.isHadamard_equiv_isHadamard'`, that a real `Fin n` matrix satisfying
the entry condition and `M.transpose * M = n I` satisfies the determinant
definition `Hadamard.IsHadamard M`.

Thus the concrete certificate only has to produce `IsHadamard'`.

## Generic construction interface

1. Represent a four-by-four matrix of `n`-by-`n` blocks as a matrix indexed by
   `Fin 4 × Fin n` using `flattenBlocks`.
2. Prove that flattening respects transpose, multiplication, and diagonal
   block matrices.
3. Define the standard Goethals--Seidel block array from circulants `A,B,C,D`
   and the reversal matrix `J`.
4. Prove its transpose-product identity from the circulant identities
   `J*X = X.transpose*J`, `J*J = 1`, pairwise commutativity, and the summed
   autocorrelation identity.
5. Reindex `Fin 4 × Fin 167` to `Fin (4*167)` and apply
   `Hadamard.isHadamard_of_isHadamard'`.

## Certificate insertion point

The future generated data file supplies four `Fin 167 → {−1,1}` sequences.
Its only finite obligation is the summed periodic-autocorrelation equality.
No determinant computation is required after the generic bridge is compiled.

No theorem in this file may use `native_decide`, `sorry`, or the unfinished
reverse implication in `Hadamard.isHadamard_equiv_isHadamard'`.
