# GPT-Pro Consult Prompt — CAGE/KKT-Core Exclusion

We are proving the last remaining inequality in Erdős Problem #23.  All
reductions are already verified; the remaining target is one of these
equivalent forms:

```text
ROWSUM-O: for every bad edge f, sum_g <p_f,p_g> <= N.
SPEC: rho(P^T P) <= N.
LPD/CORR: for all y >= 0,
  sum_f sum_{i<j} sqrt(w_{f,i} w_{f,j})
  <= 1/2 sum_v (N-S(v)) y_v,
where w_{f,i}=sum_v p_{f,i}(v)y_v.
```

Definitions: fix a maximum cut of a triangle-free graph.  `B` are cut
edges, `M` are monochromatic bad edges.  For `f=(a,b) in M`,
`ell(f)=d_B(a,b)+1`, and `p_{f,i}` is the probability distribution on layer
`i` of a uniformly random shortest `B`-geodesic from `a` to `b`.
`S(v)=sum_f p_f(v)`, and the available vertex slack in CORR is `N-S(v)`.

Standard routes already refuted exactly: ordinary Hall/min-cut over fixed
corridors, endpoint cut-metric/Crofton LP, overlap-packing LP, bounded-edge
support reductions, simple layer or pairwise Cauchy-Schwarz, and uniform
routing.

## Current new certificate class: CAGE

For every bad edge `f`, layer-pair `i<j`, gap `t` with `i<=t<j`, and actual
`B`-edge `e` used at gap `t` by some shortest `f`-geodesic, introduce
nonnegative routing variables

```text
alpha_{f,i,j,t,e}.
```

They satisfy:

```text
(R1) sum_{t=i}^{j-1} sum_e alpha_{f,i,j,t,e} = 1
     for each f,i<j.

(R2) sum_{i<=t<j} alpha_{f,i,j,t,e} = H_{f,t} pi_{f,t,e}
     for each f,t,e,
```

where

```text
pi_{f,t,e} = probability a shortest f-geodesic uses e at gap t,
H_{f,t} = sum_{i<=t<j} 1/(j-i).
```

Given alpha, define gate endpoint loads

```text
A_g(v) = sum_{i<=t<j} alpha_{f,i,j,t,e} p_{f,i}(v),
B_g(v) = sum_{i<=t<j} alpha_{f,i,j,t,e} p_{f,j}(v),
```

for gate `g=(f,t,e)`.  A CAGE certificate is alpha plus positive gate ratios
`r_g` such that for every vertex `v`,

```text
sum_g ( r_g A_g(v) + r_g^{-1} B_g(v) ) <= N - S(v).
```

This implies CORR by weighted AM-GM:
`sqrt(w_i w_j) <= (r_g w_i + r_g^{-1} w_j)/2` and summing.

Exact rational verification:

```text
N=8: total=85 ok=85 fail=0
N=9: total=650 ok=650 fail=0
N=10: total=5800 ok=5800 fail=0
N=11 first 100 load-bearing cases: ok=100 fail=0
Hard cases exact: I?BD@g]Qo[1], I?ABCc]}?[1], J???E?pNu?[2] (N=22).
```

Uniform alpha fails on hard cases:

```text
I?BD@g]Qo[1]: alpha0_ratio=1.0276, adaptive ratio=0.9985
J???E?pNu?[2]: alpha0_ratio=1.1441, adaptive ratio=0.9162
```

KKT diagnostics for the adaptive alpha LP at optimized `r`:

```text
I?BD@g]Qo[1]: 7/10 positive dual budget vertices, 3 large-slack vertices.
J???E?pNu?[2]: 11/22 positive dual budget vertices.
Odd-cycle equality case: all primal vertex budgets tight, dual highly degenerate.
```

New exact identity: for gate mass `m_g=H_{f,t} pi_{f,t,e}`, every CAGE
certificate satisfies

```text
sum_v [N-S(v) - sum_g (r_g A_g(v) + r_g^{-1}B_g(v))]
= N^2 - Gamma - sum_g m_g (r_g+r_g^{-1}-2).
```

This was exact-checked on all 13 saved rational JSON certificates.  Hence
if `Gamma=N^2`, every feasible CAGE certificate has `r_g=1` on every
positive-mass gate and all vertex budgets tight.  In strict cases, any
obstruction is distributional: total capacity is enough, but routed mass
may concentrate on the wrong vertices.

Negative diagnostic: optimized gate ratios are not a hidden potential on
the shortest-path DAG.  Fitting `log r_g = phi(tail)-phi(head)` per bad edge
has max residual about `0.305` on `I?BD@g]Qo[1]`, `0.287` on
`I?ABCc]}?[1]`, and `1.132` on the N=22 witness.  So do not assume a
vertex-potential/gradient representation of `r`.

Fixed-ratio Farkas/Hall form: for fixed positive ratios `r_g`, CAGE
feasibility is equivalent to the weighted transport inequalities

```text
sum_f OT_f(lambda,r) <= sum_v lambda_v (N-S(v))    for every lambda>=0.
```

Here `OT_f(lambda,r)` transports unit demand on every layer pair `i<j` to
gate demands `m_g=H_{f,t} pi_{f,t,e}`, with cost

```text
r_g <lambda,p_{f,i}> + r_g^{-1}<lambda,p_{f,j}>.
```

Equivalently,

```text
eta(r)=max_{lambda>=0, lambda.cap=1} sum_f OT_f(lambda,r).
```

This was confirmed numerically by the alpha-LP dual on hard cases.  The
total-surplus identity is exactly the `lambda=1` shadow; a real obstruction
is an interior weighted transport Hall failure.

Important distinction: fixed CAGE is stronger than CORR because it asks for
one `(alpha,r)` working for all `lambda`.  A direct proof of CORR may allow
the allocation and ratios to depend on `y=lambda`; then the natural target is

```text
for every lambda>=0, exists an admissible alpha and gate ratios r(lambda)
such that sum_f OT_f(lambda,r(lambda)) <= lambda.cap.
```

If you propose a theorem, please state whether it proves the stronger fixed
CAGE form or only this y-dependent conic-flow form.  Either is useful if it
implies CORR.

## Question

Please propose one concrete theorem/lemma that would prove universal CAGE
existence, or characterize a tight CAGE obstruction strongly enough to force
an odd-cycle blow-up extremal.

Desired shape:

1. A KKT-core exclusion statement for a hypothetical optimal CAGE value
   `eta>1`, using triangle-free separated corridors.
2. Or a minimax/duality theorem reducing CAGE existence to a corridor
   Hall inequality that is strictly stronger than the ordinary fixed-corridor
   Hall cuts already refuted.
3. Or a structural characterization of equality `eta=1`: KKT equations
   imply every used corridor is saturated and the graph is an odd-cycle
   blow-up.

Do not re-propose ordinary subset Hall, uniform alpha, bounded support,
or endpoint cut-metric/Crofton certificates; all have exact counterexamples.
Give one explicit next inequality or lemma, including the quantities to
exact-test on census/blow-ups.
