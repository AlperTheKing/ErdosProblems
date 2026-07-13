# C21: shifted-smooth red team

Code: [audit_shifted_smooth.py](../../compute/wave3/C21_shifted_smooth/audit_shifted_smooth.py)

Analyzer: [shifted_smooth.cpp](../../compute/wave3/C21_shifted_smooth/shifted_smooth.cpp)

Exact output: [result.json](../../compute/wave3/C21_shifted_smooth/result.json)

## Verdict

The full shifted-smooth theorem (SR-S) is not proved. Two unconditional
pieces of it are proved.

1. There is an exact infinite counterfamily to pointwise coverage: every
   even square $s=a^2$ has no arithmetically admissible factor pair at all.
   Its smooth reciprocal mass is at most $\pi^2/24$, so this family does not
   obstruct (SR-S).
2. For every fixed $J$, the reciprocal mass of smooth $s$ for which $3s+1$
   has fewer than $J$ admissible pairs is $o_J(\log z)$ along the C11
   parameters. Thus every bounded-multiplicity counterfamily, including all
   shifted primes and bounded almost-primes, is negligible at exactly the
   (SR-S) scale.

The surviving obstruction is a weighted shifted-product sum over missing
$G_2$ endpoints. Section 5 proves that the deterministic estimate

\[
 \mathcal I_z(y)=O(\log z)                                      \tag{C21-G}
\]

would imply (SR-S). No factor independence or positive density of $G$ is
used in this reduction. Estimate (C21-G) is not proved.

The exact census through $s=10^7$ supports the identities and gives finite
nontrivial Cauchy contractions, but no finite row is extrapolated.

## 1. Exact divisor matching

Use C11's notation

\[
 G_2=G\cap\{n:n\equiv2\pmod3\},\qquad m_s=3s+1.
\]

For $m\equiv1\pmod3$, let

\[
 \mathcal P(m)=\{\{a,b\}:2\le a<b,\ ab=m,
                         \ a\equiv b\equiv2\pmod3\},
\]

and put $K(s)=|\mathcal P(m_s)|$. Let $R(s)$ count the pairs in
$\mathcal P(m_s)$ whose two endpoints belong to $G_2$. C11 equation (35)
is the exact equivalence

\[
 s\in T\quad\Longleftrightarrow\quad R(s)>0                 \tag{1}
\]

for every $s\ge2$.

Factor $m=m_1m_2$, where every prime divisor of $m_1$ is $1$ modulo $3$
and every prime divisor of $m_2$ is $2$ modulo $3$. Define

\[
 D_2(m)=\#\{d:d\mid m,\ d\equiv2\pmod3\},
\]

and let $\delta_2(m)=1$ if $m_2$ is a square, and $0$ otherwise. The
quadratic character modulo $3$ gives the exact identity

\[
 \boxed{D_2(m)=\frac{\tau(m_1)(\tau(m_2)-\delta_2(m))}{2}.} \tag{2}
\]

Indeed, the character sum over divisors factorizes. A prime power
$p^e$ with $p\equiv2\pmod3$ contributes
$1-1+\cdots+(-1)^e$, which is $1$ for even $e$ and $0$ for odd $e$.

Let $\epsilon(m)=1$ when $m$ is a square with
$\sqrt m\equiv2\pmod3$, and $0$ otherwise. Complementation
$d\mapsto m/d$ gives

\[
 \boxed{D_2(m)=2K((m-1)/3)+\epsilon(m).}                    \tag{3}
\]

The C21 analyzer asserted (1), (2), and (3) for every analyzed smooth
value, not only at the reported cutoffs.

## 2. An exact smooth counterfamily

**Proposition 1.** If $a\ge2$ is even, then

\[
 \boxed{a^2\notin T.}                                      \tag{4}
\]

**Proof.** Let an odd prime $p$ divide $3a^2+1$. Then

\[
 (3a)^2\equiv-3\pmod p,
\]

so $-3$ is a quadratic residue modulo $p$. Quadratic reciprocity gives

\[
 \left(\frac{-3}{p}\right)=\left(\frac p3\right),
\]

hence $p\equiv1\pmod3$. Since $a$ is even, $3a^2+1$ is odd. Therefore
every prime divisor of $3a^2+1$ is $1$ modulo $3$, so it has no divisor
which is $2$ modulo $3$. Thus $K(a^2)=0$, and (1) proves (4). $\square$

In particular, $s=4q^2$ is a missing $z$-smooth value whenever $q$ is
$z$-smooth. This is an infinite family for every $z\ge2$, but

\[
 \sum_{\substack{q\ge1\\q\ z\text{-smooth}}}\frac1{4q^2}
 \le\frac14\zeta(2)=\frac{\pi^2}{24}.                      \tag{5}
\]

At $(y,z)=(10^7,997)$ the audit found exactly 1,500 members of this family.
Its reciprocal mass lies in the directed interval

\[
 [0.411062559101920402,\ 0.411062559101921872].              \tag{6}
\]

## 3. Splitless mass

The full arithmetic splitless family also has an exact description.

**Lemma 2.** For $s\ge2$, $K(s)=0$ if and only if either

1. $m_s$ has no prime divisor congruent to $2$ modulo $3$, or
2. $m_s=p^2$ for a prime $p\equiv2\pmod3$.

**Proof.** If $p\equiv2\pmod3$ divides $m_s$, then
$p$ and $m_s/p$ are both $2$ modulo $3$. They give an admissible pair
unless they are equal, which is exactly the second case. Both converse
directions are immediate. $\square$

Dropping smoothness and using $1/s=3/(m_s-1)\le4/m_s$ gives

\[
 \begin{aligned}
 \sum_{\substack{2\le s\le y\\K(s)=0}}\frac1s
 &\le 4\prod_{\substack{p\le3y+1\\p\equiv1\ (3)}}
              (1-p^{-1})^{-1}
      +4\sum_p p^{-2} \\
 &=O(\sqrt{\log y}).                                       \tag{7}
 \end{aligned}
\]

The last line uses Mertens' theorem in the progression $1$ modulo $3$.
Under C11 parameters (26),

\[
 \frac{\sqrt{\log y}}{\log z}
 =O\left(\frac{\sqrt{\log\log X}}{(\log X)^{1/4}}\right)
 \longrightarrow0.                                        \tag{8}
\]

Thus the entire splitless reciprocal mass is $o(\log z)$, not just the
even-square subfamily.

## 4. Every fixed multiplicity is negligible

**Proposition 3.** Fix $J\ge2$. Along the coupled C11 parameters,

\[
 \boxed{
 \sum_{\substack{2\le s\le y\\P^+(s)\le z\\K(s)<J}}\frac1s
 =o_J(\log z).}                                             \tag{9}
\]

**Proof.** The $K=0$ part is (7). Suppose $1\le K(s)<J$. From (2) and
(3),

\[
 \tau(m_1)(\tau(m_2)-\delta_2(m_s))
 =2D_2(m_s)\le4J-2.                                        \tag{10}
\]

Since $\tau(n)\ge\Omega(n)+1$, equation (10) gives

\[
 \Omega(m_1)\le4J-3,\qquad
 \Omega(m_2)\le4J-2,
\]

and hence $\Omega(m_s)\le8J-5$. For fixed $L$,

\[
 \sum_{\substack{n\le Y\\\Omega(n)\le L}}\frac1n
 \le 1+\sum_{k=1}^L\left(\sum_{p\le Y}\frac1p\right)^k
 =O_L((\log\log Y)^L).                                     \tag{11}
\]

Again dropping smoothness and using $1/s\le4/m_s$, the positive-$K$ part
of (9) is

\[
 O_J((\log\log y)^{8J-5})=o_J(\log z),                    \tag{12}
\]

because $\log z=\sqrt{\log X}/\sqrt{\log\log X}$. Combine (7) and
(12). $\square$

This is the smooth, harmonically weighted counterpart of C20's rough
low-multiplicity lemma. Neither proof uses membership statistics for $G$.

## 5. Weighted blocker identity

Let

\[
 \mathcal H_2=\{h\ge2:h\equiv2\pmod3,\ h\notin G\},
 \qquad \mathcal A_2=\{e\ge2:e\equiv2\pmod3\}.
\]

For a pair $\{a,b\}\in\mathcal P(m)$, count one blocking incidence for
each endpoint outside $G_2$, and let $I_G(m)$ be the total. Pairwise,

\[
 \boxed{K(s)-R(s)\le I_G(m_s)\le2(K(s)-R(s)).}              \tag{13}
\]

In particular, if $s\notin T$, then $K(s)\le I_G(m_s)\le2K(s)$. Summing
over the smooth set $\mathcal S_z(y)=\{2\le s\le y:P^+(s)\le z\}$ gives
the exact shifted-product identity

\[
 \begin{aligned}
 \mathcal I_z(y)
 &:=\sum_{s\in\mathcal S_z(y)}\frac{I_G(3s+1)}s \\
 &=\sum_{\substack{h\in\mathcal H_2,\ e\in\mathcal A_2\\
                    h\ne e, (he-1)/3\in\mathcal S_z(y)}}
       \frac3{he-1}.                                       \tag{14}
 \end{aligned}
\]

If both endpoints are holes, the two ordered choices of $h$ in (14) give
the required two incidences. There is no independence assumption.

For any fixed $J\ge2$, Propositions 1--3 and (13) imply

\[
 \begin{aligned}
 W_z(y)
 &=\sum_{\substack{s\in\mathcal S_z(y)\\R(s)=0}}\frac1s \\
 &\le o_J(\log z)+\frac1J\mathcal I_z(y).                  \tag{15}
 \end{aligned}
\]

Consequently, (C21-G) implies (SR-S): if
$\mathcal I_z(y)\le C\log z$ eventually, then

\[
 \limsup\frac{W_z(y)}{\log z}\le\frac CJ
\]

for every fixed $J$, and then $J\to\infty$ forces the limsup to zero.

This is the remaining C21 frontier. The closure recursion proves the
endpoint labels in (14), but it does not currently bound their total mass.

## 6. Deterministic moment contraction

Put

\[
 H=\sum_{s\in\mathcal S_z(y)}\frac1s,\quad
 A_1=\sum_{s\in\mathcal S_z(y)}\frac{R(s)}s,\quad
 A_2=\sum_{s\in\mathcal S_z(y)}\frac{R(s)^2}s.
\]

Weighted Cauchy--Schwarz gives

\[
 \sum_{\substack{s\in\mathcal S_z(y)\\R(s)>0}}\frac1s
 \ge\frac{A_1^2}{A_2},
 \qquad
 \boxed{\frac{W_z(y)}H\le1-\frac{A_1^2}{A_2H}.}            \tag{16}
\]

This contraction is exact and deterministic. Its moments are shifted-smooth
hyperbola sums over $G_2$ pairs and pair collisions; proving the right side
of (16) is $o(1)$ remains at least as distributional as (SR-S).

## 7. Exact finite census

The audit constructed $G[0..30{,}000{,}001]$ by the accepted ascending
recursion and factored every $3s+1$ for $2\le s\le10^7$. It used the five
integer cutoffs

\[
 y\in\{10^3,10^4,10^5,10^6,10^7\}
\]

and 14 integer smoothness cutoffs from $2$ through $997$. Every harmonic
sum is enclosed by directed integer bounds with denominator $10^{18}$.

The following are the $y=10^7$ rows. Decimal ratios are displays of the
rational intervals in `result.json`.

| $z$ | smooth | missing | splitless | blocked | unique-pair blocked | $W/H$ | splitless/$H$ | blocked/$H$ | Cauchy covered lower | $\mathcal I/H$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 4,519 | 3,012 | 2,113 | 899 | 590 | .782313238711 | .559857539605 | .222455699106 | .215873488223 | .311651178354 |
| 29 | 37,626 | 21,986 | 15,042 | 6,944 | 4,372 | .749747114544 | .492122258150 | .257624856395 | .240711492004 | .475744971337 |
| 97 | 269,881 | 134,382 | 89,359 | 45,023 | 26,851 | .718780816624 | .435723669164 | .283057147460 | .253307422506 | .665734789495 |
| 997 | 2,028,357 | 842,475 | 546,505 | 295,970 | 166,542 | .646287266297 | .374857401922 | .271429864375 | .288689463327 | .943191874781 |

At $(10^7,997)$ the missing counts by arithmetic-pair bin
$0,1,2,3,4,5$--$7,8$--$15,16+$ are exactly

~~~text
546505, 166542, 100559, 9674, 14827, 3486, 878, 4.
~~~

The corresponding reciprocal-mass fractions of $H$ are approximately

~~~text
.374857401922, .178477858769, .070709452165, .011994159671,
.007520547130, .002432782271, .000294577246, .000000487123.
~~~

These values illustrate why bounded multiplicity is the correct first
disposal, but they establish no trend.

The final run obtained

\[
 |G\cap[1,30{,}000{,}001]|=15{,}234{,}504
\]

and matched the accepted counts and byte hashes through $10^6$ and $10^7$.
Every row asserted the membership equivalence (1), divisor identities
(2)--(3), blocker inequality (13), splitless characterization, and the
even-square counterfamily.

## 8. Novelty and limits

The [official problem record](https://www.erdosproblems.com/424), checked
2026-07-13, remains open and lists no claimed partial solution. The
[OEIS entry A005244](https://oeis.org/A005244) contains no even-square or
shifted-harmonic observation. Targeted searches for the formulas in
Sections 2--5 found no matching result. This is a bounded novelty check,
not a claim that all literature has been exhausted.

The standard inputs used above are quadratic reciprocity, Mertens' theorem
in the progression $1$ modulo $3$, and the prime reciprocal estimate. None
of them estimates recursive membership in $G_2$. The new reduction stops
exactly at that missing distributional input, (C21-G).

## 9. Reproduction

From the repository root:

~~~powershell
python problems/424/compute/wave3/C21_shifted_smooth/audit_shifted_smooth.py `
  --limit 10000000 `
  --output problems/424/compute/wave3/C21_shifted_smooth/result.json
~~~

Two independent final runs produced byte-identical `result.json` files.
Recorded SHA-256 values are

~~~text
shifted_smooth.cpp       739B12C4F051BA4BD12A937AA5EC2DBC5D2B7139DCF575DFACC2404E9419D7CE
audit_shifted_smooth.py  3AE7F95EB7B19D878ED8599D9F74E7235559F607BB392CAC36C773ABFC58B132
result.json              134037816470BE7E890E7C18396911D5A2A86E0EAC3EDD4CAA42F34B7935A93E
G[0..30000001] bitmap    08677E7D4A444A4266865F701183608AE07E342BD639A64E69B95AA290695D16
~~~

The computation is a finite certificate. It does not prove (C21-G),
(SR-S), or positive density for $G$.

## Execution ledger

[2026-07-13T09:53:03+03:00] > PLAN | NEXT: Build exact SR-S census separating splitless from G2-blocked shifts and test moment contraction.
[2026-07-13T10:05:45+03:00] OK ATTACK | DID: Exact smoke audit, s<=1000 | RESULT: all C++/Python assertions pass | D: none
[2026-07-13T10:05:45+03:00] > ATTACK | NEXT: Run exact census with s<=10^7, G<=30000001, 14 z cutoffs, rational scale 10^18.
[2026-07-13T10:06:51+03:00] FAIL ATTACK | DID: Ran s<=10^7 audit | RESULT: WinError 32 unlinking open G memmap; no result.json | D: wrapper fix
[2026-07-13T10:06:51+03:00] > ATTACK | NEXT: Rerun identical census using byte-prefix verification without mmap.
[2026-07-13T10:07:56+03:00] FAIL ATTACK | DID: Repeated s<=10^7 audit | RESULT: WinError 32 persisted without mmap; no result.json | D: cleanup retry
[2026-07-13T10:07:56+03:00] > ATTACK | NEXT: Rerun identical census with 50x100ms bounded unlink retry.
[2026-07-13T10:12:19+03:00] OK ATTACK | DID: Exact s<=10^7 census | RESULT: 70 rows and all assertions pass | D: finite certificate
[2026-07-13T10:12:19+03:00] > VERIFY | NEXT: Add character formula, blocker mass, and even-square assertions; rerun twice.
[2026-07-13T10:21:33+03:00] OK VERIFY | DID: Two s<=10^7 reruns plus -Werror build | RESULT: byte-identical SHA-256 13403781..., AST_OK, C++ warnings zero | D: verified
[2026-07-13T10:21:33+03:00] > GATE | NEXT: Check current official #424 record, OEIS A005244, and targeted formula searches.
[2026-07-13T10:21:33+03:00] OK GATE | DID: Checked official record, OEIS, targeted searches | RESULT: no listed partial solution or matching formula found | D: write-up
[2026-07-13T10:22:57+03:00] > DECIDE | NEXT: Freeze the verified C21 partial theorem, obstruction, exact output, and reproduction hashes.
[2026-07-13T10:23:25+03:00] OK DECIDE | DID: Froze C21 artifacts | RESULT: hashes and JSON source links match; only five C21 paths modified | D: lane complete
