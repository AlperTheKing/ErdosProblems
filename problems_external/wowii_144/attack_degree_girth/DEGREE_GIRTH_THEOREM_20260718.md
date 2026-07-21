# A sharp degree--girth induced-tree bound for 2-connected graphs

## Result

Let `G` be a finite simple 2-connected graph which is not a cycle.  If its
girth is `g>=5` and its maximum degree is `Delta`, then

```text
tree(G) >= Delta + g - 2.
```

The bound is sharp: graph6 `FCR`o` is the theta graph with path lengths
`2,3,3`; it has `g=5`, `Delta=3`, and maximum induced-tree order `6`.

Consequently W144 holds for this graph class whenever
`eta(G)<=Delta(G)-1`, because

```text
g - 1 + eta <= g - 2 + Delta <= tree(G).
```

## Proof

Choose a vertex `v` of degree `Delta`.  Since `g>=5`, its neighbours are
independent, so `N[v]` induces a star.  Among all vertex sets containing
`N[v]` and inducing a tree, choose one of maximum order; call it `S` and
write `T=G[S]`.

The graph is 2-connected and is not a cycle, so `Delta>=3`.  Also `S` is a
proper subset of `V(G)`: otherwise `G=T` would be a tree.  Every vertex
`z` outside `S` which has a neighbour in `S` has at least two neighbours in
`S`.  Indeed, if it had exactly one, adjoining `z` would produce a larger
induced tree still containing `N[v]`.

Fix such a `z` and two distinct neighbours `a,b` of `z` in `S`.  Let `Q` be
the unique `a`--`b` path in `T`.  The path together with `za` and `zb` is a
cycle, hence

```text
|E(Q)| >= g-2.                                      (1)
```

Moreover

```text
|V(Q) intersect N[v]| <= 3.                         (2)
```

For completeness, if `v` is not on `Q`, then `Q` contains at most one
neighbour of `v`: two such neighbours would also be joined in `T` by their
two-edge path through `v`, contradicting uniqueness of tree paths.  If `v`
is on `Q`, every neighbour of `v` on `Q` must be immediately before or after
`v`, so there are at most two of them.  This proves (2).

Equations (1)--(2) and inclusion--exclusion give

```text
|S| >= |V(Q) union N[v]|
     >= (g-1) + (Delta+1) - 3
      = Delta+g-3.                                  (3)
```

Suppose for a contradiction that the claimed bound fails.  Then every
induced tree, and in particular `T`, has order at most `Delta+g-3`; hence
equality holds throughout (3).  The same argument applies to every outside
vertex meeting `S` and every pair of its neighbours in `S`.  We may therefore
record the following equality consequences:

```text
|S|=Delta+g-3;
S=V(Q) union N[v];
|E(Q)|=g-2;
|V(Q) intersect N[v]|=3.                            (4)
```

The last equality says that `v` is an internal vertex of `Q` and that the
two path-neighbours of `v` are precisely the other two vertices of
`Q intersect N[v]`.  Since `Delta>=3`, choose a neighbour `y` of `v` outside
`Q`.  By (4), `y` is a leaf of `T`.  A 2-connected graph has minimum degree
at least two, so `y` has a neighbour `w` outside `S`.  Maximality gives a
second neighbour `q` of `w` in `S`.

Apply (4) to the pair `y,q`.  Their distance in `T` is `g-2`.  If the two
distances in `Q` from `v` to its endpoints are `p` and `g-2-p`, then both
are positive, whereas the greatest distance from `y` to a vertex of `T` is

```text
1 + max(p,g-2-p).
```

For this to be `g-2`, one of `p,g-2-p` must be `1` and the other `g-3`.
Thus `T` has the following forced form: one path of length `g-3` from `v` to
a vertex `c`, together with `Delta-1` short leaves adjacent to `v`.  In this
tree, `c` is the unique vertex at distance `g-2` from any short leaf.

It follows more generally that for every short leaf `r` and every outside
neighbour `w_r` of `r`,

```text
N_G(w_r) intersect S = {r,c}.                       (5)
```

Indeed maximality supplies at least two neighbours in `S`, while (4) makes
every pair of them have tree-distance `g-2`; the forced broom has only the
pair displayed in (5).

There are at least two distinct short leaves, say `r` and `s`.  Choose
outside neighbours `w_r,w_s`.  They are distinct, since a common vertex
would have the two tree-neighbours `r,s` at distance `2<g-2`, contrary to
(4).  Now replace `c` by `w_r`:

```text
S' = (S - {c}) union {w_r}.
```

By (5), `G[S']` is obtained by deleting the leaf `c` from `T` and adjoining
`w_r` as a leaf at `r`.  It is therefore an induced tree of the same order
which still contains `N[v]`.

In the new tree, `w_s` has the sole old neighbour `s`; its other neighbour
`c` from (5) was deleted.  If `w_s w_r` is not an edge, adjoining `w_s` to
`S'` makes a larger induced tree containing `N[v]`, contradicting the choice
of `S`.  If `w_s w_r` is an edge, then `c,w_r,w_s` form a triangle by (5),
contradicting `g>=5`.  Both alternatives are impossible, and the theorem
follows.

## Exact falsifier-first audit

`audit_degree_girth_bound.py` independently generated every connected
triangle-free graph with nauty `geng -ctfq` through order 13, retained the
2-connected multicyclic graphs of girth at least five, and computed the exact
maximum induced-tree order by exhaustive vertex-subset search.  There were
5,644 retained graphs.  The stronger universal candidate
`tree>=Delta+g-1` fails first at `FCR`o`; the proved bound had minimum slack
zero and no failure.

On the separate exact residual

```text
eta=Delta and diameter-floor(g/2)<eta,
```

`audit_conditional_strong_bound.py` found 104 graphs through order 13, no
failure of `tree>=Delta+g-1`, and minimum slack one.  This conditional
strengthening is computational evidence only; it is not used in the theorem
above.
