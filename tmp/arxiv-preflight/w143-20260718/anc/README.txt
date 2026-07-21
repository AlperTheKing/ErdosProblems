Ancillary files: Lean 4 formalization and exact graph-atlas checks for WOWII 143
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
  LICENSE-Apache-2.0.txt     -- Apache License 2.0 text for the Lean files.

The computation/ subdirectory contains:

  atlas_check.py                 -- first exact Graph Atlas checker.
  atlas_check_independent.py     -- separately written exact implementation.
  atlas_results.json             -- full first-run records.
  atlas_independent_results.json -- full second-run records and metadata.

Both runs used Python 3.12.4 and NetworkX 3.6.1. Across all 1253 atlas graphs,
the 971 connected cyclic cases had no theorem or two-leaf violation; the
separately written checker found no violation among 199 unordered leaf pairs.

To rerun the checks and regenerate the JSON outputs, run from this directory:

  python computation/atlas_check.py
  python computation/atlas_check_independent.py

Each command rewrites its corresponding JSON file. Expected summary: 971
connected cyclic graphs and zero main/two-leaf violations; the second checker
also tests 199 unordered leaf pairs with zero pairwise violations.

Toolchain: Lean 4 v4.27.0, Mathlib as pinned by formal-conjectures @ c252a41.
Verification: full-repository `lake --wfail build` passed (8868 jobs, zero
warnings); no `sorry`, no `native_decide`;
  #print axioms WrittenOnTheWallII.GraphConjecture143.conjecture143
reports exactly [propext, Classical.choice, Quot.sound].

The three .lean files retain their original Apache-2.0 copyright and license
headers and are redistributed under the Apache License 2.0; see
LICENSE-Apache-2.0.txt. The paper source and computation files remain subject
to the license selected by the named author for the arXiv submission.
