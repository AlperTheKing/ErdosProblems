# EXP-DISS-KVN-001 Verdict

**Date:** 2026-04-16
**System:** Perturbed doubling map, delta = 0.01
**M_L (natural units):** (ln 2)^2 = 0.480453
**Expected Ruelle resonance:** tau* = 1/2 = 0.5

## Overall: PARTIAL

Median crossover epsilon = 0.1 differs from M_L = 0.4805 by a factor of 0.21. A transition exists but is not at M_L. Bridge reading needs refinement.

## Clean-matrix tau (no added noise)

| W | clean tau | deviation from 1/2 |
|---|-----------|--------------------|
| 20 | 0.48592 | 0.01408 |
| 40 | 0.46982 | 0.03018 |
| 80 | 0.48121 | 0.01879 |
| 160 | 0.47903 | 0.02097 |

## Crossover analysis

| W | clean tau | crossover epsilon | crossover / M_L |
|---|-----------|-------------------|-----------------|
| 20 | 0.48592 | 0.1 | 0.208 |
| 40 | 0.46982 | 0.1 | 0.208 |
| 80 | 0.48121 | 0.1 | 0.208 |
| 160 | 0.47903 | 0.0316 | 0.066 |

## Interpretation

If VERDICT == PASS: MOR-DISS-001 upgraded from putative to power-morphism (atlas-speak). The Mendoza-Limit reading of transfer-operator spectra survives on the canonical test case.

If VERDICT == PARTIAL or INCONCLUSIVE: MOR-DISS-001 remains a putative morphism but the specific Leg-4 signature predicted in the discovery note requires refinement. Either (i) M_L is not the right thermodynamic scale for this system, or (ii) the transition is smooth rather than sharp and the reading needs a softer formulation.
