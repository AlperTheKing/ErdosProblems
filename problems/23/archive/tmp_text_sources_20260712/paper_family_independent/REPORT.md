# Independent referee report: shortest-support Hall family

## Verdict

**VALID.** Reconstructing `G_t` solely from
`SHORTEST_SUPPORT_HALL_COUNTEREXAMPLE_FAMILY.md`, I found no mathematical
counterexample or hidden path/packing collision.  All five theorem claims hold
for every integer `t >= 1`; the Hall deficiency is positive exactly when
`t >= 3`.

The audit did not import or inspect the original family verifier.  The new
checker uses only the Python standard library.

## All-`t` referee proof

Write `G_t^0` for the graph before the `L-R` edges are added.  The displayed
shore assignment bipartitions `G_t^0`.  Moreover

```text
N_{G_t^0}(L_i) = A union {u},
N_{G_t^0}(R_j) = E union {v},
```

and these two sets are disjoint.  Hence adding any edge `L_i R_j` creates no
triangle.  The vertex and edge counts are

```text
|V| = 7t + 3,
|E| = 6t^2 + t^2 + t + 1 + 1 + t = 7t^2 + 2t + 2.
```

For every `(i,j)` in `(Z/tZ)^2`, the seven vertices

```text
L_i, A_j, B_{i+j}, C_i, D_j, E_{i+j}, R_j
```

form a simple 7-cycle.  On the seven edge blocks, its labels are

```text
(i,j), (j,i+j), (i+j,i), (i,j),
(j,i+j), (i+j,j), (i,j).
```

The repeated written pairs occur in different edge blocks.  Within each fixed
block, the corresponding map from `(i,j)` is bijective; the inverse uses only
subtraction modulo `t`.  This works for composite `t` as well as prime `t`.
Thus the `t^2` cycles are pairwise edge-disjoint and, in fact, partition all
`7t^2` chain and `L-R` edges.  The thin-channel edges lie outside the packing.

Every two-coloring has a monochromatic edge on each packed odd cycle, so it has
at least `t^2` monochromatic edges.  The stated coloring has exactly the `t^2`
edges in `L x R` monochromatic, proving `bip(G_t)=t^2`.

If equality holds, every packed cycle contains exactly one monochromatic edge
and every edge outside the packing crosses.  In particular every thin-channel
edge crosses.  The edges `L_i-u`, `u-w`, `w-v`, and `v-R_j` force all vertices
of `L union R` (and `w`) onto one shore and `u,v` onto the other.  Consequently
all `t^2` edges in `L x R` are already monochromatic.  They exhaust the budget,
so every other edge crosses; the complete chain blocks then force all seven
class colors.  This proves uniqueness up to global complementation.  Its blue
graph is connected, so it is also the unique connected maximum cut and hence
Gamma-minimal.

In that cut,

```text
N_B(L_i) = A union {u},
N_B(R_j) = E union {v}.
```

There is no common neighbor, hence no blue path of length two.  A possible
length-four path has the form `L_i-x-z-y-R_j`, where
`x in A union {u}` and `y in E union {v}`.  The four cases give

```text
N_B(A) intersect N_B(E) = empty,
N_B(A) intersect N_B(v) = empty,
N_B(u) intersect N_B(E) = empty,
N_B(u) intersect N_B(v) = {w}.
```

Therefore the only shortest blue path is

```text
L_i-u-w-v-R_j.
```

Its graph-theoretic length is four.  The union of these supports over all
`(i,j)` consists of the `t` edges `L-u`, the two edges `u-w,w-v`, and the `t`
edges `v-R`, hence has size `2t+2`.  Thus the all-bad-edge Hall set has defect

```text
t^2 - 2t - 2,
```

which is positive for every integer `t >= 3` and grows without bound.

## Independent computation

Command:

```powershell
python -B tmp/paper_family_independent/verify_family.py `
  --structural-max-t 8 `
  --json tmp/paper_family_independent/result.json
```

The checker performs the following independent tests.

- `t=1`: all `1,024` labeled cuts; minimum `1`, exactly two complementary minimizers.
- `t=2`: all `131,072` labeled cuts; minimum `4`, exactly two complementary minimizers.
- `t=3`: all `131,072` count-vector orbits under `S_t^7`, representing all `2^24` labeled cuts; minimum `9`, two complementary orbit representatives and two labeled minimizers.
- `t=4`: all `625,000` count-vector orbits under `S_t^7`, representing all `2^31` labeled cuts; minimum `16`, two complementary orbit representatives and two labeled minimizers.
- `1 <= t <= 8`: zero triangles, exact edge formula, every packed edge used once, all thin edges unused by the packing, blue distance four with exactly one shortest path per bad edge, and support size `2t+2`.

The count-vector orbit calculation is exhaustive because the cut objective on
each complete bipartite block depends only on the two class counts:

```text
k_X k_Y + (t-k_X)(t-k_Y).
```

The binomial multiplicities of all representatives sum to `2^(7t+3)`.

## Editorial notes

1. In the surrounding project convention, `ell(g)` may count the closing bad
   edge as well.  Here the blue geodesic has four edges and five vertices, so
   the associated closed odd-cycle length is `5`.  State this explicitly.
2. The source Markdown contains damaged TeX tokens such as `tge`, `Lcup R`,
   `L\times R`, and `E_rm short`.  These are typographical, not mathematical,
   errors, but must be repaired before submission.

## Artifact hashes

```text
verify_family.py  8D4D37D1F690AAD5F879288F28C8945C7CF3184F01185B1B9BAD7B1528170EAD
result.json       EE9FAED269C2A1A7E419264536BB0A0F9878AB1616D6D95FFC77F54159E7EE6D
```
