# C34: image-dual core for the unconditional contraction inequality

## 1. Statement tested

Let

\[
\mathcal A=\{n\ge 2:n\not\equiv 1\pmod 3\}.
\]

For a forward-closed set \(S\subseteq\mathcal A\) containing \(2,3\), put

\[
F(S)=\{2,3\}\cup\{ab-1:a<b,\ a,b\in S,\ ab-1\in\mathcal A\}.
\]

At cutoff \(X\), `hard` is exactly C33's hard-shape predicate.  Write

\[
H_T(X)=|\{n\le X:n\text{ is hard and }n\notin T\}|
\]

and

\[
Q_T(X)=|\{m:2m-1\le X,\ m\notin T,\ 2m-1\in T\}|.
\]

C33 found no finite countermodel to

\[
H_{F(S)}(X)\le Q_{F(S)}(X) \tag{I}
\]

at any selected hard cutoff through \(10^4\).  C34 asks what linear
certificate is enforcing (I).

## 2. LP relaxation

`lp_probe.py` copies C33's model variable-for-variable, replacing each Boolean
variable by `[0,1]`.  It uses the standard three-facet relaxation for every
AND witness, the lower and upper OR facets, forward-closure inequalities, and
the three boundary facets.  The objective is

\[
\max\left(\sum_{n\in\mathrm{hard}}(1-f_n)-\sum_c q_c\right).
\]

The LP relaxation already proves the requested tight cases:

| \(X\) | hard count | LP minimum \(\sum f_h+\sum q\) | max excess | fractional variables |
|---:|---:|---:|---:|---:|
| 54 | 1 | 1 | 0 | 0 |
| 74 | 2 | 2 | 0 | 0 |
| 186 | 8 | 8 | 0 | 0 |
| 362 | 19 | 19 | 0 | 0 |
| 500 | 27 | 33 | -6 | 0 |
| 1000 | 66 | 70 | -4 | 0 |
| 2000 | 147 | 152 | -5 | 0 |
| 5000 | 410 | 444 | -34 | 0 |
| 10000 | 878 | 946 | -68 | 0 |

The full LP was also solved at every one of the 147 hard cutoffs through
\(X=2000\); no positive objective occurred.  This is finite evidence only.

## 3. Exact Farkas certificates

HiGHS duals were reconstructed with `Fraction`, then checked by exact
stationarity and exact dual-objective equality in `verify_dual.py`.  The four
tight certificates have respectively 19, 27, 70, and 128 nonzero inequality
rows and exact dual objectives 1, 2, 8, and 19.  Exact certificates were also
verified at 500, 1000, 2000, 5000, and 10000.

All nonzero multipliers in all nine certificates are integers.  More
specifically:

* every selected boundary-lower row has multiplier `-1`;
* every selected AND or OR row has multiplier `-1`;
* forward-closure rows have negative integer multiplicities;
* bound multipliers are integers.

At \(X=10000\), the certificate uses 1226 boundary-lower rows, 1417 AND
rows, 1441 OR rows, and 544 closure rows.  Every gate/boundary multiplier is
unit; only closure and bound rows carry larger integral flow.

For a selected set \(C\) of boundary children, set \(u_n=1-s_n\) and
\(h_n=1-f_n\).  The unit boundary rows telescope as

\[
\sum_{c\in C}q_c\ge
\sum_{c\in C}\left(h_{(c+1)/2}-h_c\right).
\]

Thus the coefficient of \(h_n\) after adding the hard-hole demand is

\[
b_n=1_{n\in\mathrm{hard}}+1_{n\in C}-1_{2n-1\in C}. \tag{T}
\]

Positive \(b_n\) is discharged by one lower-image gate (or the trivial
bound \(h_n\le1\)); negative \(b_n\) is discharged by an upper-image gate
(or \(h_n\ge0\)).  The remaining terms are exactly a nonnegative integral
combination of

\[
u_n\le u_a+u_b\qquad(ab=n+1), \tag{C}
\]

with \(u_2=u_3=0\).  This is the finite local certificate template exposed by
C34: a seed-2-chain telescoping skeleton plus an integer closure flow.

### Smallest tight atom

The \(X=54\) inequality has the short human certificate

\[
u_5=0,\qquad u_{14}=0,
\]

from the closure pairs \((2,3)\) and \((3,5)\).  The image facets give

\[
h_{54}\le u_5+u_{11}=u_{11},\qquad
h_{21}\ge u_{11},\qquad h_{41}\le u_3+u_{14}=0.
\]

Since \(q_{41}\ge h_{21}-h_{41}\), one gets

\[
h_{54}\le q_{41}.
\]

This is (I) at the first hard cutoff without integrality.

## 4. Constraint ablation

`ablation.py` solved the full relaxation and seven one-family deletions at
every hard cutoff through 2000.

| removed family | first positive cutoff | excess | returned point |
|---|---:|---:|---|
| closure | 54 | 1 | integral |
| AND lower | 54 | 1 | integral |
| OR lower | 54 | 1 | integral |
| boundary lower | 54 | 1 | integral |
| AND upper | 186 | 1 | integral |
| OR upper | 186 | 1 | integral |
| boundary upper | none through 2000 | - | - |

The boundary upper facets are in fact globally redundant for this
minimization.  Given \(f_p,f_c\in[0,1]\), the minimum allowed by
\(q\ge0\) and \(q\ge f_c-f_p\) is

\[
q=\max(0,f_c-f_p),
\]

which automatically satisfies \(q\le f_c\) and \(q\le1-f_p\).

The integral ablation witnesses are included in `ablation_2000.json`.  Hence
the forward Horn closure, both directions of the image gates (from cutoff
186 onward), and the lower boundary facet are genuinely used; the finite LP
success is not coming from a vacuous bound.

## 5. What is and is not proved

C34 supplies exact finite Farkas certificates and a uniform *form* for them:
choose seed-2-chain intervals, telescope by (T), then route the endpoint
defect through the closure DAG by integer copies of (C).  It does not prove
that such a skeleton and nonnegative closure flow exist for every cutoff.
That infinite flow-existence statement is now the precise remaining theorem;
finite success through \(10^4\) is not an extrapolation.

## 6. Reproduction

```text
python problems/424/compute/wave3/C34_image_dual_core/lp_probe.py --limit 362 --output .../lp_362.json
python problems/424/compute/wave3/C34_image_dual_core/verify_dual.py --lp .../lp_362.json --certificate .../dual_362.json
python problems/424/compute/wave3/C34_image_dual_core/ablation.py --stop 2000 --output .../ablation_2000.json
```

The computations use one LP worker and stay far below the assigned 8-worker,
24-GB cap.

## 7. Addendum: grounded-core replacement for closure

This section supersedes the interpretation of the closure ablation in Sections 4--5. Let $G_X$ be the least subset of $[2,X]\cap\mathcal A$ containing $2,3$ and closed under admissible products $ab-1\le X$. Since every parent of $n=ab-1$ is smaller than $n$, this is exactly $G\cap[2,X]$, obtained in one increasing pass.

`ground_core_lp.py` deletes all forward-closure inequalities, fixes only $s_g=1$ for $g\in G_X$, and leaves every other member of $S$ arbitrary. This strictly enlarges the predecessor class relevant to the original claim.

| $X$ | $|G_X|$ | grounded LP max excess | fractional variables |
|---:|---:|---:|---:|
| 54 | 14 | 0 | 0 |
| 74 | 16 | 0 | 0 |
| 186 | 40 | 0 | 0 |
| 362 | 78 | 0 | 0 |
| 500 | 119 | -6 | 0 |
| 1000 | 250 | -4 | 0 |
| 2000 | 530 | -4 | 0 |
| 5000 | 1496 | -32 | 0 |
| 10000 | 3207 | -65 | 0 |

The grounded LP passes all 147 hard cutoffs through 2000. Its endpoint values agree with C33's exact CP-SAT values, including `-65` at 10000. Exact rational dual verification passes at all nine displayed cutoffs.

In every grounded certificate, all nonzero AND, OR, and boundary-row multipliers are exactly `-1`. There are no closure rows. Larger coefficients occur only on integer bound multipliers fixing elements of $G_X$. At $X=10000$, the exact certificate uses 1440 AND rows, 1453 OR rows, and 1227 boundary-lower rows; its dual objective is 943 against the required 878.

Therefore the earlier integral closure flow was not intrinsic: it merely re-proved $G_X\subseteq S$ inside the LP. Once grounded membership is inserted directly, the certificate is a unit gate/boundary skeleton paid by fixed core vertices. Conversely, fixing only $2,3$ fails integrally at $X=54$, so grounded information is indispensable.

The remaining infinite statement is sharper: for every cutoff, construct the unit gate/boundary skeleton using only the fixed membership $G_X\subseteq S$. No closure property of arbitrary extra members is needed. The finite computations do not prove this skeleton exists for all cutoffs.

Reproduction:

```text
python problems/424/compute/wave3/C34_image_dual_core/ground_core_lp.py --limit 10000 --output .../ground_lp_10000.json
python problems/424/compute/wave3/C34_image_dual_core/verify_ground_dual.py --lp .../ground_lp_10000.json --certificate .../ground_dual_10000.json
python problems/424/compute/wave3/C34_image_dual_core/ground_core_lp.py --stop 2000 --output .../ground_scan_2000.json
```
