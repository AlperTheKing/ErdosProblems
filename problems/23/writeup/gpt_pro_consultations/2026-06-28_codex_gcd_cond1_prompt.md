# GPT-Pro Consult: GCD Cond1 / SAT-ZMU-CONN

We are proving the remaining delta=0 step in Erdős Problem #23 after a finite-N certificate is already done. Please do **not** propose new computation or broad surveys. I need one concrete proof idea/lemma.

## Current spectral route

For a gamma-min connected-B maximum cut of a triangle-free graph, bad edges are `M` and cut edges are `B`. For each bad edge `f`, let `P_f` be the set of shortest `B`-geodesics between its endpoints and let `ell(f)` be the resulting odd cycle length. Define load

```text
T(v) = sum_{f in M} ell(f) * Pr_{P in P_f}[v in P].
```

Let `N=|V|`. Define

```text
omega(e) = sum_{f in M} a_bar(ell(f)) * tau_f(e),
a_bar(ell)=ell^3/(4(ell^2-2)),
```

where `tau_f(e)` is the probability that the shortest odd cycle `P+f` uses edge `e`; in particular `tau_f(f)=1`.

The local circulant/Fourier comparison is proven:

```text
K <= diag(T) - L_omega.
```

The whole remaining theorem is the Green-capacity domination:

```text
H := L_omega + diag(N-T) >= 0.
```

Schur split:

```text
O = {v : T(v)>N},  Q = V\O.
H_QQ = H[Q,Q].
```

Claude verified exactly that GCD is equivalent to:

```text
(cond1) H_QQ is positive definite when O nonempty;
(cond3) Schur(H/H_QQ) >= 0 on O.
```

I am attacking cond1.

## Clean reduction of cond1

`H_QQ` is a grounded Laplacian. For a component `C` of the omega-support graph induced by `Q`, define

```text
ground(v) = (N-T(v)) + omega(v,O).
```

Then

```text
x^T H_QQ x =
 sum_{uv in omega[Q]} omega_uv (x_u-x_v)^2
 + sum_{v in Q} ground(v) x_v^2.
```

So `H_QQ` is positive definite iff every omega-component in `Q` has positive ground. A dangerous component is therefore an omega/K component `C` such that

```text
T(v)=N for all v in C,
omega(C,O)=0.
```

Since the cut graph `B` is connected, if `O` is nonempty then a dangerous `C` has a `B`-edge leaving it. That edge has zero shortest-geodesic traffic `mu=0`; otherwise it is a positive omega edge and would not leave the component.

Thus cond1 follows from the already exact-verified lemma:

```text
SAT-ZMU-CONN:
If O is nonempty and a B-edge uv has mu(uv)=0 with T(u)=N,
then u's positive-traffic/K component meets O.
```

This lemma is verified with 0 violations on all exact gates, including glued-island batteries. We need a proof.

## Split of SAT-ZMU-CONN

It is enough to prove:

```text
A-alltie:
If mu(uv)=0 and T(u)=N, then T(v)=0.

C-alltie:
If O is nonempty, T(z)=0, zv in B, and T(v)=N,
then the K component of v meets O.
```

The sharper live target for C-alltie is:

```text
DIRECT-ZERO-SAT-O:
If O is nonempty, T(z)=0, zv in B, and T(v)=N,
then v directly shares a shortest bad-edge geodesic with some o in O
(i.e. K[v,o]>0 before transitive closure).
```

This qualitative target has 0 violations on full all-gamma N<=11, N=12 leaf caveat, glued batteries, Mycielskians, and blowups. Quantitative strengthenings of it are false.

## Dead routes to avoid

Do not propose:

1. Pure subset/Hall/maxflow cuts; they are too weak.
2. One-vector superharmonic certificates for GCD (`H*S>=0`, `H*T>=0`); false on Mycielskians.
3. O-K-SUPPORT (“every positive K component meets O”); false on glued islands.
4. Self-capacity `T(v)<=|Kcomp|`; false on glued islands.
5. Quantitative direct overload bounds like `2*direct_over(v)>=zbd(v)`; false at all-gamma N=11.
6. The previously tested zero-moat prefix switch with a cut-tight prefix certificate as stated; its exact premise is currently vacuous and stronger binary variants fail on the N=12 leaf.

## What I need

Give one proof route for either:

1. `A-alltie`: why a saturated endpoint of a zero-mu B-edge forces the other endpoint to have `T=0`; or
2. `DIRECT-ZERO-SAT-O` / `C-alltie`: why a zero-load B-neighbor of a saturated vertex forces direct/geodesic connection to overload, using gamma-minimality of the cut; or
3. A direct proof of `SAT-ZMU-CONN`.

Please state the candidate lemma precisely and include the switching/discharging/energy calculation. I will exact-test any intermediate inequality before trusting it.
