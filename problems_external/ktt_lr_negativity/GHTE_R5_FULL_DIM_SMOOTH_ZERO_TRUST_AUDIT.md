# Zero-Trust Audit: One Smooth Full-Dimensional Side-Five GHTE Gate

Date: 2026-07-22

Status: **PASS for this one fan only.** This is a finite validation gate. It is
not evidence for Global Hive Todd Effectivity and is not a proof of the full
King--Tollu--Toumazet conjecture.

## Audited instance

```text
lambda = (16,13,10,4,1)
mu     = (13,9,4,1,0)
nu     = (27,22,13,5,4)
```

The independent checker is
`ghte_r5_full_dim_smooth_zero_trust_audit.py`. It does not import either
`hive5.py` or `ghte_r5_full_dim_smooth_audit.py`, and it does not use the
root checker's binary-form Chow elimination.

## Independent reconstruction

The checker regenerates all 30 side-five rhombi directly on the triangular
grid, substitutes the three boundary paths, and sends the resulting exact
rational H-representation to cddlib. It obtains:

```text
intrinsic dimension: 6
intrinsic lattice:   Z^6 (the affine span is all of R^6, hence saturated)
facets/rays:         8
vertices:            16
normal-cone sizes:   6 at every vertex
maximal determinants: absolute value 1 at every vertex
```

Thus the complete normal fan is simplicial and smooth. Its cone counts are

```text
q:              0   1   2   3   4   5   6
number cones:   1   8  28  56  68  48  16
```

Every cone is regenerated as a face of a maximal normal cone; no cone list is
read from the root checker.

## Primitive balancing audit

For every incidence `tau < sigma`, quotient coordinates are obtained by
completing the rays of `tau` inside a containing unimodular maximal cone. The
inverse of that determinant-one basis gives a genuine integral basis of
`N/N_tau`; the image of the extra ray is checked primitive.

For `q=5`, the resulting exact matrix is

```text
B_5 shape: 136 x 48
rank(B_5): 46
dim ker(B_5): 2
```

The 48 actual edges are reconstructed from the two maximal cones containing
each five-cone. Their normalized lengths are positive and satisfy

```text
B_5 v_5 = 0
```

exactly over the rationals. The payload records the cone order, every
primitive quotient vector, the full `B_5` matrix, and all 48 lengths.

## Independent Todd computation

The Todd class is derived from the smooth toric Euler sequence, but evaluated
by exact fixed-point localization rather than the root checker's Chow-ring
elimination. At a maximal cone, the six primitive rays form a unimodular
basis. Evaluating its dual basis on a generic integral vector gives the six
fixed-point weights. The checker uses

```text
x/(1-exp(-x)) = 1 + x/2 + x^2/12 - x^4/720 + x^6/30240
```

and sums the localization fractions exactly. Two unrelated generic vectors
give identical target pairings and identical intersection matrices.

For `q=5`, pairing `td_5` with the eight invariant divisors gives, in the ray
order stored in the payload,

```text
(11/6, 59/20, 11/6, 67/60, 67/60, 11/6, 59/20, 11/6).
```

Let `P` be the `8 x 48` exact divisor-by-invariant-curve intersection matrix.
The checker verifies

```text
rank(P) = 2,
P B_5^T = 0,
rank(P) + rank(B_5) = 48.
```

Consequently `P` is an exact quotient-dual presentation of
`A^5(X)_Q`, and equality of all eight divisor pairings is equality modulo the
primitive balancing relations.

## Exact effective-cycle certificate for q=5

With ray indices

```text
0=(-1,1,0,-1,0,0)       4=(0,0,0,0,0,1)
1=(0,-1,1,1,-1,0)       5=(0,0,1,0,0,0)
2=(0,0,-1,0,1,0)        6=(0,1,-1,0,0,0)
3=(0,0,0,-1,1,-1)       7=(1,-1,0,0,0,0),
```

the independently found certificate is

```text
td_5 = (11/6) [V(0,1,2,3,4)]
     + (59/20)[V(0,1,2,3,5)]       in A^5(X)_Q.
```

Both coefficients are positive. The equality is replayed as an exact matrix
identity against all invariant divisors. Pairing this cycle with the actual
edge-length vector gives

```text
[n] L_H(n) = 287/60.
```

The same value follows independently from the support-number/Todd pairing and
matches the exact stretching-polynomial record
`purged_region/pop_profile.jsonl` for this triple.

## All-degree audit

The same localization/intersection method was run for every `q=0,...,6`.
Each Todd component has an exact nonnegative invariant-cycle representative:

| q | cones | rank A^q | rank B_q | effective support |
|---:|------:|----------:|---------:|------------------:|
| 0 | 1 | 1 | 0 | 1 |
| 1 | 8 | 2 | 6 | 2 |
| 2 | 28 | 3 | 25 | 3 |
| 3 | 56 | 4 | 52 | 4 |
| 4 | 68 | 3 | 65 | 3 |
| 5 | 48 | 2 | 46 | 2 |
| 6 | 16 | 1 | 15 | 1 |

For every degree, the independently computed intersection quotient
annihilates `B_q^T` and its rank complements `rank(B_q)` to the number of
`q`-cones.

## Cross-check against the root result

The root checker was run separately after the independent checker had been
completed. It reported

```text
cone counts:       (1,8,28,56,68,48,16)
Chow dimensions:  (1,2,3,4,3,2,1)
status q=0..6:    EFFECTIVE
payload SHA-256:  4e1cf7db2a43e40415d5c26e7c90bbffd50f53f25e84d84e1b4cc14778369c98
```

These counts, dimensions, and statuses agree exactly with the independent
reconstruction. No mismatch was found.

## Replay

From the repository root:

```powershell
python problems_external/ktt_lr_negativity/ghte_r5_full_dim_smooth_zero_trust_audit.py
python problems_external/ktt_lr_negativity/ghte_r5_full_dim_smooth_audit.py
```

The independent run prints

```text
PASS
B5=136x48 rank=46 edge_balance=0
all_q_chow_ranks=(1,2,3,4,3,2,1) all_q_effective=PASS
linear_coefficient=287/60
payload_sha256=69e412600c70245e2c7147686d9024bad64da54c332869ab57bbd4daa5cb3a74
```

Artifact hashes at audit completion:

```text
d82026e41b6954a2999a4cc0856ea790aeb4bb4dad531e47c3f4c9e3be5bcc68  ghte_r5_full_dim_smooth_zero_trust_audit.py
e2f09b8f59a5e32a90370fe020af2eb2bb6affc741c1e10d9904437a1b0cf317  ghte_r5_full_dim_smooth_zero_trust_payload.json
```

## Scope guard

This PASS says only that GHTE holds for every degree on this one smooth
complete side-five hive fan. It neither supplies a rank-uniform transport
theorem nor rules out a negative balanced weight on another fan. General KTT
therefore remains open.
