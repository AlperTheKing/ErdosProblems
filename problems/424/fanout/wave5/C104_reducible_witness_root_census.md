# C104: exact census of non-splitless witness-root unions

## Verdict

The non-splitless (reducible) C85 witness-root union was censused exactly at
geometric cutoffs through

\[
X=10^8.
\]

At the endpoint, the all-hard reducible union has `61,479` roots and

\[
 {32493290934487096\over2^{56}}
 \le \sum_{r\in\mathcal R_X,\ r\ {m reducible}}{1\over r-1}
 \le {32493290934548575\over2^{56}}.
\]

For the threshold-dependent union

\[
 \mathcal R_{X,D}=
 \bigcup_{\substack{h\le X\ h\ {m hard}\ d(h)\ge D+1}}
 \{r:r\text{ is a non-splitless C85 witness root of }h\},
\]

the endpoint data are:

| `c` | exact `D=floor((ln X)^c)` | hard sources | roots | exact interval for `Sigma_D` | exact interval for `Sigma_D/D` |
|---:|---:|---:|---:|---:|---:|
| `.55` | 4 | 8,474 | 3,288 | `[26297824817311732,26297824817315020]/2^56` | same interval divided by 4 |
| `.60` | 5 | 8,257 | 3,255 | `[26285572380336108,26285572380339363]/2^56` | same interval divided by 5 |
| `.65` | 6 | 2,256 | 1,457 | `[23008678728233952,23008678728235409]/2^56` | same interval divided by 6 |

The corresponding decimal displays of `Sigma_D/D` are about `0.09123891`,
`0.07295712`, and `0.05321826`.  These decimals are descriptive only; all
acceptance and comparisons use the rational intervals above.

The main finite survivor is the dyadic-bin inequality

\[
 \boxed{
 D\,\#\{r\in\mathcal R_{X,D}:2^j\le r-1<2^{j+1}\}\le2^j.}
 \tag{C104-BIN}
\]

The eventwise scan found no failure through `X=100,000,000` for any
`1<=D<=15`; the endpoint union is nonempty for `1<=D<=11`.  The associated
dyadic-prefix inequality also had no failure.  This is finite evidence, not a
theorem.

`C104-BIN` is high leverage.  If it held for all `X,D`, then each occupied
dyadic bin would contribute at most `1/D` to `Sigma_D`, and hence

\[
 \Sigma_D(X)\le {1+\lfloor\log_2X\rfloor\over D}.
\]

For `D=floor((ln X)^c)` with `c>1/2`, this would give

\[
 {\Sigma_D(X)\over D}=O((\ln X)^{1-2c})=o(1),
\]

which is exactly the missing C99 equation (28).  No proof of `C104-BIN` is
claimed here.

## 1. Audited definitions

The implementation reuses the literal C85/C99 definitions.

* `allowed(n)` means `n>=2` and `n mod 3 != 1`.
* An admissible pair for `h` is `2<=a<b`, `ab=h+1`, with both endpoints
  allowed.
* Generated values are formed in increasing order from seeds `2,3`.
* A hard source is a non-generated even value with at least one admissible
  pair and without an easy seed-3 parent, exactly as in C67/C85/C99.
* If a missing odd endpoint is `p`, its even seed-chain root is computed
  directly as

  \[
  \operatorname{root}(p)=1+{p-1\over2^{v_2(p-1)}}.
  \]

* A witness root is called reducible precisely when its state is not the
  structural-splitless state.  Thus hard and seed-3-reducible roots are both
  retained.

For each reducible root `r`, the census stores the maximum `d(h)` among hard
sources processed so far which witness `r`.  Consequently all sixteen unions
with source threshold `d(h)>=k`, `1<=k<=16`, are obtained in one pass.

## 2. Exact reciprocal arithmetic

Put `S=2^56`.  For a finite root set `R`, the census records

\[
 F(R)=\sum_{r\in R}\left\lfloor{S\over r-1}\right\rfloor.
\]

Termwise flooring gives the rigorous interval

\[
 {F(R)\over S}
 \le \sum_{r\in R}{1\over r-1}
 \le {F(R)+|R|\over S}.                       \tag{1}
\]

The interval width is at most `|R|/2^56`.  Every JSON row contains `F`,
`|R|`, reduced rational endpoints, and the dyadic-bin decomposition.  No
floating-point value participates in acceptance.

The thresholds for `c=11/20,3/5,13/20` are also certified rationally.  The
postprocessor range-reduces `ln X` to `k ln 2+ln y`, `1<=y<2`, and bounds each
logarithm by 24 terms of

\[
 \ln y=2\sum_{j\ge0}{z^{2j+1}\over2j+1},
 \qquad z={y-1\over y+1},\quad 0\le z\le{1\over3}.
\]

The omitted tail is bounded above by

\[
 {2z^{2T+1}\over(2T+1)(1-z^2)}.
\]

The script then verifies with rational arithmetic

\[
 D^q\le(\ln X)^p<(D+1)^q.
\]

The full rational log intervals and comparison certificates are in the
thresholded JSON artifact.

## 3. Geometric-cutoff data

In the next table, `H` is the number of hard sources with `d(h)>=D+1`, `R`
is the number of distinct reducible roots, and `F` is the fixed-point lower
numerator.  Every row has the exact interpretation

\[
 \Sigma_D\in[F,F+R]/2^{56},\qquad
 \Sigma_D/D\in[F,F+R]/(D2^{56}).              \tag{2}
\]

| `X` | `c` | `D` | `H` | `R` | `F` |
|---:|---:|---:|---:|---:|---:|
| 10,000 | .55 | 3 | 8 | 8 | 3775408352415665 |
| 10,000 | .60 | 3 | 8 | 8 | 3775408352415665 |
| 10,000 | .65 | 4 | 0 | 0 | 0 |
| 30,000 | .55 | 3 | 40 | 29 | 9209067129379606 |
| 30,000 | .60 | 4 | 1 | 3 | 2172285779446791 |
| 30,000 | .65 | 4 | 1 | 3 | 2172285779446791 |
| 100,000 | .55 | 3 | 175 | 93 | 14996859293210620 |
| 100,000 | .60 | 4 | 9 | 12 | 5044489940612539 |
| 100,000 | .65 | 4 | 9 | 12 | 5044489940612539 |
| 300,000 | .55 | 4 | 52 | 63 | 10673854786638732 |
| 300,000 | .60 | 4 | 52 | 63 | 10673854786638732 |
| 300,000 | .65 | 5 | 50 | 63 | 10673854786638732 |
| 1,000,000 | .55 | 4 | 163 | 155 | 14668431616640160 |
| 1,000,000 | .60 | 4 | 163 | 155 | 14668431616640160 |
| 1,000,000 | .65 | 5 | 157 | 154 | 14653941853109509 |
| 3,000,000 | .55 | 4 | 447 | 335 | 18160383446067297 |
| 3,000,000 | .60 | 5 | 434 | 334 | 18152529757343818 |
| 3,000,000 | .65 | 5 | 434 | 334 | 18152529757343818 |
| 10,000,000 | .55 | 4 | 1,272 | 739 | 21280449575699257 |
| 10,000,000 | .60 | 5 | 1,232 | 727 | 21251223627926737 |
| 10,000,000 | .65 | 6 | 294 | 310 | 16978160864112970 |
| 30,000,000 | .55 | 4 | 3,232 | 1,586 | 24132537994953835 |
| 30,000,000 | .60 | 5 | 3,145 | 1,573 | 24122797030818244 |
| 30,000,000 | .65 | 6 | 809 | 702 | 20333914453084754 |
| 100,000,000 | .55 | 4 | 8,474 | 3,288 | 26297824817311732 |
| 100,000,000 | .60 | 5 | 8,257 | 3,255 | 26285572380336108 |
| 100,000,000 | .65 | 6 | 2,256 | 1,457 | 23008678728233952 |

The all-hard reducible reciprocal mass rises from about `0.21530` at `10^4`
to about `0.45093` at `10^8`.  The thresholded values are substantially
smaller, but the finite data do not establish a limiting order.

The candidate that `Sigma_D/D` is nonincreasing at the geometric cutoffs is
false.  Exact fixed-point intervals certify increases from `X=3,000` to
`10,000` for `c=.55,.60`, and from `X=3,000` to `30,000` for `c=.65`.

## 4. Endpoint dyadic bins

At `X=10^8`, the exact counts by denominator bin
`2^j<=r-1<2^(j+1)` are:

| `j` | `D=4` count | `D=5` count | `D=6` count |
|---:|---:|---:|---:|
| 5 | 2 | 2 | 2 |
| 6 | 5 | 5 | 5 |
| 7 | 11 | 11 | 11 |
| 8 | 15 | 15 | 14 |
| 9 | 36 | 36 | 31 |
| 10 | 56 | 56 | 50 |
| 11 | 80 | 80 | 59 |
| 12 | 153 | 153 | 108 |
| 13 | 188 | 187 | 105 |
| 14 | 253 | 252 | 139 |
| 15 | 257 | 256 | 123 |
| 16 | 281 | 279 | 134 |
| 17 | 281 | 279 | 119 |
| 18 | 267 | 262 | 95 |
| 19 | 278 | 276 | 99 |
| 20 | 321 | 316 | 108 |
| 21 | 315 | 309 | 93 |
| 22 | 367 | 363 | 125 |
| 23 | 122 | 118 | 37 |

The largest exact ratios `D*count_j/2^j` are respectively

\[
 {11\over32},\qquad {55\over128},\qquad {33\over64},
\]

all below one.  The corresponding maximum prefix ratios
`D*count(r-1<2^(j+1))/2^(j+1)` are `9/32`, `45/128`, and `27/64`.

## 5. Candidate inequalities and earliest falsifiers

The eventwise scan tests each candidate immediately after every hard-source
root-union update, not only at geometric checkpoints.

### 5.1 Surviving finite candidates

No counterexample through `10^8` was found for:

\[
 D\,|R_{X,D}\cap[2^j,2^{j+1})|\le2^j,             \tag{3}
\]

where the interval refers to `r-1`, or for the prefix form

\[
 D\,|\{r\in R_{X,D}:r-1<2^{j+1}\}|\le2^{j+1}.      \tag{4}
\]

Both statements were checked for all `1<=D<=15`; (3) and (4) are nonvacuous
at the endpoint for `1<=D<=11`.

### 5.2 The quadratic strengthening is false

Replacing `D` in (3) by `D^2` fails.  The first exact failures include:

| `D` | first `X` | hard source | last inserted root | bin `j` | `D^2 count` | `2^j` |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 500,024 | 500,024 | 25,002 | 7 | 144 | 128 |
| 5 | 65,414 | 65,414 | 6,542 | 5 | 50 | 32 |
| 6 | 112,664 | 112,664 | 5,634 | 6 | 72 | 64 |
| 7 | 112,664 | 112,664 | 5,634 | 6 | 98 | 64 |
| 8 | 552,474 | 552,474 | 6,738 | 5 | 64 | 32 |
| 9 | 2,778,054 | 2,778,054 | 81,708 | 5 | 81 | 32 |
| 10 | 2,778,054 | 2,778,054 | 81,708 | 5 | 100 | 32 |
| 11 | 2,778,054 | 2,778,054 | 81,708 | 5 | 121 | 32 |

No quadratic failure for `D=1,2,3` was found through `10^8`; this too is only
finite evidence.

The stronger global candidate `D*Sigma_D<=1` also fails.  For example, the
fixed-point lower bound first certifies failure at `X=1,294,194` for `D=3`,
at `X=2,689,274` for `D=4`, at `X=967,700` for `D=5`, and at `X=1,563,176`
for `D=6`.  Thus the surviving bin inequality cannot be replaced by a
constant global reciprocal budget.

## 6. Independent verification

The C++ census was compiled with

```text
g++ -std=c++23 -O3 -march=native -Wall -Wextra -Wpedantic
```

and used one CPU thread.  The `10^8` pass took approximately 5.7 seconds on
the current machine and allocated about 300 MB for the odd-SPF, state, and
root-threshold arrays.

An independently written Python verifier uses a full SPF table, iterative
seed-parent roots, and exact `fractions.Fraction` sums.  Through `X=300,000`
it exactly matched:

* all five total counts;
* all 96 geometric-checkpoint/threshold rows;
* every reducible-root count;
* every dyadic-bin count and fixed-point numerator;
* containment of the exact `Fraction` sum in every interval (1).

Normal Python and `python -O` produced byte-identical verifier output.  A
second `10^8` C++ run gave identical JSON after deleting the timing field,
with matching internal digests

```text
classification_2_through_limit = 94633c57cc653c6e
reducible_root_upgrade_events   = 352897c3ef90202e
```

The full artifacts are:

* `problems/424/compute/wave5/C104_reducible_root_census.cpp`
* `problems/424/compute/wave5/C104_reducible_root_verify.py`
* `problems/424/compute/wave5/C104_threshold_report.py`
* `problems/424/compute/wave5/C104_reducible_root_census_100000000.raw.json`
* `problems/424/compute/wave5/C104_thresholded_reducible_roots_100000000.json`
* `problems/424/compute/wave5/C104_reducible_root_verify_300000.json`

Their SHA-256 values are pinned in
`problems/424/fanout/wave5/C104_SHA256SUMS.txt`.

## 7. Limitation

This computation neither proves C99 equation (28) nor proves `C104-BIN`.
The exact data isolate `C104-BIN` as a strictly stronger sufficient statement
with no finite failure through `10^8`, while disproving several tempting
stronger variants.  Any theorem claim requires a uniform proof of (3), not an
extrapolation from this census.
