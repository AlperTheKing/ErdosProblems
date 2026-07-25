# No decomposition into five copies of the R2 equality graph

Let `G` be the 26-vertex graph in `r2_counterexample_26.edges`.  Its degree
roles are:

- 15 vertices of degree 4, in three disjoint `K_5` components (`Q` role);
- one vertex of degree 5 (`W` role);
- five vertices of degree 6 (`V` role); and
- five vertices of degree 7 (`U` role).

The five `U` vertices induce a `K_5`.  Thus each copy of `G` contains four
pairwise disjoint distinguished `K_5` blocks: its `U` block and its three
`Q` blocks.

## Proposition

The edges of `K_26` cannot be decomposed into five permuted copies of `G`.

## Proof

Assume that five copies decompose `K_26`.  At any vertex, its five degrees,
one in each copy, sum to 25.  If its numbers of `U,V,W,Q` roles are
`u,v,w,q`, then

`u+v+w+q=5` and `7u+6v+5w+4q=25`,

so

`3u+2v+w=5`.

The only possible vertex types are

| type | `(u,v,w,q)` | number of distinguished blocks containing it |
|---|---:|---:|
| `A` | `(1,1,0,3)` | 4 |
| `B` | `(1,0,2,2)` | 3 |
| `C` | `(0,2,1,2)` | 2 |
| `D` | `(0,1,3,1)` | 1 |
| `E` | `(0,0,5,0)` | 0 |

Across all five copies there are 25 `U` roles and five `W` roles.  Therefore
the global type multiset is one of exactly:

1. `25 A + 1 E`;
2. `23 A + 2 B + 1 C`; or
3. `24 A + 1 B + 1 D`.

The five `U` blocks are pairwise disjoint: every `A` or `B` vertex has
exactly one `U` role, while the unique vertex of type `C`, `D`, or `E` has
none.  Hence the `U` blocks partition the other 25 vertices.

Any two distinguished blocks of different copies meet in at most one
vertex, since two common vertices would make their joining edge belong to
two copies.  Fix a distinguished block `B_0`, and let `b(x)` be the number
of distinguished blocks containing `x`.  Among the 16 distinguished blocks
of the other four copies, exactly

`sum_(x in B_0) (b(x)-1)`

meet `B_0`: all these intersections are distinct by the preceding
at-most-one observation.

Now take `B_0` to be a `U` block.  It contains only `A` or `B` vertices.

- In case 1, all five vertices are `A`, so `B_0` is disjoint from only
  `16-5*3=1` cross-copy block.
- In case 2, there are only two `B` vertices globally.  Even if both lie in
  `B_0`, it is disjoint from at most
  `16-(2*2+3*3)=3` cross-copy blocks.
- In case 3, there is only one `B` vertex globally, so `B_0` is disjoint
  from at most `16-(1*2+4*3)=2` cross-copy blocks.

But `B_0` must be disjoint from the four `U` blocks in the other four
copies.  Every case is impossible.  This proves the proposition.

The proposition closes only the route that tries to use five permuted copies
of this particular equality graph.  It is not a proof of Erdős Problem 617.
