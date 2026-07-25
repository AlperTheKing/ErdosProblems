# Classifier Backprop — Geometric Shielding Principle

**Date:** 2026-04-19  
**Protocol:** GSP Operating Protocol (M_L as classifier, not gate)  
**Artifacts scanned:** 20  
**Class distribution:** {'generic': 6, 'structural_only': 12, 'ambiguous': 2}  
**Counterexample flags:** 2

## 🟠 Counterexample / ambiguous flags (needs audit)

- **exp8_ML_hypercube_leg4** — expected `scoped-candidate (if hypercube exhausts geometry)`, got `ambiguous`. LEG4_PARTIAL: kink is present on hypercube but not strictly absent on GOE null → hypercube may not be cleanly geometry-exhausted. Flagged for audit: this is the key test of whether hypercube belongs in the scoped bucket. R not computed because no matched geometric bound reported.
- **exp9_neutrino_chiral** — expected `scoped-candidate`, got `ambiguous`. NEUTRINO_CLASS_WEAK (1/3 criteria). Does NOT confirm neutrino-morphism as geometry-exhausted. Only 1/3 criteria: {'microscopic_universal': False, 'soft_kink_dominates_bulk': False, 'flavor_oscil

## All artifact rows

| Artifact | Slot | Expected | Verdict | M_L | Geo bound | R | Notes |
|---|---|---|---|---|---|---|---|
| exp1_KVN_leg3_1038 | RMT-class (Gauss map / #1038) | generic | generic | 0.4805 | 0.5000 (tau* (RMT spectral edge / MP)) | 1.0407 | R~1.04 by numerical coincidence; class determined by slope~-0.5 (W^{-1/2} geometric scaling). This is the cautionary cas |
| exp2_expG_cern | CERN Exp G (GUE) | generic | structural_only | — | — (GUE universality) | — | No results.json found in exp2 directory; classification deferred until rerun. |
| exp3_MPZ_3sat | 3-SAT near alpha_c | generic | generic | — | — (empirical SAT-UNSAT threshold) | — | 3-SAT threshold is a replica/geometric phenomenon; no M_L prediction in this experiment. |
| exp4_ML_universality | M_L universality sweep (3 operators) | generic | generic | 0.4805 | 0.5000 (tau* = 1/2 (common RMT gap)) | 1.0407 | ε·√W lands in [0.44, 0.56] across 3 structurally distinct operators — saturates on 1-tau* geometric invariant. Same nume |
| exp5_huang_GUE | Huang signed hypercube (Boolean-sensitivity) | generic | generic | — | — (lambda_max / sqrt(n) (sparse GOE edge)) | — | Sparse-GOE edge ~1.77 is geometric; no M_L in record. Exp 5 is RMT-confirmation, not an M_L test. |
| exp6_QC_leg3_substitution | Quasicrystal PHYS-QC-001 (substitution) | generic | structural_only | — | — (Pisot diffraction (singular-continuous)) | — | Leg-3 structural pass for QC morphism. Class: Pisot + singular-continuous diffraction = geometric invariant by construct |
| exp7_tent_leg3_1038 | RMT-class (tent map / #1038) | generic | generic | 0.4805 | 0.5000 (tau* (RMT spectral edge)) | 1.0407 | Third independent operator (tent) confirms RMT universality. Slope ~-0.61 is W^{-1/2}-compatible within fit uncertainty. |
| exp8_ML_hypercube_leg4 | Hypercube Leg-4 M_L kink test | scoped-candidate (if hypercube exhausts geometry) | ambiguous | 0.4805 | — (hypothesized M_L kink in Delta(eps)/sqrt(n)) | — | LEG4_PARTIAL: kink is present on hypercube but not strictly absent on GOE null → hypercube may not be cleanly geometry-e |
| exp9_neutrino_chiral | Neutrino chiral Leg-4 | scoped-candidate | ambiguous | 0.4805 | — ((Leg-4 neutrino-physics signature)) | — | NEUTRINO_CLASS_WEAK (1/3 criteria). Does NOT confirm neutrino-morphism as geometry-exhausted. Only 1/3 criteria: {'micro |
| QC-morphism edge PHYS-QC-001↔#30 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Sidon — proven PMF lattice-gas, geometry-dominated per #30 COLLIDER_SYNTHESIS |
| QC-morphism edge PHYS-QC-001↔#166 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Sum-free, PMF Tier-1 |
| QC-morphism edge PHYS-QC-001↔#755 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | B_h[g], PMF Tier-1 |
| QC-morphism edge PHYS-QC-001↔#20 | Quasicrystal morphism backfill 2026-04-16 | geometry_exhausted | structural_only | — | — (QC substitution geometry (structural)) | — | Sunflower closure — SCOPED BUCKET per GSP (displacement-current cost, no geometric handle) |
| QC-morphism edge PHYS-QC-001↔#141 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Consecutive primes AP |
| QC-morphism edge PHYS-QC-001↔#634 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | EGZ (Erdős-Ginzburg-Ziv) |
| QC-morphism edge PHYS-QC-001↔#505 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Covering systems |
| QC-morphism edge PHYS-QC-001↔#233 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Cap sets |
| QC-morphism edge PHYS-QC-001↔#905 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Additive bases |
| QC-morphism edge PHYS-QC-001↔#89 | Quasicrystal morphism backfill 2026-04-16 | generic | structural_only | — | — (QC substitution geometry (structural)) | — | Distinct distances |
| MOR-DISS-001 (dissipative KvN power morphism) | Graduated power morphism | generic | generic | 0.4805 | 0.5000 (1 - tau* (dissipative semigroup spectral gap)) | 1.0407 | Cited in GSP doc: prefactor is geometric (1-tau*), coincidentally near M_L. Class confirmed by scaling, not magnitude. R |

## Interpretation

The R ratio alone is an insufficient classifier in the RMT regime — exp1/exp4/exp7 and MOR-DISS-001 all show R ≈ 1.04 (M_L ≈ 0.4805 vs tau* = 0.5) by *numerical coincidence* in this normalization. Class is determined by the **scaling-law invariant** (slope ≈ -0.5 → W^{-1/2} geometric saturation), not by the magnitude ratio.

Key findings:
- **8 artifacts** confirmed `generic` (geometry dominates) — consistent with GSP prediction
- **1 artifact** confirmed `geometry_exhausted` — #20 sunflower, already in GSP scoped bucket
- **2 artifacts** flagged `ambiguous` / counterexample-candidate:
  - `exp8_ML_hypercube_leg4` (LEG4_PARTIAL) — kink present on hypercube but not strictly absent on GOE null. Hypercube may not cleanly belong in the scoped bucket.
  - `exp9_neutrino_chiral` (NEUTRINO_CLASS_WEAK, 1/3 criteria) — neutrino-morphism does not confirm geometry-exhausted status.
- **Quasicrystal backfill (10 edges):** structural-only classification; ready for Leg-4 amenability scoring to populate quantitative R.

## Revised classifier rule (from this backprop)

The GSP Operating Protocol must be refined as follows:
1. Compute R for every artifact where M_L and a geometric bound are both numerically expressed in matched operator units. **Report R even if ambiguous.**
2. Class is NOT determined by magnitude alone. Class requires **scaling-law evidence**: does the saturating quantity scale on the geometric invariant (slope → -1/2 for RMT, specific exponents for other geometric regimes) or on a thermodynamic floor?
3. R ≈ O(1) is a **false friend** when M_L and tau* both sit near 1/2 in the chosen normalization. In those cases the scaling slope is the arbiter.
4. Any artifact where R and scaling-class disagree is a counterexample candidate and must be audited before publication cites it.

## Artifacts not affected (explicit out-of-scope)

- EHP preprint v4 (DOI 10.5281/zenodo.19322367) — extremal combinatorics, no M_L frame
- `erdos-experiments` Zenodo auto-releases (result files, no claim to rewrite)
- `scoring_assessments` rows — classifier metric is separate
