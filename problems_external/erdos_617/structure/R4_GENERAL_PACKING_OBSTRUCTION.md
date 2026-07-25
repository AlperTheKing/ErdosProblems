# General obstruction to packing five copies of `G61`

## Definitions

Let

`H = complement(C_5[3,2,2,2,2])`

on 11 vertices, where the five independent blow-up parts have sizes
`3,2,2,2,2`, and consecutive parts of the 5-cycle are joined completely.
Let

`G61 = H disjoint_union K_5 disjoint_union K_5 disjoint_union K_5`.

The graph `H` has 31 edges and independence number two.  Indeed, its
complement is a triangle-free blow-up of `C_5`.  The raw graph is stored in
`r4_g61_26.edges`.

If five pairwise edge-disjoint permuted copies of `G61` existed, their 305
edges could be extended to a five-colouring of `K_26` by assigning the 20
unused edges arbitrarily.  Adding edges cannot increase a colour graph's
independence number.  Thus such a packing would directly refute Erdős
Problem 617.

## Proposition

Five arbitrary permuted copies of `G61` cannot be pairwise edge-disjoint.

## Proof

Assume that copies indexed by five colours are pairwise edge-disjoint.  Fix
one colour `c`.  Write

- `H_c` for the 11-vertex copy of `H`; and
- `Q_(c,1),Q_(c,2),Q_(c,3)` for its three isolated `K_5` components.

Consider a `K_5` component `Q_(d,j)` of another colour `d`.  All ten pairs
inside it are colour-`d` edges.  Pairwise edge-disjointness therefore makes
its five vertices an independent set in the entire colour-`c` graph.

Every independent five-set of `G61` has exactly:

- one vertex in each of its three isolated `K_5` components; and
- two vertices in its `H` component.

This follows because an independent set takes at most one vertex from each
isolated `K_5` and at most two from `H`, and all five bounds must be tight.

Consequently, for distinct colours `c,d`,

`|Q_(d,j) intersection Q_(c,i)|=1`

for every `i,j`, and

`|Q_(d,j) intersection H_c|=2`.

The three colour-`d` `K_5` components are disjoint.  Hence their intersections
with `H_c` give three disjoint pairs, each of which is a colour-`d` edge
inside the 11-set `H_c`.  Thus the `Q` components of colour `d` contribute
exactly three colour-`d` edges inside `H_c`.

The forced component-intersection table is

| | `Q_(d,1)` | `Q_(d,2)` | `Q_(d,3)` | `H_d` |
|---|---:|---:|---:|---:|
| `Q_(c,1)` | 1 | 1 | 1 | 2 |
| `Q_(c,2)` | 1 | 1 | 1 | 2 |
| `Q_(c,3)` | 1 | 1 | 1 | 2 |
| `H_c` | 2 | 2 | 2 | 5 |

The last entry follows from the row sum

`|H_c|=2+2+2+|H_c intersection H_d|=11`.

Put `S=H_c intersection H_d`, so `|S|=5`.  Since `H_d` has independence
number two, its induced graph on `S` also has independence number at most
two.  The complement of `H_d[S]` is therefore triangle-free.  Mantel's
theorem gives at most six complement edges on five vertices, and hence

`e(H_d[S]) >= C(5,2)-6 = 4`.

Thus every colour `d != c` contributes at least

`3+4=7`

colour-`d` edges inside the fixed 11-set `H_c`.  These contributions are
pairwise disjoint and are also disjoint from the 31 colour-`c` edges of
`H_c`.  The complete graph on `H_c` would therefore contain at least

`31 + 4*7 = 59`

distinct edges.  But an 11-set has only

`C(11,2)=55`

pairs.  This contradiction proves the proposition.

## Scope

This proof covers all choices of five permutations of the specific graph
`G61`; it makes no affine, cyclic, algebraic, or symmetry assumption.
It closes the R4 packing route but does not rule out five nonisomorphic
colour graphs and does not resolve Erdős Problem 617.
