# C20: shifted-sifted factorization on the rough frontier

Code: [shifted_sifted_audit.cpp](../../compute/wave3/C20_shifted_sifted/shifted_sifted_audit.cpp)

Exact output: [result.json](../../compute/wave3/C20_shifted_sifted/result.json)

## Verdict

The full theorem (SR-R) is not proved. A uniform arithmetic-multiplicity
lemma is proved: for every fixed $K$, the $r$ for which $3r+1$ has fewer
than $K$ distinct arithmetically admissible factor pairs contribute
$o(R/\log z)$ throughout the entire mesoscopic cutoff interval. Thus
primes, bounded almost-primes, and every other bounded-witness exception
are negligible at exactly the scale required by (SR-R).

Raw multiplicity does not transfer to $G_2$-multiplicity. The exact census
contains an 11-rough missing value with 20 admissible pairs, all blocked.
More sharply, it contains an 11-rough missing value with 12 pairs and
exactly one $G_2$ endpoint in every pair. Hence the natural half-divisor
pigeonhole bound is pointwise sharp even after the number of pairs is well
above one.

The remaining input is a distribution theorem for membership in $G_2$
among complementary divisors of the shifted values $3r+1$. Standard
almost-prime and divisor-location estimates do not provide this recursive
membership correlation.

Section 4 gives a strictly weaker quantified rough statement sufficient for
positive density: a fixed positive proportion of rough values satisfying a
strict $G_2$ divisor-majority condition is enough. It is not proved here.

## 1. Divisor matching

For $m\equiv1\pmod3$ with $3\nmid m$, define

\[
D_2(m)=\#\{d:d\mid m,\ d\equiv2\pmod3\}
\]

and

\[
A(m)=\#\{(a,b):2\leq a<b,\ ab=m,\ a\equiv b\equiv2\pmod3\}.
\]

Let $\epsilon(m)$ be 1 when $m$ is a square and
$\sqrt m\equiv2\pmod3$, and 0 otherwise. Complementation
$d\mapsto m/d$ partitions the residue-2 divisors into $A(m)$ two-element
orbits and, when $\epsilon(m)=1$, one fixed point. Therefore

\[
\boxed{D_2(m)=2A(m)+\epsilon(m).} \tag{1}
\]

For a relevant rough $r$, put $m_r=3r+1$. Since $2,3\leq z$, $r$ is odd
and $3\nmid r$, so $m_r$ is even, $m_r\equiv1\pmod3$, and (1) applies.
The pairs counted by $A(m_r)$ are exactly the arithmetic candidates for
$\mathcal W(r)$ from C11.

## 2. Arithmetic multiplicity lemma

**Lemma 1.** If $m$ is even and $m\equiv1\pmod3$, then

\[
D_2(m)\geq\frac{\tau(m)}3,
\qquad
A(m)\geq\frac{\tau(m)}6-\frac12
       \geq\frac{\Omega(m)-2}{6}. \tag{2}
\]

Here $\Omega$ counts prime factors with multiplicity.

**Proof.** Let $\chi$ be the nonprincipal character modulo 3. If
$m=\prod p^{e_p}$, then

\[
\sum_{d\mid m}\chi(d)
=\prod_{p^{e_p}\parallel m}(1+\chi(p)+\cdots+\chi(p)^{e_p}). \tag{3}
\]

If some prime $p\equiv2\pmod3$ has odd exponent, its factor in (3) is
zero, so exactly $\tau(m)/2$ divisors are 2 modulo 3. Otherwise every such
exponent is even. The prime 2 occurs to an even exponent at least 2, since
$m$ is even. Writing

\[
B=\prod_{p\equiv2\ (3)}(e_p+1),
\qquad
C=\prod_{p\equiv1\ (3)}(e_p+1),
\]

gives $B\geq3$, $\tau(m)=BC$, and

\[
D_2(m)=\frac{C(B-1)}2\geq\frac{BC}{3}=\frac{\tau(m)}3.
\]

Equation (1) proves the middle inequality in (2). Finally,
$\tau(m)=\prod(e_p+1)\geq1+\sum e_p=1+\Omega(m)$, proving the last one.
$\square$

**Lemma 2 (uniform low-multiplicity disposal).** Fix $K\geq1$. Along the
coupled parameters (26), uniformly for

\[
\lfloor X/y\rfloor\leq R\leq\lfloor X/L\rfloor,
\]

one has

\[
\boxed{
\#\{2\leq r\leq R:(r,P(z))=1,\ A(3r+1)<K\}
=o_K(R/\log z).} \tag{4}
\]

**Proof.** By Lemma 1, $A(3r+1)<K$ implies
$\Omega(3r+1)\leq6K+1$. The standard fixed-$j$ Landau estimate

\[
\#\{n\leq t:\Omega(n)=j\}
\ll_j\frac{t(\log\log t)^{j-1}}{\log t}
\]

and the injectivity of $r\mapsto3r+1$ give the stronger bound

\[
O_K\left(\frac{R(\log\log R)^{6K}}{\log R}\right), \tag{5}
\]

without using the roughness condition. In the displayed cutoff interval,
$\log R\sim\log X$ uniformly, while

\[
\log z=\frac{\sqrt{\log X}}{\sqrt{\log\log X}}.
\]

Multiplying (5) by $\log z/R$ tends to zero uniformly, proving (4).
$\square$

For every fixed $K$, therefore, bounded arithmetic multiplicity is too
small to obstruct (SR-R). Equivalently, a diagonal choice $K(X)\to\infty$
can be made so slowly that the candidates with $A(3r+1)<K(X)$ still have
size $o(R/\log z)$ uniformly over the cutoff interval.

## 3. Exact blocker lemma and obstruction

Put

\[
C_G(m)=\#\{d\mid m:d\equiv2\pmod3,\ d\in G_2\},
\quad
B_G(m)=D_2(m)-C_G(m).
\]

The complementary divisor pairs form a matching. A pair is a witness
exactly when both endpoints lie in $G_2$. Thus:

**Lemma 3.** If $\mathcal W(r)=\varnothing$, then

\[
\boxed{
B_G(m_r)\geq A(m_r),
\qquad
C_G(m_r)\leq A(m_r)+\epsilon(m_r).} \tag{6}
\]

Conversely, the strict divisor-majority condition

\[
\boxed{C_G(m_r)>A(m_r)+\epsilon(m_r)} \tag{7}
\]

forces $\mathcal W(r)\ne\varnothing$.

This is the exact pigeonhole threshold. For a miss with $A(m_r)\geq K$,
(1) and (6) imply

\[
\frac{B_G(m_r)}{D_2(m_r)}
\geq\frac{A(m_r)}{2A(m_r)+1}
\geq\frac12-\frac1{4K+2}. \tag{8}
\]

Combining Lemmas 2 and 3 isolates the analytic obstruction: a proof of
(SR-R) must show that shifted rough values for which roughly half of the
residue-2 divisors are absent from $G_2$, arranged as a vertex cover of the
complementary-divisor matching, have size $o(R/\log z)$. Counting divisors,
locating divisors in intervals, or proving that $A(m_r)\to\infty$ outside a
negligible set does not estimate this $G_2$-membership bias.

## 4. Strictly weaker positive-density gate

The full (SR-R) estimate asks for normalized miss count tending to zero. A
strictly weaker sufficient condition is: for some fixed $\delta>0$,

\[
\boxed{
\inf_{\lfloor X/y\rfloor\leq R\leq\lfloor X/L\rfloor}
\frac{\log z}{R}
\#\{2\leq r\leq R:(r,P(z))=1,\ \mathcal W(r)\ne\varnothing\}
\geq\delta+o(1).} \tag{SR-R+}
\]

Indeed, (SR-R) implies (SR-R+) for every fixed
$0<\delta<e^{-\gamma}$, while (SR-R+) asks only for a fixed positive
relative proportion of the rough values.

The uniform rough-number asymptotic says that the same normalization for
all rough $r$ tends to $e^{-\gamma}$. Hence (SR-R+) gives

\[
\sup_R\frac{\log z}{R}
\#\{r\leq R:(r,P(z))=1,\ \mathcal W(r)=\varnothing\}
\leq e^{-\gamma}-\delta+o(1). \tag{9}
\]

Since $H_z(y)\sim e^\gamma\log z$, C11 equation (28) then gives

\[
E_{r,L}\leq(1-e^\gamma\delta+o(1))X. \tag{10}
\]

If the ambient and smooth errors are $o(X)$, as required separately in the
C11 window certificate, (10) leaves at least
$(e^\gamma\delta-o(1))X$ certified products. Thus density one among rough
values is unnecessary; any fixed positive relative density suffices.

By Lemma 3, the following divisor-majority statement is a concrete
sufficient target for (SR-R+):

\[
\boxed{
\inf_R\frac{\log z}{R}
\#\{r\leq R:(r,P(z))=1,\
 C_G(3r+1)>A(3r+1)+\epsilon(3r+1)\}
\geq\delta+o(1).} \tag{DM+}
\]

No bound with a fixed $\delta>0$ is proved here.
The divisor-majority property is stronger pointwise than merely having one
witness, so (DM+) and (SR-R) are not formally comparable.

## 5. Exact falsifiers

The audit rebuilt the exact distinct-input closure through 19,999,998 and
analyzed every relevant rough value for the three recorded cutoffs. It
asserted Lemma 1, the exact matching identities, and
$r\in T\Longleftrightarrow\mathcal W(r)\ne\varnothing$ at every candidate.

| $R$ | $z$ | rough | $T$-miss | strict-majority certificates | misses with exactly one $G_2$ endpoint per pair | maximum $A$ among misses |
|---:|---:|---:|---:|---:|---:|---:|
| 200,000 | 9 | 45,714 | 5,911 | 29,391 | 3,894 | 18 |
| 2,000,000 | 11 | 415,584 | 31,059 | 310,368 | 21,743 | 20 |
| 6,666,666 | 11 | 1,385,280 | 81,685 | 1,099,131 | 59,636 | 20 |

The raw-multiplicity falsifier is

\[
r=258133,\qquad
3r+1=774400=2^8\cdot5^2\cdot11^2.
\]

It is 11-rough, $A(3r+1)=20$, and $r\notin T$. Of its 20 pairs, 12 have
exactly one endpoint in $G_2$ and 8 have neither endpoint in $G_2$. The
output records all 20 pairs and both endpoint membership bits.

The half-threshold falsifier is

\[
r=1732597,\qquad
3r+1=5197792=2^5\cdot19\cdot83\cdot103.
\]

It is 11-rough and missing from $T$. Here

\[
D_2(3r+1)=24,\qquad A(3r+1)=12,\qquad C_G(3r+1)=12,
\]

and every one of the 12 complementary pairs has exactly one endpoint in
$G_2$. Thus replacing the strict inequality in (7) by a weak half-density
condition is exactly false, even at arithmetic multiplicity 12.

These are finite falsifiers. They disprove pointwise multiplicity-transfer
lemmas but do not rule out an almost-all transfer theorem as
$A(3r+1)\to\infty$.

## 6. Literature and reproduction boundary

The [official problem record](https://www.erdosproblems.com/424) was checked
on 2026-07-13 and remains open with no listed partial solution. Ford's
divisor-in-an-interval theorem estimates arithmetic divisor locations, not
membership in the recursively defined $G_2$. The shifted multiplicative
subgroup results of Kim--Yip--Yoo concern finite-field subgroup containment
and likewise do not estimate $C_G(3r+1)$.

Run from the repository root with assertions enabled:

~~~powershell
g++.EXE -O3 -std=c++20 -Wall -Wextra -Wpedantic problems/424/compute/wave3/C20_shifted_sifted/shifted_sifted_audit.cpp -o problems/424/compute/wave3/C20_shifted_sifted/shifted_sifted_audit.exe

problems/424/compute/wave3/C20_shifted_sifted/shifted_sifted_audit.exe problems/424/compute/wave3/C20_shifted_sifted/result.json
~~~

The run matched the independent reference count
$|G\cap[1,10^7]|=4,952,270$ and checked 1,389,436 distinct rough
candidates. All arithmetic in the assertions and output is integer-exact.
The finite tables are not extrapolated to an asymptotic claim.
