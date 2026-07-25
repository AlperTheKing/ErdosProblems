# Rank-uniform codimension-three BV positivity for full-dimensional hives

## Result

Let `P` be a full-dimensional size-`r` hive polytope in its standard interior
coordinate space

\[
  \mathbb R^D,\qquad D=\binom{r-1}{2}.
\]

Every three-dimensional normal cone of `P` has strictly positive
Berline--Vergne alpha value. Consequently, if `D >= 3`, the fourth-leading
coefficient of the stretched Littlewood--Richardson polynomial is strictly
positive:

\[
 [t^{D-3}]\,c_{t\lambda,t\mu}^{t\nu}>0.
\]

For `r=5`, where `D=6`, this says in particular that the cubic coefficient is
positive for every full-dimensional size-five hive polytope.

This is a rank-uniform theorem, not a fixed-rank cascade. It does **not** prove
the full KTT conjecture: lower coefficients and non-full-dimensional hive
fibres remain outside this argument.

## 1. The coefficient bridge

For a lattice `D`-polytope, the Berline--Vergne/McMullen local formula gives

\[
 e_{D-3}(P)=
 \sum_{\substack{F\le P\\\dim F=D-3}}
 \alpha^{\mathrm{BV}}(F,P)\,\operatorname{nvol}(F).                 \tag{1}
\]

Here `alpha(F,P)` depends only on the three-dimensional normal cone of `P`
along `F`, and every normalized face volume in (1) is positive.

Hive polytopes need not be lattice polytopes. This causes no problem because
their Ehrhart counting function is nevertheless an ordinary polynomial. Pick
`q` such that `qP` is a lattice polytope. Then

\[
 L_{qP}(t)=L_P(qt),\qquad e_k(qP)=q^k e_k(P).
\]

Scaling preserves all normal cones and multiplies every `k`-face normalized
volume by `q^k`. Apply (1) to `qP` and divide by `q^{D-3}`. Thus (1) also holds
for the rational hive polytope `P`.

References for the two local facts used below are Berline--Vergne,
*Local Euler--Maclaurin formula for polytopes*, arXiv:math/0507256, and
Castillo--Liu, *Berline--Vergne valuation and generalized permutohedra*,
arXiv:1509.07884, especially Lemmas 3.3 and 3.10.

## 2. Saturated simplicial cones

After boundary coordinates are eliminated, every primitive outward rhombus
normal is a nonzero vector with entries in `{0,+1,-1}` and squared Euclidean
norm at most four.

Let

\[
 C=\operatorname{cone}(n_1,n_2,n_3)
\]

be a simplicial normal cone, and first assume that `n1,n2,n3` form a basis of
the saturated lattice in their real span. Put

\[
 G=(\langle n_i,n_j\rangle)_{i,j=1}^3.
\]

The primitive generators of the polar pointed feasible cone are the negative
dual basis, so their Gram matrix is `G^{-1}`. Castillo--Liu Lemma 3.10 gives

\[
 \alpha^{\mathrm{BV}}(C)
 =\frac18+\frac1{24}\sum_{i<j}(G^{-1})_{ij}
 \left(\frac1{(G^{-1})_{ii}}+\frac1{(G^{-1})_{jj}}\right).          \tag{2}
\]

Every possible `G` lies in the following finite, rank-independent class:

- `G` is positive definite, integral and symmetric;
- its three diagonal entries lie in `{1,2,3,4}`;
- its off-diagonal entries lie in `[-4,4]`.

Exact enumeration of this superset gives 4,320 matrices. Formula (2) is
strictly positive for every one; its abstract minimum is

\[
 \frac1{264},
\]

attained, up to reordering, at

\[
 \begin{pmatrix}2&2&2\\2&3&1\\2&1&4\end{pmatrix}.
\]

This proves positivity for every saturated simplicial hive normal cone in
every rank. The exact checker is `uniform_codim3_gram_lemma.py`; its canonical
record hash is

`fb57b8cdcf595017a111f7b166067031d8ff8048ab5a3a480a1fb40272ad2593`.

## 3. Why the nonsaturated classification is finite

For a grid vertex `(x,y)` use its three boundary-distance coordinates

\[
 \delta_1=x,\qquad \delta_2=y,\qquad \delta_3=r-x-y.
\]

On one unit rhombus, each `delta_j` has range at most two. Suppose the
support-overlap graph of three rhombi is connected, where two rhombi are
adjacent when their restricted stencils share an interior coordinate. A path
through at most three rhombi shows that each `delta_j` has range at most six
on their union.

Let `m_j` be the minimum of `delta_j` on that union and remove

\[
 s_j=\max(m_j-1,0)
\]

empty strips next to boundary `j`. This translation preserves the unit-rhombus
geometry. It also preserves exactly which vertices are boundary vertices: a
side originally touched still has minimum zero, while a side not touched keeps
minimum one. In the reduced board every boundary distance is at most `6+1=7`.
Since their sum is the new board size, that size is at most 21.

Therefore boards of sizes 3 through 21 exhaust every connected three-rhombus
overlap type in every rank. The exact classification checks 761,329 connected,
rank-three triples and finds

| saturation index | occurrences |
|---:|---:|
| 1 | 760,527 |
| 2 | 801 |
| 4 | 1 |

There are no index-3 or other higher-index types. Up to row and coordinate
permutation there are 13 index-two types and one index-four type.

The canonical checker is `uniform_codim3_local_certificate.py`. It returns
`PASS`; the canonical nonsaturated-type hash is

`27b0da1c9889576779c4e7d1939243b748f16062bc16c227f104adea343cf92d`.

### Disconnected support graphs

No rank scan is needed here. If all three supports are disjoint, choosing one
nonzero coordinate from each row gives a diagonal `3 x 3` minor of determinant
`+1` or `-1`, hence saturation.

Otherwise the graph has a two-row component and one disjoint row. The third
row contributes a separate `+1` or `-1` column, so saturation reduces to the
two-row component. If those two rows are independent modulo two, an odd
`2 x 2` minor exists; a `2 x 2` matrix with entries in `{0,+1,-1}` has odd
determinant only when that determinant is `+1` or `-1`. If they are dependent
modulo two, their supports agree. Since they are not parallel, their rank-two
saturation index is exactly two, and their half-sum is an integral
`{0,+1,-1}` vector of squared norm at most four. This is precisely the
midpoint subdivision in the next section.

Thus the size-21 connected certificate plus this two-row argument covers all
ranks.

## 4. Nonsaturated simplicial cones

For every index-two type the unique nonzero saturation coset is represented by

\[
 h=\frac12\sum_{i\in S}n_i,
\]

where the exact classification gives `|S|=2`, except for twelve size-four
boundary types with `|S|=3`. In every case `h` is a nonzero `{0,+1,-1}` vector
with squared norm at most four.

If `|S|=2`, insert `h` on the corresponding two-dimensional face of `C`; this
subdivides `C` into two saturated simplicial cones. If `|S|=3`, `h` is an
interior ray and the star subdivision has three saturated simplicial cones.
Saturation is also immediate algebraically: adjoining `h` adds the unique
missing index-two coset, and the omitted original generator is twice `h` minus
the other generator(s). Each cell is therefore covered by Section 2.

The single index-four cone occurs only in size four. Up to an orthogonal
coordinate permutation its rays are

\[
 n_1=(1,-1,-1),\quad n_2=(-1,1,-1),\quad n_3=(-1,-1,1).
\]

Insert the three edge midpoints

\[
 h_{12}=(0,0,-1),\quad h_{13}=(0,-1,0),\quad h_{23}=(-1,0,0).
\]

The four saturated cells are

\[
\begin{aligned}
 &(n_1,h_{12},h_{13}),\quad (n_2,h_{12},h_{23}),\\
 &(n_3,h_{13},h_{23}),\quad (h_{12},h_{13},h_{23}).
\end{aligned}
\]

Their exact BV values are `1/24, 1/24, 1/24, 1/8`, respectively, so the
original cone has alpha value `1/4`.

Why can the cell values be added without inclusion--exclusion corrections?
Castillo--Liu Lemma 3.3 applies directly to a subdivision of the **normal**
cone. Intersections of distinct cells are lower-dimensional normal cones;
after polarity the error cones contain lines, and the BV valuation vanishes on
cones containing lines. Hence

\[
 \alpha^{\mathrm{BV}}(C)=\sum_{\text{maximal cells }C_i}
 \alpha^{\mathrm{BV}}(C_i)>0.                                    \tag{3}
\]

As an independent check, subdividing the polar feasible cone and retaining its
ordinary inclusion--exclusion term gives the same values. The auxiliary exact
checker `uniform_codim3_index2_gate.py` finds no zero or negative index-two
type through the stabilized local atlas; its minimum is `1/36`.

## 5. Nonsimplicial three-dimensional normal cones

Let `C` now be any pointed three-dimensional hive normal cone with four or more
extreme rays. Intersect it with an affine plane to obtain a convex polygon and
triangulate that polygon using only its vertices. Coning the triangles gives a
subdivision of `C` into simplicial cones, each generated by three primitive
rhombus normals. Sections 2--4 show that every cell has positive BV alpha.
Applying the normal-cone valuation identity (3) once more gives

\[
 \alpha^{\mathrm{BV}}(C)>0.
\]

This covers nonunimodular and nonsimplicial codimension-three faces uniformly
in `r`. Substitution in (1) completes the claimed fourth-leading-coefficient
theorem.

## Reproduction

From `E:\Projects\ErdosProblems` run:

```text
python problems_external\ktt_lr_negativity\uniform_codim3_gram_lemma.py
python problems_external\ktt_lr_negativity\uniform_codim3_local_certificate.py
```

Both commands use exact integer/rational arithmetic for every verdict and must
return `"status": "PASS"` with the hashes printed above.
