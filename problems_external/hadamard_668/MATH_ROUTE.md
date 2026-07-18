# Hadamard 668: cyclic GS/SDS mathematics route

Date audited: 2026-07-18

## Direct certificate and bridge

Work in the additive group `G = ZMod 167`. For a subset `X` and a nonzero
`d`, put

`N_X(d) = |{x in X : x + d in X}| = |X ∩ (X - d)|`.

Four blocks `X1,...,X4` of sizes `k1,...,k4` are a Goethals-Seidel SDS when

`sum_i N_Xi(d) = lambda` for every nonzero `d`,

where `lambda = k1 + k2 + k3 + k4 - 167`. Let `Ai` be the circulant
`{+1,-1}` matrix whose first row is `-1` exactly on `Xi`, and let `R` be the
back-diagonal permutation matrix. The SDS identities are equivalent to

`A1*A1^T + A2*A2^T + A3*A3^T + A4*A4^T = 668 I`.

The standard Goethals-Seidel array

```text
[ A1    A2 R       A3 R       A4 R     ]
[-A2 R  A1        -A4^T R     A3^T R   ]
[-A3 R  A4^T R     A1        -A2^T R   ]
[-A4 R -A3^T R     A2^T R     A1       ]
```

therefore satisfies `H H^T = 668 I`. Its entries are all `+1` or `-1`, so
`|det H| = 668^334`. This is the exact bridge to the Formal Conjectures
target; no asymptotic statement or low-defect state is a substitute.

## Complete normalized parameter enumeration

The SDS counting identity is

`sum_i k_i(k_i - 1) = lambda * 166`.

Complementing blocks if necessary, take `0 <= ki <= 83` and define the
positive odd row sums `ri = 167 - 2*ki`. Substituting
`lambda = sum_i ki - 167` into the counting identity gives the equivalent
numerical feasibility equation

`r1^2 + r2^2 + r3^2 + r4^2 = 4*167 = 668`.

Enumerating positive odd `1 <= r1 <= r2 <= r3 <= r4 <= 25` gives exactly
the following ten unordered possibilities. Permutations give all ordered
possibilities.

| row sums `r` | block sizes `k = (167-r)/2` | `lambda` |
|---|---:|---:|
| `(1,1,15,21)` | `(83,83,76,73)` | 148 |
| `(1,9,15,19)` | `(83,79,76,74)` | 145 |
| `(3,3,5,25)` | `(82,82,81,71)` | 149 |
| `(3,3,11,23)` | `(82,82,78,72)` | 147 |
| `(3,3,17,19)` | `(82,82,75,74)` | 146 |
| `(3,7,9,23)` | `(82,80,79,72)` | 146 |
| `(3,7,13,21)` | `(82,80,77,73)` | 145 |
| `(3,9,17,17)` | `(82,79,75,75)` | 144 |
| `(5,9,11,21)` | `(81,79,78,73)` | 144 |
| `(7,13,15,15)` | `(80,77,76,76)` | 142 |

Each row was independently checked against both `sum r_i^2 = 668` and the
SDS counting identity. There are no further normalized cardinality tuples.

## Highest-leverage family: two Paley blocks plus one D-optimal pair

Let `Q` be the nonzero quadratic residues modulo 167. Since
`167 = 3 (mod 4)`, `Q` is a skew `(167,83,41)` difference set:

`N_Q(d) = 41` for every nonzero `d`.

Thus the first parameter row has a much smaller direct frontier. It is
enough to find two subsets `Y,Z` with

```text
|Y| = 76,
|Z| = 73,
N_Y(d) + N_Z(d) = 66  for every nonzero d in ZMod 167.
```

Then `(Y,Q,Q,Z)` has parameters `(167;76,83,83,73;148)`, because
`66 + 41 + 41 = 148`. After moving one skew Paley block to the first GS
position, the array above is a skew-Hadamard matrix of order 668.

Equivalently, the two unknown blocks form a cyclic D-optimal SDS
`(167;76,73;66)`. For every nontrivial additive character `chi`, the exact
spectral check is

`|sum_(y in Y) chi(y)|^2 + |sum_(z in Z) chi(z)|^2 = 83`.

For the associated sign sequences the two row sums are 15 and 21, and the
nonzero-frequency PSD sum is 332. Together with the two Paley row sums
`1,1`, the zero-frequency checksum is `15^2 + 21^2 + 1^2 + 1^2 = 668`.

This Paley/D-optimal implication is not new, but it is a direct construction
route: Abuzin--Balonin--Djokovic--Kotsireas state it explicitly in their
2019 GS-family paper (lines 290--294 in the online PDF).

## Symmetry and multiplier-orbit restrictions

`(Z/167Z)^*` is cyclic of order `166 = 2*83`. Consequently its only
nontrivial proper subgroups have orders 2 and 83.

- The order-83 subgroup has nonzero orbits of size 83 (quadratic residues
  and nonresidues). Its unions have sizes only from `{0,1,83,84,166,167}`,
  so it cannot produce blocks of sizes 76 and 73. It gives no useful orbit
  reduction for the unknown D-optimal pair.
- The order-2 subgroup `{+1,-1}` is the only practical multiplier-orbit
  restriction, but imposing it on both unknown blocks is impossible here.
  For a symmetric block `X`, the involution `x -> -x-d` on the pairs counted
  by `N_X(d)` has one possible fixed point, so
  `N_X(d) mod 2 = 1_X(d/2)`. Since the target 66 is even, symmetric `Y,Z`
  would have identical membership on every nonzero sign-pair. Yet `Y` must
  contain 38 sign-pairs and `Z\{0}` only 36, a contradiction.
- The first live orbit-reduced families therefore impose symmetry on exactly
  one block: unrestricted `Y` with symmetric `Z`, then symmetric `Y` with
  unrestricted `Z`. Failure of either mixed family says nothing about the
  unrestricted Paley/D-optimal route.
- Without imposed symmetry, translations of `Y` and `Z` may be normalized
  independently and a common unit multiplier may then be applied. Hence one
  may fix `0,1 in Y` and `0 in Z` without loss. Choosing `Q` rather than the
  nonresidue Paley block is also without loss under a nonsquare multiplier.

The recommended first live family is unrestricted `Y` with symmetric `Z`,
followed by symmetric `Y` with unrestricted `Z`, then the fully unrestricted
pair. These are independent of the public four-free-block `(17,17,9,3)`
search lane.

## Prior-art and priority audit

1. Abuzin, Balonin, Djokovic and Kotsireas (2019) explicitly say that no
   cyclic GS difference family was known for `v=167`; they also give the
   repeated-skew-block/Legendre plus D-optimal-pair construction used above:
   <https://doi.org/10.31799/1684-8853-2019-5-2-9>.
2. Cati and Pasechnik's current construction database lists order 668 among
   the four unknown Hadamard orders at most 1208 (`668,716,892,1132`) and
   leaves the `n=167` entry blank:
   <https://arxiv.org/abs/2411.18897>.
3. The 2026 PatternBoost paper searches GS-type matrices and reports a
   largest example of order 252, not 668; it is an active methodology, not a
   solution collision: <https://arxiv.org/abs/2604.11101>.
4. The 2026 near-Williamson search exhausts only odd orders at most 35 and
   gives examples/existence through 63; it does not decide order 167:
   <https://arxiv.org/abs/2605.08661>.
5. Manjhi and Kujur's 2023 negacyclic paper only makes a conditional
   observation about a narrow symmetric-negacyclic `A,B,C,C` class at order
   167. It is not a nonexistence theorem for Williamson matrices, cyclic
   SDSs, or the Paley/D-optimal family:
   <https://doi.org/10.26713/cma.v14i5.2477>.
6. The public `renaissancefieldlite/Hadamard_Proof` repository was created
   2026-04-07 and last pushed 2026-04-14. Its recursive file tree contains
   only one GS signature for 668, `(17,17,9,3)` / `(167;75,75,79,82;144)`,
   with reported best score 2496 and maximum shift violation 8; it explicitly
   says the problem is unsolved. GitHub metadata reports `license: null`, so
   its code must not be copied or adapted. The independent Paley/D-optimal
   implementation here uses a different signature and mathematical route:
   <https://github.com/renaissancefieldlite/Hadamard_Proof>.

No published construction, negative result covering this family, or current
positive claim for the `(167;76,73;66)` pair was located in the 2026-07-18
audit.

## Next falsifiable action and exit

Search the exact two-block equations first with exactly one symmetric block,
then without symmetry, checking only the 83 shifts `d=1,...,83` because
`N_X(d)=N_X(-d)`. A hit is four explicit blocks `(Y,Q,Q,Z)` and is verified
by direct integer difference counts before any Lean work.

If the scheduled family budget yields no zero-defect pair, record only that
the searched family/budget was exhausted. Do not infer nonexistence of a
cyclic SDS or of a Hadamard matrix, and do not replace the exact certificate
with a low-defect state.
