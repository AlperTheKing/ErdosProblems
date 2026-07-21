Ancillary Lean 4 sources for the proof of Graffiti.pc / WOWII Conjecture 141
============================================================================

These files are copied from commit e1aac80 of the branch used for Google
DeepMind Formal Conjectures pull request #4454:

  https://github.com/google-deepmind/formal-conjectures/pull/4454

Files
-----

GraphConjecture141.lean
  The exact Formal Conjectures statement and its completed proof.

InducedTreeNeighborhood.lean
  Supporting induced-tree, neighbourhood-independence, maximality, and
  girth lemmas used by the theorem.

LargestInducedTree.lean
  The reusable largest-induced-tree API introduced earlier on the same
  branch and imported by InducedTreeNeighborhood.lean.

LICENSE-Apache-2.0.txt
  Apache License 2.0, matching the source-file headers and repository.

Verification
------------

The branch was built with the repository's Lean 4.27.0 toolchain and the
current pinned Mathlib dependencies.  The theorem contains no `sorry`,
`admit`, or `native_decide`.  The pull request is the authoritative source
for the complete repository layout and continuous-integration results.
