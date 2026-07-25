import Lake
open Lake DSL

package erdos30_sidon where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

-- ══════════════════════════════════════════════════════════════
-- Core formalization (discussed in paper)
-- ══════════════════════════════════════════════════════════════

@[default_target]
lean_lib Erdos30_Sidon_Defs where
  srcDir := "lean"
  roots := #[`Erdos30_Sidon_Defs]

lean_lib Erdos30_Lindstrom where
  srcDir := "lean"
  roots := #[`Erdos30_Lindstrom]

lean_lib Erdos30_BFR where
  srcDir := "lean"
  roots := #[`Erdos30_BFR]

lean_lib Erdos30_Singer where
  srcDir := "lean"
  roots := #[`Erdos30_Singer]

lean_lib Erdos30_Complete where
  srcDir := "lean"
  roots := #[`Erdos30_Complete]

lean_lib Erdos30_OrderedElements where
  srcDir := "lean"
  roots := #[`Erdos30_OrderedElements]

-- ══════════════════════════════════════════════════════════════
-- Scratch / supplementary files (not discussed in paper,
-- not imported by core files — kept for reference only)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos30_difference_counting where
  srcDir := "scratch"
  roots := #[`Erdos30_difference_counting]

lean_lib Sidon_SumCount_Fix where
  srcDir := "scratch"
  roots := #[`Sidon_SumCount_Fix]

-- ══════════════════════════════════════════════════════════════
-- Erdős #755 — B_h[g] Sequences (salvo attack 2026-04-19)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos755_BhG where
  srcDir := "lean"
  roots := #[`Erdos755_BhG]

lean_lib Erdos755_DifferenceCount where
  srcDir := "lean"
  roots := #[`Erdos755_DifferenceCount]

lean_lib Erdos755_Lindstrom where
  srcDir := "lean"
  roots := #[`Erdos755_Lindstrom]

lean_lib Erdos755_Singer_BhG where
  srcDir := "lean"
  roots := #[`Erdos755_Singer_BhG]

lean_lib Erdos755_Complete where
  srcDir := "lean"
  roots := #[`Erdos755_Complete]

lean_lib Erdos755_B3G where
  srcDir := "lean"
  roots := #[`Erdos755_B3G]

lean_lib Erdos755_BhG_General where
  srcDir := "lean"
  roots := #[`Erdos755_BhG_General]

-- ══════════════════════════════════════════════════════════════
-- Erdős #1 — Distinct Subset Sums (salvo attack 2026-04-19)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos1_DistinctSubsetSums where
  srcDir := "lean"
  roots := #[`Erdos1_DistinctSubsetSums]

-- ══════════════════════════════════════════════════════════════
-- Erdős #755 — Higher-order specializations (h=4,5,6)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos755_HigherOrder where
  srcDir := "lean"
  roots := #[`Erdos755_HigherOrder]

-- ══════════════════════════════════════════════════════════════
-- Erdős #166 — Sum-Free Sets (salvo attack 2026-04-19)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos166_SumFree where
  srcDir := "lean"
  roots := #[`Erdos166_SumFree]

-- ══════════════════════════════════════════════════════════════
-- Erdős #30 — Sharp Sidon Difference Bound (PMF salvo 2026-04-19)
-- ══════════════════════════════════════════════════════════════

lean_lib Erdos30_SharpDiff where
  srcDir := "lean"
  roots := #[`Erdos30_SharpDiff]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "f897ebcf72cd16f89ab4577d0c826cd14afaafc7"
