# Independent audit of the R10 D22-reduced Gamma_11 SDP

## Scope and verdict

This audit concerns only
`CODEX_R10_g11_d22_sdp.py` and its numerical export.  It does not solve a
second SDP.

The D22 reduction and the numerical expansion map pass an independent integer
reconstruction.  In particular, one equation per monomial orbit and one
stabilizer-invariant PSD block per parity-block orbit are lossless.

The Clarabel export is internally D22-consistent, but it is not a certificate:
it has coefficient residuals, 144 expanded Gram blocks with an eigenvalue below
`-1e-8`, and it misses the exact face forced by the 33 induced C5
concentrations.  It must not be rounded entrywise.

## Exact structural reconstruction

The replay script does not import the Round 7 graph or SOS helpers when it
reconstructs the graph, cuts, monomials, group actions, or coefficient maps.
It obtains:

```text
Gamma_11: 11 vertices, 22 edges, degree 4, triangle-free
D22 order: 22
cyclic-interval cuts: 56
cut orbits: 6, with sizes [1,11,11,11,11,11]
degree-4 monomials / D22 orbits: 1001 / 56
(cut, degree-4 monomial) orbits: 2611
degree-6 monomials / D22 orbits: 8008 / 392
degree-6 parity blocks / D22 orbits: 848 / 52
stabilizer-tied representative Gram scalars: 8647
```

The independently generated normalization map, multiplier-to-target map, and
Gram-to-target map agree entry-for-entry with the constructor.  A deterministic
random invariant coefficient vector was expanded to the full 8008 coefficient
rows; every full row agrees with the reduced row for its D22 orbit.

For every parity-block orbit, the script also checks:

1. the representative stabilizer exactly;
2. every unordered Gram-entry orbit under that stabilizer;
3. every representative-to-member basis permutation;
4. independence from the chosen transporter; and
5. equality between the expanded full-block coefficients and the reduced
   coefficient map.

## Why the reduction is lossless

Let D22 act simultaneously on vertices, arc cuts, multiplier monomials, target
monomials, and parity Gram blocks.

- The 56-cut family is D22-closed.
- Averaging multiplier coefficients over D22 preserves coefficientwise
  nonnegativity and the normalization identity.
- Averaging the block-diagonal Gram matrix preserves positive
  semidefiniteness and the polynomial identity.
- An invariant multiplier array is exactly a function on the 2611 pair
  orbits.
- An invariant Gram family is exactly one representative block per
  parity-block orbit, invariant under the representative stabilizer; all other
  blocks are permutation conjugates.
- The coefficient residual of invariant data is invariant.  Therefore one
  equation per degree-4 or degree-6 monomial orbit is necessary and sufficient.

Thus no feasible unrestricted certificate is lost by the D22 averaging, and
every reduced feasible point expands to a full Q4-layout certificate.

## Numerical export audit

The independently expanded numerical object gives:

```text
normalization max residual  = 2.072713526502e-05
identity max residual       = 3.453911683593e-05
minimum Gram eigenvalue     = -6.538181630119e-07
maximum Gram eigenvalue     =  6.510176663940e+02
blocks with lambda_min<-1e-8 = 144 / 848
maximum symmetry error      = 0
maximum D22 nu-copy error   = 0
maximum D22 Q-copy error    = 0
```

The zero copy errors show that the export permutation is correct.  The
residuals and negative eigenvalues show that the object remains numerical
steering data only.

## Exact induced-C5 face

There are 33 induced C5 supports in three D22 orbits.  For such a support
`U`, set `x=1_U`.  Every arc cut has
`q_S(1_U) in {1,3,5}`, while the arc minimum is 1.

For an exact certificate at `c=25`,

```text
sum_S nu_S(1_U) = 25 * 5^4 = 5^6
T(1_U) = 5^6 - sum_S nu_S(1_U) q_S(1_U) >= 0.
```

Since every multiplier is nonnegative and every `q_S(1_U)>=1`, the reverse
inequality also holds.  Hence equality is forced, and

```text
sum_S nu_S(1_U) (q_S(1_U)-1) = 0.
```

Consequently, if `q_S(1_U)>1`, then `nu_S(1_U)=0`.  Coefficientwise
nonnegativity then forces every coefficient of `nu_S` whose monomial is
supported inside `U` to vanish.  Over all 33 supports this yields:

```text
forced coefficient occurrences = 72380
forced distinct full coefficients = 24563
forced D22 multiplier orbits = 1147 / 2611
```

The largest supposedly forced-zero value in the numerical export is
`5.553442204604e-06`.

The same equality forces every PSD Gram block to kill its C5 evaluation
vector.  Among the 528 nonzero full-block vectors, transport to representative
blocks gives 74 distinct vectors, or 30 orbits after quotienting by the
representative stabilizers.  In the parity-zero 286-by-286 block, the 33 C5
evaluation vectors have exact rank 33 modulo the prime 1000003; full modular
row rank proves rank 33 over the rationals.  Therefore any exact central block
has nullity at least 33.

The numerical export misses this face:

```text
max entry over all 528 products Q_b v_U = 1.237495243155e-02
max absolute block energy             = 1.097549950163e-03
central max entry of Q0 K^T           = 9.797149744156e-03
central matrix infinity norm of Q0 K^T = 1.211303995512e-01
```

The last two figures use different norms, not different normalizations.
`9.797e-3` is the largest entry in the central `286 x 33` product.
`1.211e-1` is NumPy's matrix infinity norm, the maximum row sum across all 33
columns.  The `1.237e-2` figure is the largest entry after extending the check
from the central block to all 528 nonzero block/vector pairs.  All three use
the unscaled indicator `y=1_U`.

## Build-only audit of the exact-face scaffold

`CODEX_R10_g11_d22_face.py` was audited without launching a solve.  Its F1
list agrees exactly with the independently reconstructed 1147 multiplier
orbits.  Its transported F2 spans have the following exact ranks:

```text
block order 286: 33
five block representatives of order 66: total 30
twenty block representatives of order 11: total 11
scalar representatives: 0
total: 74
```

The complement-order total is 788.  Thirteen representative blocks receive
nontrivial kernel equations, and 26 non-scalar blocks receive the common-margin
PSD constraint.

For every one of the 52 representative blocks, the audit checks in exact
rational arithmetic that the stored projector is

```text
P = I - K^T (K K^T)^(-1) K,
```

is symmetric, annihilates the exact RREF kernel basis and every independently
transported C5 vector, and has trace `order-rank`.  Thus `P^2=P` follows
exactly from `(K K^T)^(-1)(K K^T)=I`; this is not a floating eigenvalue test.

The scaffold adds no hidden constraint: its constraint count is exactly the
base model plus one F1 vector equality, 13 F2 matrix equalities, and 26 margin
PSD inequalities.  F1 and F2 are necessary for every exact `c=25`
certificate.  The margin device is feasibility-lossless because any
face-feasible base point extends with `margin=0`; the base model already
requires every representative Gram block to be PSD.

Therefore one solve of this fixed face model is safe to launch as a numerical

## Exact status and next admissible step

No exact rational primal certificate and no exact separating dual has been
produced.  The structural reduction passes; the raw numerical point does not.
Any next construction should impose the 1147 forced multiplier-orbit zeros and
the 30 stabilizer-inequivalent Gram kernel-vector constraints before
reconstruction.  Acceptance still requires rational data, exact coefficient
identities, and exact PSD verification by an independent gate.

## Replay

From `E:\Projects\ErdosProblems`:

```text
python .\problems\23\round10\CODEX_R10_d22_AUDIT.py
```

Expected final marker:

```text
NUMERICAL_EXPORT_AUDIT_ONLY: exact rational reconstruction still required
AUDIT_PASS
```

## SHA-256

```text
AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE  CODEX_R10_g11_d22_sdp.py
BCE4332520667F6B23D404191413C520598F8DDF5C911CA162D7E015E068EDDF  CODEX_R10_g11_d22_numeric.pkl
7AA3FA1DD8F3A68D0827DCA2F6D1C001F5C2626616BAD0E85AC9F85FE9BA63FE  CODEX_R10_d22_AUDIT.py
```
