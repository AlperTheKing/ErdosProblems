# EHP114 Follow-Up Calculations: The Radial Boundary Layer

Date: 2026-05-02

Status: diagnostic calculation, not a proof of Erdos #114.

## What Was Calculated

The follow-up calculation isolates the radial family

```text
p_a(z) = z^n - a
```

and computes the lemniscate length exactly through a hypergeometric constant-term formula.

For `z^n = a + exp(i t)`, each branch contributes derivative magnitude

```text
(1/n) |a + exp(i t)|^(1/n - 1).
```

There are `n` branches, so the total length is

```text
L_n(a) = integral_0^(2 pi) |a + exp(i t)|^(1/n - 1) dt.
```

For `|a| < 1`,

```text
L_n(a) = 2 pi * 2F1(p, p; 1; a^2),
p = (n - 1)/(2n).
```

For `a > 1`, factor out `a^(1/n - 1)` and evaluate the same expression at `a^(-2)`.
For `a = 1`, use the gamma-limit form.

This avoids the numerical failure mode near the singular level set of `z^n - 1`.

## Artifact Created

```text
/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/scripts/calc_ehp114_radial_hypergeometric.py

/Users/kenbengoetxea/container-projects/apps/H2/Math/erdos-experiments/results/erdos-114/
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_RESULTS.json
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_REPORT.md
  EXP-MATH-EHP114-RADIAL-HYPERGEOMETRIC-20260502-01_RESULTS.sha256
```

Result SHA-256:

```text
4a26ca443b7d1d67cab14f5465595781eb15f10f5d5c5834e42e37db4405fe51
```

## Reference Values

The exact radial formula reproduces the known/reference values:

| n | exact L_n(1) | reference interval contains exact? |
|---:|---:|---|
| 14 | `30.852910841548542295844126311342204648430086988176` | yes |
| 15 | `32.847443161592574796553537519096796108161302188611` | yes |
| 16 | `34.842672284332028043400724196170721355069679898955` | yes |

Important boundary: the n = 15 and n = 16 values are compared to shortcut/reference artifacts, not accepted as formal proof verdicts here.

## What Changed

The earlier Fourier/Hilbert probe showed:

```text
n = 15
rank = 27 = 2n - 3
positive finite-difference deficit signal in 27/27 tested Fourier directions
```

But it also showed that the marching-squares reference length for `z^15 - 1` was low:

```text
marching L0 = 30.46510792235651
exact L*    = 32.847443161592574796553537519096796108161302188611
error       = -2.382335239236064796553537519096796108161
```

The new calculation says the radial perturbation lengths near 9 to 11 are real for `a != 1`. Marching squares was close on those smooth perturbed curves. The failure was at the singular reference curve itself.

That is the key correction:

```text
The Fourier signal is not a smooth Hessian signal.
It is a stratified singular-unfolding signal.
```

## Radial Perturbation Values for n = 15

For the perturbation used in the probe,

```text
R = 1 +/- eps / sqrt(15)
a = R^15
```

the inward side is admissible under the roots-in-unit-disk constraint. The outward side is diagnostic only.

| eps | side | exact length | deficit vs exact L* | admissible? |
|---:|---|---:|---:|---|
| 0.02 | inward | `9.055079588778662140725677042662340106324844137516` | `23.792363572813912655827860476434456001836458051095` | yes |
| 0.01 | inward | `10.005044202511062060437620514505282337056587745213` | `22.842398959081512736115917004591513771104714443398` | yes |
| 0.005 | inward | `10.965426765230090557595571010467105603531865316923` | `21.882016396362484238957966508629690504629436871688` | yes |
| 0.001 | inward | `13.127611619604648156535474235966109443782630001261` | `19.71983154198792664001806328313068666437867218735` | yes |
| 0.0001 | inward | `15.916506667280879606124118385775860829169534089614` | `16.930936494311695190429419133320935278991768098998` | yes |

Even at `eps = 0.0001`, the deficit is still about `16.93`. That is not ordinary quadratic behavior.

## Boundary-Layer Scaling

For admissible inward contractions, the deficit follows:

```text
L_15(1) - L_15(a) ~ C * eps^(1/15)
```

The fitted log-log slopes from the exact calculation:

| tail window | fitted slope |
|---:|---:|
| 4 | `0.066664875637` |
| 5 | `0.066663781389` |
| 6 | `0.066662145486` |
| 8 | `0.066652922065` |

The expected value is:

```text
1/15 = 0.0666666666666666666666666666667
```

So the calculation lands almost exactly on the singular exponent.

## Interpretation

The central object `z^n - 1` is not merely a smooth critical point of a length functional. It is a singular boundary extremizer. The origin is a multiple critical point on the lemniscate, and admissible contractions unfold that singularity with Puiseux-type scaling.

This upgrades the story:

```text
old:  finite Hessian around the regular polygon
new:  stratified Fourier/tensor deficit with a hypergeometric radial boundary layer
```

That is stronger and more honest. It explains why laptop verification becomes hard after n = 14: the proof is not just a Euclidean high-dimensional search. The geometry has a singular layer whose exponent depends on `n`.

## What This Means for the Paper Story

The exemplar in nature is not "a little perturbation around a smooth optimum." It is a symmetric field object sitting at a singular threshold. When the symmetry is perturbed, the missing layer does work.

The physical analogues remain:

1. Electrostatic equipotentials: `log |p(z)|` is literally a two-dimensional potential generated by equal line charges.
2. Plateau-Rayleigh breakup: Fourier modes reveal which perturbations matter near a symmetric threshold.
3. Rayleigh charged-droplet instability: a symmetric field object becomes mode-governed at the threshold.

The mathematical exemplar is now sharper:

```text
The flaw is the singularity.
The shadow is the boundary-layer exponent.
And the shadow does work.
```

## Actionable Next Calculations

1. Prove the radial formula as a standalone lemma:

   ```text
   L_n(a) = integral_0^(2 pi) |a + exp(i t)|^(1/n - 1) dt.
   ```

2. Turn the hypergeometric expression into an interval certificate for the admissible radial side `0 <= a < 1`.

3. Replace "Hessian certificate" language in the n = 15 proof packet with "Puiseux/hypergeometric radial boundary layer plus interval Fourier/tensor remainder."

4. Build the next probe for nonradial admissible Fourier modes, constrained so roots remain inside the unit disk.

5. Treat `n = 15` as the first case where the proof needs singular geometry, not bigger brute force.

