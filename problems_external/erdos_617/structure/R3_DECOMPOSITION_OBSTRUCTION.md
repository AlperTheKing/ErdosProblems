# Obstruction to decomposing `K_26` into five copies of the R2 graph

## The graph

Let `F` be the 11-vertex Groetzsch graph, the Mycielskian of `C_5`.  Write
its vertices as

`v_0,...,v_4, u_0,...,u_4, w`

with indices modulo five, and its edges as

- `v_i v_(i+1)`;
- `u_i v_(i-1)` and `u_i v_(i+1)`; and
- `w u_i`.

Let `H` be the complement of `F`, and let

`G = H disjoint_union K_5 disjoint_union K_5 disjoint_union K_5`.

The raw canonical edge list is `r2_counterexample_26.edges`.

In `F`, the degrees of `v_i,u_i,w` are respectively 4, 3, and 5.
Consequently, in `H` they are respectively 6, 7, and 5.  The exact degree
sequence of `G` is therefore

`4^15, 5^1, 6^5, 7^5`.

Call these degree roles `Q,W,V,U`, respectively.  The five `U` vertices
induce a `K_5` in `H`, because the `u_i` are independent in `F`.  Together
with the three `K_5` components, every copy of `G` therefore contains four
pairwise disjoint distinguished `K_5` blocks:

- one `U` block; and
- three `Q` blocks.

## Proposition

There do not exist permutations `pi_0,...,pi_4` of 26 vertices such that

`E(K_26) = disjoint_union_(c=0)^4 pi_c(E(G))`.

Thus five permuted copies of this particular equality graph cannot give a
counterexample to Erdős Problem 617.

## Proof

Assume such a decomposition exists.  At a fixed vertex `x`, let
`u(x),v(x),w(x),q(x)` be its numbers of `U,V,W,Q` roles across the five
copies.  The five copy-degrees at `x` partition its 25 incident edges, so

`u+v+w+q=5`

and

`7u+6v+5w+4q=25`.

Subtracting four times the first equation gives

`3u+2v+w=5`.

The nonnegative solutions, including the resulting number `u+q` of
distinguished blocks containing the vertex, are exactly

| type | `(u,v,w,q)` | block incidence `u+q` |
|---|---:|---:|
| `A` | `(1,1,0,3)` | 4 |
| `B` | `(1,0,2,2)` | 3 |
| `C` | `(0,2,1,2)` | 2 |
| `D` | `(0,1,3,1)` | 1 |
| `E` | `(0,0,5,0)` | 0 |

Let `n_A,...,n_E` count the five types.  Across the five copies there are
exactly 25 `U` roles and five `W` roles.  Hence

`n_A+n_B=25`,

`2n_B+n_C+3n_D+5n_E=5`,

and

`n_A+n_B+n_C+n_D+n_E=26`.

The first and third equations imply

`n_C+n_D+n_E=1`.

Substitution in the `W`-role equation gives exactly three possible global
type multisets:

1. `25 A + 1 E`;
2. `23 A + 2 B + 1 C`;
3. `24 A + 1 B + 1 D`.

In particular, precisely 25 vertices have one `U` role and the remaining
vertex has none.  The five `U` blocks are therefore pairwise disjoint and
partition those 25 vertices.

Now consider all 20 distinguished blocks, four from each copy.  Two blocks
from the same copy are disjoint.  Two blocks from different copies intersect
in at most one vertex: if they shared two vertices, the edge joining those
vertices would occur in both copies, contradicting edge-disjointness.

Fix a distinguished block `B_0` in one copy.  For a vertex `x`, write
`b(x)=u(x)+q(x)` for its distinguished-block incidence.  Each `x in B_0`
lies in exactly `b(x)-1` distinguished blocks from other copies.  Moreover,
all those other blocks are distinct as `x` varies over `B_0`, by the
at-most-one-intersection property.  Therefore the exact number of the 16
cross-copy distinguished blocks meeting `B_0` is

`sum_(x in B_0) (b(x)-1)`,

and the exact number disjoint from `B_0` is

`16 - sum_(x in B_0) (b(x)-1)`.

Take `B_0` to be a `U` block.  It contains only vertices of type `A` or `B`,
because those are the only types having a `U` role.

- In case 1, all five vertices of `B_0` are type `A`, so it is disjoint from
  exactly `16-5(4-1)=1` cross-copy block.
- In case 2, there are only two type-`B` vertices in the entire graph.
  Even if both lie in `B_0`, it is disjoint from at most
  `16-[2(3-1)+3(4-1)]=3` cross-copy blocks.
- In case 3, there is only one type-`B` vertex.  Even if it lies in `B_0`,
  the block is disjoint from at most
  `16-[(3-1)+4(4-1)]=2` cross-copy blocks.

But `B_0` must be disjoint from the four `U` blocks belonging to the other
four copies.  Each of the three exhaustive cases permits fewer than four
cross-copy blocks disjoint from `B_0`, a contradiction.

This proves the proposition.

## Scope

The argument rules out only decompositions into five isomorphic copies of
the specific graph `G=H disjoint_union 3K_5`.  It neither rules out five
nonisomorphic colour graphs nor proves the full conjecture.
