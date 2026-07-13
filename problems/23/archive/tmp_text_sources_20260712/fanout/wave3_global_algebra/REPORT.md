# Wave 3 global algebra: characteristic-two locality obstruction

## Scope

This report makes exactly one mathematical claim.  It tests the literal
transfer of the local `F_2^3` duality step in OpenAI's CDC proof to the
`t = 5` balanced-deficiency wall.  In the CDC argument, equation (4) is an
affine system over characteristic two; annihilators are localized at vertices,
and equation (9) turns every local contribution into a support-parity bit that
cancels because each edge has two endpoints.  The source is
<https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_proof.pdf>.

The candidate analogue here is the most local one available: one vector column
per selected bad atom, supported on the four complete-support edges in its
chosen length-four blue row.  Edge labels may be changed globally and atom
columns may be gauged, exactly the freedom that does not alter local support.

## The single result

**Characteristic-two local-incidence obstruction.**  Let `K` be any field of
characteristic two.  Let `E` and `A` be finite sets with `|E| = 24` and
`|A| = 25`.  For each `a in A`, let `P_a subset E` have exactly four elements.
For arbitrary nonzero scalars

```text
r_e in K^x  (e in E),       c_a in K^x  (a in A),
```

form the edge-local matrix

```text
             { r_e c_a,  e in P_a,
M[e,a] :=   {
             { 0,        e notin P_a.
```

Then

```text
rank_K(M) <= 23,        dim_K ker(M) >= 2.
```

Consequently, if the complete support family of the same 25 atoms is a
`25/24` transversal-matroid circuit (equivalently, deleting any atom leaves an
SDR onto all 24 support edges), no matrix of the displayed CDC-local form can
represent that circuit over any characteristic-two field.

### Proof

Define the nonzero row vector `y` by `y_e = r_e^(-1)`.  For every atom `a`,

```text
(y^T M)_a = sum_{e in P_a} r_e^(-1) r_e c_a
            = |P_a| c_a
            = 4 c_a
            = 0                     in char(K) = 2.
```

Thus `y` is a nonzero left annihilator.  Since there are 24 rows,
`rank_K(M) <= 23`; with 25 columns, rank-nullity gives
`dim_K ker(M) >= 2`.

On the other hand, a deletion SDR onto all 24 resources proves transversal
rank at least 24, while the ground resource set gives rank at most 24.  Hence
the 25-atom restriction has rank exactly 24.  In any linear representation it
would therefore have a one-dimensional dependency space; minimality also
forces every coefficient in its unique dependency to be nonzero.  The matrix
`M` has nullity at least two, so it is not such a representation.  This proves
the claim.

The argument permits every characteristic-two extension field and every
nonzero global edge rescaling/atom gauge.  It is not merely the observation
that the unweighted binary matrix happens to be singular.

## Finite exact gate on the accepted live-x fixture

The accepted support-level fixture at
`tmp/fanout/r42_graph_specific_exclusion/t5_live_x_classifier_v_l9_r9_5000.json`
has raw-file SHA-256
`0d5cee8baa9349f9c9bd31a47e951e6c99a1fe9fdaaa3560e4e6c337f0be1399`
and canonical payload SHA-256
`6595501f532577c3475d29e2a3c7e9f318debecd5e1014d0793e1b462d07494f`.
Its graph6 string is `Q??????wE_Bws?s?DCD??@?@???`.

I also tested the less local rescue in which a column is the unweighted union
of *all* complete shortest rows for that atom.  Let `N` be that `24 x 25`
integer footprint matrix.  Exact Kuhn matching gives size 24 after each of the
25 possible atom deletions, so its transversal rank is 24.  Exact elimination
instead gives

```text
rank_Q(N) = 20,
rank_F2(N) = 18,  rank_F3(N) = 19,
rank_F5(N) = 20,  rank_F7(N) = 20.
```

For replay, use the following zero-based row and column orders:

```text
E = [(0,9),(0,10),(0,12),(0,13),(0,15),(1,9),(1,10),(1,12),
     (1,13),(1,17),(2,9),(2,14),(2,15),(3,10),(3,11),(3,12),
     (3,13),(4,11),(4,14),(5,11),(5,16),(6,11),(7,11),(8,14)]

A = [(0,4),(0,5),(0,6),(0,7),(0,8),(1,4),(1,5),(1,6),(1,7),
     (1,8),(2,3),(2,5),(2,6),(2,7),(3,8),(9,11),(10,14),
     (10,16),(11,15),(12,14),(12,16),(13,14),(13,16),(14,17),
     (15,17)]
```

With bit `i` corresponding to `E[i]`, the 25 footprint columns are

```text
07fc1f 09e00e 21e00e 41e00e 801c11 07ede0 09e1c0 21e1c0 41e1c0
800c20 07fdff 0e0800 260800 460800 864000 07edef 067c73 186000
07f81e 06dcb5 18c000 075d39 194000 000e20 0017ff
```

The rational upper-rank certificate consists of these four independent row
relations (each equality is an equality of 25-entry rows of `N`):

```text
N_(0,10) - N_(0,12) - N_(1,10) + N_(1,12) = 0
N_(0,10) - N_(0,13) - N_(1,10) + N_(1,13) = 0
N_(0,15) - N_(2,15)                         = 0
N_(4,11) - N_(4,14)                         = 0
```

The matching lower-rank certificate is the `20 x 20` minor on row indices

```text
[0,1,2,3,4,5,6,9,10,11,13,14,15,16,17,19,20,21,22,23]
```

and column indices

```text
[0,1,2,3,4,5,6,10,11,14,15,16,17,18,19,20,21,22,23,24],
```

whose exact determinant is `-12`.  Thus `rank_Q(N) = 20`; since every
`21 x 21` minor is an integer that vanishes over `Q`, the rank is at most 20
over every field.  This exact fixture gate shows that replacing a chosen row by
the complete footprint does not repair the raw-incidence representation.

## Production consequence

The result applies immediately after
`CheckedBalancedDeficiencyRotor.circuit_cardinality` specializes to window
`t = 5`: there are 25 atoms and 24 complete-support edges, and every selected
row has four blue edges.  It blocks a proposed replacement of the R51 consumer
by a characteristic-two edge/atom incidence duality.  The failure occurs
before `FullBankRelaxedCoverCert`, physical-half exclusivity, typed bank
capacity, or the rational Farkas inequalities are introduced.

Therefore this result supplies no graph-derived FullBank provider and does
**not** bypass the `t = 5` catalogue.  A support-respecting finite-field
representation can escape the proved edge-local class by using
incidence-specific coefficients (generic weights depending jointly on atom and
support edge), but then the local edge-shared quantity whose two endpoint
occurrences drive the CDC handshake cancellation is gone.  The accepted
catalogue/extension gate remains the production route unless a new nonlocal
invariant controls those coefficients together with ordered bank capacities.

This is a representability/locality obstruction, not a reformulation of the
known Schur, fixed-Neumann, scalar-Hall, SOS, or rational finite-Farkas routes.
