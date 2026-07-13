# P49: known-theorem bridge for same-parity three-free Sidon sets

## Verdict

No complete applicable theorem chain was found.

The closest load-bearing bridge is strong 4-independence in a cyclic group.
For an **odd** positive integer set, literal Sidonicity together with

\[
                         E\cap 3E=\varnothing                         \tag{1}
\]

is exactly strong 4-independence over the integers. Bajnok--Ruzsa proved
only

\[
 s(\mathbb Z_n,4)\leq (1/\sqrt2+o(1))\sqrt n,                         \tag{2}
\]

and conjectured the sharp cyclic value

\[
 s(\mathbb Z_n,4)=(1/\sqrt3+o(1))\sqrt n.                             \tag{3}
\]

If reduction modulo \(M+1\), where \(M=\max E\), preserved
4-independence, then (3) would give
\(M\geq(3-o(1))|E|^2\). This is not an available theorem chain for two
independent reasons:

1. (3) is Bajnok--Ruzsa Conjecture 15, not a theorem;
2. the required reduction modulo \(M+1\) is false, even for an odd valid
   set and even at a diagonal pair sum.

There is a third obstruction for the stated target: an even same-parity
valid set need not be strongly 4-independent over the integers.

The classical Golomb-ruler theorem is rigorously applicable and, after
using parity, gives

\[
                         M\geq (2-o(1))|E|^2,                          \tag{4}
\]

but none of the audited \(B_h\), Freiman, support-polynomial, or
sum/difference results supplies the missing leading unit.

## 1. Exact support formulation

Let \(E=\{e_1<\cdots<e_p=M\}\) be positive and of one parity. Put

\[
 \begin{aligned}
 S_2(E)&=\{a+b:a,b\in E,\ a\leq b\},\\
 D^+(E)&=\{b-a:a,b\in E,\ a<b\}.
 \end{aligned}                                                        \tag{5}
\]

All diagonal sums \(2a\) occur in \(S_2(E)\). If \(E\) is Sidon, then

\[
 |S_2(E)|=\binom{p+1}{2},\qquad |D^+(E)|=\binom p2.                    \tag{6}
\]

The second equality includes a hypothesis check often lost in terminology:
if \(b-a=d-c>0\), then \(b+c=d+a\), and Sidonicity identifies the
oriented endpoint pairs.

Moreover,

\[
 E\cap3E=\varnothing
 \quad\Longleftrightarrow\quad
 S_2(E)\cap D^+(E)=\varnothing.                                      \tag{7}
\]

Indeed, a cross collision is

\[
 b-a=c+d\quad\Longleftrightarrow\quad b=a+c+d.                        \tag{8}
\]

Here \(c=d\) is allowed, and \(a\) may equal either of them. Thus (7)
uses every diagonal and every repeated summand in (1). Positivity makes
the orientation automatic: the element on the one-term side is larger
than the summand moved across.

Since all sums and differences in (5) are even, define the half-supports

\[
 \mathcal S=\{(a+b)/2:a\leq b\},\qquad
 \mathcal D=\{(b-a)/2:a<b\}.                                         \tag{9}
\]

They are disjoint sets of positive integers, both contained in \([1,M]\),
and

\[
                 |\mathcal S|+|\mathcal D|=p^2.                      \tag{10}
\]

Consequently the bare restricted sum/difference packing gives only

\[
                              M\geq p^2.                              \tag{11}
\]

This is sharp as a support statement: \(E=\{2,4\}\) is valid and has

\[
 \mathcal D=\{1\},\qquad \mathcal S=\{2,3,4\},\qquad M=p^2=4.         \tag{12}
\]

### Polynomial version

For \(P(x)=\sum_{e\in E}x^e\), diagonal-inclusive Sidonicity says

\[
 P(x)^2=\sum_{e\in E}x^{2e}
       +2\sum_{a<b}x^{a+b},                                          \tag{13}
\]

with no collisions between the displayed exponents, while

\[
 P(x)P(x^{-1})
   =p+\sum_{a<b}(x^{b-a}+x^{a-b})                                    \tag{14}
\]

has coefficient one at each nonzero exponent. Condition (1) is exactly
the disjointness of the positive nonconstant supports in (13)--(14).
Thus a theorem using only support cardinality recovers (10)--(11), and
the example (12) saturates it. A coefficient-three result must use the
ordered placement of these two supports, not merely their sizes or their
disjointness.

## 2. The closest bridge: cyclic strong 4-independence

### 2.1 Exact match in the odd integer case

Bajnok--Ruzsa Definition 1 calls \(A\) strongly \(t\)-independent when
every relation

\[
                  \sum_{a\in A}\lambda_a a=0,
             \qquad \sum_{a\in A}|\lambda_a|\leq t                  \tag{15}
\]

is trivial. Coefficients are arbitrary integers, so repetitions are
included. Their weak independence notion instead restricts coefficients
to \(\{-1,0,1\}\), and is not applicable here.

If every element of \(E\) is positive and odd, then

\[
 \boxed{E\text{ is strongly 4-independent over }\mathbb Z
 \iff E\text{ is Sidon and }E\cap3E=\varnothing.}                    \tag{16}
\]

To verify every case, cancel common terms from the two sides of a relation
of total length at most four. Positivity excludes a nonempty sum equal to
zero; odd parity excludes one term equalling two terms; Sidonicity handles
two terms versus two terms, including diagonals; and (1) handles one term
versus three terms, including repetitions. These exhaust the possibilities.

Weak independence cannot replace (16): \(\{1,3\}\) has no nonzero signed
relation with coefficients in \(\{-1,0,1\}\), but

\[
                             3=1+1+1.                                \tag{17}
\]

### 2.2 Exact cyclic theorem and constant

For \(s(\mathbb Z_n,4)\), the largest strongly 4-independent subset of
the cyclic group, Bajnok--Ruzsa Corollary 14 proves, for every fixed
positive \(\epsilon,\delta\) and all sufficiently large \(n\),

\[
 (1/\sqrt8-\epsilon)\sqrt n
 \leq s(\mathbb Z_n,4)
 \leq(1/\sqrt2+\delta)\sqrt n.                                      \tag{18}
\]

Their immediately following Conjecture 15 is

\[
                  \lim_{n\to\infty}
                  \frac{s(\mathbb Z_n,4)}{\sqrt n}
                  =\frac1{\sqrt3}.                                  \tag{19}
\]

The source's strong definition permits repeated summands, so (18)--(19)
have the right convention. Numerically, however, only the conjecture has
the target constant. Even under a valid interval-to-cycle transfer with
\(n=M+1\), the proved upper bound (18) would yield only
\(M\geq(2-o(1))p^2\).

### 2.3 The required interval-to-cycle transfer is false

Take

\[
                              E_0=\{1,7,11\}.                          \tag{20}
\]

Its complete certificates are

\[
 S_2(E_0)=\{2,8,12,14,18,22\},\qquad
 D^+(E_0)=\{4,6,10\}.                                                 \tag{21}
\]

The six pair sums in (21) are distinct, including the three diagonals,
and the two displayed sets are disjoint. By (7), \(E_0\cap3E_0\) is
empty with repeated summands allowed. Since \(E_0\) is odd, it is
strongly 4-independent over the integers by (16).

But \(M+1=12\), and in \(\mathbb Z_{12}\) there is the nontrivial
diagonal collision

\[
                      1+1\equiv7+7\pmod {12}.                         \tag{22}
\]

Thus the residue image is not even modular Sidon, hence is not strongly
4-independent. This falsifies the exact transfer that would turn (19)
into the target theorem.

Choosing a safely large modulus destroys the constant. Reduction modulo
any \(n>4M\) does preserve all integer relations of \(\ell_1\)-length at
most four, because their absolute values are below \(n\). Taking
\(n=4M+1\), however, (18) gives only

\[
                             M\geq(1/2-o(1))p^2,                       \tag{23}
\]

and even the conjectural (19) would give only
\(M\geq(3/4-o(1))p^2\). The useful modulus must therefore be of size
\(M+o(p^2)\), exactly where carry relations such as (22) are uncontrolled.

### 2.4 Even parity is a separate hypothesis failure

The valid set \(E=\{2,4\}\) from (12) satisfies

\[
 S_2(E)=\{4,6,8\},\qquad D^+(E)=\{2\},                                \tag{24}
\]

so it is Sidon and disjoint from \(3E\), with diagonals and repetitions
checked. Nevertheless,

\[
                                4=2+2,                                \tag{25}
\]

so it is not strongly 4-independent even over \(\mathbb Z\). Dividing
by two gives \(\{1,2\}\) and leaves the same one-versus-two obstruction.
Therefore a cyclic strong-independence theorem cannot cover all
same-parity target sets without an additional argument.

## 3. Why the nearby theorem classes do not repair the bridge

### 3.1 \(B_h\) and "sum-free Sidon" theorems

A genuine \(B_3\) set has all unordered three-term sums unique, including
repetitions. That would be far stronger than needed: direct counting gives

\[
 \binom{p+2}{3}\leq |3E|\leq3M,
 \qquad M\geq\frac13\binom{p+2}{3}.                                  \tag{26}
\]

The target hypotheses do not imply \(B_3\). The valid set

\[
                         E_1=\{1,7,19,23\}                            \tag{27}
\]

has

\[
 \begin{aligned}
 S_2(E_1)&=\{2,8,14,20,24,26,30,38,42,46\},\\
 D^+(E_1)&=\{4,6,12,16,18,22\},
 \end{aligned}                                                       \tag{28}
\]

which certifies Sidonicity and (1), but

\[
                         21=1+1+19=7+7+7.                             \tag{29}
\]

Thus repeated three-sum representations are allowed and actually occur.
Every \(B_h\) theorem with \(h\geq3\) misses at (29), while a \(B_2[g]\)
theorem is weaker than the already exact \(B_2[1]\) hypothesis.

Nathanson's primary source uses "sum-free Sidon" for a Sidon set satisfying
\(S\cap2S=\varnothing\), not \(S\cap3S=\varnothing\). For odd \(S\),
that sum-free condition is automatic by parity and adds no information;
for even target sets it is not a hypothesis, as (25) shows. Hence the
theorems under that name do not address the load-bearing equation.

Bajnok Theorem 6 exactly determines the maximum
\((3,1)\)-sum-free density in every cyclic group; in particular it lies
between \(1/5\) and \(1/3\) of the group order. Its definition allows
repeated summands, but the theorem has no Sidon hypothesis. This omission
is concrete: \(\{4,5,6\}\cap3\{4,5,6\}=\varnothing\), while
\(4+6=5+5\). Separate extremal theorems for \(B_2\) and for
\((3,1)\)-sum-free sets cannot be intersected to obtain a bound for sets
satisfying both.

### 3.2 Freiman-type inequalities and modeling

For every diagonal-inclusive Sidon set,

\[
                         |E+E|=\binom{p+1}{2},                         \tag{30}
\]

so its doubling constant is \((p+1)/2\), not bounded. The small-doubling
regime of Freiman theory is therefore absent. Concretely, Lev--Smeliansky
Theorem 1(ii), after the source's normalization and diameter hypotheses,
gives \(|2A|\geq3|A|-3\); (30) is already at least this large and is
quadratic in \(p\). That theorem supplies no information about where
\(S_2(E)\) lies relative to \(D^+(E)\).

There is also a structural invariance mismatch. Ordinary Freiman
isomorphisms preserve balanced equal-length sum equations. The equation

\[
                              a+b+c=d                                \tag{31}
\]

is not translation invariant. Translation itself is a Freiman
isomorphism of every ordinary order, yet it does not preserve (1):
\(\{2,4\}\) is valid, while its translate \(\{1,3\}\) fails because of
(17). A usable modeling theorem would have to preserve the specific
unbalanced form (31), all repeated variables, and interval scale
\(M+o(p^2)\). Standard Freiman rectification supplies none of these three
features; (22) is the explicit failure of the naive model.

### 3.3 Golomb-ruler density

Carter--Hunter--O'Bryant prove that a \(p\)-element integer Sidon set
\(Z\) has

\[
 \operatorname{diam}(Z)
 \geq p^2-1.96365p^{3/2}-O(p).                                        \tag{32}
\]

Their Sidon definition is the full equation \(a+b=c+d\), with only equal
unordered pairs declared trivial, so diagonal collisions are excluded.
It is therefore exactly applicable here.

Let \(m=\min E\) and

\[
                         Z=(E-m)/2.                                  \tag{33}
\]

Same parity makes \(Z\) integral, Sidonicity passes to \(Z\), and

\[
 \operatorname{diam}(Z)=\frac{M-m}{2}.                               \tag{34}
\]

Equations (32)--(34) rigorously give

\[
 M\geq 2p^2-3.92730p^{3/2}-O(p)+m
   =(2-o(1))p^2.                                                      \tag{35}
\]

This is the strongest directly applicable audited theorem chain, but its
proof uses only uniqueness of differences. The structured exclusion
\(D^+(E)\cap S_2(E)=\varnothing\) is not among its hypotheses, so (32)
cannot provide the additional \(p^2\) required by the target.

## 4. The theorem that is still missing

Write the exact signed-ruler normalization as

\[
 Z=\{0=z_0<\cdots<z_{p-1}=W\},\qquad E=G+2Z,\quad G\geq1.             \tag{36}
\]

Then every hypothesis, including diagonals and repeated triple summands,
is equivalent to

\[
 Z\text{ is Sidon},\qquad
 D^+(Z)\cap\bigl(G+S_2(Z)\bigr)=\varnothing.                         \tag{37}
\]

The required load-bearing theorem is precisely the order-sensitive
strengthening

\[
 \boxed{
 (37)\quad\Longrightarrow\quad
 G+2W\geq(3-o(1))p^2.}                                                \tag{38}
\]

No audited primary theorem states (38) or a stronger applicable result.
The closest cyclic route would need both:

1. a rectification theorem preserving strong 4-independence in a cyclic
   group of order \(M+o(p^2)\), despite the falsifier (20)--(22); and
2. the still-unproved Bajnok--Ruzsa Conjecture 15.

It would also need a separate reduction for even valid sets because of
(24)--(25). The polynomial/support route restates (37) but stops at the
sharp support bound (11), Freiman inequalities do not preserve (31), and
the Golomb theorem stops at (35). Therefore P49 returns a precise negative
bridge verdict, not a coefficient-three theorem.

## Primary sources

1. Bela Bajnok and Imre Z. Ruzsa,
   [*The independence number of a subset of an abelian group*](https://math.colgate.edu/~integers/d2/d2.pdf),
   *Integers* **3** (2003), A02. Definition 1 permits repetitions;
   Corollary 14 is (18), and Conjecture 15 is (19).
   [arXiv:1512.03037](https://arxiv.org/abs/1512.03037).
2. Daniel Carter, Zach Hunter, and Kevin O'Bryant,
   [*On the diameter of finite Sidon sets*](https://doi.org/10.1007/s10474-024-01499-8),
   *Acta Mathematica Hungarica* **175** (2025), 108--126. Its main
   theorem is (32); the paper also gives a weaker hand-verifiable constant
   with the same leading term.
   [arXiv:2310.20032](https://arxiv.org/abs/2310.20032).
3. Vsevolod F. Lev and Pavel Y. Smeliansky,
   [*On addition of two distinct sets of integers*](https://doi.org/10.4064/aa-70-1-85-91),
   *Acta Arithmetica* **70** (1995), 85--91. Theorem 1 gives the
   Freiman-type lower bounds discussed after (30).
4. Melvyn B. Nathanson,
   [*N-graphs, modular Sidon and sum-free sets, and partition identities*](https://arxiv.org/abs/math/0002173),
   *Ramanujan Journal* **4** (2000), 59--67,
   [doi:10.1023/A:1009830023023](https://doi.org/10.1023/A:1009830023023).
   Section 2 defines "sum-free Sidon" using \(S\cap2S=\varnothing\).
5. Bela Bajnok,
   [*On the maximum size of a \((k,l)\)-sum-free subset of an abelian group*](https://arxiv.org/abs/0803.4486),
   *International Journal of Number Theory* **5** (2009), 953--971,
   [doi:10.1142/S1793042109002481](https://doi.org/10.1142/S1793042109002481).
   Theorem 6 gives the cyclic \((3,1)\) result used above.
