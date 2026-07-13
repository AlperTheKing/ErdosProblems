# C03: exact smooth/rough census for R-A3 gates (31) and (32)

Code: [C03_smooth_rough.py](../../compute/wave3/C03_smooth_rough.py)

## Scope

This is a finite discovery and falsification census. It does not prove, refute,
or support an asymptotic estimate. In particular, no trend in the three rows
below is extrapolated beyond the computed ranges.

The run constructed the exact membership array of \(G\) through
\(B=100{,}000{,}000\). Since

\[
T=\{n\geq 1:3n\in G\},
\]

this gives exact \(T\)-membership only through
\(\lfloor B/3\rfloor=33{,}333{,}333\). The largest finite parameter \(X\)
was therefore set equal to that bound.

## Exact definitions

The bitmap uses one byte per integer, indexed from \(0\) through \(B\). It is
constructed in increasing order from the exact well-founded equivalence

\[
n\in G
\quad\Longleftrightarrow\quad
n\in\{2,3\}\ \text{or}\ n+1=ab
\ \text{for some }2\leq a<b,\ a,b\in G.
\]

The strict inequality \(a<b\) enforces the frozen distinct-value convention.
Every tested factor is smaller than \(n\), so no closure truncation is used.

All logarithms below are natural. For each finite \(X\), the real recipe is

\[
u=\sqrt{\log\log X},\qquad
y_{\mathbb R}=\exp(\sqrt{\log X}),\qquad
z_{\mathbb R}=y_{\mathbb R}^{1/u},\qquad
L_{\mathbb R}=\exp(\sqrt{\log z_{\mathbb R}}).
\]

The integer census uses directed rounding

\[
(L,y,z)=
(\lceil L_{\mathbb R}\rceil,\lfloor y_{\mathbb R}\rfloor,
\lfloor z_{\mathbb R}\rfloor).
\]

An integer \(s\geq1\) is \(z\)-smooth when every prime divisor of \(s\) is at
most \(z\); \(1\) is smooth. An integer \(r\) is counted as \(z\)-rough when
\(r>z\) and no prime at most \(z\) divides \(r\).

For gate (31), the finite quantities are

\[
H_z(y)=\sum_{\substack{s\leq y\\s\ z\text{-smooth}}}\frac1s,\qquad
W_{31}(z,y)=
\sum_{\substack{s\leq y\\s\ z\text{-smooth}\\s\notin T}}\frac1s.
\]

Every displayed reciprocal sum is an exact reduced rational. The decimal
\(W_{31}/\log z\) is only a labeled floating-point diagnostic.

For gate (32), define the ambient prefix miss rate

\[
D_z(R)=\frac{\#\{r\leq R:r\ z\text{-rough},\ r\notin T\}}{R}.
\]

The additional conditional rate

\[
C_z(R)=
\frac{\#\{r\leq R:r\ z\text{-rough},\ r\notin T\}}
{\#\{r\leq R:r\ z\text{-rough}\}}
\]

is reported for diagnosis, but the gate-(32) product in the R-A3 reduction
uses \(D_z\), not \(C_z\). The cutoff interval is exactly

\[
I_X=[\lfloor X/y\rfloor,\lfloor X/L\rfloor]\cap\mathbb Z.
\]

The program exhausts every integer \(R\in I_X\). Exact maximization can check
the left endpoint and each missing rough event: between such events the
numerator is constant while either denominator can only increase.

## Parameter triples

| \(X\) | \(u_{\mathbb R}\) | \(y_{\mathbb R}\) | \(z_{\mathbb R}\) | \(L_{\mathbb R}\) | integer \((L,y,z)\) |
|---:|---:|---:|---:|---:|---:|
| \(1{,}000{,}000\) | 1.6204295462858023 | 41.137585343138909 | 9.9124169664371067 | 4.5472640196535243 | \((5,41,9)\) |
| \(10{,}000{,}000\) | 1.6673159851399701 | 55.408600036187593 | 11.110635389055583 | 4.7196840445335635 | \((5,55,11)\) |
| \(33{,}333{,}333\) | 1.6887810163698018 | 64.198439898848775 | 11.757449374890060 | 4.8060160413382667 | \((5,64,11)\) |

## Gate (31): exact smooth census

Here "count" is the number of \(z\)-smooth \(s\leq y\).

| \(X\) | count | in \(T\) | missing | \(H_z(y)\) | reciprocal mass in \(T\) | \(W_{31}(z,y)\) | \(W_{31}/\log z\), decimal only |
|---:|---:|---:|---:|---:|---:|---:|---:|
| \(10^6\) | 26 | 6 | 20 | \(554363/151200\) | \(5843/3780\) | \(35627/16800\) | 0.965151575209355 |
| \(10^7\) | 37 | 8 | 29 | \(15522383/3880800\) | \(69313/41580\) | \(27159509/11642400\) | 0.972857399520575 |
| \(33333333\) | 41 | 8 | 33 | \(10519067/2587200\) | \(69313/41580\) | \(55856323/23284800\) | 1.00039063925201 |

The exact smooth \(T\)-members are:

- \(X=10^6\): \(1,3,9,27,28,35\).
- \(X=10^7\): \(1,3,9,11,27,28,33,35\).
- \(X=33{,}333{,}333\): \(1,3,9,11,27,28,33,35\).

The exact missing smooth values are:

- \(X=10^6\): \(2,4,5,6,7,8,10,12,14,15,16,18,20,21,24,25,30,32,36,40\).
- \(X=10^7\): \(2,4,5,6,7,8,10,12,14,15,16,18,20,21,22,24,25,30,32,36,40,42,44,45,48,49,50,54,55\).
- \(X=33{,}333{,}333\): \(2,4,5,6,7,8,10,12,14,15,16,18,20,21,22,24,25,30,32,36,40,42,44,45,48,49,50,54,55,56,60,63,64\).

Restricting to the decomposition window \(L\leq s\leq y\) gives:

| \(X\) | eligible smooth | in \(T\) | missing | exact missing reciprocal mass |
|---:|---:|---:|---:|---:|
| \(10^6\) | 22 | 4 | 18 | \(23027/16800\) |
| \(10^7\) | 33 | 6 | 27 | \(18427709/11642400\) |
| \(33333333\) | 37 | 6 | 31 | \(38392723/23284800\) |

These finite values do not decide the little-\(o\) condition in gate (31).

## Gate (32): exact rough census

Each endpoint tuple below is
\((\#\text{rough},\#\text{rough in }T,\#\text{rough missing from }T)\)
for the prefix \(r\leq R\). The slab tuple uses only
\(\lfloor X/y\rfloor\leq r\leq\lfloor X/L\rfloor\).

| \(X\) | cutoff interval \(I_X\) | left endpoint tuple | right endpoint tuple | interval slab tuple |
|---:|---:|---:|---:|---:|
| \(10^6\) | \([24390,200000]\) | \((5574,4360,1214)\) | \((45714,39803,5911)\) | \((40140,35443,4697)\) |
| \(10^7\) | \([181818,2000000]\) | \((37780,32839,4941)\) | \((415584,384525,31059)\) | \((377804,351686,26118)\) |
| \(33333333\) | \([520833,6666666]\) | \((108225,97261,10964)\) | \((1385280,1303595,81685)\) | \((1277055,1206334,70721)\) |

The exact suprema over every integer cutoff in \(I_X\) are:

| \(X\) | cutoffs exhausted | argmax \(R\) | counts at argmax (rough, in \(T\), miss) | \(\sup D_z(R)\) | \(\sup C_z(R)\) |
|---:|---:|---:|---:|---:|---:|
| \(10^6\) | 175611 | 24390 | \((5574,4360,1214)\) | \(607/12195\) | \(607/2787\) |
| \(10^7\) | 1818183 | 181921 | \((37802,32857,4945)\) | \(4945/181921\) | \(4945/37802\) |
| \(33333333\) | 6145834 | 520833 | \((108225,97261,10964)\) | \(10964/520833\) | \(10964/108225\) |

For comparison, restricting the supremum to actual cutoffs
\(R=\lfloor X/s\rfloor\) from eligible smooth \(s\in T\) gives:

| \(X\) | distinct cutoffs | maximizing \(s\) | argmax \(R\) | exact ambient miss rate |
|---:|---:|---:|---:|---:|
| \(10^6\) | 4 | 35 | 28571 | \(1358/28571\) |
| \(10^7\) | 6 | 35 | 285714 | \(2309/95238\) |
| \(33333333\) | 6 | 35 | 952380 | \(5783/317460\) |

Finally, the exact finite gate-(32) products are:

| \(X\) | \(H_z(y)\sup_{R\in I_X}D_z(R)\) | decimal | extra \(H_z(y)\sup C_z(R)\) |
|---:|---:|---:|---:|
| \(10^6\) | \(336498341/1843884000\) | 0.182494311464279 | \(336498341/421394400\) |
| \(10^7\) | \(15351636787/141199803360\) | 0.108722791545678 | \(15351636787/29340400320\) |
| \(33333333\) | \(28832762647/336874784400\) | 0.0855889605936324 | \(2217904819/5384610000\) |

The changes between these three finite products are not an asymptotic claim.

## Reproduction

From the repository root:

    python problems/424/compute/wave3/C03_smooth_rough.py --self-test

    python problems/424/compute/wave3/C03_smooth_rough.py --limit 100000000 --x-values 1000000 10000000 33333333

The script requires Python 3, NumPy, and a C++20 compiler named g++ by
default. The recorded full run used Python 3.12.4, NumPy 2.2.6, and
MSYS2 g++ 16.1.0. The embedded helper was compiled with

    g++.EXE -O3 -DNDEBUG -std=c++20 SOURCE.cpp -o HELPER.exe

The final full invocation completed in 7.803040 wall seconds. Helper source,
executable, and bitmap files were temporary; only their hashes are retained.

## Verification and SHA-256

The independent self-test at \(B=10{,}000\) compared the divisor recursion
byte-for-byte with a sorted worklist closure. Both produced exactly 3207
members. The self-test bitmap SHA-256 is

    f55ebd3b4551905df7aa33cf7f6bdc639b2fe3e05bb5e523157d7b99eb2c55c2

The same self-test also brute-forced 901 consecutive rough cutoffs and matched
the event-only maximizer's exact ambient and conditional fractions and earliest
argmaxes.

At \(B=100{,}000{,}000\), all reference checkpoint counts matched:

| bound | exact count |
|---:|---:|
| 10 | 4 |
| 100 | 23 |
| 1000 | 250 |
| 10000 | 3207 |
| 100000 | 39843 |
| 1000000 | 457599 |
| 10000000 | 4952270 |
| 100000000 | 51899129 |

The exact \(T\)-bitmap through \(33{,}333{,}333\), including index \(0\),
contains 22,524,589 one-bytes.

Recorded SHA-256 values:

| artifact and exact byte range | SHA-256 |
|---|---|
| C03_smooth_rough.py | d0ef34f6586d1bba46c8d1bdc2248c4de349157192b0717765113e2cdaffcd83 |
| embedded C++ source | d219dd8bbf150305befa46408d6e31662f5891e2176fd6c583caa04e5f3c7fd7 |
| full-run helper executable | 00c21e416f2bc698fcffb341e4dadfbe493c375abd9449cbd00a310c8913fd30 |
| \(G[0..10^6]\) bytes | 569056ee7b16336bbf9eaa0b0fcfc77376048f12d7157da440333207b8a2e365 |
| \(G[0..10^7]\) bytes | 7f5f29e1d5733d623c514c98c183796c3ab15a99d9ad9e5f0c9ff6ea627d85a0 |
| \(G[0..10^8]\) bytes | 7b1d5b6a06c04b256e87277a5b2066990550582ab7844c8c1eb3ca059445e212 |
| \(T[0..33333333]\) bytes | 0cec45767873633e8e40b68781c793847c46abf4b29a50a85612b3f0b4a4d4f2 |
| reference census JSON | e096c3abd6020fd63df934106fb858665f2e45b65d13888f7100b50e2a740356 |
| \(z=9\) rough mask on \([0,200000]\) | be37a594e600256094cb76cb089e7f04243aa0dc2c505f7e5493fe7d3615e101 |
| \(z=9\) rough-\(T\)-miss mask on \([0,200000]\) | 4c622f65a78723dfd6110d1811854c341bebf45b5eaaedb5bd721906e2f25f5b |
| \(z=11\) rough mask on \([0,6666666]\) | 0bb0bae6fce81dec02097a782073b255b4a12ba4fdab5422edad5c68b7ad77ba |
| \(z=11\) rough-\(T\)-miss mask on \([0,6666666]\) | e6762ea15f03111e1438dbd75bda850452a93f0631e47011536ad81f612ea389 |

The repository HEAD recorded by the run was
4c3ced41c5a8e4e8f0964863c181aed6e5be3d1b.

## Boundary

The census supplies exact finite inputs for gates (31) and (32). It does not
establish uniformity in \(z,y,L,X\), does not control any uncomputed scale,
and does not turn the displayed finite ratios into little-\(o\) estimates.
