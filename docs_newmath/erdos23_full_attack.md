# Erdos problem #23 full attack notes

Date: 2026-06-10

Status: ACTIVE. Starting from the finite new result `a(25)=25`, test whether
the two-deletion plus BCL plus extremal-core method can scale to the full
conjecture `a(5m) <= m^2`.

## Known finite result

We proved `a(25)=25` as follows. If a 25-vertex triangle-free graph `G` had
`beta(G) >= 26`, then the high-density case of Balogh-Clemen-Lidicky gives
`e(G) <= 95`. Deleting two successive vertices of degree at most 7 gives a
23-vertex induced triangle-free graph `F` with `beta(F) >= 20`. McKay's full
`minbip23_20x.g6` catalogue has six extremals, all with at least 100 edges,
contradicting `e(F) <= 95`.

## First generalization algebra

Let `n = 5m`. A counterexample has `beta(G) >= m^2 + 1`.

The BCL high-density theorem excludes high-density counterexamples. Using the
published threshold `0.3197 * binom(n,2)`, a remaining counterexample has

`e(G) <= ceil(0.3197 * binom(5m,2)) - 1`.

If we repeatedly delete a minimum-degree vertex, then after two deletions the
worst-case degree losses allowed by this edge cap are:

```text
m  ecap  d1,d2  loss floor(d1/2)+floor(d2/2)  beta_after_2  C5_lower(5m-2)
5   95    7,7   6                                  20          20
6   139   9,8   8                                  29          30
7   190   10,10 10                                 40          42
8   249   12,12 12                                 53          56
9   316   14,13 13                                 69          72
10  391   15,15 14                                 87          90
```

So the `m=5` proof hits the `5m-2` balanced `C5` blow-up lower bound exactly.
For `m >= 6`, the same two-deletion argument falls below that lower bound.
This strongly suggests that the finite proof is not a direct induction by
itself.

## Sufficient theorem shape

The route could still scale if one proves a stability/dense-core theorem:

> If `F` is triangle-free on `5m-2` vertices and `beta(F)` is at least the
> threshold obtained from a `5m` counterexample after two low-degree deletions,
> then `e(F)` is larger than the BCL edge cap for the original `5m` graph,
> or `F` contains a dense blow-up-of-`C5` core forcing the same contradiction.

For `m=5`, McKay's complete `n=23` catalogue supplies exactly this theorem:
`beta(F) >= 20` forces `e(F) >= 100 > 95`.

For all `m`, this would be a serious near-extremal stability theorem for
triangle-free graphs with large bipartization number. It is not currently
known from the basic AES deletion lemma alone.

## Current consults

- GPT-5.5 Pro consult sent in the existing #23 chat asking whether the finite
  proof scales, and what exact stability/finite certificate target is strongest.
- Two agents spawned:
  - Prover/stability: derive sufficient lemmas and known/failing implications.
  - Verifier/inequality: audit deletion inequalities and identify where `m=5`
    stops working.

## Agent verdicts

Both agents agree:

- The `m=5` proof is valid but relies on a special integer/certificate match:
  after two deletions it lands exactly on `a(23)=20`, and McKay's complete
  23-vertex extremal catalogue supplies `e >= 100`.
- The same two-deletion argument already misses for `m=6`: it gives only
  `beta >= 29` on 28 vertices, while the balanced `C5` lower bound there is 30.
- No proof using only the BCL high-density edge cap and greedy deletion can work
  for all `m`; the beta loss per deletion is asymptotically about `0.79925m`,
  while the balanced `C5` target drops only about `0.4m` per deletion on average.

The full problem would require a genuinely new edge-sensitive stability theorem,
for example an upper envelope

`beta(H) <= Phi(n,e)`

strong enough to rule out medium-density graphs at the deletion thresholds, or a
theorem saying near-extremal triangle-free graphs must contain a dense `C5`
blow-up core.

## Best next finite target: a(30)=36

For `m=6`, a 30-vertex counterexample would have `beta >= 37`. BCL high-density
gives

`e(G) <= ceil(0.3197 * binom(30,2)) - 1 = 139`.

Delete one vertex of degree at most `floor(2*139/30)=9`. The deletion inequality
leaves a 29-vertex induced triangle-free graph `F` with

`beta(F) >= 37 - floor(9/2) = 33`

and

`e(F) <= 139`.

Thus `a(30)=36` follows from the finite certificate:

> No triangle-free graph on 29 vertices has `beta >= 33` and `e <= 139`.

This is the cleanest next computational/stability test of whether the finite
method has legs.

Note: an earlier scratch note used `e <= 130`; that bound only follows in the
subcase where the deleted vertex has degree 9. It is not sufficient for the
full one-deletion proof.
