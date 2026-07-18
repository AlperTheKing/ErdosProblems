# Structure theorem for connected triangle-free induced-`P5`-free graphs

Throughout, graphs are finite and simple.  Write `P5` for the path on five
vertices, and take all subscripts on vertices of a `C5` modulo five.

## Theorem (`L314-Structure`)

Let `G` be a connected triangle-free graph with no induced subgraph
isomorphic to `P5`.  Exactly one of the following holds.

1. `G` is bipartite and has a bipartition `X ⊎ Y` such that the open
   neighborhoods of vertices in `X` are linearly ordered by inclusion, and
   the same is true of the open neighborhoods of vertices in `Y`.
2. There are five nonempty independent sets `A_0,...,A_4` partitioning
   `V(G)` such that, for distinct vertices `u in A_i` and `v in A_j`,
   `uv` is an edge if and only if `j=i-1` or `j=i+1` modulo five.

Thus the first alternative is precisely a connected chain graph, and the
second is precisely a blow-up of `C5` in which every consecutive pair of
bags is complete.

## A connected bipartite graph containing an induced `2K2` contains an
## induced `P5`

We first record the only auxiliary fact needed for the bipartite case.
Suppose a connected bipartite graph `H` has four vertices inducing two
disjoint edges.  Denote those edges by `a_0 a_1` and `b_0 b_1`, and put

```
A = {a_0,a_1},    B = {b_0,b_1}.
```

There is no edge from `A` to `B`.  Choose a shortest path

```
p_0 p_1 ... p_d
```

with `p_0 in A` and `p_d in B`.  Then `d >= 2`.  By minimality, no internal
vertex of the path belongs to `A` or `B`.  Let `q_0` be the other endpoint
of the edge induced by `A`, and let `q_d` be the other endpoint of the edge
induced by `B`.  Consider

```
q_0, p_0, p_1, ..., p_d, q_d.                 (1)
```

This is an induced path.  Indeed, the subpath from `p_0` to `p_d` is induced,
since a chord would shorten it.  A possible edge `q_0 p_1` is excluded by
bipartiteness: `q_0` and `p_1` are both neighbors of `p_0` and hence lie in
the same bipartition class.  An edge `q_0 p_i` with `i >= 2` would make

```
q_0, p_i, p_{i+1}, ..., p_d
```

a shorter path from `A` to `B`.  The symmetric argument excludes every
non-path edge from `q_d` to the `p_i`; at `p_{d-1}` bipartiteness applies,
and for `i <= d-2` minimality applies.  Finally `q_0 q_d` is absent because
there is no edge between `A` and `B`.  This proves the claim about (1).

Path (1) has `d+3 >= 5` vertices.  Five consecutive vertices of an induced
path again induce a path, so `H` contains an induced `P5`.

## The bipartite case

Suppose `G` is bipartite, with bipartition `X ⊎ Y`.  If two vertices
`x,x' in X` had incomparable neighborhoods, there would be vertices

```
y  in N(x)  \ N(x'),
y' in N(x') \ N(x).
```

The four vertices `x,y,x',y'` would induce exactly the two edges `xy` and
`x'y'`: the two other possible cross-edges are absent by the choices of `y`
and `y'`, and edges within a bipartition class do not exist.  They would
therefore induce a `2K2`.  The auxiliary fact, together with connectedness,
would give an induced `P5`, contrary to the hypothesis.  Hence the
neighborhoods of the vertices in `X` are linearly ordered by inclusion.
Interchanging `X` and `Y` proves the same statement on `Y`.  This is the
first alternative.

## The nonbipartite case: obtaining an induced `C5`

Now suppose `G` is not bipartite.  Choose a shortest odd cycle `C`.  It is
induced: a chord would split it into two shorter cycles, exactly one of which
is odd.  Since `G` is triangle-free, the length of `C` is at least five.  If
its length were at least seven, five consecutive vertices on this chordless
cycle would induce a `P5`.  Consequently `C` has length exactly five.  Label
it in cyclic order as

```
C = c_0 c_1 c_2 c_3 c_4 c_0.
```

## Every vertex lies on `C` or has a two-vertex `C`-neighborhood

For a vertex `v` outside `C` that has a neighbor on `C`, no two of its
neighbors on `C` are consecutive, since they and `v` would form a triangle.
An independent set in `C5` has at most two vertices, so
`1 <= |N(v) intersect V(C)| <= 2`.

The lower value cannot occur.  If `v` had the unique neighbor `c_i` on `C`,
then

```
v, c_i, c_{i+1}, c_{i+2}, c_{i+3}
```

would induce a `P5`: `v` has no other neighbor among the displayed cycle
vertices, and four consecutive vertices of an induced `C5` induce a `P4`.
Thus `v` has exactly two neighbors on `C`.  They are nonconsecutive and
hence, for a unique index `i`, they are

```
N(v) intersect V(C) = {c_{i-1},c_{i+1}}.      (2)
```

There is also no vertex at distance at least two from `C`.  Otherwise a
shortest path to `C` contains adjacent vertices `u,v` with `u` at distance
two and `v` at distance one from `C`.  By (2), for some `i` the two
`C`-neighbors of `v` are `c_{i-1}` and `c_{i+1}`.  Then

```
u, v, c_{i-1}, c_{i-2}, c_{i-3}              (3)
```

induces a `P5`.  To check every possible chord: `u` has no neighbor on `C`;
`v` has no `C`-neighbors other than `c_{i-1}` and `c_{i+1}`, and neither
`c_{i-2}` nor `c_{i-3}` is `c_{i+1}` modulo five; and the three displayed
cycle vertices are consecutive in reverse cyclic order and have no chord.
This contradicts the hypothesis.  Connectedness now implies that every
vertex belongs to `C` or is adjacent to `C`.

## The five bags and all adjacency cases

For every `i` define

```
A_i = {v in V(G) : N(v) intersect V(C) = {c_{i-1},c_{i+1}}}.
```

Each `c_i` belongs to `A_i`.  The preceding section shows that every vertex
belongs to one of these sets, and the five displayed pairs of cycle vertices
are distinct, so the sets form a partition of `V(G)` into five nonempty
bags.

We now determine all edges between and within the bags.

* **One bag.**  If two vertices of `A_i` were adjacent, then together with
  their common neighbor `c_{i-1}` they would form a triangle.  Hence every
  `A_i` is independent.

* **Nonconsecutive bags.**  Apart from equality, two nonconsecutive indices
  have difference two modulo five.  Vertices in `A_i` and `A_{i+2}` share
  the cycle neighbor `c_{i+1}`; vertices in `A_i` and `A_{i-2}` share
  `c_{i-1}`.  An edge between either pair would complete a triangle with
  that common neighbor.  Thus no edge joins nonconsecutive bags.

* **Consecutive bags.**  Let `u in A_i` and `v in A_{i+1}`.  Suppose, for a
  contradiction, that `uv` is not an edge.  Since
  `c_{i-3}=c_{i+2}` modulo five, the sequence

  ```
  u, c_{i-1}, c_{i-2}, c_{i-3}, v             (4)
  ```

  is a path: `u` is adjacent to `c_{i-1}`, the three cycle vertices are
  consecutive, and `v`, whose cycle-neighborhood is
  `{c_i,c_{i+2}}`, is adjacent to `c_{i-3}=c_{i+2}`.

  Sequence (4) is induced.  Among its three cycle vertices there are only
  the two displayed cycle edges.  Of those vertices, `u` is adjacent only
  to `c_{i-1}`, because its cycle-neighborhood is
  `{c_{i-1},c_{i+1}}`; and `v` is adjacent only to `c_{i-3}`, because its
  cycle-neighborhood is `{c_i,c_{i+2}}`.  The remaining possible chord is
  `uv`, which was assumed absent.  Thus (4) is an induced `P5`, a
  contradiction.  Every vertex of `A_i` is therefore adjacent to every
  vertex of `A_{i+1}`.  Shifting the index covers all five consecutive
  pairs.

It follows that two vertices in different bags are adjacent exactly when
their bag indices are consecutive modulo five.  This proves the second
alternative, including completeness rather than merely the existence of a
homomorphism to `C5`.

## Exhaustiveness and exclusivity

Every graph is either bipartite or nonbipartite, so the two arguments are
exhaustive.  They are mutually exclusive as well: selecting one vertex from
each of the five nonempty bags in the second alternative produces a `C5`,
so such a graph is not bipartite.  Therefore exactly one alternative holds.

