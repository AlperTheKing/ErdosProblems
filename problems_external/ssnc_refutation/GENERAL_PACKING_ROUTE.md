# General fixed-target packing route

Status: **BLOCKED**.  The packing argument gives an exact necessary condition
for a strict counterexample and excludes the two densest possible degree
layers.  The current published minimal-counterexample reductions do not turn
that condition into a contradiction for the remaining layers.  This note is
not a proof of Seymour's Second-Neighborhood Conjecture and does not authorize
an order-by-order search.

## Setup

Let `D` be an oriented graph on `n` vertices such that

\[
  |N^{++}(v)|<|N^+(v)|
\]

for every vertex `v`, where `N^{++}(v)` is the new second
out-neighborhood.  Write

- `delta` for the actual minimum outdegree of `D`;
- `k=n-2 delta`;
- `q` for the number of unordered nonadjacent vertex pairs;
- `e_v=d^+(v)-delta` and `E=sum_v e_v`;
- `mu_v` for the missing degree of `v`;
- `t_v=e_v+mu_v` and `T=sum_v t_v`;
- `A={v:e_v=0}`, `b=|V(D)\A|`; and
- `s=|{v:t_v>0}|`.

The average-outdegree bound gives `delta <= (n-1)/2`, and hence `k>=1`.
Counting arcs and missing incidences gives the exact identities

\[
\begin{aligned}
  E
    &=\binom n2-q-n\delta
      =\frac{n(k-1)}2-q,\\
  \sum_v\mu_v&=2q,\\
  T
    &=E+2q
      =\frac{n(k-1)}2+q.
\end{aligned} \tag{1}
\]

Since every positive excess is at least one,

\[
  b\leq E. \tag{2}
\]

## General unreachable-pair lower bound

For `v in A`, put `C_v={v} union N^+(v)`, so `|C_v|=delta+1`.
There are `n-delta-1` vertices outside `C_v`.  The strict-counterexample
assumption gives `|N^{++}(v)|<=delta-1`, so at least

\[
  (n-\delta-1)-(\delta-1)=n-2\delta=k
\]

vertices are unreachable from `v` by a directed walk of length at most two.
Define

\[
  \mathcal R
    =\{(v,u):v\in A,\ u\notin C_v\cup N^{++}(v)\}.
\]

Then

\[
  |\mathcal R|\geq k|A|=k(n-b). \tag{3}
\]

## Fixed-target capacity

Fix a target `u` and set

\[
  R_u=\{v\in A:(v,u)\in\mathcal R\},
  \qquad r_u=|R_u|,
\]

and

\[
  U_u=V(D)\setminus(\{u\}\cup N^-(u)).
\]

For every `v in R_u`, neither `v` nor any out-neighbor of `v` points to
`u`; otherwise `u` would be reachable in one or two steps.  Thus

\[
  C_v\subseteq U_u. \tag{4}
\]

The vertices other than `u` split into its out-neighbors, in-neighbors, and
nonneighbors, so

\[
  |U_u|=d^+(u)+\mu_u=\delta+t_u. \tag{5}
\]

If `t_u=0`, (4)--(5) would put a `(delta+1)`-element set inside a
`delta`-element set, and therefore `r_u=0`.  If `t_u>=1`, define

\[
  B_v=U_u\setminus C_v
  \qquad(v\in R_u).
\]

Then `|B_v|=t_u-1`.  For two distinct `v,w in R_u`, the absence of digons
implies that at least one of `w notin C_v` or `v notin C_w` holds.  Since
both sources lie in `U_u`, at least one of `w in B_v` or `v in B_w` holds.
The sets `B_v` therefore cover every unordered pair of sources, and

\[
  \binom{r_u}{2}
    \leq\sum_{v\in R_u}|B_v\cap R_u|
    \leq r_u(t_u-1).
\]

For `r_u>0`, this gives the exact target-capacity bound

\[
  r_u\leq 2t_u-1. \tag{6}
\]

Summing (6) over the `s` vertices with positive `t_u`, and using (1), gives

\[
  |\mathcal R|
    \leq 2T-s
    =n(k-1)+2q-s. \tag{7}
\]

## Necessary inequality and the layers it closes

Combining (3) and (7), every strict counterexample must satisfy

\[
  k(n-b)\leq n(k-1)+2q-s,
\]

or, equivalently,

\[
  \boxed{\;kb+2q\geq n+s\;}. \tag{8}
\]

This is the exact necessary inequality furnished by the route.  Together
with (1)--(2), it rules out `k=1` and `k=2`:

- If `k=1`, then `E=-q>=0`, hence `q=E=b=s=0`; (8) would say `0>=n`.
- If `k=2`, then `E=n/2-q` and `T=n/2+q>0`, so `s>=1`, while
  `2b+2q<=2E+2q=n`, contradicting (8).

Consequently every strict counterexample must obey

\[
  \boxed{\;k\geq3\;},
  \qquad\text{equivalently}\qquad
  \boxed{\;n\geq2\delta+3\;}. \tag{9}
\]

For `k>=3`, the aggregate constraints are arithmetically feasible.  Indeed,
(1)--(2) only yield

\[
  kb+2q
    \leq kE+2q
    =\frac{nk(k-1)}2+(2-k)q, \tag{10}
\]

which does not contradict (8) in general.

## Audit of published minimal-counterexample reductions

Only primary sources were used for this audit.

1. Tyler Seacrest, *Seymour's Second Neighborhood Conjecture for Subsets of
   Vertices*,
   [arXiv:1808.06293](https://arxiv.org/abs/1808.06293), proves that if a
   counterexample with minimum outdegree `delta` exists, then a counterexample
   exists on at most `binom(delta+1,2)` vertices (Corollary 5, after the
   edge-minimal set inequality in Lemma 4).  Even under the strongest direct
   parameter reading, this gives

   \[
     n\leq\binom{\delta+1}{2},
   \]

   which is compatible with (9) for every `delta>=5`.  The reduction does not
   bound `b`, `q`, or `s` in (8).  If its reduction changes the minimum-degree
   parameter, it is weaker for the present purpose, not stronger.

2. Alberto Espuny Diaz, Antonio Girao, Bertille Granet, and Gal Kronenberg,
   *Seymour's second neighborhood conjecture: random graphs and reductions*,
   [arXiv:2403.02842](https://arxiv.org/abs/2403.02842) and the
   [published article](https://onlinelibrary.wiley.com/doi/full/10.1002/rsa.21251),
   prove that a vertex-minimal counterexample is strongly connected and has
   `delta>sqrt(n)` (Proposition 4), while failure of the conjecture would also
   yield arbitrarily large strongly connected counterexamples of bounded
   minimum outdegree (Proposition 5).  Proposition 4 gives `n<delta^2`, which
   remains compatible with (9), and Proposition 5 moves toward larger `k`,
   where (8) is weaker.  Neither proposition controls the saturation terms in
   (8).

3. The current primary preprint of Arpan Sadhukhan, R. B. Sandeep, and Sagnik
   Sen, *A proof of Seymour's second neighborhood conjecture for oriented
   graphs with minimum out-degree equal to 7*,
   [arXiv:2606.30588](https://arxiv.org/abs/2606.30588), states the stronger
   threshold theorem `delta<=7` (Theorem 1.1).  If that computer-assisted
   result is accepted, a counterexample must have `delta>=8`; this removes
   small minimum degrees but imposes no restriction on `b`, `q`, `s`, or `k`
   that contradicts (8).

The numerical compatibility is therefore:

| Source | Necessary parameter restriction | Interaction with packing |
|---|---:|---|
| fixed-target packing | `n>=2 delta+3` | required by (8) |
| vertex-minimal reduction | `n<delta^2` | compatible for `delta>=4` |
| Seacrest finite reduction | `n<=delta(delta+1)/2` | compatible for `delta>=5` |
| current degree-7 preprint | `delta>=8` for a counterexample | still compatible with both size bounds |

No cited reduction implies `k<=2`, and none supplies a strict improvement to
the target-capacity sum (7).

## Exact bottleneck: simultaneous saturation is feasible

The failure of the aggregate route is already sharp at `k=3`.  Take

\[
  n=2\delta+3,\qquad q=n,\qquad e_v=0,\qquad\mu_v=2
\]

for every vertex.  Then

\[
  E=b=0,\qquad T=2n,\qquad s=n,
\]

and (8) holds with equality:

\[
  kb+2q=2n=n+s.
\]

These are not merely formal parameters.  For odd `n=2 delta+3`, delete a
Hamilton cycle from `K_n`.  The resulting connected `2 delta`-regular graph
has an Eulerian orientation, in which every vertex has outdegree `delta` and
missing degree two; orienting along an Euler tour also gives a strongly
connected orientation.  This construction is **not** asserted to be a
counterexample.  Choosing `delta>=8` shows that degree accounting,
missing-pair accounting, strong connectivity, the current degree threshold,
and each cited size reduction are all compatible with the equality pattern.
A proof must use additional global information about the simultaneous sets
`C_v`, `B_v`, and `R_u`.

## Missing theorem-closing implication

To close the full conjecture by this route, one would need to derive from
minimality or another global structural lemma, for every remaining `k>=3`,
the strict inequality

\[
  kb+2q<n+s, \tag{11}
\]

or an equivalent strict improvement of the summed target capacity (7).
Equation (11) would contradict the necessary condition (8).  The current
published reductions above do not imply (11), and the `k=3` equality model
shows why the local pair-cover argument alone cannot imply it.

**BLOCKED: published reductions do not control `b`, `q`, `s`, or exclude
simultaneous target-capacity saturation for `k>=3`.**

The route therefore stops here.  Its proved output is exactly (8)--(9), not
the full conjecture and not a license for a cascade of bounded-order cases.
