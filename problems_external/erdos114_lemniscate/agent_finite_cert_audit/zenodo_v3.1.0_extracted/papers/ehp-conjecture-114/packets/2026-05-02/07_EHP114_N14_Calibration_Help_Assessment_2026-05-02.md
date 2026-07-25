# EHP114 n = 14 Calibration: Does It Help?

Date: 2026-05-02

Short answer: yes. `n = 14` is the right calibration case.

It does not prove the general theorem. It does help convert the proof program
from an interesting n = 15 frontier story into a disciplined architecture that
first explains the strongest already-computed case.

## New Calibration Artifact

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/results/erdos-114/
  EXP-MATH-EHP114-N14-RADIAL-HYPERGEOMETRIC-CALIBRATION-20260502-01_RESULTS.json
  EXP-MATH-EHP114-N14-RADIAL-HYPERGEOMETRIC-CALIBRATION-20260502-01_REPORT.md
  EXP-MATH-EHP114-N14-RADIAL-HYPERGEOMETRIC-CALIBRATION-20260502-01_RESULTS.sha256
```

Result SHA-256:

```text
6cad8337bed8f93b362e1f78cf1d9ec9b34075efe43ddb03dff5c189793e954a
```

The calculator script was generalized so separate experiment IDs can be emitted
without overwriting the n = 15 artifact:

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/scripts/calc_ehp114_radial_hypergeometric.py
```

## What n = 14 Confirms

The exact hypergeometric/gamma value is:

```text
L_14(1) = 30.852910841548542295844126311342204648430086988176
```

It lands inside the existing n = 14 interval artifact:

```text
30.852910841548532 <= L_14 <= 30.852910841548546
```

That matters because n = 14 is the last locally available heavy-compute case.
The radial exact formula is not merely numerically plausible; it agrees with the
existing interval-backed value.

## Boundary-Layer Scaling

For admissible inward radial contractions, the exact calculation fits:

```text
L_14(1) - L_14(a) ~ C * eps^(1/14)
```

Expected exponent:

```text
1/14 = 0.0714285714285714285714285714286
```

Fitted slopes:

| tail window | fitted slope |
|---:|---:|
| 4 | `0.071426652466` |
| 5 | `0.071425485343` |
| 6 | `0.071423743770` |
| 8 | `0.071413955970` |

So n = 14 shows the same singular boundary-layer behavior as n = 15, with the
expected exponent changed from `1/15` to `1/14`.

## Why This Helps

The proof architecture can now be staged:

```text
1. Prove the radial hypergeometric lemma for all n.
2. Use n = 14 as the calibration case.
3. Rebuild the known n = 14 result through singular/Fourier/tensor language.
4. Only then push n = 15 as the frontier case.
```

This is better than trying to jump directly to n = 15. If the machinery cannot
explain n = 14, it should not be trusted at n = 15. If it does explain n = 14,
the n = 15 push becomes a credible extension rather than an isolated numerical
claim.

## What n = 14 Does Not Do

It does not prove:

```text
all nonradial perturbations are controlled;
the tensor remainder is bounded;
the theorem holds globally away from the regular polygon;
the general all-n Erdos #114 statement.
```

It supports the proof program; it is not the proof itself.

## Recommended Next Move

The next real proof gate is:

```text
n = 14 interval Fourier/tensor calibration
```

That means:

1. Build the reduced `2n - 3 = 25` Fourier root-perturbation basis for n = 14.
2. Restrict to admissible perturbations, especially roots moving inward or tangentially inside the unit disk.
3. Replace floating marching-squares length estimates with interval or exact contour bounds.
4. Show every nonradial admissible mode has a certified deficit after accounting for the singular radial boundary layer.

If that closes, n = 14 becomes the rehearsal proof. Then n = 15 is no longer a
blind leap; it is the first extension of a calibrated architecture.
