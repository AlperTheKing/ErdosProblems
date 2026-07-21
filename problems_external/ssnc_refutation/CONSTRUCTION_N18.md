# The `n = 18`, minimum-outdegree-8 layer

Status: exact finite obstruction.  This note does **not** prove Seymour's
Second-Neighborhood Conjecture and does not justify moving to another order.

## Statement

There is no oriented graph on 18 vertices with minimum outdegree at least 8
such that

\[
  |N^{++}(v)| < |N^+(v)|
\]

for every vertex `v`.  Here `N^{++}(v)` is the new second out-neighborhood:
the vertices reachable by a directed two-step walk after removing `v` and the
direct out-neighbors of `v`.

## Edge accounting

Suppose, for contradiction, that such a graph `D` exists.  Let

- `q` be the number of unordered nonadjacent vertex pairs;
- `d_v = |N^+(v)|`;
- `e_v = d_v - 8 >= 0`; and
- `mu_v` be the number of vertices nonadjacent to `v`.

There are `binom(18,2) = 153` unordered pairs.  Because `D` has neither loops
nor digons, it has exactly `153 - q` arcs.  Consequently

\[
  \sum_v e_v = (153-q)-18\mathbin{\cdot}8 = 9-q,
  \qquad
  \sum_v \mu_v = 2q.
\]

In particular, `0 <= q <= 9`.

Let

\[
  A=\{v:d_v=8\}, \qquad b=18-|A|=|\{v:e_v>0\}|.
\]

Every positive `e_v` is at least one, so

\[
  b \leq \sum_v e_v=9-q,
  \qquad |A|\geq 9+q. \tag{1}
\]

## Unreachable-pair lower bound

For `v in A`, put

\[
  C_v=\{v\}\cup N^+(v).
\]

Then `|C_v|=9`, and its complement also has size 9.  The new second
out-neighborhood lies in that complement and, under the assumed strict
inequality, has size at most 7.  Hence at least two vertices are neither in
`C_v` nor in `N^{++}(v)`.

Define

\[
  \mathcal R=\{(v,u):v\in A,\ u\notin C_v\cup N^{++}(v)\}.
\]

By (1),

\[
  |\mathcal R|\geq 2|A|\geq 18+2q. \tag{2}
\]

## Fixed-target packing bound

Fix a target vertex `u`, and let

\[
  R_u=\{v\in A:(v,u)\in\mathcal R\},\qquad r_u=|R_u|.
\]

Also define

\[
  U_u=V(D)\setminus(\{u\}\cup N^-(u)).
\]

If `v in R_u`, then `v` does not point to `u`; moreover, no vertex of
`N^+(v)` points to `u`, since that would give a directed two-step walk from
`v` to `u`.  Therefore

\[
  C_v\subseteq U_u. \tag{3}
\]

The other 17 vertices split into out-neighbors, in-neighbors, and nonneighbors
of `u`.  Thus, with

\[
  t_u=e_u+\mu_u,
\]

we have

\[
  |U_u|=d_u+\mu_u=8+t_u. \tag{4}
\]

If `t_u=0`, equations (3)--(4) would place the 9-element set `C_v` inside an
8-element set, so `r_u=0`.

Now assume `t_u>=1`.  For each `v in R_u`, let

\[
  B_v=U_u\setminus C_v.
\]

By (3)--(4), `|B_v|=t_u-1`.  For two distinct vertices `v,w in R_u`, it is
impossible that both `w in C_v` and `v in C_w`: those two memberships would
give the forbidden digon `v -> w -> v`.  Since both `v` and `w` lie in
`U_u`, at least one of `w in B_v` or `v in B_w` must hold.  The ordered
exclusions supplied by the sets `B_v` therefore cover every unordered pair
from `R_u`.  Hence

\[
  \binom{r_u}{2}
  \leq \sum_{v\in R_u}|B_v\cap R_u|
  \leq r_u(t_u-1).
\]

When `r_u>0`, division by `r_u` gives

\[
  r_u\leq 2t_u-1. \tag{5}
\]

## Contradiction

Let `S={u:t_u>0}` and `s=|S|`.  The accounting identities give

\[
  \sum_u t_u
  =\sum_u e_u+\sum_u\mu_u
  =(9-q)+2q=9+q,
\]

so `s>=1`.  Summing (5), while using `r_u=0` outside `S`, yields

\[
\begin{aligned}
  |\mathcal R|
    &=\sum_u r_u\\
    &\leq\sum_{u\in S}(2t_u-1)\\
    &=2(9+q)-s\\
    &<18+2q.
\end{aligned} \tag{6}
\]

The strict upper bound (6) contradicts the lower bound (2).  Therefore the
assumed graph does not exist.

## Scope and audit points

- The proof uses only `n=18`, minimum outdegree at least 8, and the absence of
  loops and digons.
- It does not use the recent minimum-outdegree-7 preprint, the tournament
  theorem, solver output, or an asymptotic surrogate.
- Vertices with outdegree greater than 8 enter only through the nonnegative
  excesses `e_v`; only degree-8 vertices are used as sources in `mathcal R`.
- The strict inequality is load-bearing: for a degree-8 source it leaves at
  least two vertices outside its first and new second out-neighborhoods.
- No adjacency certificate is produced, because the entire registered
  `n=18`, minimum-outdegree-8 certificate class is excluded.
