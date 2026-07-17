# R9 Gate-T dispersion audit

## Verdict

The fixed-`L` Gate T is neither proved nor refuted.  The response does contain
a correct unconditional asymptotic lemma after restoring the orientation of
fractions lost by the browser's rendered-text extraction.  It proves that a
positive fraction of labelled edges cannot be concentrated on fewer than
`60^((1-delta)K)` product values.  It does not prevent exponentially many
fibres of multiplicity greater than every fixed `L`.

## Correct statement

Use the notation of `R9_gateT_dispersion_prompt.md`, and put

```text
iota_K = |I_K|.
```

For every `K>=2` and every product value `z`,

```text
r_K(z) <= tau(z / (2^v_2(z) 3^v_3(z))).                 (R9.1)
```

For every fixed real `delta` with `0<delta<1`, there is a finite constant
`A_delta` such that every set `Z_K` of product values with

```text
|Z_K| <= 60^((1-delta)K)
```

satisfies

```text
(1/N_K) sum_{z in Z_K} r_K(z)
    <= (4 A_delta / iota_K) 60^(-delta K/2).             (R9.2)
```

In particular the left side tends to zero.  The necessary lower bound is

```text
N_K >= (iota_K/4) 60^K.                                  (R9.3)
```

The extracted raw text interchanges displayed numerators and denominators in
several MathJax fractions.  Formulas (R9.2)-(R9.3) are the normalization
forced by the proof and by direct recomputation.

## Proof audit

### 1. Factor ranges and colors

Every offset in `D_k` lies in `[0,Q^k)`: if `0<=d<M`, applying the map with
multiplier `m` gives `md+(m-2)<mM`.  Hence the two possible `U_i` ranges are
contained in `(16Q^i,18Q^i)` and `(32Q^i,36Q^i)`, while
`V_j` is contained in `(24Q^j,27Q^j)`.  Equal products therefore have the
same `U` color because the corresponding product intervals
`(384Q^K,486Q^K)` and `(768Q^K,972Q^K)` are disjoint.

For a selected offset `d`, the corresponding `u` is odd and divisible by
three.  Every `v` is two modulo three.  Thus all powers of two in `z=uv`
come from `v`, and all powers of three come from `u`.

### 2. Label-preserving divisor injection

The intervals `(16Q^i,36Q^i)` are disjoint as `i` varies.  A divisor `u` of
`z` therefore determines the scale label `i`, then the offset `d`, then
`v=z/u`, and finally the other offset.  The map

```text
u -> u / 3^v_3(z)
```

injects the full labelled fibre over `z` into the divisors of
`z/(2^v_2(z)3^v_3(z))`.  This proves (R9.1), including the scale labels.

### 3. Uniform subexponential fibre bound

For every `theta>0` there is a finite `C_theta` with
`tau(n)<=C_theta n^theta`.  For primes with `p^theta>=2`, use
`nu+1<=2^nu<=p^(theta nu)`.  Only finitely many smaller primes remain, and
the maximum of `(nu+1)p^(-theta nu)` is finite for each.  Since all products
are below `972Q^K`,

```text
r_K(z) <= C_theta 972^theta Q^(theta K).                 (R9.4)
```

### 4. Exact 60-block code

The 60 permutations of the multiset `(2,2,2,3,3,5)` have 60 distinct
offsets in `[0,Q)`.  Concatenating `k` such blocks gives unique base-`Q`
offsets, so `|D_k|>=60^k`.  Every word contains a `3`-map, hence its
corresponding `H_k` residue is zero or two modulo three.  The selected
majority class therefore has at least `60^k/2` elements.  Summing
`|C_i||C_{K-i}|` over `i in I_K` gives (R9.3).

### 5. Dispersion

Choose

```text
theta = delta log(60) / (2 log(Q)),
A_delta = C_theta 972^theta.
```

Then (R9.4) is at most `A_delta 60^(delta K/2)`.  A set of at most
`60^((1-delta)K)` products carries at most
`A_delta 60^((1-delta/2)K)` labelled edges.  Division by (R9.3) proves
(R9.2).

### 6. Polynomial transversality

For an edge template, write

```text
P(T) = (a Q^i T + x)(3 Q^j T + y),
x = ad+1, y = 3e+2.
```

Here `x` is odd and divisible by three, while `y` is two modulo three.
Two equal same-color polynomials have the same unordered pair of negative
roots.  Direct root matching forces `i=i'` by the two-adic valuation and
then identical offsets.  Crossed matching would force simultaneously
`j'>i` from the two-adic valuation and `i>j'` from the three-adic valuation,
which is impossible.  Thus distinct templates give distinct polynomials.
Their difference at common total scale is nonzero linear.  Consequently a
fixed collision template cannot be pumped through infinitely many distinct
common inner inputs.  This observation is correct but is not needed for
(R9.1)-(R9.2).

## Independent exact check

`R9_gateT_dispersion_verify.py` independently checks:

- the exact 60-offset list and its distinctness;
- base-`Q` injection for one, two, and three concatenated blocks;
- the two residue classes and majority bound;
- the exact formula for `iota_K` through `K=300`;
- the labelled divisor injection on the `K=3` block subsystem.

Normal and optimized Python runs are text-identical.  The verifier source
SHA-256 is

```text
C44A58C3D794B3BB1F70AD89A0E79D0597F27BAD0C9EF80D566B3EE5AAF9E773
```

and its canonical output SHA-256 is

```text
6645D34ABC5197488441A21A9186810FF3900F2570E48E819E442B75903C6B2E
```

## Exact remaining gap

R9 excludes bounded, polynomial, and sub-`60^K` concentration mechanisms.
It does not imply a fixed `L`.  A Gate-T counterexample may still distribute
almost all edges among exponentially many distinct fibres, each with
multiplicity greater than `L`.  Closing Gate T requires an anti-clustering
estimate in precisely that dispersed regime.
