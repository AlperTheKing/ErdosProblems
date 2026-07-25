import Lake
open Lake DSL

package ehp_n3 where
  leanOptions := #[⟨`autoImplicit, false⟩]

-- EHP_N3.lean4: Proof architecture for the n=3 Erdős–Herzog–Piranian conjecture.
-- Scope: PROOF ARCHITECTURE — 13 axioms, 0 sorries, 2 proven theorems.
-- The two proven theorems (ehp_n3_global_maximum, ehp_n3) typecheck
-- given the declared axioms.  The axioms themselves are not discharged here.
lean_lib EHP_N3 where
  srcDir := "."
  roots := #[`EHP_N3]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "f897ebcf72cd16f89ab4577d0c826cd14afaafc7"
