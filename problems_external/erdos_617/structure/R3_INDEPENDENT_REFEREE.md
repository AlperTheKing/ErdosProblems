# Independent referee report on the R3 decomposition obstruction

## Verdict

The proof in `R3_DECOMPOSITION_OBSTRUCTION.md` is sound for its stated scope:
there is no edge decomposition of `K_26` into five permuted copies of
`G = complement(M(C_5)) disjoint_union 3K_5`.

It does not prove Erdős Problem 617, because an unrestricted colouring need
not have five colour graphs isomorphic to `G`.

## Reconstruction

In the Grötzsch graph `F=M(C_5)`, the original, shadow, and apex vertices
have degrees 4, 3, and 5. Complementing inside its 11 vertices gives degrees
6, 7, and 5. Adding three disjoint `K_5` components gives the degree
multiset

`4^15, 5^1, 6^5, 7^5`.

The five degree-7 shadow vertices form a clique in the complement because
they form an independent set in `F`. Therefore every copy has four selected,
pairwise disjoint `K_5` blocks: this degree-7 clique and the three components.
A vertex is in a selected block in a copy exactly when its degree there is
4 or 7.

For a fixed vertex, write `(u,v,w,q)` for its numbers of degree
`(7,6,5,4)` roles. Edge decomposition implies

`u+v+w+q=5` and `7u+6v+5w+4q=25`.

Independent enumeration of the nonnegative integer solutions gives exactly:

```
(u,v,w,q)    selected-block incidence u+q
(1,1,0,3)                 4
(1,0,2,2)                 3
(0,2,1,2)                 2
(0,1,3,1)                 1
(0,0,5,0)                 0
```

Call these `A,B,C,D,E`. Across five copies the total numbers of `U` and `W`
roles are 25 and 5. Solving

`n_A+n_B=25`,

`2n_B+n_C+3n_D+5n_E=5`,

and `sum n_i=26` gives only

```
25A+E,  23A+2B+C,  24A+B+D.
```

The remaining `V` and `Q` totals are respectively 25 and 75 in all three
cases, so no omitted aggregate-role equation creates another case.

Every `A` or `B` vertex has exactly one `U` role; the unique other vertex has
none. Hence the five `U` blocks are disjoint and cover the 25 `A/B`
vertices.

Selected blocks in different copies meet in at most one vertex, since two
common vertices would make their joining edge occur in both copies. Fix a
`U` block `B_0`. If `b(x)` is the number of selected blocks containing `x`,
then the number of other-copy blocks meeting `B_0` is exactly

`sum_(x in B_0)(b(x)-1)`.

There is no double counting: one other-copy block cannot contain two
vertices of `B_0`. There are 16 selected blocks in the other four copies.
Putting every globally available lower-incidence `B` vertex into `B_0`
maximizes the number disjoint from it. The three respective maxima are

```
16-5*3 = 1,
16-(2*2+3*3) = 3,
16-(1*2+4*3) = 2.
```

But the four other `U` blocks are all disjoint from `B_0`, requiring at least
four. Each global case is contradictory.

## Counterexample search against the proof

An independent PowerShell enumeration reproduced all five local role tuples
and exactly the three global multisets above. It also returned maximum
cross-copy disjoint-block counts `1,3,2`; none reaches four. A separate parse
of `r2_counterexample_26.edges` reproduced degree multiset
`4^15,5^1,6^5,7^5` and confirmed all ten edges of the degree-7 `U` clique.

No counterexample to any degree-role, block-intersection, or equality step
was found. The proof does not assume that these are all `K_5` subgraphs of a
copy; it uses only the four explicitly selected, disjoint cliques, which is
sufficient.
