# C114: integrated Carleson gate

## DIRECT ROUTE

1. **Exact final deliverable.** Prove or exactly refute the existence of an
   absolute constant `C` such that, uniformly for integers `X>=2,D>=1`,
   \[
   \sum_{j\ge\lceil\sqrt D\rceil}{N_j(X,D)\over2^j}
   \le {C(1+\lfloor\log_2X\rfloor)\over\sqrt D}.       \tag{IC}
   \]
   Here `N_j(X,D)` counts distinct reducible C85 witness roots in bin `j`
   witnessed by a hard source `h<=X` with `d(h)>=D+1`.
2. **Current frontier lemma or finite certificate.** With
   `q_X(r)=max_h(d(h)-1)` over hard sources through `X` witnessed by `r`, prove
   an aggregate capped layer-cake estimate strong enough to bound `(IC)`, or
   give an exact scalable root-upgrade/source-incidence family for which the
   normalized left side is unbounded.
3. **Logical bridge.** For `J=ceil(sqrt(D))`, bins `j<J` have reciprocal mass
   at most `J/2`.  Thus `(IC)` gives
   \[
   {\Sigma_D(X)\over D}
   \le {J\over2D}+{C(1+\lfloor\log_2X\rfloor)\over D^{3/2}}.
   \]
   Taking `D=floor((log X)^c)` with `2/3<c<log 2` makes both terms `o(1)`;
   C99.3 absorbs low-pair sources and C99.5 absorbs structural roots, so C85
   equation (27) gives `H(X)=o(X)`.
4. **Next falsifiable action.** Reconstruct every root-upgrade event in a
   bounded exact prefix and test, with integer arithmetic, candidate
   layer-cake charges from each upgrade to source pairs and denominator slots;
   reject each bridge at its first event-level counterexample and retain only
   an inequality whose summed charge implies `(IC)`.
5. **Exit condition.** Stop with a proof of `(IC)`, an exact unbounded
   counterfamily, or a genuinely weaker proved inequality with the complete
   C99 exponent bridge.  Stop any branch whose incidence charge has an exact
   counterexample or whose summed estimate does not imply one of these three
   deliverables.

## Status

The uniform estimate `(IC)` is neither proved nor refuted.  A genuinely
weaker selected-square-layer inequality is proved sufficient for C99 below.
Its bridge uses only layer cake and monotonicity; it does not imply a
pointwise bin tail.

The direct source-local incidence route is dead.  Exact certificates refute
successively stronger attempts to pay root-upgrade layers by source witness
roots.  The last source-local count fails at `h=77,317,236`.  An aggregate
upgrade inequality survives through `10^9`, but has no summable cross-source
budget and is recorded only as a finite fact.

## 1. Exact square layer cake

For a reducible witness root `r`, put

\[
 q_X(r)=\max\bigl(\{d(h)-1:h\le X,\ h\text{ hard},\ r\sim h\}\cup\{0\}\bigr),
 \qquad j(r)=\lfloor\log_2(r-1)\rfloor.
\]

Define the integrated tail

\[
 T_D(X)=\sum_{j\ge\lceil\sqrt D\rceil}{N_j(X,D)\over2^j}.
 \tag{1}
\]

For integer `D>=1`, the condition `j>=ceil(sqrt(D))` is exactly `D<=j^2`.
Consequently

\[
 T_D(X)=\sum_r {1\over2^{j(r)}}
 1_{\{D\le\min(q_X(r),j(r)^2)\}}.                 \tag{2}
\]

In particular, `T_D(X)` is nonincreasing in `D`.

### Lemma C114.1 (exact interval layer cake)

For integers `0<=a<b`,

\[
 \sum_{D=a+1}^{b}T_D(X)
 =\sum_r {\bigl[\min\{q_X(r),j(r)^2,b\}-a\bigr]_+\over2^{j(r)}}.
 \tag{3}
\]

#### Proof

A fixed root contributes on the left for precisely the integers

\[
 a<D\le\min\{q_X(r),j(r)^2,b\}.
\]

Their number is the positive part on the right.  Summing over roots proves
(3).  This is an identity of finite rational numbers.  QED.

For `m>=1`, specialize (3) to the square block

\[
 B_m(X):=\sum_{D=m^2+1}^{(m+1)^2}T_D(X)
 =\sum_r {\bigl[\min\{q_X(r),j(r)^2,(m+1)^2\}-m^2\bigr]_+
              \over2^{j(r)}}.                       \tag{4}
\]

Monotonicity and the `2m+1` integers in this block give the exact bridge

\[
 (2m+1)T_{(m+1)^2}(X)\le B_m(X).                    \tag{5}
\]

## 2. Weaker sufficient inequality

### Theorem C114.2 (one selected square layer suffices)

Fix

\[
 {2\over3}<c<\log 2,
 \qquad m_X=\left\lfloor(\log X)^{c/2}\right\rfloor,
 \qquad D_X=(m_X+1)^2,                               \tag{6}
\]

where the logarithm in (6) is natural.  The single asymptotic inequality

\[
 \boxed{B_{m_X}(X)=o(m_X^3)}                         \tag{C114-SB}
\]

implies the residual-root estimate required in C99 equation (28), and hence
closes the C85+C99 contraction route.

#### Proof

Every witness root is even, so `r-1` is odd.  A bin `j>=1` contains at most
`2^(j-1)` possible denominators, and its reciprocal contribution is at most
`1/2`.  The bins below `m_X+1=ceil(sqrt(D_X))` therefore contribute at most
`(m_X+1)/2` to `Sigma_{D_X}(X)`.  Equations (1) and (5) give

\[
 {\Sigma_{D_X}(X)\over D_X}
 \le {1\over2(m_X+1)}
  +{B_{m_X}(X)\over(2m_X+1)(m_X+1)^2}=o(1).          \tag{7}
\]

Here `D_X=(log X)^{c+o(1)}`.  Choose fixed `c<c'<log 2`.  For all large
`X`, `D_X<=(log X)^{c'}`, so C99 Theorem C99.3 makes the sources with
`d(h)<=D_X` sparse.  C99 Proposition C99.5 gives

\[
 {W_E(X)\over D_X}
 =O\bigl((\log X)^{1/2-c+o(1)}\bigr)=o(1).           \tag{8}
\]

Substituting (7)-(8) in the thresholded form of C85 equation (27) gives
`H(X)=o(X)`.  The existing contraction then gives positive lower density.
QED.

`(C114-SB)` is genuinely weaker than `(IC)`.  Indeed, `(IC)` would give

\[
 B_{m_X}(X)
 \le C(1+\lfloor\log_2X\rfloor){2m_X+1\over m_X}
 =O(\log X)=o(m_X^3),                                \tag{9}
\]

where the last step is exactly `3c/2>1`.  Conversely, `(C114-SB)` controls
only one square block at each `X` and permits block mass of any order
`o(m_X^3)`, much larger than the `O(log X)` consequence of `(IC)`.  It need
not control any individual bin or any other threshold.

## 3. Source-incidence falsifiers

For a hard source `h`, let `A(h)` be the number of all distinct witness roots
and `M(h)` the number of reducible witness roots.  At a root-upgrade event let
`Delta q_r` and `Delta s_r` denote the increases of `q_X(r)` and
`ceil(sqrt(q_X(r)))`, respectively.

The following candidate charges are exactly false.

1. **New co-roots pay `Delta q`.**  At `h=5114`, root `86` increases from
   `q=1` to `q=3`, but the source adds only one previously unseen co-root.
2. **All source roots pay square-root increments.**  At `h=100554`,
   `A(h)=7`, while four upgraded roots have square-root increments
   `1,1,3,3`, totaling `8`.
3. **Historical co-roots pay the final height.**  At `h=672914`, the new
   reducible root `67292` has `q=3`, but its complete co-root union is only
   `{8,170}`.
4. **A source with a reducible root has `A(h)M(h)>=d(h)-1`.**  The first
   failure in the exact scan is

   \[
   h=77,317,236,\qquad h+1=23\cdot89\cdot107\cdot353. \tag{10}
   \]

   Its four pairs and selected missing endpoints are

| pair | missing endpoint | root | state |
|---|---:|---:|---|
| `(23,3361619)` | `23` | `12` | structural |
| `(89,868733)` | `89` | `12` | structural |
| `(107,722591)` | `107` | `54` | reducible hard |
| `(353,219029)` | `353` | `12` | structural |

Thus `d=4`, `A=2`, `M=1`, and `A M=2<3=d-1`.  All four pairs are blocked,
so (10) is an actual hard-source certificate, not an abstract hypergraph.

The eventwise inequality

\[
 \sum_{r\text{ upgraded at }h}\Delta q_r\le A(h)M(h)             \tag{11}
\]

has no failure through `10^9`.  This is finite evidence only.  It does not
imply (1): after summing (11), the same witness root can be charged at
arbitrarily many source events, and neither C85 nor a root-upgrade invariant
provides a uniform bound for that cross-source load.  The fixed-star
obstruction in C85 makes this omission load-bearing.

**DEAD: source-local incidence -- the surviving event budget has no
summable cross-source root-load bound, while every proposed distinct-root
label is exactly false.**

## 4. Exact finite verification

The independent Python implementation checks `(IC)` after every source that
changes at least one `q_X(r)`.  Through `X=10^6` it reports `45,583` hard
sources, `3,015` root upgrades, maximum `d=9`, and `19,773` eventwise
threshold tests.  There is no `C=1` failure.  Its largest eventwise squared
constant is

\[
 {11868363\over6710886400}
\]

at `X=999774,D=3`, where `T_D=1989/4096` and `L_X=20`.  Normal and
`python -O` outputs are byte-identical.

The C++ source-incidence scan exactly matches those three Python totals at
`10^6`.  At `10^8` its classification digest is
`94633c57cc653c6e`, exactly the pinned C104 digest.  Through `10^9` it scans
`29,010,146` hard sources and `403,428` root upgrades, with maximum `d=16`;
(11) has no failure.

Exact postprocessing of the C108 endpoint census at `X=3*10^9` verifies
(3)-(5), threshold monotonicity, and all square-block identities.  The
largest endpoint squared constant is

\[
 {42730031265752943\over18446744073709551616}          \tag{12}
\]

at `D=7`, with
`T_7=78129957/134217728`.  This reproduces the C110 value by a separate
postprocessor.  Normal and optimized outputs are byte-identical.  These are
finite facts and do not prove `(IC)` or `(C114-SB)`.

## 5. Reproduction

```powershell
python problems/424/compute/wave5/C114_integrated_probe.py `
  --limit 1000000 `
  --output problems/424/compute/wave5/C114_integrated_probe_1000000.json

g++ -std=c++23 -O3 -march=native -Wall -Wextra -Wpedantic `
  problems/424/compute/wave5/C114_source_incidence_scan.cpp `
  -o problems/424/compute/wave5/C114_source_incidence_scan.exe

problems/424/compute/wave5/C114_source_incidence_scan.exe `
  1000000000 `
  problems/424/compute/wave5/C114_source_incidence_scan_1000000000.json

python problems/424/compute/wave5/C114_layercake_verify.py `
  --input problems/424/compute/wave5/C108_weighted_token_gate_3000000000.json `
  --output problems/424/compute/wave5/C114_layercake_3000000000.json
```

The two replay hashes are

```text
EB4B0608D271C1C296E0E211290E8170E3A57EDD30836BCC44DA0D8AF543A9EC  C114_integrated_probe_1000000.json
51E9F90B6183A9B678DA79FEC45EE93141C6514BEDCA0A4D4A8BA2C6E9BC9A1A  C114_layercake_3000000000.json
```

**Verdict.**  The requested uniform Carleson bound remains open.  The direct
layer-cake output is `(C114-SB)`, a strictly weaker selected-scale condition
with the full C99 exponent bridge.  Source-local root incidence does not
prove it; the precise missing input is a summable cross-source upgrade-load
bound.
