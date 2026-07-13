# Primary-source audit: Erdos-Graham and Guy E31

## Definitions fixed for this audit

For a set `S` of positive integers, put

\[
 S(X)=|S\cap[1,X]|,\qquad
 \underline d(S)=\liminf_{X\to\infty}\frac{S(X)}X,
 \qquad
 \overline d(S)=\limsup_{X\to\infty}\frac{S(X)}X.
\]

The natural (asymptotic) density `d(S)` exists when the liminf and limsup
are equal.  "Asymptotic density 1" and the number-theoretic phrase "almost
all integers" both mean `S(X)/X -> 1`.  The sprint question is the weaker
claim `underline d(S)>0`.

For the sprint question I use the set-valued stages

\[
A_0=\{2,3\},\qquad
A_{n+1}=A_n\cup\{xy-1:x,y\in A_n,\ x\ne y\},\qquad
A=\bigcup_{n\geq0}A_n.                                      \tag{1}
\]

Thus every use of the operation in this report has `x != y` as distinct
integer values.  This convention is not silently substituted into the
index-based historical formulations below.

## What the primary sources actually say

### Erdos 1977, the semantic baseline

On printed p. 71, Erdos starts with `a_1=2,a_2=3`, says to form products of
two **distinct elements**, subtract 1, append the results, and repeat
indefinitely.  He then asks whether the sequence has "positive density."
This is the cleanest primary-source support for (1): distinctness is of
values, not merely of positions.  See [Er77c, p. 71](https://users.renyi.hu/~p_erdos/1977-27.pdf).

The paragraph does not define "positive density."  This ambiguity is real:
on the immediately preceding printed page Erdos separately discusses
"density" and "lower density."  Therefore the literal 1977 text does not by
itself decide between existence of a positive natural density and positive
lower density.  The current problem asks the explicit lower-density version.

Exact PDF audited:

```text
SHA256 8fc7f48707af5c2536e792226c9e14505fc05cd46078e0c6e05a00810f8229ea
bytes  2794180
URL    https://users.renyi.hu/~p_erdos/1977-27.pdf
```

### Erdos-Graham 1980, p. 84

Bibliographic record: P. Erdos and R. L. Graham, *Old and New Problems and
Results in Combinatorial Number Theory*, Monographies de L'Enseignement
Mathematique, no. 28, Geneva, 1980.

The displayed formulation is internally inconsistent.  It prints
`b_1=1,b_2=2`, then says that, after `b_1,...,b_n` are defined, all
`b_i b_j-1` with `i != j` are appended.  The very next line instead lists

\[
2,3,5,9,14,17,26,27,33,41,\ldots
\]

and asks: "Is it true that B has asymptotic density 1?"  See
[ErGr80, p. 84](https://mathweb.ucsd.edu/~ronspubs/80_11_number_theory.pdf).
The listed terms require intended seeds `2,3`; they do not follow from the
printed seeds `1,2`.

This is an exact obstruction, not a stylistic complaint.  Under set closure
with distinct values, the only allowed seed pair is `1 != 2`, and
`1*2-1=1`; hence the literal closure is just `{1,2}`.  Under a literal
sequence/index interpretation, appending duplicate 1's creates a different
process and still does not justify the displayed list.  The seed must be
corrected before p. 84 can denote the intended problem.

The operation on p. 84 says `i != j`, so it requires distinct indices.  It
does not say that equal values at two indices are forbidden.  This is a
semantic gap from (1) unless duplicate values are discarded.

There is no proof fragment attached to this question.  The book's
bibliography identifies `[Hofs (77)]` only as `D. Hofstadter (Personal
communication)`.  No density definition or lower bound is supplied.

Exact PDF audited:

```text
SHA256 0cbf0c32f0ab1e1c71db5121a88bac905bf976c4a6ab6bb6d7d9cf9ddd184ed3
bytes  5253644
URL    https://mathweb.ucsd.edu/~ronspubs/80_11_number_theory.pdf
```

### Guy, E31, all three editions

Bibliographic records: Richard K. Guy, *Unsolved Problems in Number
Theory*, Springer-Verlag, first edition (1981), E31, pp. 129-130; second
edition (1994), pp. 231-232; third edition (2004), pp. 353-355.

Guy repairs the seeds.  The first edition, E31(c), defines `c_1=2,c_2=3`;
whenever `c_1,...,c_n` are defined it forms every

\[
c_i c_j-1\qquad(1\leq i<j\leq n)
\]

and appends the results.  Its displayed list agrees with (1), beginning
`2,3,5,9,14,17,26,27,33,41,...`.  It asks: "Does the result include almost
all of the integers?"  See [first edition, pp. 129-130](https://books.google.com/books?id=t_3lBwAAQBAJ&pg=PA130).

The [second edition, pp. 231-232](https://books.google.com/books?id=ZrwrAAAAYAAJ&pg=PA231)
(1994) and [third edition, pp. 353-355](https://books.google.com/books?id=1AP2CEGxTkgC&pg=PA354)
(2004) retain the same seeds, `i<j` condition, list, and "almost all"
question.  The third-edition list through 129 is

```text
2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69,
77, 80, 81, 84, 87, 98, 99, 101, 105, 122, 125, 129
```

Guy's condition is still on distinct indices.  The displayed increasing,
duplicate-free list indicates set-style output, but E31 does not explicitly
say that repeated numerical outputs are discarded.  For the value-distinct
problem (1), Erdos 1977 is the unambiguous source.

No edition gives an argument toward the density question for sequence (c).
The first edition cites Erdos-Graham, pp. 83-84.  The second-edition E31
bibliography again cites Erdos-Graham and also contains references for the
other Hofstadter sequences in the section.  The third edition keeps the
Erdos-Graham citation and adds an OEIS block containing `A005243-A005244`;
it does not add a proof or density estimate for (c).  The current
[OEIS A005244](https://oeis.org/A005244) uses seeds 2,3 and a set/subset
implementation, but its prose "any 2 previous elements" is not itself an
explicit statement of `x != y`.

The reference chain specific to sequence (c) is therefore short.  Erdos
1977 says that Hofstadter had recently told him the problem.  Erdos-Graham
1980 labels Hofstadter as a personal communication.  Guy cites
Erdos-Graham, pp. 83-84.  The later references in E31 chiefly concern the
other two Hofstadter sequences; the third edition additionally points to
OEIS A005244.  None is a cited proof fragment for (c).

## Proved obstruction to the claimed density-one versions

**Lemma (mod-3 exclusion, with `x != y`).**  For every `n >= 0`,

\[
A_n\subseteq\{m\geq1:m\equiv0\text{ or }2\pmod3\}.
\]

**Proof.**  The claim holds for `A_0={2,3}`.  Suppose it holds for `A_n`,
and let `x,y in A_n` with `x != y`, exactly as required in (1).  Their
residue pair belongs to `{0,2}^2`.  Directly,

\[
0\cdot0-1\equiv2,\quad 0\cdot2-1\equiv2,\quad
2\cdot0-1\equiv2,\quad 2\cdot2-1\equiv0\pmod3.
\]

Thus every allowed new value `xy-1`, with `x != y`, again has residue 0 or
2.  Induction proves the stage claim, and taking the union proves it for
`A`.  QED.

**Corollary.**  Every positive integer congruent to 1 modulo 3 is absent.
There are exactly `floor((X+2)/3)` such integers in `[1,X]`, so

\[
|A\cap[1,X]|\leq X-\left\lfloor\frac{X+2}{3}\right\rfloor,
\qquad \overline d(A)\leq\frac23.                         \tag{2}
\]

Consequently the Erdos-Graham density-one question and Guy's "almost all"
question have a rigorous negative answer for the intended seeds.  This does
not decide whether `underline d(A)>0`.  The same mod-3
observation is now recorded on the [current Problem 424 page](https://www.erdosproblems.com/424),
which attributes it to Stefan Steinerberger.

## Exact regression computation

The following command was executed from the repository root with Python
3.12.  `A` is a set and `combinations(sorted(A),2)` enumerates only pairs of
distinct values, so every generated product preserves `x != y`.

```powershell
python -c "from itertools import combinations; B=10000; A={2,3}; rounds=0
while True:
 new={x*y-1 for x,y in combinations(sorted(A),2) if x*y-1<=B}
 old=len(A); A|=new; rounds+=1
 if len(A)==old: break
s=sorted(A); assert all(x%3!=1 for x in s); print('B=',B,'rounds=',rounds,'count=',len(s)); print('first30=',s[:30]); print('residue_counts=',{r:sum(x%3==r for x in s) for r in range(3)}); print('max=',s[-1])"
```

Output:

```text
B= 10000 rounds= 12 count= 3207
first30= [2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69, 77, 80, 81, 84, 87, 98, 99, 101, 105, 122, 125, 129, 131, 134]
residue_counts= {0: 1314, 1: 0, 2: 1893}
max= 9999
```

This truncated closure is exact for `A intersect [1,B]`: if an allowed
`z=xy-1<=B` has positive operands from (1), then `x,y>=2`, hence
`x<=z<=B` and `y<=z<=B`.  No value above the cutoff can be an operand in a
new value below the cutoff.  The computation is only a source-term and
invariant regression test; (2), not the finite run, is the rigorous
asymptotic obstruction.

For reproducible Google Books snippet checks used in the edition audit:

```powershell
Invoke-RestMethod 'https://books.google.com/books?jscmd=SearchWithinVolume2&vid=ZrwrAAAAYAAJ&q=33%2041' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'https://books.google.com/books?jscmd=SearchWithinVolume2&vid=1AP2CEGxTkgC&q=when%20c1' | ConvertTo-Json -Depth 8
```

## Limitations of the audit

1. Neither Erdos-Graham nor Guy contains a proof fragment for positive or
   lower density; they only state the stronger, false density-one question.
2. The Erdos-Graham printed seeds are erroneous, and its `i != j` is an
   index condition.  Any use of that page must state both corrections.
3. Guy corrects the seeds but retains an index condition and does not
   explicitly specify duplicate suppression.  This report's theorem and
   computation use the requested distinct-value condition `x != y`.
4. The first-edition and primary PDF page images were directly inspected.
   Google Books supplies indexed snippets rather than unrestricted page
   images for parts of the later Guy editions; the cited page, formula,
   sequence, question, and bibliography were cross-queried by adjacent
   terms.  No claim is made about unqueried prose elsewhere in those books.
