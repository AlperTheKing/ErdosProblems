# P90: literature audit for the phase-retaining loose-triangle bound

## Verdict

No theorem located in the audited primary sources proves

\[
                    T_F(B,h)\leq C_S(B,h)                 \tag{C84}
\]

for an endpoint-normalized ordered Sidon fold system with positive defect and
the literal hole. The closest graph-theoretic object is a proper edge-coloring
whose failures to be strong are counted by `T_F`; the closest hypergraph object
is the six-vertex **triforce** (a linear/Berge triangle). Existing theorems
either assume the color classes are induced matchings already, give lower
bounds for triforce counts, or use dense/relative removal at a scale on which
the whole Sidon set may be deleted.

There is one fully applicable phase-free theorem. Prendiville's dense-Sidon
transference implies that every sufficiently large frontier set has
`Omega(p^4)` pairwise-distinct equal-three-sum sextuples. This confirms that
ordinary Sidon correlation theorems see abundant translation-invariant
collisions, but those collisions do not retain `h` or `b` and therefore do not
bound `T_F`.

The audit includes primary sources available through 2026-07-13, including
Tung's June 2026 theorem on non-translation-invariant equations in `B_h` sets.

## 1. Exact strong-edge-coloring reformulation

Let `G_AC` be the bipartite graph on labelled copies `B_A,B_C` with one edge
`ac` for each fold

\[
             a+c+h=u+v,\qquad a\leq c<u\leq v.
\]

Color `ac` by the first high mark `u`. P82.1 says that the `(a,c)`, `(a,u)`,
and `(c,u)` projections are injective. Hence this is a proper edge-coloring:
for each `u`,

\[
       M_u:=\{ac:\text{the fold on }ac\text{ has first high mark }u\}
\]

is a matching. Write `A_u,C_u` for its two endpoint sets. Then

\[
 \boxed{\quad C_S+T_F=\sum_{u\in B}e_{G_{AC}}(A_u,C_u),\qquad
 T_F=\sum_{u\in B}\bigl(e_{G_{AC}}(A_u,C_u)-|M_u|\bigr).\quad}       \tag{1}
\]

Indeed, an edge of `G_AC[A_u,C_u]` is either the unique canonical edge of
`M_u`, or it is the middle edge of a three-edge path whose two end edges have
color `u`. The latter is exactly one P82 loose triangle. Thus `T_F` counts
the non-rainbow `P_4`'s (end edges of one color), equivalently the total defect
of the original proper coloring from being a strong edge-coloring. C84 is
exactly the assertion that this total inducedness excess is at most the number
of colored edges.

This formulation is more specific than a bound on the strong chromatic index:
the original arithmetic color `u` and its endpoint phase must be retained.

## 2. Induced matchings and Ruzsa-Szemeredi graphs

Fox--Huang--Sudakov define an `(r,t)` Ruzsa-Szemeredi graph to be a graph whose
edge set is partitioned into `t` **induced** matchings, each of size `r`. Their
main results treat `r=cn`: for `c>1/4`, `t` is bounded in terms of `c`; at
`c=1/4`, `t=Theta(log n)` is possible; and for fixed `1/5<c<1/4`,
`t=O(n/log n)`. Source:
[Fox--Huang--Sudakov, *On graphs decomposable into induced matchings of linear
sizes*](https://arxiv.org/abs/1512.07852).

**Mismatch.** In (1), the `M_u` are matchings but need not be induced. Their
inducedness violations are precisely the quantity being bounded. P82's exact
P75 audit tests all 12 choices of two raw fold roles as graph endpoints and a
third as color; none gives induced color classes, and the minimum violation
count is 19. Therefore the defining hypothesis of an RS graph is the desired
conclusion in zero-defect form, not a consequence of the three injective
shadows. The cited theorems contain no stability statement bounding the
number of violations in a prescribed, growing-color edge-coloring.

The standard diamond-free/induced-matching theorem is the zero-triangle
special case used by P82: if every graph edge lies in exactly one triangle,
then the graph has `o(n^2)` edges. It says `T_F=0 => C_S=o(p^2)`; it supplies
no estimate of `T_F` from the literal hole.

Strong-edge-coloring results also do not repair this. A strong edge-coloring
is, by definition, a partition into induced matchings. The recent theorem of
Bi--Bradshaw--Dhawan--Xu states that every fixed-`t` `K_{t,t}`-free graph of
maximum degree `d` has strong chromatic index at most
`(1+o(1))d^2/log d`. Source:
[Bi--Bradshaw--Dhawan--Xu, *The strong chromatic index of K_{t,t}-free
graphs*](https://arxiv.org/abs/2603.15207).

**Mismatch.** No fixed `K_{t,t}` exclusion is known for `G_AC` (P79 contains
a valid `K_{5,5}`), and the theorem constructs a new coloring. It neither
preserves the arithmetic colors `u` nor bounds the defect of the original
coloring in (1).

## 3. The exact linear-hypergraph configuration

Fox--Sah--Sawhney--Stoner--Zhao call the three-edge six-vertex hypergraph

\[
          \{123',12'3,1'23\}
\]

the **triforce**. This is exactly the P82 loose triangle in the linear
3-partite fold hypergraph. They prove that the minimum triforce homomorphism
density among 3-uniform hypergraphs of edge density `alpha` is
`alpha^(4-o(1))` and is `omega(alpha^4)` as `alpha -> 0`. Source:
[Fox--Sah--Sawhney--Stoner--Zhao, *Triforce and Corners*, Theorems 1.2 and
1.4](https://arxiv.org/abs/1903.04863).

**Mismatch.** This is a lower-bound/supersaturation theorem. It has no
arithmetic labels, endpoint, prescribed missing coefficient, or upper bound
of the form `T_F=O(C_S)`. At the fold-hypergraph density
`alpha=C_S/p^3`, it does not specialize to C84. The stronger lower bound in
P82 comes instead from the dense shadow graph and its `C_S` edge-disjoint
canonical triangles.

The three injective shadows alone cannot imply even `T_F=O(C_S)`. For
`A=C=U=Z/nZ`, take the Latin-square hypergraph

\[
             H_n=\{(a,c,a+c):a,c\in\mathbb Z/n\mathbb Z\}.          \tag{2}
\]

All three two-coordinate projections are injective. Its `AC` shadow is
`K_{n,n}`, properly colored by `a+c`; every color is a perfect matching. Thus

\[
       |E(H_n)|=n^2,\qquad
       \sum_u e_{K_{n,n}}(A_u,C_u)=n^3,\qquad
       T=n^3-n^2.                                                        \tag{3}
\]

Hence `T/|E|=n-1`. This proves that any applicable theorem must use the
integer endpoint phase/literal hole, not only linearity, tripartiteness,
ordered shadows, or proper edge-coloring.

## 4. Berge books and local triangle bounds

A `k`-book is a family of `k` Berge triangles sharing a hyperedge.
Ghosh--Gyori--Nagy-Gyorgy--Paulos--Xiao--Zamora prove that a `k`-book-free
3-uniform hypergraph has at most `(1+o(1))n^2/8` hyperedges. Source:
[Ghosh et al., *Book free 3-Uniform Hypergraphs*](https://arxiv.org/abs/2110.01184).
Gerbner gives sharp variants for Berge books. Source:
[Gerbner, *The Turan number of Berge book hypergraphs*](https://arxiv.org/abs/2111.11162).

**Mismatch.** These results assume a fixed pointwise upper bound on the
number of Berge triangles sharing an edge. The literal hole does not state
such a book exclusion, and P83/P87 only give cubic global bounds. Even under
fixed book-freeness, the cited conclusion is quadratic in the number of
vertices and does not yield the sharp count `T_F<=C_S`.

## 5. Induced and colored arithmetic removal

Fox--Tidor--Zhao prove induced arithmetic removal for a fixed collection of
`r`-colored complexity-one patterns over a fixed finite field: if a coloring
`phi:F_q^n\{0}->[r]` has `o(1)` density of every pattern, one may recolor an
`o(1)` fraction of the whole vector space to eliminate the patterns. They
also discuss inhomogeneous patterns. Source:
[Fox--Tidor--Zhao, *Induced arithmetic removal: complexity 1 patterns over
finite fields*](https://arxiv.org/abs/1911.03427).

Ordinary colored removal for a full-rank system `Ax=b` similarly deletes
`o(q)` elements from each variable set when the system has
`o(q^(m-k))` solutions. Source:
[Kral--Serra--Vena, *A Removal Lemma for Systems of Linear Equations over
Finite Fields*, Theorem 1](https://arxiv.org/abs/0809.1846).

**Mismatch.**

* In (1), the prescribed color set is `U=B`, so the number of arithmetic
  colors grows with `p`; the induced theorem fixes `r` and the pattern family.
* Encoding only membership/nonmembership uses two colors but has ambient size
  `h=Theta(p^2)` and a color class of size `p=o(h)`. Recoloring all of `B` is
  permitted by an `o(h)` conclusion, so the theorem is vacuous at the required
  scale.
* Removal concerns copies of one fixed linear system. The desired implication
  relates many triforces in the fold system to a different, distinguished
  coefficient `r_{3B}(h-1-b)`. No cited removal theorem provides that bridge.

Relative hypergraph removal avoids the deletion-scale problem only under a
linear-forms pseudorandom majorant: the majorant must have asymptotically the
expected density for every subgraph of the two-blow-up of the pattern.
Source: [Conlon--Fox--Zhao, *A relative Szemeredi theorem*, Theorem
2.12](https://arxiv.org/abs/1305.5440). Integer Sidonicity and positive defect
do not supply this two-blow-up hypothesis; it is substantially stronger than
the exact fourth-moment identity `E_+(B)=2p^2-p`.

## 6. What dense-Sidon theorems do apply

Prendiville's Theorem 1.1 applies to `S subset [N]` with
`|S|>=delta*N^(1/2)`, near-Sidon energy
`E(S)<=(2+eta)|S|^2`, a translation-invariant equation
`a_1x_1+...+a_sx_s=0`, and `s>=5`. For exact Sidon sets (`eta=0`) and fixed
`delta>0`, it gives at least

\[
          \exp(-O_{a_i}(1/\delta))N^{s/2-1}              \tag{4}
\]

solutions for all sufficiently large `N`. Source:
[Prendiville, *Solving equations in dense Sidon sets*, Theorem
1.1](https://arxiv.org/abs/2005.03484).

This theorem applies fully to the frontier after shifting `B` by one and
taking `N=h`. Positive defect gives

\[
 h<{3p^2-p+2\over2},\qquad {p\over\sqrt h}
   \geq \sqrt{2/3}-o(1),                                \tag{5}
\]

while difference uniqueness gives `h-1>=binom(p,2)` and Sidonicity gives
`E(B)=2p^2-p`. Thus `h=Theta(p^2)`. With coefficients
`(1,1,1,-1,-1,-1)`, (4) yields

\[
 \#\{x_1+x_2+x_3=x_4+x_5+x_6:x_i\in B\}=\Omega(h^2)
 =\Omega(p^4).                                          \tag{6}
\]

The repeated-coordinate contribution is `O(h^(7/4))` by the degeneracy
estimate in Prendiville's proof of Corollary 1.2, so (6) remains
`Omega(p^4)` with all six variables pairwise distinct.

**Mismatch.** Equation (6) is exactly the phase-free equal-three-sum output
already visible in P85. Its coefficients sum to zero, so translating the set
or subtracting fold equations removes `h` and `b`. Loose fold triangles are a
special `O(p^3)` subfamily satisfying three endpoint fold equations and the
P83/P87 phase stencil. The theorem gives no control on that subfamily.

Ortega--Prendiville's Fourier theorem states, for Sidon `S subset [N]`,

\[
 \left\|\widehat{1_S}-{ |S|\over N}\widehat{1_{[N]}}\right\|_\infty
 \ll N^{1/2}\left(\left|1-{|S|\over N^{1/2}}\right|+N^{-1/4}\right)^{1/2}.
                                                                    \tag{7}
\]

Source: [Ortega--Prendiville, *Extremal Sidon Sets are Fourier Uniform*,
Theorem 6.3](https://arxiv.org/abs/2110.13447).

**Mismatch.** In the positive-defect range, `p/sqrt(h)` may stay a fixed
distance from one (down to `sqrt(2/3)+o(1)`). Then (7) is only `O(sqrt h)=O(p)`
and gives no Fourier little-oh. It also controls one-frequency marginals,
whereas P84(17) needs correlated off-diagonal two-frequency quartic slices.

## 7. Current four-variable cutoff

Tung's 2026 results for a `B_h` set require more than `2h` variables for the
general linear-equation theorem. For non-translation-invariant equations in
Sidon sets, the dichotomy theorem requires a zero-sum subcollection of at least
five coefficients. Source:
[Tung, *Linear equations and chromatic thresholds in B_h sets*, Theorems 1.3
and 1.8](https://arxiv.org/html/2606.30767).

**Mismatch.** Here `h=2` in the `B_h` notation, while the literal hole is the
four-variable inhomogeneous equation

\[
                       x+y+z-w=-b.                     \tag{8}
\]

It lies exactly outside the `s>2h` range. Its coefficient multiset
`(1,1,1,-1)` has no zero-sum subcollection larger than two, so it also fails
the hypothesis of the non-translation-invariant dichotomy. Thus the newest
general theorem located does not reach the forbidden coefficient in this
problem.

## 8. Corners and popular differences

Berger's theorem concerns a fixed-density set `A subset G x G` and guarantees
a nonzero group difference supporting many ordinary corners
`(x,y),(x+d,y),(x,y+d)`. Source:
[Berger, *Popular Differences for Corners in Abelian
Groups*](https://arxiv.org/abs/1909.12350). The sharper finite-field density
scale is tied to the triforce theorem cited above.

**Mismatch.** A quadratic fold count makes a rank projection dense, so these
theorems do produce rank corners. They preserve equality of rank increments,
not the integer mark map, the repeated arithmetic color `u`, the endpoint
equation `a+c+h=u+v`, or the phase `h-1-b`. In the value grid the relevant set
has density `O(p^-2)`, outside the dense hypothesis. This is the exact
rank/value obstruction in P85.

## 9. Literature boundary

The closest theorem-shaped statement not found in the audited literature is
the following arithmetic strong-coloring defect bound:

> If the proper coloring in Section 1 comes from endpoint-ordered integer
> Sidon folds, has positive defect, and satisfies
> `Delta+(B) disjoint (B+B+b)`, then
> `sum_u(e_G(A_u,C_u)-|M_u|) <= |E(G)|`.

All known general results discard at least one load-bearing item: the original
color, the integer endpoint, the moving forbidden coefficient, the order cut,
or the relative deletion scale. Consequently no primary-source theorem in
this audit proves C84, `T_F=O(C_S)`, `T_F=o(p^3)`, or an infinite
counterfamily.
