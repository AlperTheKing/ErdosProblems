# B01: the fixed affine subsystem does not yet yield a proof

## Verdict

Let (B) be the least set containing (2,3,5) and closed under

\[
T_k(x)=kx-1,\qquad k\in\{2,3,5\},\quad x\ne k.
\]

I did not prove that (B) has positive lower density. In particular, there
are no justified constants (c>0) and (X_0) for which

\[
|B\cap[1,X]|\ge cX\qquad(X\ge X_0).
\]

Giving numerical constants here would therefore be false. The exact work
below isolates two genuine obstructions: the standard finite residue
unique-decoding mechanism is necessarily subcritical, and the elementary
second-moment mechanism loses a power at every tested scale. The census also
continues to decrease through (10^{11}).

## Exact reduction

The only first exits from the seeds that produce a new value are

\[
T_2(5)=T_5(2)=9,\qquad T_3(5)=T_5(3)=14.
\]

Every descendant of (9) or (14) is greater than (5), so all three maps
are thereafter licensed. Hence, exactly,

\[
B=\{2,3,5\}\cup\{T_w(9):w\in\{2,3,5\}^*\}
 \cup\{T_w(14):w\in\{2,3,5\}^*\}. \tag{1}
\]

Consequently, if (b_n=1_{n\in B}), then for (n\ge6)

\[
b_n=\bigvee_{\substack{k\in\{2,3,5\}\\k\mid n+1\\(n+1)/k\ne k}}
b_{(n+1)/k}. \tag{2}
\]

Every parent in (2) is smaller than (n). Thus strong induction proves that
(2) is both sound and complete, and it gives an exact one-pass census.

## Extended exact census

The B01 C++ recurrence reproduced the supplied rows and continued them:

| (X) | (|B\cap[1,X]|) | density |
|---:|---:|---:|
| (10^3) | 212 | 0.2120000000 |
| (10^4) | 2,061 | 0.2061000000 |
| (10^5) | 20,192 | 0.2019200000 |
| (10^6) | 197,450 | 0.1974500000 |
| (10^7) | 1,938,458 | 0.1938458000 |
| (10^8) | 19,072,023 | 0.1907202300 |
| (10^9) | 187,749,502 | 0.1877495020 |
| (10^{10}) | 1,849,014,105 | 0.1849014105 |

The independent B02 layer-parallel recurrence subsequently obtained

\[
|B\cap[1,10^{11}]|=18{,}222{,}202{,}754,
\qquad d_B(10^{11})=0.18222202754.
\]

The density decreases in every complete decade from (10^3) through
(10^{11}). This neither proves zero density nor supplies a positive lower
bound. Maximum gaps in the B01 run grow from (180) below (10^5) to
(16{,}436) below (10^{10}), so a bounded-gap proof is also unavailable.

## Exact collision identity

Write (C(X)=|B\cap[1,X]|) and (M_k=\lfloor(X+1)/k\rfloor). Pairwise
intersections of the three affine images have the exact forms

\[
\begin{aligned}
P_{23}(X)&=\#\{t\le (X+1)/6:2t,3t\in B\},\\
P_{25}(X)&=\#\{t\le (X+1)/10:2t,5t\in B\},\\
P_{35}(X)&=\#\{t\le (X+1)/15:3t,5t\in B\},\\
P_{235}(X)&=\#\{t\le (X+1)/30:6t,10t,15t\in B\}.
\end{aligned}
\]

For (X\ge24), inclusion-exclusion gives

\[
C(X)=C(M_2)+C(M_3)+C(M_5)-1-\Delta(X), \tag{3}
\]

where

\[
\Delta=P_{23}+P_{25}+P_{35}-P_{235}. \tag{4}
\]

The reciprocal slopes sum to (31/30), so the critical collision ratio is
(1/30). At (X=10^{11}), the independent exact mask census gives

\[
\Delta(X)=726{,}373{,}017,
\qquad \frac{\Delta(X)}{C(X)}=0.039861976447,
\]

which exceeds (1/30) by (0.006528643114). The excess decreases, but not
at a rate from which a summable loss can be proved.

Indeed, put (F(X)=C(X)-1/2). Equation (3) is

\[
F(X)+\Delta(X)=F(M_2)+F(M_3)+F(M_5). \tag{5}
\]

A sufficient induction lemma would be a uniform dyadic estimate

\[
\Delta(X)\le (1/30+\varepsilon_j)F(X)
\quad(2^j\le X<2^{j+1}),\qquad
\sum_j\varepsilon_j<\infty. \tag{6}
\]

Then each dyadic layer loses at most the factor

\[
\frac{31/30}{31/30+\varepsilon_j},
\]

whose infinite product is positive. This would give explicit (c,X_0)
after a finite base check. Estimate (6) is the precise missing lemma; the
data do not verify its summability.

## Why global finite residue decoding cannot work

For a nonempty word (w), write

\[
T_w(x)=a_wx-b_w.
\]

The update ((a,b)\mapsto(ka,kb+1)) proves

\[
a_w\ge2,\qquad 1\le b_w<a_w. \tag{7}
\]

Consider any finite automaton whose states are complete residue classes
modulo a fixed modulus. Suppose an edge into a state is labelled by a block
(w), and incoming affine images are pairwise disjoint so that the last edge
is uniquely decodable from the output residue. Give that edge weight
(a_w^{-1}), and let (A) be the weighted transition matrix.

Disjointness of arithmetic progressions makes every column sum at most one,
so (ho(A)\le1). Equality is impossible. If (ho(A)=1), a recurrent
class of the transpose substochastic chain has no mass loss. The union (U)
of its residue classes is then exactly covered by its incoming affine images.
It cannot contain (0), since (0=a_wx-b_w) and (7) would force
(0<x<1). Because nonempty periodic (U) contains negative integers, take
its largest negative member (y). An exact predecessor (x\in U) cannot be
nonnegative; if (x\le-1), then

\[
y=a_wx-b_w<x<0,
\]

contradicting maximality of (y). Therefore

\[
\rho(A)<1. \tag{8}
\]

By continuity, (ho(A(s))<1) for some (s<1), where edge weights are
(a_w^{-s}). The resulting uniquely decoded language has only (O(X^s))
values up to (X). Thus no globally residue-decodable finite automaton of
this standard kind can prove positive density for (B), regardless of the
chosen modulus or finite block set.

This does not rule out uniqueness only on the positive orbit, but that weaker
property needs an additional theorem and was not obtained.

## Second-moment attempt

Counting all licensed derivations gives a linear recurrence for the
representation multiplicity (r(n)). Let

\[
R_1(X)=\sum_{n\le X}r(n),\qquad R_2(X)=\sum_{n\le X}r(n)^2.
\]

The renewal exponent is the root

\[
2^{-\sigma}+3^{-\sigma}+5^{-\sigma}=1,
\qquad \sigma=1.032812265771883\ldots.
\]

A bound (R_2(X)=O(X^{2\sigma-1})) would imply (C(X)=\Omega(X)) by
Cauchy-Schwarz. The exact moment recurrence instead gives the following
Cauchy lower-bound ratios (R_1(X)^2/(XR_2(X))):

\[
0.1507571\ (10^7),\quad
0.1427721\ (10^8),\quad
0.1356460\ (10^9).
\]

The local growth of (R_2) is about (X^{1.088}), while
(2\sigma-1=1.0656245315\ldots). Hence this unweighted second moment does
not close the required linear estimate.

Exact collisions are structural, not merely finite-scale noise. For example,
the two application-order words

\[
255232\quad\hbox{and}\quad322255
\]

both induce the affine map (x\mapsto600x-381).

## Modular warning

Let (R_a=\{x\bmod 30^a:x\in B\}). Then

\[
\overline d(B)\le |R_a|/30^a.
\]

The independent exact modular orbit counts for (a=1,\ldots,7) are

\[
16,\ 389,\ 10144,\ 274958,\ 7587398,\ 212613518,\ 6011481468.
\]

The corresponding fractions decrease from (0.533333\ldots) to
(0.274873409602). Positive lower density would force these fractions to
remain bounded away from zero. Proving instead that they tend to zero would
prove that this affine subsystem has upper density zero. Neither direction is
currently established.

## Reproduction

B01 code is under `problems/424/compute/wave2/B01`:

```powershell
python problems/424/compute/wave2/B01/analyze_affine.py --limit 10000000
g++ -O3 -std=c++17 problems/424/compute/wave2/B01/census_affine.cpp -o problems/424/compute/wave2/B01/census_affine.exe
problems/424/compute/wave2/B01/census_affine.exe 10000000000
g++ -O3 -std=c++17 problems/424/compute/wave2/B01/moments_affine.cpp -o problems/424/compute/wave2/B01/moments_affine.exe
problems/424/compute/wave2/B01/moments_affine.exe 1000000000
```

The finite calculations are exact integer recurrences. They are diagnostics
and obstruction checks, not a replacement for the missing estimate (6).
