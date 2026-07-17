Ancillary files: Lean 4 formalization of Graffiti.pc / WOWII Conjecture 143
===========================================================================

Files (as on branch codex/wowii-143-proof of
https://github.com/AlperTheKing/formal-conjectures, commits 6aab64f + eb64455,
against google-deepmind/formal-conjectures @ c252a41):

  GraphConjecture143.lean   -- the conjecture statement (unchanged from
                               upstream) with the short assembly proof;
                               category updated to `research solved`.
  LargestInducedTree.lean   -- reusable induced-tree API: one-vertex tree
                               extension, geodesic induced trees, maximum
                               induced tree containing a prescribed pair,
                               boundary/two-neighbour maximality obstruction,
                               cycle-closing girth bounds, two-leaf bound.
  Degrees.lean              -- degree-sequence API incl. extraction of two
                               degree-one vertices from secondSmallestDegree = 1.

Toolchain: Lean 4 v4.27.0, Mathlib as pinned by formal-conjectures @ c252a41.
Verification: full-repository `lake build --wfail` passes (8868 jobs, zero
warnings); no `sorry`, no `native_decide`;
  #print axioms WrittenOnTheWallII.GraphConjecture143.conjecture143
reports exactly [propext, Classical.choice, Quot.sound].
The proof was additionally re-derived and compiled in a second, independently
written assembly as a cross-check.
