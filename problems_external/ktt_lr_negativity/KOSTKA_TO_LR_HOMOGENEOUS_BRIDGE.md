# Dilation-Compatible Skew-Kostka-to-LR Bridge

Status: exact algebraic bridge proved; computational gate not yet run.

## Statement

Let `lambda/beta` be a skew shape and let

```text
w = (w_1,...,w_k),   W = w_1+...+w_k = |lambda|-|beta|,
```

with zero parts of `w` deleted. Put `s=ell(beta)` and define tail sums

```text
T_j = w_j+...+w_k  (1 <= j <= k),   T_(k+1)=0.
```

Define two partitions

```text
R = (W+beta_1,...,W+beta_s,T_1,T_2,...,T_k),
S = (W,...,W,T_2,T_3,...,T_k,0),
        s copies
```

where the final zero is omitted in partition notation. Then, for every
integer `n>=0`,

```text
K_(n lambda / n beta, n w) = c^(n R)_(n lambda, n S).       (1)
```

Consequently, a negative ordinary monomial coefficient in one stretched
skew-Kostka polynomial is an actual counterexample to full KTT.

## Proof

In row `i<=s`, the skew diagram `R/S` contains the interval of cells

```text
W+1,...,W+beta_i.
```

These rows form a translate of `beta`. In row `s+j`, the diagram contains

```text
T_(j+1)+1,...,T_j,
```

a single row of length `w_j`. The translated `beta` component and all of the
single-row components have disjoint row sets and disjoint column sets.
Therefore the skew Schur function factors as

```text
s_(R/S) = s_beta h_(w_1)...h_(w_k).                         (2)
```

Taking the coefficient of `s_lambda` and using the Hall inner product gives

```text
c^R_(lambda,S)
  = <s_lambda,s_(R/S)>
  = <s_lambda,s_beta h_(w_1)...h_(w_k)>
  = <s_(lambda/beta),h_(w_1)...h_(w_k)>
  = K_(lambda/beta,w).                                      (3)
```

The last equality is the iterated Pieri-chain description of semistandard
tableaux: the successive differences are horizontal strips of sizes
`w_1,...,w_k`.

The construction is homogeneous. Replacing `(lambda,beta,w)` by
`(n lambda,n beta,n w)` replaces `W` and every `T_j` by `nW` and `nT_j`,
hence replaces `(R,S)` by `(nR,nS)`. Applying (3) after this replacement proves
(1).

## Exact counterexample certificate

A candidate is accepted only if all of the following hold.

1. The skew-Kostka polynomial is reconstructed over `Q` from exact counts
   through a certified degree and has a negative ordinary monomial
   coefficient.
2. At least two additional dilations, not used for interpolation, match the
   polynomial.
3. Formula (1) is checked at every interpolation and held-out dilation by an
   independent LR counter.
4. A second implementation independently reconstructs the same polynomial.
5. The displayed partitions satisfy the size and dominance conventions of
   an LR triple, and the base coefficient is nonzero.

## DIRECT ROUTE -- BOUNDED KOSTKA FALSIFICATION GATE

### 1. Exact final deliverable

One certified negative stretched skew-Kostka polynomial, converted by (1) to
an explicit LR triple and independently replayed as a full KTT counterexample.

### 2. Current frontier

Determine whether a weight-sliced Gelfand--Tsetlin polytope can have a
negative Ehrhart coefficient. The 2026 `kostka` implementation is useful only
after zero-trust validation: one README example reports an alleged Ehrhart
polynomial with constant term different from one, so its dimension/interpolation
path cannot presently be treated as a certificate.

### 3. Logical bridge

Equation (1) is dilation-compatible and converts the entire stretching
polynomial, not just its value at `n=1`. Thus any verified negative coefficient
is literally a KTT counterexample.

### 4. Next falsifiable action

Pin and build the public `kostka` source. First audit its degree and Ehrhart
commands against exact small cases and the invariant `P(0)=1`. Then run one
bounded gate consisting of:

```text
all nonempty skew instances with |lambda|<=12,
ell(lambda)<=6, ell(w)<=6, K_(lambda/beta,w)>0,
followed by 50,000 deterministic adversarial instances with
|lambda|<=40, ell(lambda)<=8, ell(w)<=8.
```

Weights may be sorted because the unflagged Kostka number is invariant under
permuting their parts. Every screened polynomial must use a certified degree
or stabilization plus two held-out exact values. Any negative candidate is
immediately sent through the five-point certificate contract above.

### 5. Exit condition

If the exact bounded gate has no negative coefficient and exposes no finite
structural family forcing negativity, record

```text
DEAD: bounded Kostka falsification exhausted -- no theorem-closing bridge.
```

Do not enlarge the bound or start a cascade of additional Kostka censuses.
Return to the rank-uniform GHTE/theorem route. A null result is not evidence
for full KTT.
