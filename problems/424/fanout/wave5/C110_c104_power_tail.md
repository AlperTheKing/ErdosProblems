# C110: weaker residual-root power tail

## DIRECT ROUTE

1. **Exact final deliverable.** Prove or falsify that there are absolute
   constants `C<infinity`, `alpha>1/log(2)-1`, and a function
   `J(D)=o(D)` such that, uniformly in integers `X>=2`, `D>=1`, and
   `j>=J(D)`,
   \[
   |\{r\in\mathcal R_{X,D}:2^j\le r-1<2^{j+1}\}|
   \le C\,2^j/D^\alpha. \tag{PT}
   \]
   A proof with `alpha=1/2` is sufficient.
2. **Current frontier lemma or finite certificate.** Establish a uniform
   square-root saving in `D` for distinct reducible roots in each bin above
   the moving cutoff `J(D)`, using the source-root incidence hypergraph and
   allowing every fixed root to have unbounded source load.
3. **Logical bridge.** Every dyadic bin has reciprocal root mass `O(1)` by
   cardinality alone, so bins `j<J(D)` contribute `O(J(D))`.  Above the
   cutoff, `(PT)` contributes `O((1+log X)/D^alpha)`.  Hence
   \[
   {\Sigma_D(X)\over D}
   =O\left({J(D)\over D}+{1+\log X\over D^{\alpha+1}}\right). \tag{B}
   \]
   With `D=floor((log X)^c)`, `J(D)=o(D)` kills the first term.  C99 absorbs
   low-pair sources for every fixed `c<log 2`, while the second term is
   `o(1)` whenever `c(alpha+1)>1`.  Thus
   `alpha>1/log(2)-1` closes C99, and `alpha=1/2` permits any fixed
   `2/3<c<log 2`.
4. **Next falsifiable action.** Derive candidate source-root incidence and
   divisor-injection inequalities for one dyadic bin, then exactly enumerate
   every incidence through a bounded prefix and compare both sides at every
   source event above candidate cutoffs `J(D)`; reject an inequality at its
   first exact counterexample.  Fixed-bin load growth is not a falsifier.
5. **Exit condition.** Exit with a proof of `(PT)`, an exact unbounded
   counterfamily or structural falsifier to `(PT)`, or a strictly weaker
   sufficient lemma together with an explicit exponent gate that still
   implies C99.  Stop a branch immediately if it only adds a bounded census
   or lacks this bridge.

## Status

The moving-cutoff reduction is proved below.  The requested power tail is
neither proved nor falsified.  A strictly weaker integrated Carleson tail is
isolated, with an exact rational gate.  The most direct source-level
square-root injection is exactly false at `h=1154`.

## 1. Moving-cutoff reduction

Write

\[
 N_j(X,D)=|\{r\in\mathcal R_{X,D}:2^j\le r-1<2^{j+1}\}|,
 \qquad L_X=1+\lfloor\log_2X\rfloor.
\]

Every witness root is even: a missing endpoint `p` is odd and

\[
 r=1+{p-1\over2^{v_2(p-1)}}
\]

is one plus an odd number.  Therefore `r-1` is odd.  For `j>=1`, its dyadic
bin contains exactly `2^(j-1)` possible odd denominators.  Consequently,
for every root subset,

\[
 \sum_{2^j\le r-1<2^{j+1}}{1\over r-1}
 \le {N_j(X,D)\over2^j}\le {1\over2}.       \tag{1}
\]

Also `r-1<=p-1<=h<=X`, so there are at most `L_X` relevant bins.

### Theorem C110.1 (moving-cutoff power tail is sufficient)

Suppose there are constants `C<infinity` and
`alpha>1/log(2)-1`, and a function `J(D)=o(D)`, such that

\[
 N_j(X,D)\le {C2^j\over D^\alpha}             \tag{2}
\]

uniformly for `j>=J(D)`.  Then the residual-root term in C99 is `o(X)`, so
the C85+C99 route closes.

#### Proof

Equations (1)-(2) give

\[
 \Sigma_D(X)\le {J(D)\over2}+{CL_X\over D^\alpha}. \tag{3}
\]

Choose a fixed `c` with

\[
 \max\left\{{1\over2},{1\over\alpha+1}\right\}<c<\log2. \tag{4}
\]

Such a `c` exists exactly under the stated lower bound on `alpha`.  Put
`D=floor((log X)^c)`.  C99 gives `B_D(X)=o(X)`, and C99 Proposition 5 absorbs
the structural bank because `c>1/2`.  After the further C85 factor `1/(D+1)`,
the two terms in (3) are

\[
 {J(D)\over D}=o(1),\qquad
 {L_X\over D^{\alpha+1}}
 =O((\log X)^{1-c(\alpha+1)})=o(1).           \tag{5}
\]

Substitution in C99 equation (23) or (27) proves the claim.  Notice that no
fixed-root load is bounded or assumed bounded.  QED.

For `alpha=1/2`, one may take

\[
 J(D)=\lceil\sqrt D\rceil,
 \qquad {2\over3}<c<\log2.                    \tag{6}
\]

## 2. A strictly weaker sufficient lemma

The pointwise bound (2) is stronger than needed.  Define the dyadic
Carleson upper mass

\[
 \mathcal C_{X,D,J}
 =\sum_{j\ge J(D)}{N_j(X,D)\over2^j}.          \tag{7}
\]

### Lemma C110.2 (integrated moving tail)

The conclusion of Theorem C110.1 remains true if (2) is replaced by

\[
 \mathcal C_{X,D,J}\le {CL_X\over D^\alpha}   \tag{C110-CAR}
\]

for the same parameter range.

#### Proof

The actual reciprocal contribution of a tail bin is at most
`N_j(X,D)/2^j`.  Thus (1) and (7) give

\[
 \Sigma_D(X)\le J(D)/2+\mathcal C_{X,D,J}.
\]

Equations (4)-(5) apply unchanged.  QED.

This is strictly weaker as a counting inequality: it permits excess in one
bin to be paid for by unused mass in other bins.  For example, take
`D=L^2`, `J(D)=L`, one bin `j=L` with `N_j=2^(j-1)`, and all other counts
zero.  Its integrated left side is `1/2`, while the pointwise square-root
ratio is `L/2` and is unbounded.  The profile also respects the parity
cardinality ceiling in (1).

### Exact square-root gate

For the concrete choice (6) and `C=1`, `(C110-CAR)` is equivalent to the
entirely rational inequality

\[
 \boxed{
 D\left(\sum_{j\ge\lceil\sqrt D\rceil}
 {N_j(X,D)\over2^j}\right)^2\le L_X^2.}       \tag{C110-GATE}
\]

There is no floating-point acceptance and no irrational comparison:
`ceil(sqrt(D))` is computed by integer square root, and clearing the largest
power-of-two denominator makes `(C110-GATE)` an integer inequality.  A proof
of this gate for all `X,D` is a strictly weaker sufficient target than the
requested pointwise square-root tail.

## 3. Source-hypergraph obstruction

A natural attempted proof was to let `m(h)` be the number of distinct
reducible witness roots of a hard source and claim

\[
 m(h)^2\ge d(h)-1.                              \tag{8}
\]

This would make each source expose square-root-many reducible roots.  It is
false at

\[
 h=1154,\qquad h+1=1155=3\cdot5\cdot7\cdot11.
\]

The four admissible pairs and one selected missing endpoint from each are

| pair | missing endpoint | root | root type |
|---|---:|---:|---|
| `(5,231)` | `231` | `116` | reducible |
| `(11,105)` | `11` | `6` | structural splitless |
| `(15,77)` | `15` | `8` | structural splitless |
| `(33,35)` | `35` | `18` | structural splitless |

The opposite endpoint in every row is generated.  Hence `h` is hard,
`d(h)=4`, and its only reducible witness root is `116`; therefore
`m(h)^2=1<3=d(h)-1`.  The same source is the first failure when (8) is tested
only at root-upgrade events.  This kills the direct local square-root
injection; structural and reducible roots must be pooled together or the
argument must be genuinely global.

The weaker mixed diagnostic

\[
 (\#\hbox{ all witness roots})m(h)\ge d(h)-1       \tag{9}
\]

had no failure through `10^6`, but no proof is claimed and it is not by
itself sufficient for `(C110-GATE)`.

## 4. Exact finite gates

The current C108 weighted-token implementation was compiled without source
changes to the owned executable `C110_weighted_gate.exe` and run through
`X=10^8`.  It reconstructs the complete closure and stores

\[
 q_X(r)=\max\{d(h)-1:h\le X\text{ hard and }r\text{ witnesses }h\}.
\]

Its classification digest is `94633c57cc653c6e`, exactly the C104 digest.
The event-monotone deadline test

\[
 \sum_{\substack{s\le r\\2^j\le s-1<2^{j+1}}}
 \min\{\lceil\sqrt{q_X(s)}\rceil,j\}
 \le r-2^j                                      \tag{10}
\]

has no failure.  Because every weight only increases with `X`, an endpoint
pass is also an every-event pass.  The largest full-bin square-root load is
`38/128=19/64`, in bin `j=7`.  Equation (10) would imply the requested
moving square-root tail with `J(D)=ceil(sqrt(D))`, but it remains an unproved
stronger gate.

The exact postprocessor checks `(C110-GATE)` and the pointwise square ratio.

| `X` | tested `D` | largest pointwise square ratio | largest integrated square ratio |
|---:|---:|---:|---:|
| `10^8` | `1..11` | `847/16384` | `110909714393023/51298814505517056` |
| `3*10^9` | `1..17` | `275/4096` | `42730031265752943/18446744073709551616` |

The `10^8` row is a fresh C110 reconstruction.  The `3*10^9` row is exact
postprocessing of a refreshed C108 integer reconstruction, not an independent
implementation.  At `3*10^9`, the two deadline fields in (10) are also null.
Normal and `python -O` postprocessing outputs are byte-identical.

A separate C110 C++ implementation tests, at every root-upgrade event, the
stronger integrated inequality

\[
 D\sum_j{N_j(X,D)\over2^j}\le L_X.             \tag{11}
\]

It finds no failure through `X=2*10^9` for every nonempty threshold
`1<=D<=15`; `maximum d(h)=16`.  Equation (11) implies `(C110-GATE)` because
`1/D<=1/sqrt(D)`.  The same run also finds no failure of the still stronger
version with `L_X` replaced by the number of occupied bins.  An independently
written Python verifier exactly matches classification, threshold loads,
blocker profiles, and all first-failure fields through `300000`.  These are
finite facts only.

A targeted 64-bit plus-prime lift search also tested five fixed-root source
bases of pair count `12` or `16` against `4781` to `4784` eligible primes per
base through prime `100000`.  It found no hard fixed-root lift and hence no
C104-BIN falsifier.  This search is not used in the bridge: moving cutoffs
allow fixed-root loads to be unbounded.

The independent Python source-hypergraph probe exactly matches all C104
totals at `X=300000`.  Normal and optimized runs are byte-identical at both
`300000` and `10^6`; at `10^6` it checks all `45583` hard sources and all
root-upgrade events, with maximum `d(h)=9`.

## 5. Reproduction and status

```powershell
g++ -std=c++23 -O3 -march=native -Wall -Wextra -Wpedantic `
  problems/424/compute/wave5/C108_weighted_token_gate.cpp `
  -o problems/424/compute/wave5/C110_weighted_gate.exe

problems/424/compute/wave5/C110_weighted_gate.exe 100000000 `
  problems/424/compute/wave5/C110_weighted_gate_100000000.json

python problems/424/compute/wave5/C110_tail_postprocess.py `
  problems/424/compute/wave5/C110_weighted_gate_100000000.json `
  problems/424/compute/wave5/C110_tail_audit_100000000.json

python problems/424/compute/wave5/C110_source_hypergraph_probe.py `
  --limit 300000 `
  --reference problems/424/compute/wave5/C104_reducible_root_census_300000.raw.json `
  --output problems/424/compute/wave5/C110_source_hypergraph_300000.json
```

The dependency `C108_weighted_token_gate.cpp` has SHA-256
`0A93FDF9680FF2168BA81B5AA16F4E2BC94C3205D95E824E57122FC72B311C12`.
Hashes of all owned artifacts are pinned in `C110_SHA256SUMS.txt`.

**Verdict.** The moving cutoff fully removes fixed-root load as a logical
obstruction.  Neither the moving pointwise tail nor `(C110-CAR)` is proved or
falsified.  `(C110-GATE)` is the strictly weaker sufficient frontier; the
local reducible-neighborhood route to it is dead by the exact `h=1154`
certificate.
