# EXP4 — Mendoza's Limit Universality Meta-Test
## Verdict: RMT_UNIVERSAL

**Date:** 2026-04-17
**Explanation:** All maps obey RMT scaling. M_L either emergent or subleading.

### Per-Map Summary

#### TENT
- Clean τ₂ (average): 0.50648
- **Hypothesis Verdict:** RMT_WINS
- Slope: -0.6015 (dev from 0: 0.601, dev from -0.5: 0.101)
- Prefactor: 0.46168

#### ARNOLD
- Clean τ₂ (average): 0.27812
- **Hypothesis Verdict:** RMT_WINS
- Slope: -0.5107 (dev from 0: 0.511, dev from -0.5: 0.011)
- Prefactor: 0.43692

#### RANDOM_MARKOV
- Clean τ₂ (average): 0.15349
- **Hypothesis Verdict:** RMT_WINS
- Slope: -0.5183 (dev from 0: 0.518, dev from -0.5: 0.018)
- Prefactor: 0.56186

### Interpretation

**M_L Universality Scope:**
- If M_L_SCOPE_CONFIRMED: M_L is a real physical constant, but specific to chaotic maps with positive Lyapunov exponent. Use as atlas codomain only for deterministic chaos problems (Bernstein, sunflower, channel capacity with state-dependent costs).
- If RMT_UNIVERSAL: M_L is an emergent property of large random matrices, not fundamental. Atlas should use 1/√W scaling as default.
- If MIXED or AMBIGUOUS: Further work needed; report results transparently without claiming universality.

### Raw Results
See `exp4_results.json` for full sweep data, per-map fits, and residuals.
