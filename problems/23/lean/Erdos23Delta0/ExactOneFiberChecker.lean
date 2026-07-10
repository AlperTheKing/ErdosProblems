import Mathlib

/-!
# Exact-one fiber checker

This file provides the finite R7 checker only. It enumerates subsets of the
union of the supplied supports and does not assert that a witness exists.

The checker is generic: callers choose the support notion explicitly. In
particular, carried path support and full all-geodesic support must not be
silently identified by this module.
-/

namespace Erdos23Delta0

/-- Decide whether the finite support family has a subset meeting every root
support in exactly one edge. -/
def checkExactOneFiberExists {Root Edge : Type*} [DecidableEq Edge]
    (roots : Finset Root) (support : Root → Finset Edge) : Bool :=
  decide (∃ fiber ∈ (roots.biUnion support).powerset,
    ∀ root ∈ roots, (fiber ∩ support root).card = 1)

/-- Correctness of `checkExactOneFiberExists`: accepted fibers are precisely
the subsets of the total support having one edge in every listed root support.
-/
theorem checkExactOneFiberExists_iff {Root Edge : Type*} [DecidableEq Edge]
    (roots : Finset Root) (support : Root → Finset Edge) :
    checkExactOneFiberExists roots support = true ↔
      ∃ fiber : Finset Edge,
        fiber ⊆ roots.biUnion support ∧
          ∀ root ∈ roots, (fiber ∩ support root).card = 1 := by
  simp [checkExactOneFiberExists]

end Erdos23Delta0
