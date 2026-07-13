# Problem 424: modern adjacent literature and exact obstructions

## 1. Exact object and distinctness convention

For $B\subseteq \mathbb N_{>0}$, write

\[
B\widehat\times B:=\{xy:x,y\in B,\ x\ne y\}.
\]

Throughout this note,

\[
A=\bigcap\{B\subseteq\mathbb N_{>0}:\{2,3\}\subseteq B,
\quad B\widehat\times B-1\subseteq B\}.
\]

Thus $x\ne y$ always means distinct integer values. No assertion below uses
$x^2-1\in A$ merely from $x\in A$.

The original source is Erdos, *Problems and results on combinatorial number
theory III*, p. 71. It explicitly says "products of two distinct elements" and
asks whether the resulting sequence has positive density [original PDF,
printed p. 71](https://www.renyi.hu/~p_erdos/1977-27.pdf). The current problem
page interprets this as positive lower density

\[
\underline d(A):=\liminf_{X\to\infty}\frac{|A\cap[1,X]|}{X}>0
\]

and records no claimed partial or complete solution
[Erdos Problems #424](https://www.erdosproblems.com/424).

## 2. Exact affine-semigroup reduction

For $d\in A$, put $f_d(t)=dt-1$. Applying $f_d$ is licensed only when
$t\ne d$.

### Lemma 2.1 (admissible fixed-alphabet orbit)

Let $D\subset A$ be finite and let $t_0\in A$ satisfy $t_0>\max D$. Define

\[
\mathcal O_D(t_0)=\{f_{d_r}\circ\cdots\circ f_{d_1}(t_0):
r\ge 0,\ d_i\in D\}.
\]

Then every operation in every displayed composition has distinct inputs, and
$\mathcal O_D(t_0)\subseteq A$.

**Proof.** If $t>\max D$, then $t\ne d$ for every $d\in D$, so closure gives
$f_d(t)\in A$. Also, for $d\ge2$ and $t\ge2$, $f_d(t)=dt-1>t$.
Induction on the word length keeps the current value strictly above every
member of $D$, proving both assertions. QED.

Such a $t_0$ always exists: from any $t\in A\setminus\{2\}$, the admissible
iteration $t\mapsto2t-1$ is strictly increasing.

Conjugate by $h(t)=t-1$. The induced maps are

\[
g_d:=h\circ f_d\circ h^{-1},\qquad
g_d(u)=du+(d-2),
\]

so they have integer slope $d>1$ and nonnegative constant term. This is
exactly the one-dimensional affine-orbit framework of Shamazov--Talambutsa.

### The applicable theorem

The Erdos--Lagarias upper bound, stated as Theorem 1 of Shamazov and
Talambutsa, is as follows. Let $F=\{u\mapsto a_i u+b_i\}$, where
$a_i\ge1$, $b_i\ge0$, and let $S\subset\mathbb R_{>0}$ be discrete. If

\[
\alpha=\sum_i a_i^{-\sigma}<1,
\]

then for $Y\ge1$ the orbit **multiset** obeys

\[
|\langle F:S\rangle^\#\cap[0,Y]|
\le \frac{Y^\sigma}{1-\alpha}
\sum_{\substack{s\in S\\s\le Y}}s^{-\sigma}.
\]

See [Shamazov--Talambutsa, Theorem 1](https://arxiv.org/pdf/2507.06875),
published as *Expositiones Mathematicae* 44(3) (2026), 125765,
[doi:10.1016/j.exmath.2026.125765](https://doi.org/10.1016/j.exmath.2026.125765).

### Corollary 2.2 (exact bound for every subcritical induced orbit)

Under Lemma 2.1, if $\sigma>0$ and

\[
\alpha_D(\sigma):=\sum_{d\in D}d^{-\sigma}<1,
\]

then, for $X\ge t_0$,

\[
|\mathcal O_D(t_0)\cap[1,X]|
\le
\frac{(X-1)^\sigma}
{(1-\alpha_D(\sigma))(t_0-1)^\sigma}.
\]

**Proof.** Apply the theorem to $F=\{g_d:d\in D\}$,
$S=\{t_0-1\}$, and $Y=X-1$. Conjugation is a bijection between the two
orbits. Counting the orbit set is bounded by counting its orbit multiset. QED.

For the concrete admissible suborbit $D=\{2,3\}$, $t_0=5$, let $\rho$ be the
unique positive root of

\[
2^{-\rho}+3^{-\rho}=1.
\]

Since $2^{-1}+3^{-1}=5/6<1$, one has $\rho<1$. Corollary 2.2 with any
$\rho<\sigma<1$ proves

\[
|\mathcal O_{\{2,3\}}(5)\cap[1,X]|=O_\sigma(X^\sigma)=o(X).
\]

Thus iterating only the permanently available multipliers $2,3$ cannot by
itself supply a positive-density subset of $A$. This does not upper-bound
$A$, because $A$ continually creates new multipliers.

### Why the positive-density affine theorem does not apply

The same paper proves positive density when the affine images form an exact
covering system

\[
g_{d_1}(\mathbb Z)\sqcup\cdots\sqcup g_{d_k}(\mathbb Z)=\mathbb Z
\]

([Theorem 7](https://arxiv.org/pdf/2507.06875)). For the maps forced by Problem
424,

\[
g_d(\mathbb Z)=d\mathbb Z+(d-2)=d\mathbb Z-2.
\]

For any $d,e\ge2$, both images contain
$\operatorname{lcm}(d,e)\mathbb Z-2$. Hence no two induced maps have disjoint
integer images, and no $D$ with $|D|\ge2$ can satisfy the exact-covering
hypothesis. This obstruction is independent of any freeness question.

The paper's other near-linear theorem assumes both a free affine semigroup and
$\sum_{d\in D}1/d=1$, and yields only

\[
\Omega\!\left(X/(\log X)^{(|D|-1)/2}\right),
\]

not $\Omega(X)$ ([Theorem 5](https://arxiv.org/pdf/2507.06875)). The natural
alphabet $D=\{2,3,5\}\subset A$ is already supercritical since

\[
\frac12+\frac13+\frac15=\frac{31}{30}>1,
\]

but no theorem in that paper turns supercritical word multiplicity into a
linear lower bound for the **set** orbit. Collisions are the missing issue.

## 3. A finite-field theorem preserving distinct inputs

Kim, Yip, and Yoo define the restricted product exactly as here:

\[
B\widehat\times B=\{bb':b,b'\in B,\ b\ne b'\}.
\]

For a prime $p\equiv1\pmod d$, let

\[
S_d=\{z^d:z\in\mathbb F_p^*\}.
\]

Their Theorem 1.5(2) says that if $B\subset\mathbb F_p^*$ and

\[
B\widehat\times B+\lambda\subseteq S_d\cup\{0\},
\]

then

\[
|B|\le \sqrt{\frac{2(p-1)}d}+4.
\]

See [Kim--Yip--Yoo, Theorem 1.5](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/multiplicative-structure-of-shifted-multiplicative-subgroups-and-its-applications-to-diophantine-tuples/6B2287DA5C0E21824226536C45516473),
*Canadian Journal of Mathematics* (2025),
[doi:10.4153/S0008414X25000136](https://doi.org/10.4153/S0008414X25000136).

### Corollary 3.1 (power-subgroup obstruction for residue closures)

Let

\[
R_p=\{a\bmod p:a\in A\},\qquad R_p^*=R_p\cap\mathbb F_p^*.
\]

If $d\ge2$, $p\equiv1\pmod d$, and $R_p^*\subseteq S_d$, then

\[
|R_p^*|\le \sqrt{\frac{2(p-1)}d}+4.
\]

**Proof.** Take distinct $r,s\in R_p^*$. Choose $x,y\in A$ reducing to
$r,s$. Since $r\ne s$, necessarily $x\ne y$; therefore $xy-1\in A$, and
hence $rs-1\in R_p$. Under $R_p^*\subseteq S_d$, this gives

\[
R_p^*\widehat\times R_p^*-1\subseteq S_d\cup\{0\}.
\]

Apply Kim--Yip--Yoo with $B=R_p^*$ and $\lambda=-1$. QED.

The hypothesis $R_p^*\subseteq S_d$ is substantial. The theorem gives no
bound for an arbitrary residue closure $R_p$, and a bound for one fixed
modulus does not imply an asymptotic-density bound over the integers.

## 4. Proved word-growth obstruction for large seeds

Green's Problem 63 remarks that replacing $2,3$ by $9,10$ gives a zero-density
closure because words grow too fast. Green's displayed definition omits the
distinctness clause, so that remark requires a check for the exact operation.

### Lemma 4.1 (restricted binary-tree bound)

Let $S\subset\mathbb N$ be finite, $|S|=k$, and suppose every $s\in S$
satisfies $s\ge m\ge2$. Let $C(S)$ be the smallest set containing $S$ and
closed under

\[
(x,y)\longmapsto xy-1\qquad\text{only when }x\ne y.
\]

Put $\lambda=m-m^{-1}$. If $\lambda>4k$, then

\[
|C(S)\cap[1,X]|=O_{S}\left(X^\theta\right),
\qquad
\theta=\frac{\log(4k)}{\log\lambda}<1.
\]

In particular, $C(S)$ has upper asymptotic density zero.

**Proof.** Every $z\in C(S)$ has a finite full binary expression tree whose
leaves are labelled by elements of $S$, whose internal operation is $uv-1$,
and whose two evaluated children at every internal vertex are distinct. For an
upper bound, count all ordered labelled full binary trees, including trees
that violate this last condition.

First, an expression with $n$ leaves has value at least

\[
m^n(1-m^{-2})^{n-1}=m\lambda^{n-1}. \tag{1}
\]

For $n=1$, this is the leaf bound. Inductively, let the child values be
$u,v\ge m$, with $n_1,n_2$ leaves. Since $uv\ge m^2$,

\[
uv-1\ge(1-m^{-2})uv.
\]

Multiplying the two inductive lower bounds gives (1) with
$n=n_1+n_2$. This proof did not add a forbidden equal-input operation; it
only overcounts such trees after obtaining a lower bound valid for all trees.

If the value is at most $X\ge m$, (1) implies

\[
n-1\le \frac{\log(X/m)}{\log\lambda}.
\]

There are $\operatorname{Cat}_{n-1}$ ordered full binary tree shapes with
$n$ leaves and $k^n$ leaf labellings. Since
$\operatorname{Cat}_{n-1}\le4^{n-1}$, summing over the allowed $n$ gives

\[
|C(S)\cap[1,X]|
\le k\sum_{j\le \log(X/m)/\log\lambda}(4k)^j
=O_S(X^{\log(4k)/\log\lambda}).
\]

If $\lambda>4k$, the exponent is below $1$. QED.

### Exact counterexample to a seed-independent density principle

For $S=\{9,10\}$, $k=2$, $m=9$, and

\[
\lambda=9-\frac19=\frac{80}{9}>8=4k.
\]

Therefore the closure using only **distinct** values satisfies

\[
|C(\{9,10\})\cap[1,X]|
=O\!\left(X^{\log 8/\log(80/9)}\right)=o(X).
\]

This validates the large-seed obstruction while preserving $x\ne y$ at every
generated node. It also shows that no theorem based only on having two seeds
and closure under the same restricted polynomial can force positive density;
the small values $2,3$ are load-bearing.

## 5. Adjacent theorem families that do not transfer

### Recursively defined sets under linear operations

Klarner and Rado study closures under a finite family of finitary **linear**
operations

\[
\rho(x_1,\ldots,x_r)=a+m_1x_1+\cdots+m_rx_r
\]

and prove structural results for such closures
([Pacific J. Math. 53 (1974), 445--463](https://msp.org/pjm/1974/53-2/pjm-v53-n2-p13-p.pdf)).
Their framework contains the fixed unary maps in Lemma 2.1, but $xy-1$ is
nonlinear and its available coefficient $x$ is itself generated. Their
closure theorems therefore do not apply to $A$ as a whole.

### Polynomial semigroup dynamics

Bell, Hindes, and Zhong count points of bounded height in orbits of a fixed
finite semigroup of polarized self-maps. Their orbit theorems require
polarization weights/degrees $d_i>1$; on $\mathbb P^1$ the maps relevant to
Problem 424 are affine automorphisms of degree $1$. Their abstract weighted
word Proposition 2.2 recovers the critical equation
$\sum d_i^{-\rho}=1$, but not a density result for this expanding-alphabet
binary closure
([Canadian J. Math. 77 (2025), 2061--2082](https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/counting-points-by-height-in-semigroup-orbits/BFCACB2A52A7512A44359803717B4A12)).

### Multiplicative bases and density of product sets

Pach--Sandor define a multiplicative basis of order $h$ by the covering
condition that every target integer is a product of $h$ basis elements
([arXiv:1602.06724](https://arxiv.org/abs/1602.06724)).
Hegyvari--Hennecart--Pach study how the density of $B$ controls the density of
the unrestricted product set $B^2$
([arXiv:1902.02512](https://arxiv.org/abs/1902.02512)). Both directions differ
from

\[
A\widehat\times A-1\subseteq A.
\]

They assume density or a product-covering conclusion and do not infer density
from a shifted restricted-product closure. Dropping either the shift or the
distinctness condition would be an invalid transfer.

## 6. Direct-citation and exact-phrase search record

Searches were run on 2026-07-13 using the exact identifier and phrases

```text
"A005244"
"A005244" mathematics paper
"xy-1" "positive density" set integers
"a_i a_j - 1" Hofstadter sequence
"take all products of any 2 previous elements" subtract 1
finite field subset closed under xy-1 distinct elements theorem
recursive product set sequence density number theory
affine semigroup orbit integer density
```

The exact-identifier searches returned the OEIS entry, Erdos Problems #424,
Green's open-problem list, and derivative reference pages; they did not return
a research article proving a result about the restricted binary closure. The
[OEIS A005244 entry](https://oeis.org/A005244) lists Guy's *Unsolved Problems
in Number Theory*, Sloane--Plouffe's encyclopedia, code/data links, and no
research paper on its density. Green's current
[Problem 63](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
restates the question and gives the $9,10$ obstruction, but its displayed
closure omits $a_1\ne a_2$; results using a square operation cannot be imported
from that formulation.

The adjacent-topic searches located the affine-orbit and restricted-product
theorems applied above. Within the sources and citation trails checked, no
theorem was found whose hypotheses are the dynamically expanding, restricted
binary closure

\[
x,y\in A,\ x\ne y\Longrightarrow xy-1\in A
\]

and whose conclusion controls $\underline d(A)$. This is a documented search
outcome, not a claim that such a theorem cannot exist outside the searched
indices or under different terminology.

## 7. Reproducibility and limitations

- No code or floating-point computation is used in this note.
- Lemma 2.1 and Corollaries 2.2 and 3.1 can be checked symbolically from the
  displayed definitions and the linked theorem statements.
- Lemma 4.1 uses only the exact inequalities
  $uv-1\ge(1-m^{-2})uv$ and
  $\operatorname{Cat}_{n-1}\le4^{n-1}$.
- The exact large-seed check is $80/9>8$; no finite census is involved.
- The affine results concern fixed finite suborbits of $A$, not the whole
  expanding-alphabet closure.
- The finite-field result is conditional on power-subgroup containment and
  gives local information only.
- None of the cited theorems or proved lemmas decides
  $\underline d(A)>0$ for the seeds $2,3$.
