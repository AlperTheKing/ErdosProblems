# 2x2-Closed Y-Dependent CAGE Candidate

This is a proof-mining note, not a proof.

## Setup

Fix a graph, a nonnegative test vector `y`, and one bad edge `f`.
Let `P_f` be the interval-gate routing polytope used in CAGE:

- one unit of demand for each layer pair `(i,j)`, `i<j`;
- fixed gate marginals
  `m_g = H_t pi_{t,e}` for each gate `g=(f,t,e)`;
- variables `alpha_{p,g}` only when gate `g` lies between the two layers of pair `p=(i,j)`.

For a route `alpha`, define the y-dependent edge contribution

```text
Phi_f(alpha,y) =
sum_g 2 sqrt( (A_g(alpha).y) (B_g(alpha).y) ).
```

The global y-dependent CAGE sufficient condition is

```text
sum_f Phi_f(alpha_f,y) <= sum_v (N-S(v)) y_v.
```

## 2x2 Move

For two layer pairs `p,q` and two gates `g,h`, suppose all four variables

```text
alpha_{p,g}, alpha_{q,h}, alpha_{p,h}, alpha_{q,g}
```

exist. A positive 2x2 swap of size `eps` is

```text
alpha_{p,g} -= eps
alpha_{q,h} -= eps
alpha_{p,h} += eps
alpha_{q,g} += eps
```

with `0 < eps <= min(alpha_{p,g}, alpha_{q,h})`.
It preserves every pair marginal and every gate marginal.

A route is **2x2-closed for y** if no positive 2x2 swap decreases `Phi_f(.,y)`.

## Candidate Lemma

For every connected-B triangle-free maximum-cut configuration and every `y>=0`, there exist CAGE routes
`alpha_f(y) in P_f`, one for each bad edge, such that:

1. every `alpha_f(y)` is 2x2-closed for `y`;
2. the y-dependent CAGE inequality holds:

```text
sum_f Phi_f(alpha_f(y),y) <= sum_v (N-S(v)) y_v.
```

Equivalently, if `alpha_f` is chosen as a global minimizer of the concave function `Phi_f(.,y)` over `P_f`,
then the inequality should hold. The stronger proof target would be to show that 2x2 closure is enough, avoiding
full vertex enumeration of `P_f`.

## Diagnostics

Script:

```text
problems/23/writeup/_codex_cage_2swap_closure.py
```

Procedure:

1. Start from the floating fixed adaptive CAGE route.
2. For a sampled `y`, greedily apply improving 2x2 swaps independently for each `f`.
3. Evaluate the y-dependent CAGE gap.

Results:

```text
I?BD@g]Qo[1]:
  alpha0 hard y gap before adaptive route: +0.027634728
  fixed adaptive route at same y:          -0.009481126
  after 2x2 closure:                       -0.015876099
  random worst over 300 sampled y:         -0.015876099
```

```text
J???E?pNu\?[2]:
  alpha0 hard y gap before adaptive route: +0.144055985
  fixed adaptive route at same y:          -0.223890869
  after 2x2 closure:                       -0.233656621
  random worst over 60 sampled y:          -0.233656621
```

```text
I?ABCc]}?[1]:
  alpha0 hard y gap before adaptive route: -0.022483379
  fixed adaptive route at same y:          -0.140716506
  after 2x2 closure:                       -0.257478345
  random worst over 200 sampled y:         -0.182293549
```

Equality cases stayed fixed:

```text
H?bB@_W[1]:
  alpha0 hard y gap:                       0
  after 2x2 closure:                       0
  random worst over 120 sampled y:         0

J?AEB?oE?W?[1]:
  alpha0 hard y gap:                       0
  after 2x2 closure:                       0
  random worst over 120 sampled y:         0
```

Small-census alpha0-hard-y screen:

```text
N=8:
  checked 85 graphs with bad edges
  positive closed gaps: 0
  worst gap: -1/7

N=9:
  checked 650 graphs with bad edges
  positive closed gaps: 0
  worst gap: 0 at H?bB@_W
```

The hard `alpha0`-maximizing `y` remained the worst sampled `y` after closure in the two main hard tests.

## Caveats

- This is floating structure mining.
- Greedy 2x2 closure is not canonical; different improving-swap orders may end at different local minima.
- A 2x2-closed route need not be a global minimizer of the concave objective.
- The current diagnostics do not prove the all-`y` statement; they only failed to falsify it on the hard directions.
