# Scalar heat-bath report

The descendant could not write this file through its restricted writer; this
lead transcription preserves its exact final result.

For nonnegative rational weights `mu_x` with `sum mu_x = 1`,

`barDelta = sum_x mu_x Delta_x = barC + barH`.

At a global scoped-score minimizer every legal single- or multi-coordinate
alternative has `Delta_x >= 0`, hence `barDelta >= 0`. Together with
`barH <= 0`, this implies `barC = barDelta-barH >= -barH >= 0`, not negative
drift. Minimal shore deficiency plus `HitNeedDelta <= 0` is therefore
insufficient without a direct negative collision upper bound.

Exact `Fraction` tests on `accounting/default.json`, coordinate menu sizes
`3,5,5`:

- uniform coordinate heat bath: `C=-16`, `H=-3`, `Delta=-19`;
- uniform over all 13 alternatives: `C=-16`, `H=-3`, `Delta=-19`;
- inverse-menu weights `1/(3m_i)`: `Delta=-19`.

Smallest abstract falsifier: a singleton inclusion-minimal shore with demand
2, source 1, defect 1, and one legal alternative `C=1,H=0,Delta=1`. It
satisfies global nondecrease and `H<=0` but falsifies strict negative drift and
`C<=-defect`. A separate exact two-coordinate model has singleton deltas
`1,1` and joint delta `-3`, showing why one-coordinate heat baths miss
simultaneous descent.

Proof gap: construct a graph-derived multi-coordinate distribution satisfying
`barC <= -defect + (-barH) - epsilon`, equivalently `barDelta < 0`.
