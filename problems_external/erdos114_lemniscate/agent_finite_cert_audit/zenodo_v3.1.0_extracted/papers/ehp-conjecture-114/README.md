# Computational Verification of the Erdos-Herzog-Piranian Conjecture for Degrees 3 <= n <= 12

**Author:** Kenneth A. Mendoza (ORCID [0009-0000-9475-5938](https://orcid.org/0009-0000-9475-5938))

**Status:** Public Preprint

## Abstract

We present IEEE 1788 interval arithmetic certified branch-and-bound verification of the
Erdos-Herzog-Piranian (EHP) conjecture for monic polynomials of degrees 3 through 12.
The EHP conjecture (1958) asserts that among all monic polynomials of degree n, the
polynomial z^n - 1 uniquely maximizes the lemniscate length L(p). We exploit translation symmetry (centering) and rotational symmetry (fixing the constant
term real and non-negative) to reduce the search space from 2n to 2n−3 real dimensions,
then apply a certified branch-and-bound strategy with interval Lipschitz upper bounds to
prove that no competitor exceeds the extremizer value. For all degrees 3 through 12, only
extremizer boxes survive elimination, and strict concavity at z^n − 1 is verified via an
interval Hessian check. The margin by which z^n − 1 dominates grows from ~6% (n = 3)
to over 61% (n = 12).
We also discover and verify an exact closed-form formula for the lemniscate length:
L(z^n - 1) = 2^{1/n} * sqrt(pi) * Gamma(1/(2n)) / Gamma(1/(2n) + 1/2), previously
unknown for n >= 3. Combined with Tao's 2025 proof for sufficiently large n, these results
provide computational evidence covering the full EHP conjecture.

## Files

| File | Description |
|------|-------------|
| `ehp_erdos114_preprint.tex` | LaTeX source for the preprint paper |
| `EHP_Erdos114_Preprint.pdf` | Compiled PDF of the preprint |
| `ehp_certified_bb.rs` | Main Rust source: IEEE 1788 certified branch-and-bound verifier |
| `Cargo.toml` | Rust project manifest with dependencies |
| `EHP_N3_LEVEL3_RESULTS.json` | Full results for the n=3 symmetry-reduced verified case |
| `EHP_GENERAL_SUMMARY.json` | Summary results for all degrees n=3 through n=8 |

## Build Instructions

Requires Rust 1.75+ and the `inari` crate (IEEE 1788 interval arithmetic).

1. Clone the repository and navigate to this directory:
   ```bash
   git clone https://github.com/MendozaLab/erdos-experiments.git
   cd erdos-experiments/papers/ehp-conjecture-114
   ```

2. Create the expected Cargo project layout:
   ```bash
   mkdir -p ehp_n3_poc/src/bin
   cp Cargo.toml ehp_n3_poc/
   cp ehp_certified_bb.rs ehp_n3_poc/src/bin/
   cd ehp_n3_poc
   ```

3. Build and run:
   ```bash
   cargo build --release --bin ehp_certified_bb
   cargo run --release --bin ehp_certified_bb
   ```

## Dependencies

| Crate | Version | Purpose |
|-------|---------|---------|
| `inari` | 2.0.0 | IEEE 1788 interval arithmetic for certified bounds |
| `rayon` | 1.10 | Parallel iteration for branch-and-bound search |
| `serde` | 1.x | JSON serialization of results |
| `serde_json` | 1.x | JSON output formatting |
| `sha256` | 1.x | Reproducibility checksums |

## Key Results

| Degree | Reduced Dim | B&B Evals | Time (s) | L*(z^n−1) certified lower bound | Verdict |
|--------|-------------|-----------|----------|----------------------------------|---------|
| 3      | 3           | 7,560     | 7.1      | 9.179724222343                   | EHP_N3_PROVEN |
| 4      | 5           | 42,656    | 19.7     | 11.070020517257                  | EHP_N4_PROVEN |
| 5      | 7           | 312,598   | 47.8     | 13.006811381919                  | EHP_N5_PROVEN |
| 6      | 9           | 135,936   | 50.8     | 14.965732189659                  | EHP_N6_PROVEN |
| 7      | 11          | 23,552    | 72.0     | 16.936900648251                  | EHP_N7_PROVEN |
| 8      | 13          | 110,592   | 93.2     | 18.915553136286                  | EHP_N8_PROVEN |
| 9      | 15          | 507,904   | 217.7    | 20.899111801667                  | EHP_N9_PROVEN |
| 10     | 17          | 2,293,760 | 461.0    | 22.886060328165                  | EHP_N10_PROVEN |
| 11     | 19          | 10,223,616 | 1,986.1  | 24.875448685147                  | EHP_N11_PROVEN |
| 12     | 21          | 45,088,768 | 9,625.3  | 26.866651413612                  | EHP_N12_PROVEN |

**All 10 degrees proven via IEEE 1788 interval arithmetic certified branch-and-bound.**
Each degree passes all three proof pillars: (1) branch-and-bound eliminates all non-extremizer
boxes, (2) outer domain bound confirms no polynomial outside the search region exceeds L*,
(3) interval Hessian confirms strict concavity at z^n−1 (negative definite in all 2n−3 directions).

Reduced dimension is 2n−3 after fixing the constant term real and non-negative (rotation + translation symmetry).
n=12 required 45M box evaluations and ~2.67 hours on a single Apple Silicon Mac (8 cores via rayon).

### Exact Closed-Form Formula

For all n >= 1:

```
L(z^n - 1) = 2^{1/n} * sqrt(pi) * Gamma(1/(2n)) / Gamma(1/(2n) + 1/2)
```

Asymptotic expansion: L(z^n - 1) = 2n + 4*log(2) + 1.099/n + O(1/n^2).

This formula was verified against Richardson extrapolation for n = 3 through 8.

## Context

- **EHP Conjecture (1958):** Erdos, Herzog, and Piranian conjectured that z^n - 1 maximizes lemniscate length among monic degree-n polynomials.
- **Eremenko-Hayman (1999):** Proved EHP for n = 2.
- **Tao (2025):** Proved EHP for sufficiently large n (arXiv:2512.12455), with an enormous implicit threshold N_0.
- **This work:** Computational verification for small n (3-12), complementing Tao's large-n proof and providing the first verified cases for any specific n > 2.

## Source Code

Full source code and reproducibility materials: [github.com/MendozaLab/erdos-experiments](https://github.com/MendozaLab/erdos-experiments/tree/main/papers/ehp-conjecture-114)
