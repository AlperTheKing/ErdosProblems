# General KTT Proof Workflow — Direct Route Registry V7

Selected: 2026-07-22

Status: DEAD. V6 is the symmetric specialization `r1=r2=r3`; the exact
all-parameter formula below proves that the V7 linear coefficient is positive.

Language: English for internal plans, prompts, code, checkers, and artifacts.
User-facing discussion may be Turkish.

## Exact target

Prove full KTT in every rank, or produce one exact stretched LR polynomial
with a negative ordinary monomial coefficient and two independent replays.

## DIRECT ROUTE — ARBITRARY THREE-ROW UNIT-COLUMN TRANSPORTATION FAMILY

### 1. Exact final deliverable

For positive integers `r1,r2,r3`, put `N=r1+r2+r3`. For every
`1<=k<N`, let `T_(r,k)` be the full `3 x (k+1)` transportation polytope with

```text
row margins    (r1,r2,r3),
column margins (N-k,1^k).
```

Find a member with a negative linear Ehrhart coefficient and transfer it
homogeneously to one LR triple, or prove that the linear coefficient is
strictly positive throughout this entire all-parameter family.

### 2. Current frontier lemma

Define

```text
F_k(x) = (1/2) sum_(t=1)^(k-x) t/(x+t)   if x<k,
         0                                 if x>=k.
```

The load-bearing claim is the exact identity

```text
[n]L_(r,k)(n)
 = 3k/2 - sum_i F_k(r_i) - sum_(i<j) F_k(r_i+r_j).          (1)
```

Its single-cap terms follow from the one-variable bounded-composition
generating function. The remaining frontier is a rigorous derivation of the
pair term

```text
[n]C_ij(n) = -F_k(r_i+r_j),
```

including the small-dilation coefficient-extraction convention. Once (1) is
proved, prove its sign without a parameter census.

### 3. Explicit logical bridge

Projection to the `k` unit columns identifies `L_(r,k)(n)` with the number of
`k` weak three-part compositions of `n` whose aggregate row sums are at most
`n r_i`. Inclusion-exclusion has only single and pair violations because a
triple violation is impossible when `N>k`; therefore the cap formulas imply
(1).

Set

```text
A=(N,r2+r3,r3),       B=(r2+r3,r3),
w=(N-k,1^k),
R=(N+r2+r3,N+r3,N,k,k-1,...,1),
S=(N,N,k,k-1,...,1).
```

The rows of `A/B` occupy disjoint column intervals, so their multiplicity
matrices are exactly the transportation tables. The homogeneous
skew-Kostka-to-LR bridge then gives, for every `n>=0`,

```text
L_(r,k)(n)=K_(nA/nB,nw)=c^(nR)_(nA,nS).                    (2)
```

Thus a negative value in (1) is literally a KTT counterexample. A proof that
(1) is positive eliminates this entire counterexample mechanism but does not
prove full KTT.

### 4. Next falsifiable action

Derive the pair term directly from its exact bivariate rational generating
function, validate (1) by raw dynamic programming, exact interpolation, and
two held-out dilations on asymmetric cases, and obtain an independent hostile
derivation of both (1) and (2). Then prove or refute the sign of (1) for all
positive row margins. Do not launch an open-ended margin sweep.

### 5. Exit condition

Success:

```text
one parameter tuple with [n]L_(r,k)<0, followed by an exact transportation,
skew-Kostka, and two-engine LR certificate through two held-out dilations.
```

Failure:

```text
DEAD: every arbitrary-row one-large-plus-unit-column 3-row transportation
family has positive linear coefficient -- <exact formula and sign proof>.
```

If the pair formula fails, stop this route unless the same finite generating
function supplies a corrected theorem-closing formula. V7 is the terminal
unit-column transportation generalization; do not replace it by a cascade of
larger bounded transportation families.

## Scope guard

This is one all-parameter theorem problem with an exact LR bridge, not a
finite null search. The bounded skew-Kostka gate remains independent. GHTE
remains an open sufficient theorem. Full KTT remains open unless an actual LR
counterexample or a rank-uniform proof for all hives is produced.

## Resolution

The frontier identity is correct, and the correction terms satisfy the
uniform integral bound

```text
[n]L_(r,k)(n)
 = 3k/2 - sum_i F_k(r_i) - sum_(i<j) F_k(r_i+r_j)
 >= 3/2 > 0.
```

Equality holds exactly when `k=1`. A direct exact DP reconstructed 185
asymmetric polynomials and checked 370 held-out dilations; an independent
coefficient-chamber audit includes `P<Q`, `P=Q`, and `Q<P` and proves the
terminating Dixon limit. The homogeneous all-`n` skew-Kostka-to-LR bridge was
also independently replayed, including `n=0`.

Canonical artifacts are
`ARBITRARY_ROW_UNIT_TRANSPORT_LINEAR_HOSTILE_AUDIT.md` and
`V7_FULL_UNIT_COLUMN_ZERO_TRUST_AUDIT.md`. Therefore the registered exit is

```text
DEAD: every arbitrary-row one-large-plus-unit-column three-row
transportation family has positive linear coefficient.
```

This proves no statement about its higher coefficients or general KTT.
