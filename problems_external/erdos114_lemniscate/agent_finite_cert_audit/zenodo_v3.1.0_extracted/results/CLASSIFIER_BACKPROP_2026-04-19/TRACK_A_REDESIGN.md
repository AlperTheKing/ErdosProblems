# Track A — Control Redesign for exp8 (hypercube Leg-4) and exp9 (neutrino chiral)

**Date:** 2026-04-19
**Trigger:** Classifier backprop 2026-04-19 flagged both as ambiguous / counterexample-candidates.
**Status:** Design doc; no recompute yet. Track B pilot must not proceed until this lands.

---

## exp8 — Hypercube Leg-4 M_L kink test

### What we expected
Hypercube is a candidate "geometry-exhausted" regime: finite coordination n, no O(1) continuous spectrum, should show a clean kink in Δ(ε)/√n at ε ≈ M_L. The GOE null — with its O(1) semicircle spectral gap — was supposed to show no such kink. The prediction: kink-on-cube AND kink-absent-on-null.

### What we measured
Kink locations on cube and null coincide at every n (0.5227, 0.4773, 0.4773). Strength ratios (cube/null): 2.93, 0.37, 0.92. Three failure modes stacked:

| Failure | Evidence | Diagnosis |
|---|---|---|
| **F1. Wrong null** | Both curves show a kink at the same ε | GOE is not "geometry absent" — it has a canonical spectral gap and semicircle edge, which is itself a strong geometric structure. Any M_L-scale feature would also appear in GOE if the feature is an artifact of the ε-grid. |
| **F2. Noise-dominated n** | Strength ratio flips direction across n=6,7,8 | n=6,7,8 → 64, 128, 256 hypercube nodes. Finite-size fluctuations in the kink-strength estimator are larger than any hypothesized M_L signal. |
| **F3. Kink detector is artifactual** | Same ε on both curves | The detector (peak of discrete second derivative on a shared ε-grid) will find the same feature on any pair of curves that share a smoothness/sampling structure. |

### Redesign

**R1. Replace the null with a genuine "geometry-killed" control.** The null must destroy the hypercube's geometric signature while keeping bulk statistical properties comparable. Three candidates, run all three as independent nulls:

| Null | Destroys | Keeps | Role |
|---|---|---|---|
| **Erdős–Rényi G(2^n, p = n/2^n)** | Cube connectivity, coordination structure, Huang signature | Node count, average degree | Canonical "random graph" null |
| **Sign-randomized hypercube** | Huang sign pattern (the source of Huang's λ_max = √n bound) | Cube adjacency, coordination | Isolates the *signed* structure vs the *unsigned* graph |
| **Degree-preserving shuffle** | Specific adjacency | Degree sequence | Nuisance-parameter null — controls for degree distribution alone |

The M_L-kink hypothesis should be robust across all three. If it passes only against GOE, the hypothesis is specific to "GOE vs cube," not to "geometry-absent vs geometry-exhausted."

**R2. Scale n up, with explicit finite-size scaling fit.** Target n ∈ {10, 11, 12, 13} = 1024 to 8192 nodes. 8192 is still tractable for sparse Hamiltonian diagonalization. Fit kink-strength vs 2^n with an explicit exponent; predict the scaling from the M_L hypothesis. If the fit's slope is consistent with the prediction, signal; if flat or inconsistent, noise.

**R3. Replace peak-of-derivative detection with model selection.** For each (n, ε-grid), fit two piecewise-linear models to Δ(ε)/√n:

- **M0**: single-slope linear fit (no kink)
- **M1**: two-slope piecewise linear with kink at ε = M_L (fixed, not data-determined)

Compare AIC and BIC. M_L hypothesis PASS iff: (a) M1 preferred on hypercube across all nulls, (b) M0 preferred or weakly preferred on at least one null. ε-position treated as a *fixed hypothesis parameter*, not a data-found peak — this kills the "same ε on both curves" artifact.

**R4. Explicit pass/fail thresholds, pre-registered.** Pass iff:
- Kink-strength ratio (cube / each null) ≥ 3 at n ≥ 11.
- Kink-strength scaling exponent matches M_L prediction within 2σ.
- M1 – M0 ΔBIC ≥ 10 on cube, ≤ 2 on at least one null.

No verbal "partial" pass. Pre-register the thresholds in the JSON before running.

### Expected outcome if the principle holds
Hypercube should bind on M_L where the three geometry-killed nulls do not. If cube still matches its nulls after R1–R4, hypercube does **not** belong in the scoped-exhausted bucket, and the GSP scoped roster must drop it.

---

## exp9 — Neutrino chiral (Ulam–Galerkin doubling-map sigma_min)

### What we expected
sigma_min of the Ulam–Galerkin matrix for a doubling-map would land in the chiral-RMT soft-edge universality class (neutrino analog). Three independent criteria: microscopic universality of σ_min · W, soft-edge kink dominating bulk kink, and flavor-oscillation signature.

### What we measured
- `microscopic_universal: False` — σ_min · W = [0.007, **1.78e-14**, 0.002, 0.008]. One value is numerical underflow.
- `soft_kink_dominates_bulk: False` — bulk kink exceeds soft kink by factors of 2–10× at every W.
- `flavor_oscillation_present: True` — but range shrinks monotonically 0.53 → 0.45 → 0.38 → 0.33 with W.

### Diagnosis (criterion by criterion)

| Criterion | Result | Diagnosis |
|---|---|---|
| 1. microscopic_universal | FAIL | **Methodology defect.** 1.78e-14 at n=40 is numerical underflow, not a physics signal. Σ_min of a doubling-map Ulam–Galerkin can legitimately be numerically near-zero (depending on grid), and the pipeline did not guard against that. |
| 2. soft_kink_dominates_bulk | FAIL | **Real negative.** Bulk feature is 2–10× stronger than soft. This is exactly the opposite of the chiral-soft-edge prediction. The operator's spectrum is bulk-dominated. |
| 3. flavor_oscillation_present | PASS but questionable | Range shrinks monotonically with W → consistent with noise averaging out, not a real persistent oscillation. **A PASS that looks like a fail under a sharper test.** |

### Redesign

**R1. Don't tune criteria to make a failed hypothesis pass.** Criterion 2 is a clean negative. The Ulam–Galerkin doubling-map σ_min does **not** have chiral-soft-edge structure. The honest response is to accept this as evidence against the neutrino-morphism for this operator — not to loosen the criterion.

**R2. Two paths forward, user choice:**

| Path | What it does | Scoped-slot consequence |
|---|---|---|
| **A. Drop the operator** | Remove Ulam–Galerkin doubling-map from the neutrino-morphism candidate list. Conclude: no operator has been identified that exhibits chiral-RMT class within the atlas. | Neutrino slot in the scoped bucket becomes unpopulated — candidate for removal from the scoped roster entirely. |
| **B. Replace the operator** | Pick an operator with actual chiral structure: Dirac-like block matrix, bipartite random matrix, signed bipartite adjacency. Rerun with the same 3 criteria. | Scoped slot retained if new operator passes; otherwise same as path A. |

**R3. Fix the numerical guard for criterion 1.** Regardless of path, the pipeline must flag σ_min · W values within 10^-10 as "numerical floor reached" and exclude them from the universality check. Otherwise criterion 1 will fail spuriously on any operator with a true near-zero σ_min (half of the chiral class!).

**R4. Tighten criterion 3 against the "range shrinks with W" pitfall.** The current criterion is range > threshold. Replace with: range should *stabilize or grow* with W for a real oscillation (finite-size convergence to the true limiting distribution), not shrink. A monotonic decay with W is noise averaging, and the current version incorrectly rewards it.

### Expected outcome if the principle holds
With path B + R3 + R4, a genuinely chiral operator (e.g., bipartite random matrix) should pass criteria 2 and 3 cleanly. If no operator in the atlas passes, the neutrino slot is empty and should be removed from the GSP scoped roster — a clean deletion, not a counterexample.

---

## Summary for Track B handoff

| Artifact | Status after Track A | Track B implication |
|---|---|---|
| exp8_ML_hypercube_leg4 | Redesigned test spec above (R1–R4). Three geometry-killed nulls + model-selection kink test + pre-registered thresholds + larger n. | Do NOT use exp8 as a scoped-slot confirmation until the redesign passes. When designing Leg-4 for the 10 QC edges, adopt the same three controls: (a) geometry-killed null, (b) larger n with explicit scaling fit, (c) model-selection instead of peak detection. |
| exp9_neutrino_chiral | Real negative on criterion 2. Methodology defect on criterion 1. Soft PASS on criterion 3 that looks like noise under sharper test. | The *neutrino slot* in the GSP scoped roster is under threat. Before Track B cites the scoped roster, user must pick path A (drop) or path B (replace operator). Recommended: path A now, revisit if a chiral operator enters the atlas. |

## Decisions required from user before Track B starts

1. **exp8 redesign:** proceed with all three nulls (ER + sign-randomized + degree-shuffle) or pilot one first?
2. **exp9:** path A (drop neutrino slot) or path B (swap operator)?
3. **Pre-registration:** should the pass/fail thresholds in R4 be frozen in a committed JSON before any recompute? (Recommended: yes.)
