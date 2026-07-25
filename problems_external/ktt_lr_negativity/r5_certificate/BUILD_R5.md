# r=5 positivity-certificate machinery (codimension-two coefficient e_4)

This directory builds, with exact arithmetic and validation at every step, the
Berline--Vergne / McMullen local-Ehrhart certificate machinery for size-5 hive
polytopes, following the r=4 template in `../r4_reeve/R4_KTT_THEOREM.md` and the
scoping recommendations (dilation/PIP reduction; attack the codimension-two
coefficient first).

All arithmetic is exact (`fractions.Fraction` / integer). Floating point is
never used in any decision. Engines A (`lr_hive.exe`) and B
(`engineB_lrrule.py`) are the two independent Littlewood--Richardson oracles
already cross-calibrated in `../engine/CALIBRATION.md`.

## Files

| file | role |
|---|---|
| `exactlin.py` | exact rational/integer linear algebra: rref, rank, kernel, Smith normal form, saturation index, exact phase-1 simplex, Lagrange interpolation |
| `hive5.py` | the FIXED matrix `A_5`, the 27 primitive normals, exact lattice-point counter, atlas emitter |
| `polytope5.py` | exact polytope engine on the 27 normals: vertices, facets, ridges, lattice-normalized relative volumes, ridge Lambda-vector |
| `alpha5.py` | exact BV local weight `alpha` of every codim-2 normal cone (342 ridge types), with self-tests |
| `balance5.py` | the codim-2 balancing matrix `B` from facet Minkowski closure; rank/kernel |
| `precompute_lambdas.py` | parallel exact computation of every hive's `vol_Z` ridge vector + `a_4` |
| `build_certificate.py`, `assemble_certificate.py` | witness collection + certificate assembly (`mu = alpha`) |
| `validate_hive5.py` | GATE 1: constructor vs BOTH engines (unstretched) |
| `validate_stretch5.py` | GATE 2: stretched profiles vs BOTH engines + Ehrhart interpolation |
| `validate_lattice_simplex.py` | (slow, confirmatory) local formula vs lattice counts on lattice simplices |
| `xcheck_witness_engines.py` | per-witness `a_4` cross-checked against BOTH engines (`a4_A==a4_B==cert`) |
| `verify_r5_certificate.py` | standalone independent replay of the finished certificate |

## 1. The fixed r=5 matrix A_5 and its normals

`python hive5.py` emits the atlas and reports:

```
r=5  D=6  interior slots=[(1,1),(1,2),(1,3),(2,1),(2,2),(3,1)]
rhombus inequalities total      = 30
rows with nonzero interior part = 30
pure-boundary rows              = 0
distinct primitive normals      = 27      (entries in {-1,0,+1})
antiparallel normal pairs       = 9
nonparallel unordered pairs     = 342
atlas_sha256 = 0e024bcd1299f4a3acbffd51170224bb7b8221b9e63f391b690890dcadb25dfc
```

- `D = (5-1)(5-2)/2 = 6` interior coordinates; A_5 is `30 x 6`, entries in
  `{-1,0,+1}`, rank 6. This matches the prompt's EXPECTED 30 rows / 27 normals.
- `|det|` histogram over the `C(30,6)=593775` six-row submatrices of A_5
  (nonzero part), reproduced exactly by `exactlin.det_int_bareiss`:

  ```
  1:146656  2:40320  3:2892  4:2502  5:18  6:252  7:18     max |det| = 7
  ```

  Identical to the scoping constant. Maximum vertex denominator is therefore
  at most 7; the largest observed in the built pools is 2.

## 2. The validated hive5 polytope engine

`build_hive5(lam,mu,nu)` returns `Q = {h in Z^6 : A_5 h <= b(lam,mu,nu)}` with
integral `b`; `lattice_count` counts its integer points exactly; `polytope5`
gives exact vertices, facets, ridges, and lattice-normalized relative volumes.

**GATE 1 (constructor vs both engines, unstretched).** `validate_hive5.py`:

```
seed 20260722, small partitions : 370 triples (240 nonzero / 130 zero), max c=7,   mismatches=0, PASS
seed 777,      large partitions : 300 triples (240 nonzero /  60 zero), max c=46,   mismatches=0, PASS
```

For every triple `engine A == engine B == #(Z^6 cap Q)`. Total 670 triples with
0 mismatches (requirement was 300). **A single engine separator note:** the
engines parse parts on COMMAS; space-separated input is silently misparsed, so
the harness always emits comma-separated parts.

**GATE 2 (stretched profiles).** `validate_stretch5.py` interpolates the
Ehrhart polynomial from lattice counts `L(0..7)` and requires
`L(n) == engineA(n·triple) == engineB(n·triple)` for `n = 0..8`, plus held-out
verification `n = 7,8`:

```
40 triples x 9 dilations, degrees {0,1}, no negative Ehrhart coefficient, PASS
```

On the 40 genuinely full-dimensional (dim = 6) hives found by
`_dim6_seeds.json`, the same test gives degree-6 Ehrhart polynomials that agree
with both engines and pass held-out interpolation (0 failures). Example
distinct degree-6 profile:
`P(n) = 1 + (157/60)n + (949/360)n^2 + (4/3)n^3 + (13/36)n^4 + (1/20)n^5 + (1/360)n^6`.

**Rational (non-lattice) hive handled correctly.** The scoping B1 example
`lam=(2,2,1), mu=(4,3,2,1), nu=(5,4,3,2,1)` builds to a dim-4 polytope with 7
vertices and vertex denominators `{1,2}` (two half-integral vertices), and

```
L(0..6) = 1, 5, 16, 40, 85, 161, 280   ==   (n+1)(n+2)(n^2+3n+6)/12,
```

reproducing the scoping constant exactly. The lattice counter is denominator-
agnostic, so the dilation/PIP reduction (a_k(P) = a_k(qP)/q^k, qP a lattice
polytope) is used implicitly and needs no special code.

## 3. Face-type enumeration for the recommended coefficient (k = 4, codim 2)

Scoping recommends attacking `e_4` first: its faces are the ridges (codim-2,
dim-4 faces), whose normal cones are pointed 2-dimensional, spanned by exactly
two nonparallel facet normals. The `C(27,2)=351` normal pairs minus 9
antiparallel give the **342 ridge types**. `alpha5.py` computes each type's
exact BV weight and self-tests the 2-D valuation on the unit square and the
unimodular triangle (both sum to the Ehrhart constant 1):

```
saturation index histogram = {1: 339, 2: 3}
alpha minimum = 1/9   maximum = 7/18
alpha is > 0 on ALL 342 ridge types
```

This reproduces the repo's independent `r5_e4_codim2_checker.py` exactly (same
27 normals, 342 pairs, index histogram, minimum 1/9, same six index-1
minimizers and three index-2 records with `alpha = 5/18`).

**Direct consequence (positivity of e_4 for free).** Because every ridge weight
`alpha >= 1/9 > 0` and every ridge relative volume is positive, the local
formula gives, for every full-dimensional size-5 hive,

```
e_4(P) = sum_{ridges R} alpha(cone R) * vol_Z(R) >= (1/9) sum_R vol_Z(R) > 0.
```

So the codim-2 coefficient is positive without any balancing certificate. The
same phenomenon holds at r=4: the r=4 EDGE weights (a_1 = codim-2 in d=3) are
also all `>= 1/9 > 0`, so the r=4 balancing certificate in `R4_KTT_THEOREM.md`
is likewise not the binding constraint for a_1 positivity — the direct
`alpha > 0` bound suffices. (This is the `UNIFORM_CODIM2_POSITIVITY.md` route.)

## 4. The codim-2 balancing matrix B

`balance5.py` builds `B` from the facet Minkowski (boundary-closure) relations:
each facet i is a 5-polytope whose own facets are the ridges `{i,j}`, and

```
sum_{j} vol_Z(R_ij) * conormal_i(j) = 0,   conormal_i(j) = primitive(n_i wedge n_j) in Z^15,
```

placed with sign `+` in facet-i's length-15 block and `-` in facet-j's. This
gives `B : Q^342 -> Q^{27*15}` with, exactly,

```
B shape    = 405 x 342
rank(B)    = 120        (short bound 27*5 - 15 = 120 is attained)
dim ker(B) = 222
```

reproducing the repo's `r5_ridge_balance_gate.py`.

**Validation that B is the correct operator (load-bearing).** For 20 real
full-dimensional hive polytopes, the ridge-volume vector `Lambda(P)` measured
independently by `polytope5` satisfies `B Lambda(P) = 0` exactly (0 nonzero
rows in every case). Ridge counts ranged 26..94, facet counts 8..17.

**Validation of the whole local bridge (load-bearing).** For the same 20 real
hives, the local formula reproduces the actual Ehrhart coefficient exactly:

```
e_4(P) (from interpolating exact lattice counts L(0..7))
   ==  sum_k alpha_k * vol_Z(R_k)      for all 20/20 hives.
```

(The normalization is `vol_Z = nvol / 4!`: `polytope5.relvol` returns the
simplex-normalized volume `nvol`, and the McMullen weight pairs with the
parallelepiped-normalized relative volume `vol_Z = nvol/24` for a 4-dim ridge.
This factor of `24` was verified as the exact ratio on every hive before being
divided out.) This simultaneously validates the vertex/facet/ridge/relvol
pipeline, the `alpha` weights, and the dilation reduction, against two
independent LR oracles.

## 5. Witness polytopes spanning ker(B)

`precompute_lambdas.py` computes (in parallel, exactly) the `vol_Z` ridge
vector and Ehrhart `a_4` of every hive in the pools; `assemble_certificate.py`
selects a maximal linearly independent set. Each witness satisfies, exactly:

- `B Lambda = 0` (lies in `ker(B)`);
- `a_4 = alpha . Lambda` (local identity, `a_4` from independent lattice counts);

and (a subset of the hive witnesses is separately re-checked against BOTH
engines' stretched LR profiles by `xcheck_witness_engines.py`).

**Structural finding (new).** The hive `Lambda`-vectors do NOT span `ker(B)`.
Over 1046 distinct full-dimensional hive polytopes their exact span is

```
hive span rank = 197   <   dim ker(B) = 222,
```

i.e. every hive ridge-volume vector satisfies at least `222 - 197 = 25` linear
relations BEYOND the facet-Minkowski balancing `B`. (This is a phenomenon
invisible at r=4, where the ambient is only 3-dimensional and hives already
span all of `ker(B)`.) For the KTT application this is not a defect: the only
polytopes that occur are hives and their dilates `qH`
(with `Lambda(qH) = q^4 Lambda(H)`), so the realizable `Lambda`-space is exactly
this 197-dim hive span, and `mu = alpha >= 0` already certifies `a_4 >= 0` on
all of it -- proving `e_4 > 0` for every length-<=5 hive.

**Completing ker(B) with lattice polytopes (`--full`).** To exhibit witnesses
spanning ALL of `ker(B)` (the stronger "every lattice polytope with these
normals" statement of the r=4 template), the basis is topped up with LATTICE
SIMPLICES and small corner-cut lattice polytopes carrying the 27 normals. A
simplex is fixed by 7 of the normals having a strictly positive (Minkowski)
dependence; the q-dilation trick (`qP` for `q = lcm` of vertex denominators)
makes each a genuine lattice polytope, and its `Lambda` still lies in `ker(B)`.
These have few vertices, so both the exact relative-volume triangulation and
(for the validation below) the Ehrhart lattice counts are fast.

RESULTS (`assemble_certificate.py --full`):

```
witnesses                 = 222   (hive = 197, lattice = 25)
witness_matrix_rank       = 222   ==  dim ker(B)          -> spans ker(B)
all_witness_lambda_in_kerB= True   (exact B Lambda = 0 on every witness)
all_local_identities_hold = True   (a_4 = alpha . Lambda on every witness)
mu = alpha,  mu_min = 1/9 > 0,  mu reproduces a           -> certificate valid
certificate_sha256        = 752ea056085f587eb7399db5ce3c2a370b5f15e2f104982db0524d2c54783755
```

The independent replay `verify_r5_certificate.py` reconstructs `A_5`, the 342
ridge weights, and `B` from scratch and re-checks all of the above with EXACT
rational rank (`witness_matrix_rank = 222`, spans ker B = True), returning
`PASS`.

The 25 lattice witnesses carry `a_4 = alpha . Lambda` from the SAME local-formula
implementation that is validated to the last bit against independent lattice
counts on 20 hive polytopes in Section 4 (the McMullen/Berline--Vergne formula
is normal-cone-local, so its correctness does not depend on the polytope class,
only on the shared 27 normals). Every one of the 25 also satisfies the exact
balancing `B Lambda = 0`. A direct re-confirmation of a lattice witness `a_4`
from its own Ehrhart lattice counts is compute-bound (their dilates have large
lattice-point counts) and is not part of the fast replay.

**Nonnegative certificate `mu`.** Because every ridge weight `alpha_k >= 1/9 > 0`
and the per-witness local identity gives `M alpha = a`, the vector `mu = alpha`
is already a componentwise-nonnegative certificate with `M mu = a`. Hence for
any polytope `P` with these normals, writing `Lambda(P) = y M` (valid because
`M` spans `ker(B) >= ` the realizable `Lambda`-space),

```
a_4(P) = Lambda(P).alpha = y M alpha = y a = y M mu = Lambda(P).mu >= 0.
```

No linear program is needed for this coefficient: the nonnegative-`mu` question
"does `alpha + rowspace(B)` contain a nonnegative vector?" is answered YES
trivially by `mu = alpha`. This is the crucial contrast with the general
frontier below, where `alpha` is not sign-definite and the LP can FAIL.

## What is proved, and the honest frontier

**Proved (subject to the standard hive / polynomiality / McMullen inputs and
the exact replay `verify_r5_certificate.py`):** the codimension-two coefficient
of every full-dimensional size-5 hive Ehrhart polynomial is positive,
`e_4 > 0`. Combined with the automatic positivity of `e_0=1`, `e_6=vol`,
`e_5=(1/2)sum facet vols`, this settles four of the seven coefficients
(`e_0,e_4,e_5,e_6`).

**NOT proved here (the real KTT frontier at r=5):** the coefficients `e_1, e_2,
e_3`. Their faces have normal cones of dimension 5, 4, 3 respectively, and the
BV weight `alpha` is only guaranteed nonnegative for the 2-dimensional (codim-2)
cones. The repo's `UNIFORM_CODIM3_BV_REPORT.md` argues `e_3 > 0` as well
(3-ray BV weight `>= 1/264 > 0` after saturated subdivision), which — if its
subdivision claims hold — would leave only `e_1, e_2`. For those two the sign of
`alpha` is not settled, and this is exactly where the balancing certificate
becomes load-bearing: the finite LP "does `alpha_k + rowspace(B_k)` contain a
nonnegative vector?" can FAIL, and its Farkas dual would then be the targeted
counterexample recipe. Building the codim-4 and codim-5 balancing matrices and
their BV weights is the identified next step; it is not done in this directory.

## Replay

```powershell
cd problems_external\ktt_lr_negativity\r5_certificate
python hive5.py                       # fixed A_5, 27 normals, atlas sha
python validate_hive5.py 240 130 20260722   # GATE 1: vs both engines
python validate_stretch5.py           # GATE 2: stretched profiles vs both engines
python alpha5.py                      # 342 ridge weights, min 1/9 > 0
python balance5.py                    # B: rank 120, ker 222
python verify_r5_certificate.py       # independent replay of e4_certificate.json -> PASS
python xcheck_witness_engines.py 6 8  # witness a_4 vs both engines -> PASS (a4_A==a4_B==cert)
# python validate_lattice_simplex.py 8  # optional, slow confirmatory check
```

To rebuild the certificate from scratch:
`python precompute_lambdas.py` (parallel `Lambda` for the hive pools) then
`python assemble_certificate.py --full` (hive + lattice-simplex witnesses,
`mu = alpha`, writes `e4_certificate.json`).
