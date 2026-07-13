# GPT-Pro question: support-plus-difference Hall lemma

We are studying the following finite combinatorial object arising from
Erdos Problem 864.

Let `B` be an integer Sidon set of size `p`.  A fold is a quadruple

`F=(a,c,u,v)`, with `a,c,u,v in B`, `a<=c<u<=v`, and
`a+c+h=u+v`.

The fold projections `(a,c)`, `(a,u)`, `(c,u)` are all injective.  A loose
triangle is a triple of distinct folds

`F0=(a,c,r,s)`, `Fz=(a,z,u,w)`, `Fx=(x,c,u,y)`.

Its three supporting resources are the folds `F0,Fz,Fx`.  Put
`X=x-a`, `Z=z-c`.  The three positive integers

`|X|, |Z|, |X-Z|`

are represented positive differences of `B`.  Sidonicity makes every
positive difference correspond to a unique unordered pair of marks.

Proposed lemma: for every family `T` of loose triangles,

`|T| <= |support_folds(T)| + |difference_labels(T)|`,

where `difference_labels(T)` is the union of the three labels above.
Equivalently, the triangles can be matched injectively to either one of
their three supporting folds or one of their three difference labels.

This would give `T_F <= C_S + binom(p,2)=O(p^2)`, which is sufficient for
the established hypergraph-removal reduction.

Exact evidence: zero failures on 791,869 complete endpoint Sidon fold
systems of width at most 30, all 2,085 translations of the large P88 fold
system, and the P75, P94, P98, and P105 hard witnesses.  Matching to
differences alone fails three P88 translations.

Known false weakenings that must not be proposed:

1. Matching only to the three supporting folds fails (116 triangles have
   maximum matching 105).
2. Componentwise triangle<=fold fails even with positive defect and the
   literal hole (110 triangles on 109 folds).
3. Matching only to the two outer fold labels and the span difference is
   false for an abstract 13-vertex linear proper-middle system (20 demands,
   matching 19).
4. The purely abstract ordered-linear-hypergraph matrix `(S,E,dE)` is false
   (51 rows, rank 50); any proof may need the actual Sidon difference-pair
   uniqueness and the displayed fold equations.

Please do exactly one of the following:

- give a rigorous proof of the proposed Hall inequality, explicitly proving
  the Hall condition for every subfamily; or
- give a concrete finite counterexample satisfying all fold equations and
  Sidon conditions; or
- isolate one strictly weaker lemma that still implies an `O(p^2)` bound
  and provide its complete proof.

Do not assume reflected extremizers, positive defect, or the literal hole;
this candidate is intended as an unconditional fold-system lemma.  Treat
unordered sums with diagonals and signed values of `X,Z` correctly.
