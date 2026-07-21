# Exact structural constraints at order 18

Scope: this note concerns a hypothetical oriented graph `D` on 18 vertices
with minimum out-degree 8 that is a counterexample to SSNC.  Every statement
labelled **necessary** is safe to impose on that search.  None of the
constraints, nor an unsuccessful bounded search using them, proves SSNC.

## 1. Degree and missing-edge bookkeeping

Let

- `h` be the number of missing unordered pairs;
- `mu(v)` be the number of missing pairs incident with `v`;
- `d(v)=d+(v)=8+e(v)`, where `e(v)>=0`;
- `Z={v:d(v)=8}` and `z=|Z|`.

There are `binom(18,2)=153` unordered pairs, so

```
sum_v d(v) = 153-h = 144 + sum_v e(v).
```

Consequently the following identities are **necessary**:

```
h + sum_v e(v) = 9,                         (1)
sum_v mu(v) = 2h,                           (2)
d-(v) = 17-d(v)-mu(v) = 9-e(v)-mu(v).       (3)
```

Write

```
b(v) = e(v)+mu(v) = 9-d-(v).
```

Then `0<=b(v)<=9` and

```
sum_v b(v) = 9+h.                           (4)
```

At most `9-h` vertices have positive excess.  Hence

```
z >= 18-(9-h) = 9+h,                        (5)
max_v d(v) <= 8+(9-h) = 17-h.               (6)
```

These are equalities or pigeonhole consequences, not heuristic estimates.

## 2. Accepted special cases force at least four missing pairs

Let `H` be the undirected missing graph of `D`.  Two peer-reviewed special
cases apply directly:

1. SSNC holds when `H` is a matching.
2. SSNC holds when `H` is the union of two stars, including intersecting
   stars.

The second result means that a counterexample must have
`tau(H)>=3`, because every graph whose missing edges have a two-vertex cover
is the union of two stars.  The matching result is a separate exclusion.

If a three-edge graph is not a matching, two of its edges share a vertex
`x`.  The third edge, together with `x`, gives a vertex cover of size at most
two.  Thus every graph with at most three edges is either a matching or has
vertex-cover number at most two.  Therefore a counterexample necessarily has

```
4 <= h <= 9.                                (7)
```

Equivalently, the number of arcs is restricted to

```
144 <= |A(D)| <= 149.                       (8)
```

Additional exact consequences for the missing graph are:

- `H` is not a matching, so some vertex has `mu(v)>=2`;
- `tau(H)>=3`, so no two vertices cover all missing edges;
- `H` contains two disjoint edges (otherwise it is a star or a triangle);
- at least four vertices have positive missing degree.

For a SAT/PB model, `tau(H)>=3` can be imposed without choosing a cover: for
every pair of vertices `x,y`, require at least one missing edge with both
endpoints outside `{x,y}`.

Combining (1), (5), (6), and (7) gives the following exact table.

| `h` | `sum e(v)` | guaranteed `z` | maximum possible `d+(v)` |
|---:|---:|---:|---:|
| 4 | 5 | 13 | 13 |
| 5 | 4 | 14 | 12 |
| 6 | 3 | 15 | 11 |
| 7 | 2 | 16 | 10 |
| 8 | 1 | 17 | 9 |
| 9 | 0 | 18 | 8 |

For `h=8`, the degree sequence is exactly one 9 and seventeen 8s.  For
`h=9`, every out-degree is 8.  In every other row, the positive `e(v)` values
form an integer partition of `9-h`.

## 3. Only degree-8 vertices are load-bearing

For any vertex,

```
N2+(v) subseteq V(D) \ ({v} union N+(v)),
```

so `|N2+(v)|<=17-d(v)`.  If `d(v)>=9`, then

```
|N2+(v)| <= 8 < d(v)
```

automatically.  Thus, under `delta+(D)>=8`, the graph is a counterexample if
and only if every vertex in `Z` fails the second-neighborhood property.

Define the unreachable set

```
U(v) = V(D) \ ({v} union N+(v) union N2+(v)).
```

For `v in Z`, the nine vertices outside `{v} union N+(v)` split into
`N2+(v)` and `U(v)`.  Therefore

```
|N2+(v)| < 8  iff  |U(v)| >= 2.             (9)
```

This is an exact replacement of the counterexample inequality at order 18:
each of at least 13 degree-8 vertices must have two distinct unreachable
witnesses.  No constraint on `N2+` is needed for a vertex of degree at least
9.

## 4. Exact characterization of an unreachable witness

Let `M(w)` be the set of vertices nonadjacent to `w`, and define

```
C(v) = {v} union N+(v),
T(w) = N+(w) union M(w)
     = V(D) \ ({w} union N-(w)).
```

For `v in Z`, `|C(v)|=9`, while

```
|T(w)| = d+(w)+mu(w) = 8+b(w).
```

The following equivalence is **necessary and sufficient**:

```
w in U(v)  iff  C(v) subseteq T(w).         (10)
```

Proof.  If `w in U(v)`, then `v` does not point to `w`, and no
`u in N+(v)` points to `w`.  Since the graph has no digons, each element of
`C(v)` is either an out-neighbor or a nonneighbor of `w`, proving the
inclusion.  Conversely, the inclusion says that neither `v` nor any
out-neighbor of `v` points to `w`; hence `w` is neither a first nor a second
out-neighbor of `v`.

Immediate exact consequences are:

1. Every witness has `b(w)>=1`, equivalently `d-(w)<=8`.  A vertex with
   `(d+(w),mu(w))=(8,0)` cannot witness any degree-8 root.
2. If `b(w)=1` and `w in U(v)`, then both sets in (10) have size 9, so
   `C(v)=T(w)`.
3. If `w->v` is a witness arc and
   `r=|M(w) intersect N+(v)|`, then

   ```
   d+(w) >= 1+d+(v)-r,
   ```

   and therefore `r>=1` when both `v` and `w` have out-degree 8.
4. If `v,w` are nonadjacent and `w in U(v)`, the analogous bound is
   `d+(w)>=d+(v)-r`.

The inclusion (10), rather than a one-way two-step variable, is also a useful
independent certificate for checking a search witness.

## 5. Global witness-count cuts

Let

```
c(w) = |{v in Z : w in U(v)}|,
P = sum_w c(w).
```

Equation (9) gives

```
P >= 2z >= 2(9+h).                          (11)
```

At most `2h` of these ordered witness pairs can use a missing pair between
the root and witness: each missing edge supplies at most its two directions.
Thus at least

```
P-2h >= 18                                 (12)
```

ordered witness pairs must be arcs `w->v`.

There is also a capacity bound for each witness.  The sets `C(v)` for
distinct `v in Z` are distinct: equality for `v!=x` would imply both `v->x`
and `x->v`.  By (10), every root witnessed by `w` supplies a distinct
9-subset of `T(w)`.  Hence

```
c(w) <= binom(8+b(w),9),                    (13)
sum_w binom(8+b(w),9) >= 2z.                (14)
```

In particular, `b=0` has capacity zero and `b=1` has capacity one.  If all
vertices have `b<=2` and `r` vertices have `b=2`, then (4) and (14) give

```
r >= ceil((2z-(9+h))/8) >= ceil((9+h)/8).   (15)
```

Thus, under `b<=2`, at least two vertices have `b=2` for `4<=h<=7`, and at
least three do for `h=8,9`.  Equivalently, every candidate either satisfies
those multiplicities or has a vertex with `b>=3`.

## 6. Audited non-constraints

The following tempting strengthenings are false.  The examples below are
not SSNC counterexamples; they show exactly which conclusions do not follow
from orientation and minimum degree alone.

Let vertices be `Z/18Z`.  Start with the oriented graph `B` having

```
i -> i+s  for s=1,...,8,
```

and leaving the nine antipodal pairs `{i,i+9}` missing.  It is 8-out-regular.
A direct set calculation gives `|N2+(i)|=8` and
`U(i)={i-1 mod 18}`.

- Therefore minimum out-degree 8 alone does not give the two witnesses in
  (9); the global counterexample assumption is essential.
- Orient any `k` antipodal pairs as `i->i+9`, for `i=0,...,k-1`.
  The resulting graph has `h=9-k`, exactly `k` vertices of degree 9, and all
  other vertices of degree 8.  Hence all raw values `0<=h<=9` occur and the
  bookkeeping bounds are sharp before the accepted special-case exclusions.
- In `B`, orient the formerly missing pair `{8,17}` as `17->8`.  Then
  `17 in U(0)`, but `d+(17)=9` and `mu(17)=0`.  An unreachable witness need
  not have degree 8 or be incident with a missing edge, and it need not use a
  missing edge into `N+(0)`.
- For a nonadjacent-witness example, reverse the eight arcs `i->9`,
  `i=1,...,8`, and orient the eight antipodal pairs as `i->i+9` for those
  same `i`.  The only missing pair is `{0,9}`, all vertices except 9 have
  out-degree 8, vertex 9 has out-degree 16, and `U(0)={9}`.  Thus a witness
  need not be an in-neighbor of its root.

These examples were replayed by direct enumeration of first and new second
neighborhoods.  They do not weaken constraints (7)--(15), all of which also
use either accepted SSNC special cases or the global counterexample predicate.

## References used for the missing-graph exclusions

- H. Wang and M. Lu, *Seymour's second neighborhood conjecture for some
  oriented graphs*, Graphs and Combinatorics 42 (2026), Article 19,
  https://doi.org/10.1007/s00373-026-03014-y (matching and one-star cases).
- M. Daamouch, D. Al-Mniny, and S. Ghazal, *About the second neighborhood
  conjecture for tournaments missing two stars or disjoint paths*,
  Contributions to Discrete Mathematics 20 (2025), 363--383,
  https://doi.org/10.55016/ojs/cdm.v20i2.77499 (Theorem 3.2, two stars).
