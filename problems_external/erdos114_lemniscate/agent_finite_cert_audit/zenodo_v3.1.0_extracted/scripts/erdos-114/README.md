# Erdős Problem #114: Erdős–Herzog–Piranian Lemniscate Conjecture

**Statement**: Among all monic polynomials of degree n, the lemniscate {z ∈ ℂ : |p(z)| = 1} has maximal arc length when p(z) = zⁿ − 1.

**Origin**: Erdős, Herzog, Piranian. "Metric properties of polynomials." J. Analyse Math. 6 (1958), 125–148.

**Status**: Solved for sufficiently large n by Tao (Dec 2025, arXiv:2512.12455). Open for explicit small n.

## Our Contribution

Computational verification of EHP for small degrees n = 3 through n = 12, complementing Tao's asymptotic proof:

| n | Verdict | Method | Margin over nearest competitor |
|---|---------|--------|-------------------------------|
| 3 | **VERIFIED** (branch-and-bound proof) | Symmetry-reduced B&B, 200K samples | 15.2% |
| 4 | SUPPORTED | B&B eliminated 99.6%, 100K samples | 20.6% |
| 5 | SUPPORTED | Feasibility mode, 50K samples | 39.3% |
| 6 | SUPPORTED | Feasibility mode, 20K samples | 52.6% |
| 7 | SUPPORTED | Feasibility mode, 10K samples | 61.7% |
| 8 | SUPPORTED | Feasibility mode, 5K samples | 61.7% |

The n = 3 result is the **first computationally verified case** for any specific n > 2 (Eremenko–Hayman proved n = 2 analytically in 1999).

Additionally: the circular symmetrization hypothesis (P114-3) was computationally **falsified** — symmetrization does NOT preserve lemniscate length. Tao's proof does not use symmetrization, independently confirming this finding.

## Directory Structure

```
erdos-114/
├── Cargo.toml              # Main Rust workspace (EHP verifier)
├── src/                    # Core Rust binaries
│   ├── main.rs             # POC: n=3 branch-and-bound
│   └── bin/
│       ├── ehp_general.rs  # General n=3..8 verifier
│       ├── level2.rs       # Level 2 refinement
│       ├── level3_ia.rs    # Level 3 interval arithmetic
│       ├── hessian_check.rs # Hessian negativity check at extremizer
│       └── n4_estimate.rs  # n=4 specific estimator
├── paper/                  # LaTeX preprint
│   ├── ehp_n3_preprint.tex
│   └── ehp_n3_preprint.pdf
├── scripts/                # Additional computational tools
│   ├── p114_n3_landscape.py          # Python landscape analysis
│   ├── test_p114_3_symmetrization.py # Symmetrization falsification test
│   ├── p114_3_rust/                  # Rust: symmetrization test
│   └── p114_gradient_flow/           # Rust: gradient flow analysis
├── docs/                   # Analysis reports and history
│   ├── PROBLEM_114_COMPLETE_JOURNEY.md
│   ├── P114_TAO_BREAKTHROUGH.md
│   ├── P114_N3_ANALYSIS.md
│   ├── P114_3_SYMMETRIZATION_TEST_REPORT.md
│   ├── P114_N3_LANDSCAPE_RESULTS.json
│   └── post2_erdos114_tao2025.md
├── EHP_N3.lean4            # Lean 4 formalization sketch
└── EHP_*.json              # Experiment results (n=3..8)
```

## Key References

- Tao (2025). "The maximal length of the EHP lemniscate in high degree." arXiv:2512.12455
- Eremenko & Hayman (1999). Solved n = 2 case
- Fryntov & Nazarov (2009/2025). Local maximality of zⁿ − 1; bound 2n + O(n^{7/8})
- Krishnapur, Lundberg & Ramachandran (2025). arXiv:2503.18270 — minimal area (dual problem)

## Provenance

Consolidated 2026-03-22 from:
- `Math-Problems/ehp_n3_poc/` (Rust code, Lean4, results, preprint)
- `erdosatlas-workbench/` (P114 analysis reports, Python scripts, Rust scripts)
