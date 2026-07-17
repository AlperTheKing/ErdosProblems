# Erdős Problem 128 — adversarial direct-route attack

Date: 2026-07-13.

## Verdict

A new exact reduction is proved:

> **Low-edge exclusion lemma.** Let `G` be any simple graph on 20 vertices
> such that every 10-vertex induced subgraph has at least 9 edges. Then
> `e(G) >= 43`.

Triangle-freeness is not needed for this lemma. Applied to the direct
`n = 20` certificate route, Razborov's Corollary 3.7 then gives the rigorously
smaller residual profile

```text
43 <= e(G) <= 70,    alpha(G) <= 7,    5 <= Delta(G) <= 7.
```

This is a necessary reduction, not a counterexample and not a solution of
Problem 128.

## Direct bridge

The registered terminal object is a triangle-free graph on 20 vertices whose
every 10-set spans at least 9 edges. The lemma applies literally to that
object, so it deletes the complete edge layers `e = 39,40,41,42` from the
finite certificate problem. It neither changes graph order nor introduces an
asymptotic surrogate or an auxiliary graph family.

## 1. Preliminary deletion bound

Write `e=e(G)` and `d(v)` for the degree of `v`. Fix `v` and sum the induced
edge counts over the 10-subsets of `V(G)\{v}`. Every edge not incident with
`v` occurs in exactly `C(17,8)` such sets. Hence

```text
(e-d(v)) C(17,8) >= 9 C(19,10).
```

Since

```text
9 C(19,10) / C(17,8) = 171/5,
```

integrality gives

```text
e-d(v) >= 35                                           (1)
```

for every `v`. Summing (1) over all 20 vertices gives

```text
18e = sum_v (e-d(v)) >= 700,
```

so `e>=39`. Moreover, if `e` is fixed, (1) gives

```text
Delta(G) <= e-35.                                      (2)
```

Only the lower bound `e>=39` is needed below; (2) is an independent check on
the low layers.

## 2. Complementary-half averaging

Choose a 10-set `A` uniformly and put `B=V(G)\A`. A fixed edge lies inside
`A` with probability

```text
C(18,8)/C(20,10) = 9/38.
```

Therefore

```text
E[e(A)+e(B)] = 9e/19.                                 (3)
```

For `e=39,40,41,42`, the floors of (3) are respectively

```text
18, 18, 19, 19.
```

Every half has at least 9 edges, so some complementary pair has one of the
following internal-edge pairs:

```text
e=39,40:       (e(A),e(B)) = (9,9);
e=41,42:       (e(A),e(B)) = (9,9) or (9,10), up to order.    (4)
```

It remains to exclude exactly the six cases in (4).

## 3. The exact swap inequality

For `x in A`, `y in B`, use the notation

```text
a_x = d_A(x),        b_y = d_B(y),
r_x = d_B(x),        r_y = d_A(y),
epsilon_xy = 1 if xy is an edge, and 0 otherwise.
```

Replacing `x` by `y` in `A` and using the 9-edge lower bound gives

```text
r_y-epsilon_xy >= a_x-(e(A)-9).                       (5)
```

The symmetric inequality obtained from `B-y+x` is

```text
r_x-epsilon_xy >= b_y-(e(B)-9).                       (6)
```

These inequalities hold for every ordered pair `(x,y)`.

### The degree-2 core of a 9-edge half

Suppose `e(A)=9` and the cross-edge count is `c<30`. If some `a_x>=3`,
then (5) forces `r_y>=3` for all ten `y in B`, whence `c>=30`, a
contradiction. Thus `Delta(G[A])<=2`.

The degree sum in `G[A]` is 18. Relative to ten vertices of degree 2, its
total degree deficit is only 2. Consequently

```text
A_2 = {x in A : a_x=2} has size at least 8.            (7)
```

For `x in A_2`, (5) implies `r_y>=2` for every `y in B`; if `xy` is an
edge, it implies `r_y>=3`. Put

```text
q_y=r_y-2 >= 0,        Q=sum_y q_y=c-20.               (8)
```

Thus every cross neighbour of `A_2` lies at a vertex with `q_y>=1`.

## 4. Excluding `(9,9)`

Now both halves have degree-2 cores `A_2,B_2`, each of size at least 8.
Let `Q_A2` and `Q_B2` be the sums of the excesses `q=r-2` over these cores,
and let `E_22` count cross edges between the two cores.

At most two vertices of `B` lie outside `B_2`. Comparing all incidences from
`A_2` with the capacity of those exceptional vertices gives

```text
E_22 >= 12-Q+Q_A2+Q_B2.                               (9)
```

For completeness: the left core sends at least `16+Q_A2` incidences; the
non-core vertices of `B` receive at most `4+(Q-Q_B2)` incidences.

Every endpoint in `B_2` of an `A_2`--`B_2` edge has positive integral
excess. If the total excess on such endpoints is at most `Q_B2`, their number
is at most `Q_B2`, and their total cross degree is at most `3Q_B2`. Hence

```text
E_22 <= 3Q_B2,
E_22 <= 3Q_A2.                                        (10)
```

Combining (9) with the two inequalities (10) yields

```text
24-2Q <= Q_A2+Q_B2 <= 2Q,
```

so necessarily `Q>=6`, equivalently `c>=26`. But the `(9,9)` cases in
(4) have

```text
c=e-18 in {21,22,23,24}.
```

All four are impossible.

## 5. Excluding `(9,10)`

Let `e(A)=9`, `e(B)=10`. The core `A_2` again has at least eight vertices.
By (8), all its cross edges land at vertices of positive excess. Vertices
with positive integral excess have total receiving capacity at most `3Q`.

It remains to lower-bound the number of incidences sent by `A_2`. Since
`G[B]` has degree sum 20, some `y in B` has `b_y>=2`. Equation (6) gives
`r_x>=1` for every `x in A_2`.

- If some `b_y>=3`, (6) immediately gives `r_x>=2` for every `x in A_2`.
- Otherwise every `b_y<=2`, and degree sum 20 forces every `b_y=2`.
  Each `x in A_2` has a cross neighbour `y`; applying (6) to that edge gives
  `r_x-1>=1`, hence again `r_x>=2`.

Thus `A_2` sends at least 16 cross incidences, while all eligible receivers
have capacity at most `3Q`. In the two cases from (4),

```text
e=41: c=22, Q=2, 3Q=6<16;
e=42: c=23, Q=3, 3Q=9<16.
```

Both cases are impossible. Together with Sections 1--4, this proves
`e(G)>=43`.

## 6. Primary-source consequence

Razborov, *More about sparse halves in triangle-free graphs*,
arXiv:2104.09406v2, defines `beta(G)` as the minimum half-edge count divided
by `n^2`. Corollary 3.7 states that the half-graph conjecture holds for every
triangle-free graph with normalized independence number at least `2/5`:

<https://arxiv.org/pdf/2104.09406#page=7>

For the present certificate, `beta(G)>=9/400>1/50`. Therefore the corollary
forces `alpha(G)<8`, hence

```text
alpha(G)<=7.
```

Every neighbourhood in a triangle-free graph is independent, so
`Delta(G)<=7`, and the handshake lemma gives `e(G)<=70`. Conversely,
`e(G)>=43` forces `Delta(G)>=5`. This proves the residual profile stated in
the verdict. It also tightens the `e<=79` line in the previous audit: once
`alpha<=7` is invoked, the correct immediate edge upper bound is 70.

## 7. Independent exact arithmetic audit

`verify/adversarial_route_arithmetic.py` checks the binomial ratio, generates
all six cases forced by (3)--(4), and checks the two capacity contradictions
using exact rational/integer arithmetic.

Command:

```powershell
python -B problems/128/verify/adversarial_route_arithmetic.py
```

Output ends with:

```text
PASS: every 39 <= e <= 42 case forced by exact averaging is killed
```

Script SHA-256:

```text
B859F03317C79DE5D45C664753A6739D8A0E657ACB0216DA10D90E68EE9ABBA2
```

The script is an arithmetic cross-check, not a graph solver and not a
substitute for the proof above.

## Exit statement

The load-bearing reduction is complete. It supplies no witness and no global
nonexistence theorem. It does not authorize another graph order, encoding,
special-family cascade, or asymptotic reformulation. Any continuation of the
`n=20` direct route must work inside the exact residual domain
`43<=e<=70`, `alpha<=7`, `5<=Delta<=7` and must still terminate in either an
explicit verifier-passing graph or a proof excluding all such graphs.
