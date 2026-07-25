# R4 affine-skeleton obstruction

## Restricted family

Let the old vertices be the affine plane `F_5^2`, with one additional vertex
`infinity`.  For each of five colours `c`, choose a distinct affine
direction.  Use three of the five parallel lines in that direction as the
three isolated `K_5` components of a copy of

`G61 = complement(C_5[3,2,2,2,2]) disjoint_union 3K_5`.

The other two parallel lines, together with `infinity`, support the
11-vertex component `H=complement(C_5[3,2,2,2,2])`.

This is called the natural affine skeleton.  The five directions must be
distinct: two colours using the same direction each select three of five
lines, so they share at least one selected line and hence ten edges.

## Proposition

Five copies following the natural affine skeleton cannot be pairwise
edge-disjoint.

## Proof

For colour `c`, let `T_c` be the ten old vertices on its two unselected
parallel lines.  Since `infinity` lies in the 11-vertex component, its degree
in that copy is at least five.  Five edge-disjoint copies can contribute at
most its full degree 25, so its degree is exactly five in every copy.

Let `N_c` be the five old neighbours of `infinity` in colour `c`, and put
`M_c=T_c\N_c`.  The five `N_c` partition `F_5^2`, because their 25 incident
edges at `infinity` are pairwise disjoint and exhaust all such edges.

A degree-five vertex of `H` lies in a size-two blow-up part adjacent to the
unique size-three part.  Its five non-neighbours are the size-three part and
the opposite nonadjacent size-two part.  Those two parts form an independent
set in the underlying 5-cycle, so they form a `K_5` in the complement.
Consequently each `M_c` is a colour-`c` `K_5`.

Thus, for distinct colours,

`|M_c intersection M_d| <= 1`;

otherwise the edge joining two common vertices would belong to both copies.

For distinct affine directions, two unions of two parallel lines meet in
exactly four points.  Hence

`|T_c intersection T_d|=4`.

Since `N_c` and `N_d` are disjoint, for every unordered colour pair
`{c,d}` we have

`4 = |N_c intersection M_d|`
`  + |M_c intersection N_d|`
`  + |M_c intersection M_d|`.

Summing over all ten colour pairs, the first two terms combine to

`sum_(c != d) |N_c intersection M_d|`.

For fixed `d`, the set `M_d` is disjoint from `N_d`, and the five `N_c`
partition the plane.  Therefore its five points occur exactly once among
`N_c`, `c != d`.  It follows that

`sum_(c != d) |N_c intersection M_d| = sum_d |M_d| = 25`.

The summed pair identities now give

`sum_(c<d) |M_c intersection M_d| = 10*4-25 = 15`.

There are only ten pairs and each intersection has size at most one, so the
left side is at most ten.  This contradiction proves the proposition.

## Scope

This eliminates only the natural affine skeleton: three selected parallel
lines for the isolated `K_5` components and the other two lines plus one
common vertex for `H`.  It does not exclude arbitrary pairwise edge-disjoint
permutations of `G61`, and it does not resolve Erdős Problem 617.
