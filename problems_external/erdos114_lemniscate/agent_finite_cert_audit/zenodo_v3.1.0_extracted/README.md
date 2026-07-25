# Erdős Problem Computational Experiments

Computational solvers and experimental results for open Erdős problems.

**Author**: Kenneth A. Mendoza ([ORCID 0009-0000-9475-5938](https://orcid.org/0009-0000-9475-5938))  
**Preprint**: [Zenodo 19229245](https://zenodo.org/records/19229245)
**License**: Apache 2.0

---

## Visualization

[![Bound Sweep Visualizer](https://img.shields.io/badge/Bound_Sweep-Static_View-222222?style=for-the-badge)](https://erdos-interactive-visualizer.pages.dev/)

The bound sweep visualizer shows the phase-space transition between analytical boundaries and computational bounds for Problem #114. An [interactive version with animated parameter sweep](https://mendozalab.io/workbench/interactive-morphism-engine) is also available.

---

## Problem #114 — Erdős–Herzog–Piranian Lemniscate Conjecture

**Statement**: Among all monic polynomials of degree n, the lemniscate {z ∈ ℂ : |p(z)| = 1} has maximal arc length when p(z) = zⁿ − 1.

**Prize**: $250 · **Status**: Open for small n (solved for sufficiently large n by Tao, Dec 2025)

### Background

- **n = 2**: Proved by Eremenko–Hayman (1999), who also showed a maximizer exists with all critical points on the lemniscate
- **n ≥ N₀**: Proved by Tao (arXiv:2512.12455, Dec 2025) with a tower-exponential threshold N₀
- **n = 3–14**: Certified computationally in this repository (Mendoza, 2026)
- **n = 15**: In computation (Modal clusters proposed)
- **n = 16–18**: Open but computationally feasible via distributed architectures
- **n = 19 to N₀**: Open, beyond current hardware

### Results

All cases use IEEE 1788 certified interval arithmetic via the `inari` Rust crate, cross-checked against Python/mpmath on both x86_64 and arm64. Certified enclosures for L(zⁿ − 1) have widths ≲ 2.5 × 10⁻¹⁴.

| n | Dim. | L(zⁿ − 1) certified interval | Margin vs tested competitors | B&B evals | Time |
|---|------|-------------------------------|------------------------------|-----------|------|
| 3 | 1 | [9.17972422234315, 9.17972422234317] | 17.1% | 8 | < 1 s |
| 4 | 3 | [11.0700205172566, 11.0700205172566] | 28.9% | 13,504 | 254 s |
| 5 | 5 | [13.0068113819187, 13.0068113819187] | 45.4% | 32 | < 1 s |
| 6 | 7 | [14.9657321896586, 14.9657321896586] | 54.3% | 128 | < 1 s |
| 7 | 9 | [16.9369006482509, 16.9369006482509] | 62.3% | 512 | 8 s |
| 8 | 11 | [18.9155531362862, 18.9155531362863] | 67.3% | 2,048 | 1 s |
| 9 | 13 | [20.8991118016671, 20.8991118016671] | 69.6% | 8,192 | 4 s |
| 10 | 15 | [22.8860603281654, 22.8860603281654] | 71.4% | 32,768 | 12 s |
| 11 | 17 | [24.8754486851478, 24.8754486851479] | — | 10,223,616 | 33 min |
| 12 | 19 | [26.8666514136128, 26.8666514136128] | — | 45,088,768 | 2.67 hr |
| 13 | 23 | [28.8592399558882, 28.8592399558882] | — | 197,132,288 | 15.5 hr |
| 14 | 25 | [30.8529108415485, 30.8529108415485] | — | 855,638,016 | 74.8 hr |

**Dim.** is the reduced parameter space dimension 2n − 5 (symmetry-reduced from 2(n−1)).

**Margins increase monotonically** from 17.1% (n=3) to 71.4% (n=10), consistent with Tao's asymptotic result. Zero counterexamples found across the full search.
n=11 through n=14 use the full IEEE 1788 certified B&B (branch-and-bound) proof; competitor margin not separately computed for these degrees.

**Search methodology**: Margins are relative to the best competitor found across three tested families: (1) the Eremenko–Hayman family (all critical points on the lemniscate), (2) zⁿ + c for c on a fine grid, and (3) random monic sampling. The interval arithmetic certifies the arc-length evaluation; the branch-and-bound certifies exhaustive coverage of each family. These are not certified global gaps over all monic polynomials.

### Exact Formula (proven)

For the conjectured maximizer:

```
L(zⁿ − 1) = 2^{1/n} · √π · Γ(1/(2n)) / Γ(1/(2n) + 1/2)
```

Equivalently, in Tao's beta-function form: `L(zⁿ − 1) = 2^{1/n} · B(1/2, 1/(2n))`, using `B(a,b) = Γ(a)Γ(b)/Γ(a+b)`.

Verified against Python/mpmath at 50+ decimal digits for n = 3–10. Asymptotic: L(zⁿ − 1) = 2πn + 4 log 2 + O(1/n), consistent with Fryntov–Nazarov.

### Methodology

- **Symmetry reduction**: Translation (fix aₙ₋₁ = 0) + rotation (fix a₀ ∈ ℝ≥0) reduces search from 2(n−1) to 2n−5 real dimensions — a 1D search at n=3, 15D at n=10
- **Branch-and-bound**: Certified upper bound per box via Lipschitz constant + diameter; comparison u_i.sup() < L*.inf() uses directed rounding throughout. All non-extremizer boxes eliminated at level 0 for n ≥ 5
- **IEEE 1788 arithmetic**: Full certificate chain — Lipschitz bounds, fill distances, grid error envelopes, elimination comparisons — via `inari::Interval` with directed rounding
- **Dual implementation**: Rust/inari (primary) and Python/mpmath (cross-check) produce identical certified enclosures on x86_64 and arm64
- **Hessian check**: All eigenvalues strictly negative at zⁿ − 1 (verified at four step sizes), confirming strict local optimality
- **Boundary verification**: L(p) < L(zⁿ − 1) confirmed on the frontier of the feasible region
- **Symmetrization falsified**: Circular symmetrization does not preserve lemniscate length; consistent with Tao's proof, which avoids symmetrization

### Computational Gap

Our results cover n ∈ {3, …, 14}. Tao's proof covers n ≥ N₀ (tower-exponential, N₀ ≫ 10¹⁰⁰). The gap n ∈ {15, …, N₀ − 1} remains open. Practical limit on current hardware: n ≲ 15–18.

### Preprint

[Computational Verification of the EHP Conjecture for 3 ≤ n ≤ 14 (PDF)](papers/EHP_Bounds_Computational_Draft.pdf)
[Zenodo deposit](https://zenodo.org/records/19184468)

### Code and Results

```
scripts/erdos-114/
├── Cargo.toml
├── src/
│   ├── main.rs                    # n=3 branch-and-bound
│   └── bin/
│       ├── ehp_general.rs         # General n=3..8 verifier
│       ├── ehp_general_ieee1788.rs # IEEE 1788 certified verifier (n=3..10)
│       ├── ehp_n3_ieee1788.rs     # n=3 certified B&B
│       ├── level2.rs / level3_ia.rs # Refinement stages
│       └── hessian_check.rs       # Hessian negativity at extremizer
results/erdos-114/
├── EHP_GENERAL_SUMMARY.json           # n=3..8 results
├── EXP-MM-EHP-007-n{3..8}-inari_RESULTS.json  # Per-degree certified results
```

Reproducible via: `cargo run --release --bin ehp_general_ieee1788`

### References

- Eremenko, A. & Hayman, W. (1999). On the length of lemniscates. Michigan Math. J. 46.
- Tao, T. (2025). "The Erdős–Herzog–Piranian conjecture for large polynomial degrees." arXiv:2512.12455
- Fryntov, A. & Nazarov, F. (2025). On the local extremality of lemniscates of zⁿ − 1.
- Krishnapur, M., Lundberg, E. & Ramachandran, K. (2025). arXiv:2503.18270 (minimal area, dual problem)
- Pommerenke, C. (1961). "On metric properties of complex polynomials." Michigan Math. J. 8, 97–115.
- Tanaka, M. inari: IEEE 1788 interval arithmetic for Rust. https://crates.io/crates/inari

---

## Other Experiments

| Problem | Script | Prize | Key Finding |
|---------|--------|-------|-------------|
| #86 C₄-free hypercube | `scripts/erdos-86/` | $100 | Exact ILP for n=2–5; ratio ex(Q_n,C₄)/e(Q_n) declines 0.75→0.583 for n=2–10 |
| #123 d-completeness | `scripts/erdos-123/` | $250 | Coprime triples containing 2 are d-complete to N=10,000; triples without 2 fail |
| #161 Discrepancy jumps | `scripts/erdos-161/` | $500 | F^(2)(n,α) step function; universal jump at α ≈ 1/3 across n=4–8 |
| #30 Sidon sets | `scripts/erdos-30/` | $1,000 | Erdős–Turán 1941 upper bound formalized in Lean 4, 0 sorry |

All results are in `results/` as JSON with SHA-256 checksums.

---

## Citation

```bibtex
@misc{mendoza2026erdos-experiments,
  author = {Mendoza, Kenneth A.},
  title  = {Computational Verification of the {Erd\H{o}s--Herzog--Piranian} Conjecture
            for Degrees $3 \leq n \leq 14$},
  year   = {2026},
  url    = {https://github.com/MendozaLab/erdos-experiments},
  note   = {ORCID: 0009-0000-9475-5938}
}
```

## License

Apache 2.0 — see [LICENSE](LICENSE). Contributions welcome under the same license.
