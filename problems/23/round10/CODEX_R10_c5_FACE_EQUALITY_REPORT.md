# Gamma_11 equality face through q=50

## Scope

This is an exact finite face computation for the registered `c=25`,
degree-4, 56-cut D22 certificate.  It uses every primitive equality ray found
by the complete integer collector through total mass 50.  It neither solves
the SDP nor proves the all-real arc inequality.

## Plateau cross-check

The collector returned 439 primitive
D22-orbit representatives.  Independently, complete induced C5-blow-up
partitions were enumerated inside Gamma_11 and all balanced class-sum grid
points through q=50 were generated.  The two canonical ray sets are exactly
equal.  Thus all 439 collected rays
are balanced C5-colourable, including the non-indicator q=10 witness.

Support histogram:

```text
{"5": 3, "6": 94, "7": 342}
```

## Incremental exact face

| q max | equality orbits | forced nu orbits | kernel rank | Gram-face rank | Gram dimension |
|---:|---:|---:|---:|---:|---:|
| 5 | 3 | 1147 | 74 | 1471 | 7176 |
| 10 | 9 | 2051 | 302 | 4921 | 3726 |
| 15 | 22 | 2085 | 399 | 6092 | 2555 |
| 20 | 40 | 2085 | 402 | 6129 | 2518 |
| 25 | 76 | 2085 | 402 | 6129 | 2518 |
| 30 | 109 | 2085 | 402 | 6129 | 2518 |
| 35 | 178 | 2085 | 402 | 6129 | 2518 |
| 40 | 244 | 2085 | 402 | 6129 | 2518 |
| 45 | 343 | 2085 | 402 | 6129 | 2518 |
| 50 | 439 | 2085 | 402 | 6129 | 2518 |

The q=5 row reproduces the indicator-only face exactly.  The final difference
from that baseline is:

```text
{
  "additional_forced_multiplier_orbits": 938,
  "additional_gram_face_equation_rank": 4658,
  "additional_kernel_rank": 328
}
```

The final generalized dimensions are:

```text
{
  "face_linear_variables": 3044,
  "forced_multiplier_orbits": 2085,
  "gram_face_equation_rank": 6129,
  "gram_face_orbit_dimension": 2518,
  "gram_orbit_scalars": 8647,
  "kernel_rank_total": 402,
  "live_multiplier_orbits": 526,
  "normalization_equations": 56,
  "raw_kernel_equations": 49312,
  "target_equations": 392,
  "unique_kernel_equations": 11198
}
```

## Artifact

`CODEX_R10_c5_FACE_EQUALITY_data.npz` stores the 439 equality representatives, complete blow-up
partitions, forced/live multiplier orbit IDs, all original exact coefficient
maps restricted to the live multipliers, and an exact independent integer CSR
basis `gram_face` for the generalized equations `Q_p v_p(a)=0`.

The Gram-face rank is exact blockwise: the invariant symmetric-form character
formula gives the rational rank upper bound, and modular elimination selects
that many original integer evaluation equations with a nonzero minor.
