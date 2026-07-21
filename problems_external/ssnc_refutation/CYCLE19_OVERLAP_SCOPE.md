# Exact scope of the root-block overlap obstruction

Status: **ALL MISSING 2-FACTORS ARE EXCLUDED IN THE SHARP REGULAR CELL**.

This note determines the hypotheses actually used by
`CYCLE19_OVERLAP_OBSTRUCTION.md`.  It starts from the fixed-target packing
identities and does not inspect a generator or use a solver.  The result is a
finite structural theorem, not a proof of Seymour's second-neighborhood
conjecture.

## 1. General order-19 notation

Let `D` be an oriented graph on 19 vertices with minimum outdegree 8 and
assume, for contradiction, that every vertex is strict:

\[
 |N^{++}(v)|<|N^+(v)|.
\]

Write

\[
 e_v=d^+(v)-8,\qquad
 \mu_v=\text{missing degree of }v,\qquad
 t_v=e_v+\mu_v.
\]

Let

\[
 C_v=\{v\}\cup N^+(v),\quad
 W_v=V\setminus(C_v\cup N^{++}(v)),
\]

and, for a target `u`,

\[
 U_u=V\setminus(\{u\}\cup N^-(u)),\qquad
 R_u=\{v:u\in W_v\},\qquad r_u=|R_u|.
\]

The general identities are

\[
 \sum_v e_v=19-q,qquad
 \sum_v\mu_v=2q,qquad
 |W_v|\geq\max(0,3-2e_v),                            \tag{1}
\]

and, for every `v in R_u`,

\[
 C_v\subseteq U_u,qquad
 |U_u\setminus C_v|=t_u-e_v-1.                       \tag{2}
\]

The strengthened target packing inequality is

\[
 {r_u\choose2}
 \leq r_u(t_u-1)-\sum_{v\in R_u}e_v.                 \tag{3}
\]

## 2. What exactly creates a three-root block

Call `u` a **good target** if

\[
 t_u=2\quad\hbox{and}\quad r_u=3.                   \tag{4}
\]

For such a target, (3) reads

\[
 3\leq3-\sum_{v\in R_u}e_v.
\]

Thus every root has `e_v=0`, and equality holds at every step of the pair
cover.  Equation (2) makes each complement `U_u minus C_v` a singleton.  The
three singleton exclusions cover the three unordered root pairs exactly
once.  Consequently:

1. no root pair is missing;
2. `R_u` induces a directed triangle; and
3. if `pi_u(v)` is the unique in-neighbour of `v` in that triangle, then

\[
 U_u\setminus C_v=\{\pi_u(v)\}.                      \tag{5}
\]

Writing `A` for the adjacency matrix, `M_u` for the indicator row of the
missing neighbours of `u`, and `mathbf e_x` for a unit row, (5) is exactly

\[
 \boxed{A_u+M_u=\mathbf e_v+A_v+\mathbf e_{\pi_u(v)}}
 \qquad(v\in R_u).                                   \tag{6}
\]

Thus `t_u=2` alone does **not** produce the row equation: the additional
saturation `r_u=3` is load-bearing.

## 3. Linearity and the overlap contradiction are local

For every oriented graph, the target sets `U_u` are injective.  Indeed, if
`U_u=U_w` for distinct `u,w`, then `u notin U_w` forces `u -> w`, while
`w notin U_u` forces `w -> u`, a digon.

Suppose two good root blocks share two roots `a,b`, and assume `a -> b`.
In both directed triangles `a` is the unique in-neighbour of `b`.  Equation
(6) then gives

\[
 U_u=C_b\cup\{a\}=U_w,
\]

contradicting injectivity.  Hence distinct good blocks intersect in at most
one point.

Equation (6) also says that the three adjacency rows indexed by a good block
agree in every coordinate outside that block.  If two good blocks `B,C`
intersect in exactly `{a}`, choose the unique arcs `a -> b` in `B` and
`a -> d` in `C`.  External row agreement gives both `b -> d` and `d -> b`.
Therefore distinct good blocks cannot intersect at all.

The maximal local conclusion is

\[
 \boxed{\text{every vertex belongs to at most one good root block}.} \tag{7}
\]

In particular, on 19 vertices there are at most six good targets.  This
local statement remains valid for arbitrary missing graphs and arbitrary
values of the other `e`, `mu`, and `t` parameters.

## 4. Every missing 2-factor is excluded

Now assume

\[
 e_v=0,\qquad \mu_v=2                              \tag{8}
\]

for every vertex.  Equivalently, every outdegree is 8 and the missing graph
is an arbitrary 2-factor; it need not be connected.

Every source has at least three unreachable targets by (1).  Every target
has `t_u=2`, and (3) gives `r_u<=3`.  Double-counting the unreachable
incidences yields

\[
 57\leq\sum_v|W_v|=\sum_u r_u\leq57.
\]

All inequalities are equalities.  Hence every source belongs to exactly
three root blocks and every target is good.  This contradicts (7).

Therefore no strict counterexample exists among outdegree-8 orientations of
`K_19-F` for **any** 2-factor `F`.  Connectedness of `F`, a cyclic labelling,
and every special property of `C_19` are unused.

The same proof is order-independent: if `n=2 delta+3`, every vertex has
outdegree `delta`, and every missing degree is two, then a hypothetical strict
counterexample again has at least three unreachable targets per source and
at most three roots per target.  For `delta>=1`, the equality and overlap
argument excludes the entire family.

## 5. First missing implication beyond the 2-factor cell

The broader order-19 identities do not force good targets.  This already
fails with `q=19` and `e_v=0` if the missing degrees are not all two.

For a concrete feasible missing-degree pattern, take a 9-cycle on vertices
`h_0,...,h_8`, attach two leaves to `h_0`, and attach one leaf to each of
`h_1,...,h_8`.  This missing graph has 19 vertices and 19 edges, with degree
multiset

\[
 \{4,3^8,1^{10}\}.                                   \tag{9}
\]

All missing degrees are positive and none equals two.  Under a hypothetical
strict failure with `e_v=0`, the source lower bounds and target upper bounds
would still sum to 57, but saturation would give root-block sizes

\[
 7,\quad 5\text{ (eight times)},\quad
 1\text{ (ten times)},                               \tag{10}
\]

not size three.  Thus neither (5) nor the three-root linearity argument is
available.  This is a falsifying parameter model for the attempted inference
that `q=19,e=0` alone forces the overlap obstruction; it is not asserted to
be an SSNC counterexample.

For `q<19`, some excess is present and even the source incidence lower bound
in (1) changes.  The first absent implication is again the forced supply of
three-root saturated targets.  No extension to those patterns follows from
the present proof.

## Exact scope

The rigorously closed family is:

\[
 \boxed{n=2\delta+3,\ d^+(v)=\delta,\ \mu_v=2
        \text{ for every }v,}
\]

which includes every order-19, outdegree-8 orientation with an arbitrary
missing 2-factor.  More generally, good root blocks are pairwise disjoint.
Beyond this, the packing identities do not force enough good blocks, and the
overlap route stops at that missing implication.

