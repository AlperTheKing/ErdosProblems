# Formal Verification of Sidon Set Upper Bounds in Lean 4

## Erdos Problem #30 — $1,000 Prize (OPEN)

**Question:** Is h(N) = N^{1/2} + O_epsilon(N^epsilon) for every epsilon > 0?

This repository contains a Lean 4 formalization of the two principal upper bounds
for Sidon sets (B_2 sets), covering the main known results on the upper bound side
of Erdos Problem #30.

## What is formalized

| Result | Statement | File | Status |
|--------|-----------|------|--------|
| **Shared definition** | IsSidonSet (B₂ property) | `Erdos30_Sidon_Defs.lean` | Canonical definition |
| **Erdos-Turan (1941)** | k(k-1) <= 2N | `Erdos30_Complete.lean` | Fully proved, 0 sorry, 0 axioms |
| **Lindstrom parametric (1969)** | k^2 <= 2Nt + kt | `Erdos30_Lindstrom.lean` | Fully proved |
| **Lindstrom quadratic (1969)** | l(2k-l-1)^2 <= 4(l+1)N | `Erdos30_Lindstrom.lean` | Proved from axiom |
| **Lindstrom weak (1969)** | k <= sqrt(2N) + 1 | `Erdos30_Lindstrom.lean` | Fully proved |
| **Lindstrom full (1969)** | k <= sqrt(N) + N^{1/4} + 1 | `Erdos30_Lindstrom.lean` | Axiom (R->N step) |
| **BFR sum counting (2023)** | \|distinctSums\| = k(k+1)/2 | `Erdos30_BFR.lean` | Fully proved |
| **BFR Cauchy-Schwarz (2023)** | Variance decomposition | `Erdos30_BFR.lean` | Fully proved |
| **BFR bound (2023)** | 1000k <= 1000*sqrt(N) + 998*sqrt(sqrt(N)) + 1000 | `Erdos30_BFR.lean` | Proved from axiom |
| **Singer lower bound (1938)** | h(N) >= (1-o(1))*sqrt(N) | `Erdos30_Singer.lean` | Partial (q=2,3,5 verified) |

## Architecture

All files import `IsSidonSet` from the shared `Erdos30_Sidon_Defs.lean`, eliminating
duplicate definitions across the formalization. The three main files (Lindstrom, BFR,
Singer) compile against Mathlib via `lake build`.

## Verification status

- **Zero sorry stubs** in the three main files (Erdos30_Lindstrom.lean, Erdos30_BFR.lean, Erdos30_Singer.lean)
- **4 axioms** (upper bound chain) with full bibliographic references; `singer_sidon_exists` in the Singer file is a separate lower-bound axiom not counted in the four (see paper Section 3.2 table)
- **13+ theorems** fully machine-checked
- **1,131 lines** of verified Lean 4 code (4 main files: Defs + Lindstrom + BFR + Singer)

## Build

Requires: Lean 4 v4.24.0, Mathlib at commit `f897ebcf72cd16f89ab4577d0c826cd14afaafc7`.

```bash
# From the lakefile.lean that imports Mathlib:
lake build Erdos30_Sidon_Defs   # shared IsSidonSet definition
lake build Erdos30_Lindstrom    # should produce 0 errors, 0 sorry
lake build Erdos30_BFR          # should produce 0 errors, 0 sorry
lake build Erdos30_Singer       # should produce 0 errors, 0 sorry
```

## Axiom inventory

| Axiom | Statement | Closure path |
|-------|-----------|--------------|
| `sidon_elem_bound` | k(k-1) <= 2M | Proved in Erdos30_Complete (namespace conflict) |
| `order_diff_counting` | Sorted diffs with bounded sum | Requires orderEmbOfFin + telescoping |
| `lindstrom_bound` | k <= floor(sqrt(N)) + floor(N^{1/4}) + 1 | Requires R->N Nat.sqrt bounding |
| `bfr_core_bound` | 1000(k-1) <= 1000*floor(sqrt(N)) + 998*floor(N^{1/4}) | Full BFR Sections 2-4 (~15 lemmas) |


## Scratch / supplementary files

The `scratch/` directory contains exploratory files not part of the main package and not imported by any core file:

| File | Notes |
|------|-------|
| `Erdos30_difference_counting.lean` | TIER 3 — textbook k(k−1) ≤ 2N bound via difference counting. Duplicate of `Erdos30_Complete.lean`, kept for reference. |
| `Sidon_SumCount_Fix.lean` | Sum-counting helper generated during development. Referenced only in comments in BFR and Singer; not imported. |

These files compile independently but are excluded from the core package boundary.
## References

- Balogh, Furedi, Roy (2023). "An upper bound on the size of Sidon sets." Amer. Math. Monthly 130(5). arXiv: 2103.15850
- Lindstrom (1969). "An inequality for B_2-sequences." J. Combinatorial Theory 6(2).
- Erdos, Turan (1941). "On a problem of Sidon in additive number theory." J. London Math. Soc. 16.
- Singer (1938). "A theorem in finite projective geometry." Trans. Amer. Math. Soc. 43.

## License

Apache 2.0

## Author

K. Mendoza, Mendoza Laboratory (ken@mendozalab.io)
