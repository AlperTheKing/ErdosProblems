# exp9_v2 — Chiral-RMT Soft-Edge Test (Bipartite Gaussian)

**Date:** 2026-04-19
**Preregistration:** `TRACK_A_PREREGISTRATION.json :: exp9_v2`
**Operator used:** bipartite_gaussian (primary, no fallback)
**Wall time:** 1.9 s

## Verdict

**CHIRAL_CLASS_REJECTED**

Rule: C1 AND C2 AND C3 → CHIRAL_CLASS_CONFIRMED; C2 fails → CHIRAL_CLASS_REJECTED; C2 passes but C1 or C3 fails → CHIRAL_CLASS_WEAK.

## Criteria evidence

| Criterion | Threshold | Observed | Pass? |
|---|---|---|---|
| C1 microscopic universality (max KS across consecutive W) | ≤ 0.10 | 1.0000 | FAIL |
| C2 soft/bulk kink at every W | ≥ 1.0 at every W | min = 0.681, max = 1.401 | FAIL |
| C3 flavor oscillation β_lower_2σ | ≥ −0.10 | 0.3036 (β = 0.3352, SE = 0.0158) | PASS |

### C1 — KS distances between consecutive W

| pair | KS |
|---|---|
| (20,40) | 1.0000 |
| (40,80) | 1.0000 |
| (80,160) | 1.0000 |
| (160,320) | 1.0000 |

### C2 — soft_over_bulk per W

| W | ratio | per-W verdict |
|---|---|---|
| W=20 | 0.681 | FAIL |
| W=40 | 0.720 | FAIL |
| W=80 | 0.899 | FAIL |
| W=160 | 1.156 | PASS |
| W=320 | 1.401 | PASS |

### Floor-filter exclusion rates per W

| W | excluded / total | rate |
|---|---|---|
| W=20 | 0/100 | 0.0% |
| W=40 | 0/100 | 0.0% |
| W=80 | 0/100 | 0.0% |
| W=160 | 0/100 | 0.0% |
| W=320 | 0/100 | 0.0% |

Max exclusion fraction: 0.00% — methodology flag not raised (pre-reg threshold 5%).

## Implementation notes

Primary operator (bipartite Gaussian M=2W, N=W, entries N(0,1/sqrt(W))) used per pre-reg rule — no implementation blocker encountered. SVD via numpy.linalg.svd(full_matrices=False). Soft and bulk kink strengths operationalized as the pre-reg 'Simpler reproducible version': max |second difference| of the ascending-sorted spectrum restricted to the bottom 5% (soft) and the middle 40-60% band (bulk), averaged across realizations. C3 range operationalized as the canonical P95−P5 of the filtered σ_min·W distribution per W (documented in output).

Seeds: `seed(W, idx) = 20260419 + W*10000 + idx`. Deterministic.

Artifacts: `exp9_v2_results.json` (full numerics, this directory).
