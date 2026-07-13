# B02: red-team of the {2,3,5} affine subsystem

## Verdict

Let \(B\) be the least set containing \(2,3,5\) and closed under

\[
T_k(x)=kx-1,\qquad k\in\{2,3,5\},\quad x\ne k.
\]

The apparent density near \(0.19\) does not remain numerically stable. The
exact count is

\[
|B\cap[1,10^{11}]|=18{,}222{,}202{,}754,
\qquad d_B(10^{11})=0.18222202754.
\]

The density falls in every complete decade from \(10^3\) through \(10^{11}\).
This does not prove zero density, but the farther census is more consistent
with a slowly vanishing density than with a settled \(0.19\) density.

There is a second independent warning. If \(R_a\) is the exact orbit modulo
\(30^a\), then

\[
\frac{|R_1|}{30}=0.533333\ldots,\qquad
\frac{|R_7|}{30^7}=0.274873409602,
\]

and all seven computed fractions decrease. Proving
\(|R_a|=o(30^a)\) would prove that \(B\) has upper density zero.

No density theorem is proved here. The sharp positive-density frontier is the
summable excess-collision estimate in the section "The missing theorem".

## Relation to Problem 424

The full Problem 424 set \(A\) contains \(2,3\), hence
\(5=2\cdot3-1\). Thus \(\{2,3,5\}\subset A\). Every licensed operation used
to construct \(B\) is also licensed in \(A\), so

\[
B\subseteq A.
\]

Consequently, positive lower density for \(B\) would solve Problem 424.

The equal-input restriction affects only the attempted seed transitions
\(T_2(2)=3\), \(T_3(3)=8\), and \(T_5(5)=24\). The first new values are
\(9=T_2(5)=T_5(2)\) and \(14=T_3(5)=T_5(3)\). Every later state is greater
than 5, so every one of the three maps is then licensed. In particular,

\[
B=\{2,3,5\}\ \cup\
\{T_w(9):w\in\{2,3,5\}^*\}\ \cup\
\{T_w(14):w\in\{2,3,5\}^*\}.
\tag{1}
\]

## Exact reverse recurrence

Write \(b_n=1_{n\in B}\). Set \(b_2=b_3=b_5=1\), with the other values below
6 equal to zero. For \(n\ge6\),

\[
b_n=\bigvee_{\substack{k\in\{2,3,5\}\\k\mid n+1\\(n+1)/k\ne k}}
b_{(n+1)/k}. \tag{2}
\]

This is exact. A forward witness \(n=kx-1\) gives the parent
\(x=(n+1)/k<n\). Conversely, every parent selected in (2) gives a licensed
forward operation. Strong induction therefore proves both directions. For
\(n\ge25\), the unequal-parent test is automatic.

Equation (2) is also a finite 30-residue transducer. Put
\(n+1=30q+r\), \(0\le r<30\), and

\[
K(r)=\{k\in\{2,3,5\}:k\mid r\}.
\]

For \(n\ge25\),

\[
b_{30q+r-1}=\bigvee_{k\in K(r)}
b_{(30/k)q+r/k}. \tag{3}
\]

The eight transition masks are:

| \(K(r)\) | residues \(r\) |
|---|---|
| \(\varnothing\) | 1, 7, 11, 13, 17, 19, 23, 29 |
| \(\{2\}\) | 2, 4, 8, 14, 16, 22, 26, 28 |
| \(\{3\}\) | 3, 9, 21, 27 |
| \(\{5\}\) | 5, 25 |
| \(\{2,3\}\) | 6, 12, 18, 24 |
| \(\{2,5\}\) | 10, 20 |
| \(\{3,5\}\) | 15 |
| \(\{2,3,5\}\) | 0 |

The C++ census evaluates (2) in layers
\([L,2L-2]\). Every parent of a member of such a layer is below \(L\), so a
layer is race-free and can be evaluated with up to 64 OpenMP workers.

## Exact census through \(10^{11}\)

| \(X\) | \(C(X)=|B\cap[1,X]|\) | \(C(X)/X\) |
|---:|---:|---:|
| \(10^3\) | 212 | 0.212000000000 |
| \(10^4\) | 2,061 | 0.206100000000 |
| \(10^5\) | 20,192 | 0.201920000000 |
| \(10^6\) | 197,450 | 0.197450000000 |
| \(10^7\) | 1,938,458 | 0.193845800000 |
| \(10^8\) | 19,072,023 | 0.190720230000 |
| \(10^9\) | 187,749,502 | 0.187749502000 |
| \(10^{10}\) | 1,849,014,105 | 0.184901410500 |
| \(10^{11}\) | 18,222,202,754 | 0.182222027540 |

The \(10^{11}\) run used 100,000,000,001 membership bytes. With 64 workers,
generation took 13.63 seconds and the checkpoint/mask scan took 2.41 seconds.
These timings are informational; the integer counts are the result.

## Exact collision recurrence

For \(X\ge24\), put

\[
M_k=\left\lfloor\frac{X+1}{k}\right\rfloor,\qquad C(X)=|B\cap[1,X]|.
\]

Let

\[
\begin{aligned}
P_{23}(X)&=\#\{t\le (X+1)/6:2t,3t\in B\},\\
P_{25}(X)&=\#\{t\le (X+1)/10:2t,5t\in B\},\\
P_{35}(X)&=\#\{t\le (X+1)/15:3t,5t\in B\},\\
P_{235}(X)&=\#\{t\le (X+1)/30:6t,10t,15t\in B\},
\end{aligned}
\]

where the upper bounds mean integer floors. Define the collision tax

\[
\Delta(X)=P_{23}(X)+P_{25}(X)+P_{35}(X)-P_{235}(X). \tag{4}
\]

Inclusion-exclusion among \(T_2(B\setminus\{2\})\),
\(T_3(B\setminus\{3\})\), and \(T_5(B\setminus\{5\})\) gives the exact
recurrence

\[
C(X)=C(M_2)+C(M_3)+C(M_5)-1-\Delta(X). \tag{5}
\]

Equivalently, each child having exactly two parents contributes 1 to
\(\Delta\), and each child having three parents contributes 2.

At \(X=10^{11}\), the seven nonempty parent-mask counts for masks
\(2,3,23,5,25,35,235\) are respectively

\[
\begin{split}
&8{,}586{,}937{,}317,\quad 5{,}659{,}661{,}598,\quad
294{,}443{,}090,\\
&3{,}249{,}663{,}656,\quad 270{,}627{,}676,\quad
160{,}436{,}579,\quad 432{,}836.
\end{split}
\]

Thus

\[
\Delta(10^{11})=726{,}373{,}017.
\]

The critical ratio is \(1/30\), because
\(1/2+1/3+1/5=31/30\). Numerically:

| \(X\) | \(\Delta(X)/C(X)\) | excess over \(1/30\) | \(\log X\) times excess |
|---:|---:|---:|---:|
| \(10^8\) | 0.040753568722 | 0.007420235389 | 0.136685787141 |
| \(10^9\) | 0.040526280597 | 0.007192947264 | 0.149061358296 |
| \(10^{10}\) | 0.040217274600 | 0.006883941267 | 0.158508605416 |
| \(10^{11}\) | 0.039861976447 | 0.006528643114 | 0.165360319432 |

The excess decreases, but it has not entered a visibly summable regime. In
particular, \((\log X)(\Delta/C-1/30)\) is increasing over these four
decades, whereas the stronger sufficient estimate (P') below would make this
quantity tend to zero.

For orientation only, let \(t=\log X\) and
\(d(t)=C(e^t)/e^t\). A smooth expansion of (5) gives

\[
\frac{d'(t)}{d(t)}
\mathrel{\approx}
-\frac{\Delta(e^t)/C(e^t)-1/30}{\mu},
\qquad
\mu=\sum_{k=2,3,5}\frac{\log k}{k}=1.034665268989496.
\tag{6}
\]

Thus an excess asymptotic to \(\alpha\mu/t\) predicts
\(d(t)\asymp t^{-\alpha}\), hence zero density. A log-power fit to the four
points \(10^8,\ldots,10^{11}\) gives \(\alpha=0.1431\); its maximum relative
error on those points is \(0.00064\). A positive-limit fit also remains
possible on so short a range, so (6) is a diagnostic and not a proof.

## Exact modular orbit

Let

\[
R_a=\{x\bmod 30^a:x\in B\}.
\]

By (1), \(R_a\) is exactly the finite automaton orbit initialized at residues
9 and 14, with transitions

\[
r\longmapsto 2r-1,\quad 3r-1,\quad 5r-1\pmod {30^a},
\]

and with the three seed residues adjoined. Therefore

\[
\overline d(B)\le\frac{|R_a|}{30^a}\qquad\text{for every }a. \tag{7}
\]

The exact breadth-first census is:

| \(a\) | \(30^a\) | \(|R_a|\) | \(|R_a|/30^a\) |
|---:|---:|---:|---:|
| 1 | 30 | 16 | 0.533333333333 |
| 2 | 900 | 389 | 0.432222222222 |
| 3 | 27,000 | 10,144 | 0.375703703704 |
| 4 | 810,000 | 274,958 | 0.339454320988 |
| 5 | 24,300,000 | 7,587,398 | 0.312238600823 |
| 6 | 729,000,000 | 212,613,518 | 0.291650916324 |
| 7 | 21,870,000,000 | 6,011,481,468 | 0.274873409602 |

Reduction \(R_{a+1}\to R_a\) is onto. Define its normalized average lift
deficit by

\[
e_a=1-\frac{|R_{a+1}|}{30|R_a|}.
\]

Then

\[
\frac{|R_a|}{30^a}
=\frac{|R_1|}{30}\prod_{j<a}(1-e_j). \tag{8}
\]

The computed values of \(a e_a\), for \(a=1,\ldots,6\), are

\[
0.18958,\ 0.26153,\ 0.28945,\ 0.32070,\ 0.32968,\ 0.34516.
\]

This is compatible with \(e_a\asymp c/a\), which would make (8) tend to zero
polynomially. It is not compatible, at these depths, with an already visible
summable lift deficit. The single modular theorem

\[
|R_a|=o(30^a) \tag{M0}
\]

would prove that \(B\) has upper density zero. A concrete sufficient version
is \(e_a\ge c/a\) for all sufficiently large \(a\).

## The missing theorem

Set

\[
F(X)=C(X)-\frac12.
\]

Equation (5) becomes

\[
F(X)+\Delta(X)=F(M_2)+F(M_3)+F(M_5). \tag{9}
\]

The smallest concrete positive-density estimate isolated by this wave is:

> **Summable excess-collision theorem.** There are nonnegative
> \(\varepsilon_j\) with \(\sum_j\varepsilon_j<\infty\) such that, uniformly
> for \(2^j\le X<2^{j+1}\),
> \[
> \Delta(X)\le\left(\frac1{30}+\varepsilon_j\right)F(X). \tag{P}
> \]

Theorem (P) implies \(\underline d(B)>0\). Indeed, (9) gives

\[
F(X)\ge
\frac{F(M_2)+F(M_3)+F(M_5)}
{31/30+\varepsilon_j}. \tag{10}
\]

If the earlier arguments satisfy \(F(Y)\ge c_j(Y+1)\), then

\[
\sum_{k=2,3,5}F(M_k)
\ge c_j\sum_{k=2,3,5}(M_k+1)
\ge c_j\frac{31}{30}(X+1).
\]

All parents lie in earlier dyadic layers. Strong induction therefore loses at
most the factor
\((31/30)/(31/30+\varepsilon_j)\) on layer \(j\). The infinite product of
these factors is positive exactly when the excesses are summable, proving a
positive linear lower barrier for \(F\), hence for \(C\).

A more conventional but stronger target is: for some \(\eta>0\),

\[
\Delta(X)\le
\left(\frac1{30}+\frac{O(1)}{(\log X)^{1+\eta}}\right)F(X)
\quad\text{uniformly in }X. \tag{P'}
\]

Any positive-density proof must also overcome the modular gate. From (7) and
(8), positive lower density forces

\[
\inf_a\frac{|R_a|}{30^a}>0,
\qquad\text{equivalently}\qquad
\sum_a e_a<\infty. \tag{M+}
\]

The current computations point in the opposite direction for both (P') and
(M+). The best next theorem target is therefore modular: prove or disprove
\(e_a\gg1/a\). It is finite-state at every level and, unlike an Archimedean
density extrapolation, either gives a zero-density proof through (M0) or
removes the strongest observed obstruction to (P).

## Reproduction and checks

Source files:

- problems/424/compute/wave2/B02/affine_census.cpp
- problems/424/compute/wave2/B02/residue_closure.cpp
- problems/424/compute/wave2/B02/test_affine_census.py

From the repository root:

~~~powershell
cd problems/424/compute/wave2/B02
python -m unittest -v test_affine_census.py
g++ -O3 -march=native -fopenmp -std=c++20 -Wall -Wextra -pedantic affine_census.cpp -o affine_census.exe
.\affine_census.exe --limit 100000000000 --threads 64
g++ -O3 -march=native -std=c++20 -Wall -Wextra -pedantic residue_closure.cpp -o residue_closure.exe
.\residue_closure.exe --max-power 7
~~~

The Python tests compare (2) with literal fixed-point closure for every bound
through 500, verify the supplied counts through \(10^5\), test the forbidden
equal-input sentinels 8 and 24, and independently reproduce the first three
modular orbit counts. All four tests pass.

Finite counts, model fits, and decreasing modular fractions do not prove an
asymptotic statement. In particular, neither (P), (P'), (M0), nor (M+) is
claimed here.
