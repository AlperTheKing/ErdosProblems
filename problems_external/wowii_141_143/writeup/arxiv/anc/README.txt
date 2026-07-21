Ancillary Lean 4 sources for "Three Graffiti.pc Conjectures on Largest Induced Trees"
=====================================================================================

The manuscript proves Written on the Wall II Conjectures 141, 142, and 143.
The corresponding machine-checked Lean sources are grouped by conjecture:

  w141/GraphConjecture141.lean
  w141/InducedTreeNeighborhood.lean
  w141/LargestInducedTree.lean

  w142/GraphConjecture142.lean
  w142/GraphConjecture142Proof.lean

  w143/GraphConjecture143.lean
  w143/Degrees.lean
  w143/LargestInducedTree.lean

The w141 and w143 source snapshots were checked with Lean 4.27.0 against the
Formal Conjectures/Mathlib revision used for pull request #4454.  The w142
snapshot is from commit 46bf39015f5c3c3ba3bfcf9f752b4b1e49b584ac and was
checked against the Formal Conjectures pinned toolchain; the upstream metadata
update is pull request #4457.  None of the eight Lean files contains `sorry`
or `admit`.

The directory layout is documentary.  To rebuild inside a Formal Conjectures
checkout, place each file at the import path named in its header (the two
LargestInducedTree.lean snapshots belong to their respective developments and
are intentionally kept in separate directories here).  Use the repository's
pinned elan toolchain and run `lake env lean` on the three GraphConjecture
entry files.

The redistributed Lean sources are governed by the Apache License 2.0; a copy
is included as LICENSE-Apache-2.0.txt.  The paper source is not covered by that
software license.