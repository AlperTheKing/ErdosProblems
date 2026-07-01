# GPT-Pro Consult Prompt: CAGE / CORR KKT Obstruction

We are working on Erdős Problem #23.  Please do not give a survey; give one
concrete lemma, identity, or certificate that is exact-testable.

## Final target

For a triangle-free graph with a connected maximum cut:

- `B` = cut edges, bipartite and connected.
- `M` = bad/monochromatic edges.
- Each bad edge `f=(a,b)` has odd length `ell(f)=d_B(a,b)+1 >= 5`.
- `cyc[f]` = all shortest `B`-geodesics between the endpoints of `f`.
- `p_f(v)` = fraction of shortest `f`-geodesics through vertex `v`.
- `O_{fg}=sum_v p_f(v)p_g(v)`.

Everything is reduced to proving any one of:

```text
ROWSUM-O:  for every f, sum_g O_fg <= N.
SPEC:      rho(O) <= N.
LPD/CORR:  for all y>=0,
           sum_f sum_{i<j} sqrt(w_{f,i} w_{f,j})
           <= 1/2 sum_v (N-S(v)) y_v,
           w_{f,i}=sum_{v in layer i of f} y_v p_{f,i}(v),
           S(v)=sum_f p_f(v).
```

The CORR form is the current best route.

## CAGE certificate route

For each bad edge `f`, each layer pair `i<j`, and each gate
`g=(f,t,e)` where `i<=t<j` and `e` is a `B`-edge used in gap `t` by a
shortest `f`-geodesic, introduce transport variables

```text
alpha_{f,i,j,t,e} >= 0.
```

Let

```text
pi_{f,t,e} = probability a random shortest f-geodesic uses B-edge e in gap t,
H_{f,t} = sum_{0<=i<=t<j<ell(f)} 1/(j-i).
```

CAGE asks for `alpha` and positive gate ratios `r_g` satisfying:

```text
(R1)  sum_{t,e between i,j} alpha_{f,i,j,t,e} = 1
      for every f,i<j.

(R2)  sum_{i<=t<j} alpha_{f,i,j,t,e} = H_{f,t} pi_{f,t,e}
      for every gate g=(f,t,e).
```

Define routed loads

```text
A_g(v)=sum alpha_{f,i,j,t,e} p_{f,i}(v),
B_g(v)=sum alpha_{f,i,j,t,e} p_{f,j}(v).
```

The vertex budget is

```text
sum_g ( r_g A_g(v) + r_g^{-1} B_g(v) ) <= N - S(v)
```

for every vertex `v`.

If a CAGE certificate exists, AM-GM proves CORR/LPD, hence ROWSUM/SPEC and
the conjecture. This implication has been exact-verified; the only missing
piece is universal CAGE existence.

## Fixed-ratio Farkas form

For fixed positive ratios `r_g`, CAGE feasibility is equivalent to:

```text
sum_f OT_f(lambda,r) <= sum_v lambda_v (N-S(v))
```

for every `lambda>=0`, where `OT_f(lambda,r)` is the transportation cost of
sending every layer pair `i<j` to gate marginals

```text
m_g=H_{f,t} pi_{f,t,e}
```

with cost

```text
c_lambda((i,j),g)
= r_g       * sum_v lambda_v p_{f,i}(v)
 + r_g^{-1} * sum_v lambda_v p_{f,j}(v).
```

At a hypothetical KKT obstruction, positive routes use zero-reduced-cost gates
and every nondegenerate gate ratio balances:

```text
r_g^2 * <lambda,A_g> = <lambda,B_g>.
```

## What is already dead

Do not propose these:

1. Fixed positive-coefficient Schur/HARVEST current inequalities.  They fail
   on complete C5 blow-ups `[k+1,k,k+1,k,k+1]` at large k.  In particular
   `25*rho_o >= 4(cU_o-a_o)` is false already at `[6,5,6,5,6]`.
2. Any fixed finite-depth Jacobi/Neumann truncation.  Required depth grows
   with blow-up size.
3. Local layer-size, prefix-size, support-size, centered interval, or selected
   fractional-SPLIT certificates.  They all have exact counterexamples.
4. Scalar Hall/max-flow on subsets, raw level sets, or arbitrary prefix unions.
   These miss interior/mixed `lambda` and have exact falsifiers.
5. Uniform CAGE routing `alpha0`.  It fails on hard cases; adaptive alpha is
   load-bearing.

## Positive guardrails

Complete odd-cycle blow-ups are harmless for ROWSUM:

For `C_m[x_0,...,x_{m-1}]`, if the maximum cut leaves the minimum adjacent
product `x_0*x_1` bad, then for a bad edge `f`

```text
(O1)_f = x_0+x_1+x_0*x_1*sum_{i=2}^{m-1} 1/x_i <= N.
```

The proof uses only the minimum adjacent product inequalities.  For the C5
family `[k+1,k,k+1,k,k+1]`, ROWSUM has slack exactly `1` at every scale even
though the false Schur current bounds fail.

Exact CAGE certificates exist on all tested hard cases, including the N=22
witness and census slices.  Equality certificates occur only at odd-cycle
blow-up extremals.

## Request

Give one concrete proof atom for universal CAGE existence or KKT-core
exclusion.

Acceptable outputs:

1. A finite inequality in the CAGE/Farkas variables that, if violated, gives a
   triangle-free/max-cut contradiction.
2. A structural lemma about a CAGE KKT obstruction, stated so it can be checked
   from `(M, ell, cyc, p_f, gates, lambda, alpha, r)`.
3. An explicit construction of ratios `r_g` or transport `alpha` from the
   shortest-geodesic corridor geometry.

For any proposed lemma, state exactly:

- how to compute every term;
- why it implies CAGE/CORR;
- where triangle-freeness enters;
- why it is not one of the dead routes above.

Please avoid framing-only answers.  I need a formula/lemma that can be passed
to an exact rational verifier.
