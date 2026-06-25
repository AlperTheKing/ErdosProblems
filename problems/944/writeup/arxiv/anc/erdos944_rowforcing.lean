import Mathlib

/-!
Anti-diagonal / diagonal forcing core for Erdős #944 (Theorem C support, 2026-06-13).

Among the 21 valid 6-edge-cut matrices (3×3 ℕ-matrices, entry sum 6, all six
permutation-diagonal sums ≥ 2), the row-sum vector determines the rows in the two
extreme cases used by the bipartite-shore exclusion:

* row sums a permutation of `(3,3,0)`  ⇒  both nonzero rows are `(1,1,1)`
  (each cut triple is rainbow in every partner colouring — the anti-diagonal kill);
* row sums a permutation of `(6,0,0)`  ⇒  the nonzero row is `(2,2,2)`
  (the six cut endpoints split `2+2+2` — the diagonal/always-balanced forcing).

Both are decidable facts about the finite enumeration; proved by `decide`, no
`native_decide`.
-/

namespace Erdos944C

/-- Length-`k`, sum-`n` lists of naturals (weak compositions), row-major matrices. -/
def comps : ℕ → ℕ → List (List ℕ)
  | 0, 0 => [[]]
  | 0, _ + 1 => []
  | k + 1, n => (List.range (n + 1)).flatMap fun a => (comps k (n - a)).map (a :: ·)

/-- All six permutation-diagonal sums of `[a,b,c; d,e,f; g,h,i]` are ≥ 2. -/
def diagOK : List ℕ → Bool
  | [a, b, c, d, e, f, g, h, i] =>
    decide (2 ≤ a + e + i) && decide (2 ≤ a + f + h) && decide (2 ≤ b + d + i) &&
    decide (2 ≤ b + f + g) && decide (2 ≤ c + d + h) && decide (2 ≤ c + e + g)
  | _ => false

/-- Row-forcing predicate: in the `(3,3,0)` row-sum case both nonzero rows equal
`[1,1,1]`; in the `(6,0,0)` row-sum case the nonzero row equals `[2,2,2]`. -/
def rowForcing : List ℕ → Bool
  | [a, b, c, d, e, f, g, h, i] =>
      let r0 := [a, b, c]; let r1 := [d, e, f]; let r2 := [g, h, i]
      let s0 := a + b + c; let s1 := d + e + f; let s2 := g + h + i
      let is330 := (s0 == 0 && s1 == 3 && s2 == 3) || (s0 == 3 && s1 == 0 && s2 == 3) ||
                   (s0 == 3 && s1 == 3 && s2 == 0)
      let is600 := (s0 == 6 && s1 == 0 && s2 == 0) || (s0 == 0 && s1 == 6 && s2 == 0) ||
                   (s0 == 0 && s1 == 0 && s2 == 6)
      let ok330 := !is330 ||
        ((s0 == 0 || r0 == [1, 1, 1]) && (s1 == 0 || r1 == [1, 1, 1]) &&
         (s2 == 0 || r2 == [1, 1, 1]))
      let ok600 := !is600 ||
        ((!(s0 == 6) || r0 == [2, 2, 2]) && (!(s1 == 6) || r1 == [2, 2, 2]) &&
         (!(s2 == 6) || r2 == [2, 2, 2]))
      ok330 && ok600
  | _ => true

set_option maxRecDepth 100000 in
/-- Every valid 6-cut matrix satisfies the row-forcing law: `(3,3,0)` row sums force
both nonzero rows to be `(1,1,1)`, and `(6,0,0)` row sums force the nonzero row to be
`(2,2,2)`. This is the matrix input to the anti-diagonal and diagonal cases of the
bipartite-shore exclusion (Theorem C). -/
theorem cut_row_forcing : ((comps 9 6).filter diagOK).all rowForcing = true := by decide

end Erdos944C
