# A proof of Graffiti.pc / WOWII Conjecture 141

Status: candidate proof, independently refereed on 2026-07-18.

## Theorem

Let `G` be a finite nontrivial connected simple graph.  Write `g(G)` for its
girth, with `g(G)=0` when `G` is acyclic; write `t(G)` for the maximum order of
an induced tree; and put

```text
L(G) = max { alpha(G[N(v)]) : v in V(G) }.
```

Then

```text
t(G) >= floor(g(G)/2) - 1 + L(G).
```

## Proof

Put `L=L(G)`.  Choose a vertex `v` attaining the maximum and an independent
set `I` in `N(v)` with `|I|=L`.

First note that the subgraph induced by `{v} union I` is a star: `v` is
adjacent to every member of `I`, and there are no edges within `I`.  It is
therefore an induced tree on `L+1` vertices.  If `G` is acyclic, the convention
`g=0` makes the desired lower bound `L-1`; if `g=3`, it is `L`.  The star proves
both cases.  A cyclic simple graph has no other girth below four.

Suppose henceforth that `g>=4`, and set

```text
r = floor(g/2) - 1.
```

We use the following standard BFS bound.

### Lemma

For every vertex `v` of a finite connected cyclic graph,

```text
g(G) <= 2 ecc(v) + 1.
```

Indeed, root a breadth-first spanning tree `T` at `v`.  A cycle of `G` has an
edge `ab` outside `T`.  The edge `ab` together with the unique `a`--`b` path
in `T` is a cycle, so

```text
g(G) <= d_T(a,b)+1
     <= d_T(v,a)+d_T(v,b)+1
      = d_G(v,a)+d_G(v,b)+1
     <= 2 ecc(v)+1.
```

This proves the lemma.

The lemma implies `ecc(v)>=floor(g/2)`.  Hence a geodesic from `v` to an
eccentric vertex has a prefix

```text
P = (x_0=v, x_1, ..., x_r)
```

of length `r`.  Let `S=I union V(P)`.  We show that `G[S]` is a tree.

A geodesic is induced: a chord `x_a x_b` with `b>=a+2` would replace the
subpath from `x_a` to `x_b` by one edge and give a `v`--`x_b` path shorter
than `b`.  Also

```text
I intersect V(P) is contained in {x_1},
```

because every member of `I` is adjacent to `v`, while `d(v,x_j)=j`.

It remains to rule out unintended edges between `I` and the path.  If
`i=x_1` belongs to `I`, all its edges to path vertices are already governed by
the fact that `P` is induced.  Now let `i` be in `I`, with `i!=x_1`, and
suppose that `i x_j` is an edge for some `j>=1`.  Since `i` is not a path
vertex,

```text
v, i, x_j, x_(j-1), ..., x_1, v
```

is a simple cycle of length `j+2`.  But

```text
j+2 <= r+2 = floor(g/2)+1 < g,
```

contradicting the definition of girth.  Finally, there are no edges within
`I`, by its choice.

Consequently `G[S]` consists exactly of the star centered at `v` and the path
`P`.  They share only `v` when `x_1` is not in `I`, and share the edge
`v x_1` when `x_1` is in `I`.  In either case their union is a tree.  Moreover,

```text
|S| = |I| + |V(P)| - |I intersect V(P)|
    >= L + (r+1) - 1
     = L + r.
```

