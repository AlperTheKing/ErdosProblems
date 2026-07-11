import Mathlib

/-!
# The split-2/3 obstruction for linear five-block designs

If the blocks of a `2-(n,5,1)` design were oriented as edge-disjoint odd
five-cycles under a cut leaving exactly one bad edge on every block, every
block would contain two vertices on one cut side and three on the other.
The point-incidence and same-side-pair counts below make that impossible as
soon as `n >= 7`.

This is the exact counting obstruction discovered by the PG(2,4) falsifier
gate.  The theorem is stated only in terms of the four integer counts needed
by the later graph-derived application.
-/

namespace Erdos23Delta0
namespace Gamma
namespace LinearFiveDesignColorObstruction

/-- The quadratic forced by a full pair design is strictly positive once
`n >= 7`.  The completed-square identity is

`2*q = 5*(2*s-n)^2 + n*(n-6)`.
-/
theorem split23_quadratic_pos (n s : ℤ) (hn : 7 ≤ n) :
    0 < 10 * s ^ 2 - 10 * n * s + 3 * n * (n - 1) := by
  nlinarith [sq_nonneg (2 * s - n)]

/-- No five-uniform pair design on at least seven points admits a coloring
with two or three red points in every block.

`blocks` is the number of blocks and `threeRed` the number containing three
red points.  The hypotheses are the doubled standard counts:

* `20*blocks = n*(n-1)` from unique coverage of every point pair;
* `s*(n-1) = 8*blocks + 4*threeRed` from red incidences;
* `s*(s-1) = 2*blocks + 4*threeRed` from red pairs.
-/
theorem no_split23_pair_design
    (n s blocks threeRed : ℤ) (hn : 7 ≤ n)
    (hblocks : 20 * blocks = n * (n - 1))
    (hincidence : s * (n - 1) = 8 * blocks + 4 * threeRed)
    (hpairs : s * (s - 1) = 2 * blocks + 4 * threeRed) : False := by
  have hcross : s * (n - s) = 6 * blocks := by
    nlinarith [hincidence, hpairs]
  have hzero : 10 * s ^ 2 - 10 * n * s + 3 * n * (n - 1) = 0 := by
    nlinarith [hblocks, hcross]
  have hpos := split23_quadratic_pos n s hn
  linarith

#print axioms split23_quadratic_pos
#print axioms no_split23_pair_design

end LinearFiveDesignColorObstruction
end Gamma
end Erdos23Delta0
