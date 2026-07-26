# Exact induced-C5 face for the Gamma_11 D22 certificate

## Scope

This file concerns only the registered fixed `c=25`, degree-4 multiplier,
56 cyclic-interval-cut certificate.  It does not establish feasibility and
does not claim `ARCBOUND_Gamma_11 <= L^2/25`.

## Exact derivation

Let `C` be any induced 5-cycle and put `x=1_C`, so `L(x)=5`.  For a cut `S`,
let `k_S(C)` be the number of its monochromatic edges on `C`.  Odd-cycle
parity gives `k_S(C) in {1,3,5}`.  The multiplier normalization and target
identity give

`T(1_C) = 5^6 - sum_S nu_S(1_C) k_S(C)
          = -sum_S nu_S(1_C)(k_S(C)-1)`.

Every `nu_S(1_C)` is nonnegative, while the SOS condition gives `T(1_C)>=0`.
Thus equality holds term by term.  If `k_S(C)>1`, then `nu_S(1_C)=0`; because
`nu_S` has nonnegative coefficients, every coefficient indexed by a
degree-4 monomial whose support lies in `C` must vanish.

Also `T(y^2)=sum_p z_p(y)^T Q_p z_p(y)=0` at `y=1_C`.  Each summand is
nonnegative, hence `Q_p v_(p,C)=0`, where the coordinate at a degree-6
monomial `beta` is `1` iff `supp(beta) subset C`, and `0` otherwise.  Sign
choices on `C` change this vector only by a common sign inside a parity block,
so they add no further kernel vectors.

## Independently rebuilt counts

```text
{
  "cut_c5_k_distribution": {
    "1": 814,
    "3": 737,
    "5": 297
  },
  "cuts": 56,
  "edges": 22,
  "face_dimension_by_psd_order": {
    "1": 26,
    "11": 938,
    "286": 1526,
    "66": 4686
  },
  "forced_multiplier_full_entries": 24563,
  "forced_multiplier_orbits": 1147,
  "gram_face_orbit_dimensions": 7176,
  "gram_kernel_candidate_vectors": 74,
  "gram_kernel_independent_equations": 1471,
  "gram_kernel_independent_vectors": 74,
  "gram_kernel_raw_equations": 11539,
  "gram_kernel_unique_equations": 1530,
  "gram_orbit_scalars": 8647,
  "graph": "Gamma_11=And(4)",
  "group_order": 22,
  "induced_c5_orbit_sizes": [
    11,
    11,
    11
  ],
  "induced_c5_representatives": [
    [
      0,
      1,
      4,
      5,
      8
    ],
    [
      0,
      1,
      4,
      6,
      8
    ],
    [
      0,
      2,
      4,
      6,
      8
    ]
  ],
  "induced_c5s": 33,
  "kernel_dimension_by_psd_order": {
    "1": 0,
    "11": 11,
    "286": 33,
    "66": 30
  },
  "live_multiplier_orbits": 1464,
  "multiplier_degree": 4,
  "multiplier_full_entries": 56056,
  "multiplier_monomials": 1001,
  "multiplier_orbits": 2611,
  "normalization_equations": 56,
  "parity_block_orbits": 52,
  "parity_blocks_full": 848,
  "prime_exact_row_basis": 2000003,
  "psd_order_counts": {
    "1": 26,
    "11": 20,
    "66": 5,
    "286": 1
  },
  "remaining_certificate_equations": 448,
  "target_degree": 6,
  "target_monomials": 8008,
  "target_orbit_equations": 392,
  "total_face_linear_variables": 8640,
  "vertices": 11
}
```

## Exact sparse reduction

`CODEX_R10_c5_FACE_data.npz` contains integer CSR matrices:

- `normalization_live`: the 56 normalization-orbit equations after deleting
  the forced multiplier orbit columns;
- `target_nu_live`: the multiplier contribution to the 392 target-orbit
  equations after the same deletion;
- `target_gram`: the Gram contribution to those 392 equations;
- `gram_face`: an exact independent row basis of the representative-block
  equations `Q_p v_(p,C)=0`.

The variable order is `nu[live_multiplier_orbits]` followed by the 52 Gram
orbit-variable vectors concatenated in `gram_offsets` order.  The exact
system is

```text
normalization_live * nu_live = normalization_rhs
target_nu_live * nu_live + target_gram * q = target_rhs
gram_face * q = 0
```

with `nu_live >= 0`, `nu[forced_multiplier_orbits]=0`, and the original 52
representative PSD constraints unchanged.  The Gram-face rows are selected
from integer equations by modular elimination.  Their rank is exact, not
heuristic: the invariant symmetric-form character formula supplies the
rational upper bound block by block, and the displayed modular pivots reach
that bound, furnishing a nonzero integer minor.
