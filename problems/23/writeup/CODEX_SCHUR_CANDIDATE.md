# Codex Schur Candidate for SPEC

This is a working note, not a proof.

Let `P[v,f]=p_f(v)`, `K=P P^T`, and `T=K 1`.  Put

```text
A = N I - K.
```

Then `A` is a symmetric Z-matrix: its off-diagonal entries are nonpositive.
The target `(SPEC)` is exactly `A >= 0`.

Partition the vertices by row-sum sign:

```text
O = {v : T(v) > N},       Q = V \ O.
```

For `q in Q`, the full row sum of `A` is `N-T(q) >= 0`.  Since
`A[q,o] = -K[q,o] <= 0`, the row sum inside the principal block is

```text
sum_{q' in Q} A[q,q'] = N - T(q) + sum_{o in O} K[q,o] >= 0.
```

Thus `A_QQ` is a symmetric diagonally dominant Z-matrix.  Each connected
component of `Q` with either positive internal row sum somewhere or a
connection to `O` is a nonsingular Stieltjes block.  Components with zero row
sum and no connection to `O` decouple from the Schur complement and can be
handled separately.

Assuming `A_QQ` is inverted on the non-decoupled part, define

```text
E = A_OO - A_OQ A_QQ^{-1} A_QO.
```

Schur complements of nonsingular Stieltjes matrices are again symmetric
Z-matrices, so `E` has nonpositive off-diagonal entries.  Therefore `E` is PSD
as soon as all its row sums are nonnegative.

The remaining lemma is:

```text
(Schur row-sum lemma)
For every overloaded vertex o in O,
sum_{o' in O} E[o,o'] >= 0.
```

Equivalently, let `g` be the solution on `Q`

```text
A_QQ g = N - T   (restricted to Q).
```

The M-matrix maximum principle gives `0 <= g <= 1`.  The Schur row-sum lemma
is equivalent to

```text
sum_{q in Q} K[o,q] g(q) >= T(o)-N       for every o in O.
```

Interpretation: underload in `Q` induces a harmonic potential `g`; every
overloaded vertex must see enough effective conductance into that potential
to pay its overload.

There is an equivalent boundary-potential form.  Put `phi(o)=1` for `o in O`
and `phi(q)=1-g(q)` for `q in Q`.  Then

```text
K phi = N phi       on Q,
K phi <= N phi      on O
```

is exactly the Schur row-sum lemma.  Thus the Schur certificate constructs a
positive `N`-superharmonic vector for the nonnegative matrix `K`.

## Finite-depth sublemma under test

Since

```text
g = (N I - K_QQ)^(-1) (N-T)_Q
  = sum_{t>=0} (K_QQ/N)^t (N-T)_Q / N,
```

the following stronger local inequality would imply the full Schur row-sum
lemma:

```text
g_2 := (N-T)_Q/N + K_QQ (N-T)_Q/N^2,

N - T(o) + sum_{q in Q} K[o,q] g_2(q) >= 0
for every overloaded o in O.
```

Named hard cases pass this exact `k=2` truncation.  An exact gate request is
posted to Claude before treating it as real.

Local numeric status:

```text
_codex_schur_rowsum_test.py --mode named
_codex_schur_rowsum_test.py --mode census --nmax 10
_codex_schur_rowsum_test.py --mode census --nmax 11 --stride 20
```

all had `bad_row=0` and `bad_eig=0`.  The exact-test request is posted to
`coordination/CODEX_TO_CLAUDE.md`.
