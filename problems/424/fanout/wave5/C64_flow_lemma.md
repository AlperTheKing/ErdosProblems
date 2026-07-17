# C64: exact SCB token-flow lemma

## Statement

Fix a cutoff `X`.  Let `A_X` be the allowed integers, `H_X` the hard-shaped
integers, and `S_X` the structural splitless nonseeds.  For each admissible
factorization `n+1=ab`, choose a nonnegative weight

\[
\alpha_{n;a,b}\ge0,
\]

and for each seed-2 edge `m -> 2m-1 <= X` choose

\[
0\le\beta_{2m-1}\le1.
\]

Put

\[
A^+(v)=\sum_{ab=v+1}\alpha_{v;a,b},\qquad
A^-(v)=\sum_{n:\,v\in\{a,b\}}\alpha_{n;a,b},
\]

and, with absent boundary weights interpreted as zero,

\[
R(v)=A^+(v)-A^-(v)+\beta_{2v-1}-\beta_v.       \tag{1}
\]

For every vertex other than the seeds and the fixed splitless vertices, put

\[
\gamma(v)=\max\{R(v)-{\bf1}_{H_X}(v),0\}.       \tag{2}
\]

Define the seed credit

\[
C(\alpha,\beta)=
-R(2)-R(3)-\sum_{n;a,b}\alpha_{n;a,b}
-\sum_{v\notin S_X\cup\{2,3\}}\gamma(v).     \tag{3}
\]

If

\[
C(\alpha,\beta)\ge |H_X|,                     \tag{4}
\]

then every splitless-free forward-closed set `T` satisfies

\[
H_T(X)\le Q_T(X).                              \tag{SCB}
\]

The weights may be real.  The special case `gamma=0` is a genuine
capacity-respecting token flow.  The discovered finite certificates are
integral, use `beta` in `{0,1}`, and select at most one factorization for
each output, but some have positive congestion penalties `gamma`.

## Proof

Write `t_v=1_T(v)`, and let `q_{2m-1}` be the indicator of the boundary
event `m notin T`, `2m-1 in T`.  Forward closure gives

\[
t_n-t_a-t_b\ge-1                              \tag{5}
\]

for every admissible factorization.  The boundary indicator gives

\[
q_{2m-1}+t_m-t_{2m-1}\ge0.                    \tag{6}
\]

Multiply (5) by `alpha`, multiply (6) by `beta`, and sum.  The coefficient
of `t_v` is exactly `R(v)`, so

\[
\sum_v R(v)t_v+
\sum_m\beta_{2m-1}q_{2m-1}
\ge -\sum\alpha.                              \tag{7}
\]

Now set

\[
\mathcal O=\sum_{v\in H_X}t_v+sum_mq_{2m-1}.
\]

For a nonseed nonsplitless vertex, the coefficient left after subtracting
(7) from `O` is `d_v=1_H(v)-R(v)`.  If `d_v>=0`, then `d_v t_v>=0`; if
`d_v<0`, then `t_v<=1` gives `d_v t_v>=d_v=-gamma(v)`.  For a boundary
variable the remaining coefficient is `1-beta>=0`.  A splitless vertex has
`t_v=0`, while `t_2=t_3=1`.  Consequently (7) yields

\[
\mathcal O\ge -\sum\alpha-R(2)-R(3)-\sum_v\gamma(v)
=C(\alpha,\beta).
\]

By (4), `O>=|H_X|`.  Since

\[
\mathcal O=|H_X|-H_T(X)+Q_T(X),
\]

this is exactly (SCB).

## Interpretation and exact replay

A hard vertex supplies one token.  A closure row splits one token at `n`
into two tokens at its factors.  A selected seed-2 row moves one token from
`m` to `2m-1`.  Free vertices may discard surplus; overproducing a free
vertex beyond its hard supply costs one unit per excess token; splitless
vertices are fixed grounds.  The certificate succeeds when arrivals at
seeds 2 and 3, minus split and congestion costs, cover all hard vertices.

`C64_flow_certificate.py` discards all stored LP bound multipliers and checks
only (1)--(4) with Python integers.  Thus it is an independent algebraic
replay of the finite C56 certificates, not another call to the optimizer.

The remaining theorem-strength task is explicit: construct such a flow for
every cutoff `X`, or find a splitless-free forward-closed counterexample.
