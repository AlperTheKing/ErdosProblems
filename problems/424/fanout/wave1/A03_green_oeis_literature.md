# Problem 424: Green Problem 63 and OEIS A005244 audit

Access date for all web sources: 2026-07-13.

## 1. Exact object

For distinct-value semantics, put

\[
A_0=\{2,3\},\qquad
A_{r+1}=A_r\cup\{xy-1:x,y\in A_r,\ x\ne y\},\qquad
A=\bigcup_{r\geq 0}A_r.
\]

Thus every internal node in a derivation has children with **different
integer values**.  Write

\[
A(X)=|A\cap[1,X]|,
\qquad \underline d(A)=\liminf_{X\to\infty}\frac{A(X)}X.
\]

The question is whether \(\underline d(A)>0\).

## 2. Primary-source audit

### Erdos 1977: the original formulation

Page 71 of P. Erdos, *Problems and results on combinatorial number theory
III*, explicitly says to form products of "two distinct elements" and asks
whether the resulting sequence has positive density:

<https://www.renyi.hu/~p_erdos/1977-27.pdf#page=29>

This is the distinct-value rule above.  The source states no lemma, numerical
bound, or partial lower-density result.

### Erdos--Graham 1980 and Guy E31

The later references are P. Erdos and R. L. Graham, *Old and New Problems and
Results in Combinatorial Number Theory*, p. 84, and R. K. Guy, *Unsolved
Problems in Number Theory*, section E31.  The current Erdos Problems note
reports that these versions ask whether almost all integers occur.  That
stronger assertion is false by the mod-3 lemma in section 4 below.  The note
also explains that the 1977 positive-density question is the intended surviving
question:

<https://www.erdosproblems.com/424>

MathWorld's E31 summary uses \(1\leq i<j\leq n\), hence preserves distinct
indices/values, but gives only the definition and initial terms:

<https://mathworld.wolfram.com/HofstadterSequences.html>

No positive lower bound is stated in either accessible summary.

### Green, Problem 63

The December 2025 version of Ben Green's *100 Open Problems*, Problem 63,
asks the positive-density question, predicts "probably yes", and says that a
proof may combine theory and computation.  It also asserts that the analogous
statement for seeds 9 and 10 fails and motivates this by expression-word
growth.  It gives no theorem for seeds 2 and 3 and cites only Erdos [108],
A005244, and the Erdos Problems page:

<https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf#page=31>

There is a semantic omission in Green's displayed definition: it says
\(a_1a_2-1\in A\) whenever \(a_1,a_2\in A\), without \(a_1\ne a_2\).  Read
literally, Green's set contains

\[
8=3\cdot3-1.
\]

The distinct-input set does not contain 8: a representation \(8=xy-1\) would
give \(xy=9\); the positive factor pairs are \((1,9),(3,3),(9,1)\), where 1 is
never generated and \((3,3)\) violates \(x\ne y\).  Hence Green's literal set
is not A005244.  His link to A005244 and the original source strongly indicate
that omission of distinctness is typographical, but arguments quoted from the
Green formulation must restore \(x\ne y\).

## 3. OEIS A005244 and every substantive linked item

The entry is <https://oeis.org/A005244>; its machine-readable record is
<https://oeis.org/A005244/internal>.

* **Definition and programs.**  The prose "any 2 previous elements" is
  ambiguous, but the terms and Mathematica code enforce distinctness: the
  latter uses `Subsets[s,{2}]`.  The Haskell initialization redundantly obtains
  the seed 3 as \(2\cdot2-1\); after that, each current element is multiplied
  only by already emitted elements, so it produces no new self-product and
  enumerates the intended sequence.  In particular, 8 is absent.
* **Zumkeller table.**  <https://oeis.org/A005244/b005244.txt> is a b-file of
  10,000 finite values, not an asymptotic theorem.
* **A139127.**  <https://oeis.org/A139127> records a greatest preceding
  divisor of \(a(n)+1\).  This repackages one parent in a representation and
  supplies no growth or density estimate.
* **A139128.**  <https://oeis.org/A139128> counts representations
  \(a(n)=a(i)a(j)-1\) with the exact condition \(i<j\).  Its linked table is
  finite (10,000 entries); no uniform lower bound for representations and no
  density theorem is stated.
* **A171413.**  <https://oeis.org/A171413> is simply the complement of
  A005244.  Its displayed Mathematica code again uses two-element subsets.
  Its prose accidentally says "start with 2", while its code correctly starts
  with `{2,3}`.  It contains no asymptotic claim.
* **Erdos Problems link.**  <https://www.erdosproblems.com/424> supplies the
  mod-3 upper obstruction proved below, defines positive density as positive
  lower density, and states no claimed partial or complete solution.
* **Database link.**  <https://github.com/teorth/erdosproblems> mirrors the
  problem/OEIS metadata and supplies no separate theorem.
* **MathWorld link.**
  <https://mathworld.wolfram.com/HofstadterSequences.html> explicitly uses
  \(i<j\), lists initial terms, and cites Guy E31 and OEIS; it states no density
  estimate.
* **Printed OEIS references.**  Guy E31 is the problem-book discussion above.
  N. J. A. Sloane and S. Plouffe, *The Encyclopedia of Integer Sequences*
  (1995), is cited by OEIS only as including the sequence; the OEIS record does
  not attribute any theorem to it.

The OEIS "sequence in context" links
A220315, A070819, A195667, A058541, A023672, and A023567, and its adjacent-ID
links A005241--A005243 and A005245--A005247, are automatic navigation by
initial-term context or database number.  They are not `Cf.` cross-references
and do not state results about A005244.  Of the adjacent entries, A005243 is
the other Hofstadter problem described immediately before Problem 424 in the
1977 source; it uses sums of consecutive earlier terms, not \(xy-1\).

A direct web search for the exact identifier `A005244`, the defining phrase,
and `Erdos Problem 424` found one Mathematics Stack Exchange question in
addition to the sources above.  It has one answer, which only points back to
OEIS and Erdos Problems and repeats the \(2/3\) upper bound:

<https://math.stackexchange.com/questions/4970785/show-that-the-set-ab-1-is-dense-in-natural-numbers>

Accordingly, the only proved density statement in this source chain is the
upper obstruction \(\overline d(A)\leq2/3\); no linked source proves
\(A(X)\gg X\), even on a subsequence of all large \(X\).

## 4. Proved lemma for the target set: the mod-3 obstruction

**Lemma 1.** Every \(a\in A\) is congruent to 0 or 2 modulo 3.  Consequently

\[
A(X)\leq X-\left\lfloor\frac{X+2}{3}\right\rfloor
       =\frac{2X}{3}+O(1),
\qquad
\overline d(A)\leq\frac23.
\]

**Proof.** Both seeds have residue in \(\{0,2\}\).  If distinct
\(x,y\in A_r\) have residues in this set, then

\[
xy-1\equiv
\begin{cases}
2\pmod3,&3\mid xy,\\
0\pmod3,&x\equiv y\equiv2\pmod3.
\end{cases}
\]

Thus induction on \(r\) proves the residue assertion.  There are
\(\lfloor(X+2)/3\rfloor\) positive integers at most \(X\) congruent to 1
modulo 3, and none belongs to \(A\), proving the count.  The closure step was
applied only to \(x\ne y\).  QED.

## 5. Proved version of Green's 9,10 obstruction

Green's word-count explanation can be made rigorous and remains valid under
the required distinct-input rule.

For seeds \(s,t\), let \(A_{s,t}\) be the smallest set containing \(s,t\) and
closed under \(xy-1\) only for distinct values \(x\ne y\).

**Lemma 2.** If \(s,t\geq9\), then

\[
|A_{s,t}\cap[1,X]|
 < \frac7{15}(X-1)^{\log_8 7}\quad(X\geq9).
\]

In particular, \(A_{9,10}\) has natural density zero.

**Proof.** Represent a derivation by a rooted full binary tree whose leaves
are colored \(s\) or \(t\), and whose internal node evaluates to the product
of its children minus 1.  A valid derivation additionally requires the two
child values at every internal node to be distinct.  We now forget that
restriction, thereby counting a superset of valid derivations.

If a tree has \(n\) leaves, its value is at least \(8^n+1\).  This follows by
induction.  It is true at a leaf because \(s,t\geq9\); and if the child trees
have \(i,j\) leaves, then

\[
(8^i+1)(8^j+1)-1
=8^{i+j}+8^i+8^j\geq8^{i+j}+1.
\]

Let \(w_n\) be the number of unordered rooted full binary trees with \(n\)
leaves colored in two colors, and let \(W(z)=\sum_{n\geq1}w_nz^n\).  For
trees of height at most \(h\), write \(W_h\).  The two colored leaves and the
unordered pair of child trees give the exact recurrence

\[
W_{h+1}(z)=2z+\frac12\bigl(W_h(z)^2+W_h(z^2)\bigr).
\]

Take \(r=1/7\).  If \(W_h(r)\leq2/5\), positivity of the coefficients and
the fact that every tree has at least one leaf give

\[
W_h(r^2)\leq rW_h(r).
\]

Therefore

\[
W_{h+1}(r)
\leq\frac27+\frac12\left(\frac4{25}+\frac2{35}\right)
=\frac{69}{175}<\frac25.
\]

The initial polynomial is \(W_0(r)=2/7<2/5\), so induction and monotone
passage to all finite heights yield \(W(1/7)\leq2/5\).  Hence
\(w_n\leq(2/5)7^n\), and

\[
\sum_{n=1}^{N}w_n
\leq\frac25\sum_{n=1}^{N}7^n
<\frac1{15}7^{N+1}.
\]

Every generated value at most \(X\) has a derivation with
\(n\leq N=\lfloor\log_8(X-1)\rfloor\) leaves.  Counting values by their
derivation trees and using \(7^N\leq(X-1)^{\log_8 7}\) proves the displayed
bound.  Since \(\log_8 7<1\), division by \(X\) tends to zero.  Allowing
equal-child trees only enlarged the count, so the conclusion applies in
particular to the distinct-input closure.  QED.

## 6. Reproduction checks and limitations

No code or finite search is used in either proof.  The exact arithmetic check
in Lemma 2 is

```text
2/7 + (1/2)(4/25 + 2/35)
= 50/175 + 14/175 + 5/175
= 69/175 < 70/175 = 2/5.
```

Commands: none; this was a literature audit with proof, and no code or
auxiliary file was created.  Source checks are reproducible from the URLs
above.  On the OEIS page,
`internal format` exposes the complete entry; `A139128` displays `i < j` in
its definition; and page 71 of the 1977 PDF contains the phrase "two distinct
elements".

Lemma 1 is an upper-density obstruction only.  Lemma 2 explains Green's
different-seed example but does not transfer to seeds 2 and 3: its lower bound
\(8^n+1\) comes from every leaf being at least 9, whereas the target has leaves
2 and 3.  The 10,000-term b-file, representation-count tables, and the reported
finite experiment below \(10^9\) on Mathematics Stack Exchange cannot imply a
positive liminf.  None controls \(A(X)\) uniformly for all sufficiently large
\(X\).
