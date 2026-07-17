# Erdős Problem 128 — Order-selection audit

## Verdict

There is no proved strict advantage of `n=20` over every other order `n<=20`.
It remains a valid bounded one-shot order, but it must not be described as the
provably best small order.  The exact elementary criteria below rank different
orders differently, and there is no deletion or extension lemma transporting
candidate existence between them.

No graph search or special-family enumeration was used in this audit.

## General exact bounds

Put

\[
s=\lfloor n/2\rfloor,\qquad
t=\left\lfloor\frac{n^2}{50}\right\rfloor+1.
\]

Thus a finite counterexample at order `n` would be triangle-free and every
`s`-vertex set would span at least `t` edges.

### Deleted-vertex averaging lemma

For every vertex `v`, the graph `G-v` still has at least `t` edges in each of
its `s`-sets.  Double-counting pairs consisting of an edge of `G-v` and an
`s`-set containing that edge gives

\[
(e-d(v)){n-3\choose s-2}\ge t{n-1\choose s}.
\]

Consequently, with

\[
q=\left\lceil\frac{t(n-1)(n-2)}{s(s-1)}\right\rceil,
\]

we have `e-d(v)>=q` for every `v`.  Summing over all vertices yields

\[
(n-2)e=\sum_v(e-d(v))\ge nq,
\qquad
e\ge\left\lceil\frac{nq}{n-2}\right\rceil.
\]

### Independent-core lemma

Assume `2t>s-1`.  If an independent set `A` had size `s-1`, then every
vertex outside `A` would have at least `t` neighbours in `A`, because
`A` together with that vertex is an `s`-set.  Two adjacent outside vertices
have disjoint neighbourhoods in `A` in a triangle-free graph, contradicting
`2t>s-1`.  Hence the complement of `A` is also independent and contains an
independent `s`-set, again a contradiction.  Therefore

\[
\alpha(G)\le s-2.
\]

Every neighbourhood in a triangle-free graph is independent, so

\[
\Delta(G)\le s-2,
\qquad
e\le\left\lfloor\frac{n(s-2)}2\right\rfloor.
\]

Together with the exact values `R(3,3)=6` and `R(3,4)=9`, these elementary
conditions exclude every order through `n=11`.

## Surviving orders through 20

| `n` | `s` | `t` | number of `s`-sets | `q` | necessary edge interval | `alpha, Delta` |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 6 | 3 | 924 | 11 | `14 <= e <= 24` | `<= 4` |
| 13 | 6 | 4 | 1,716 | 18 | `22 <= e <= 26` | `<= 4` |
| 14 | 7 | 4 | 3,432 | 15 | `18 <= e <= 35` | `<= 5` |
| 15 | 7 | 5 | 6,435 | 22 | `26 <= e <= 37` | `<= 5` |
| 16 | 8 | 6 | 12,870 | 23 | `27 <= e <= 48` | `<= 6` |
| 17 | 8 | 6 | 24,310 | 26 | `30 <= e <= 51` | `<= 6` |
| 18 | 9 | 7 | 48,620 | 27 | `31 <= e <= 63` | `<= 7` |
| 19 | 9 | 8 | 92,378 | 34 | `38 <= e <= 66` | `<= 7` |
| 20 | 10 | 9 | 184,756 | 35 | `39 <= e <= 80` | `<= 8` |

The `n=20` lower bound `e>=39` here explains why plain all-set averaging,
which only gives `e>=38`, is not sharp enough.

## Why the criteria do not select one best order

- `n=20` has the loosest relative independent-set bound in the table:
  `8/20=2/5`.
- It also has the largest direct encoding: 184,756 half-set constraints.
- At `n=14`, the required local density is `4/21<1/5`, and the necessary
  global edge density is `18/91<39/190`.
- At `n=18`, the corresponding inequalities are `7/36<1/5` and
  `31/153<39/190`.
- No proved cross-order transformation shows that satisfying the constraints
  at one surviving order is easier or implies satisfaction at another.

Accordingly, the accurate selection statement is:

> `n=20` was chosen as one exact, bounded experimental order.

It was not proved to be the optimal order among `n<=20`.  This correction does
not authorise an order cascade; the precommitted one-shot exit remains in force.
