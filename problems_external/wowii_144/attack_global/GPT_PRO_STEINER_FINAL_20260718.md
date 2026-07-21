# GPT Pro audit of the rooted Steiner-radius route

Date: 2026-07-18.

## Status

The consultation did **not** prove or refute the registered W144-S lemma

```text
srad_(g-1)(G) >= g-2+eta(G).
```

After 87 minutes it explicitly stopped without conclusion.  It did prove the exact
shortest-cycle attachment lemma below and returned an exact obstruction to a stronger
root-free reduction.  Neither item closes W144-S.

## Proven shortest-cycle attachment lemma

Let `Q` be a shortest cycle of a connected graph `G` of girth `g>=5`.  Let
`x` lie outside `Q`, put `h=d_G(x,Q)`, choose nonadjacent `a,b` on `Q`, and set

```text
A=V(Q)-{a,b},   S=A union {x}.
```

Then `|S|=g-1` and the Steiner distance of `S` satisfies

```text
d_G(S) >= g-2+h.
```

### Proof

Choose a connected induced subgraph `H` of minimum order containing `S`.  If `H`
contains a cycle `R`, minimality assigns to every vertex of `R` a distinct terminal:
either the vertex itself is in `S`, or a component attached to `R` only there contains
a terminal.  Hence `|R|<=|S|=g-1`, contradicting girth `g`.  Thus `H` is a tree.

Write `q=|V(H)-S|`.  Then `d_G(S)=|V(H)|-1=g-2+q`.  The path in `H` from `x` to its
first vertex of `Q` contains at least `h-1` nonterminals, so `q>=h-1`.  If equality
held, these would be all Steiner vertices.  Since `Q-{a,b}` has two nonempty path
components, the penultimate vertex on that path would have to attach to both components
of `Q-{a,b}`.  Its two cycle neighbours together with the shorter cycle arc would form
a cycle of length at most `floor(g/2)+2<g`, a contradiction.  Therefore `q>=h`, proving
the claim.

This gives the registered target for a root `v` only when the terminals can be selected
with `v in S` and `h>=eta(G)`.  That selection is not universally available, so the
arbitrary-root Steiner-radius lemma remains open.

## Exact obstruction to the root-free reduction

The stronger proposal that one can first find a root-free `(g-2)`-set of Steiner
distance at least `g-2+eta` is false.  The graph

```text
HhEK__D
```

has edges

```text
01,05,06,12,23,34,36,37,45,58,78.
```

An independent exact recomputation gives

```text
n=9, girth=5, radius=2, center={3}, eta=2,
max Steiner distance over all triples=4,
rooted four-terminal Steiner eccentricity e_4(v)=5 for every vertex v.
```

Thus no triple reaches `g-2+eta=5`, although the actual rooted four-terminal target
holds with equality at every root.  This kills only the root-free reduction, not
W144-S or W144.
