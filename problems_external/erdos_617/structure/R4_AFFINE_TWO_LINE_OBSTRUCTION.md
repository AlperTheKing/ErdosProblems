# Obstruction to the natural affine two-line-support construction

This note concerns the following direct attempt to pack five copies of
`G61` into `K_26`.

Use old vertices `F_5^2` and one common vertex `infinity`.  For each colour
`c`, choose one affine direction.  Three of its five parallel lines are the
three isolated `K_5` components of the copy.  The remaining two lines,
together with `infinity`, support the 11-vertex component

`H = complement(C_5[3,2,2,2,2])`.

The five directions must be distinct: two colours using the same direction
would each choose three of its five lines, hence would share a selected
line and all ten edges of its `K_5`.

## Proposition

Five copies in this affine two-line-support family cannot be pairwise
edge-disjoint.

## Proof

For colour `c`, let `T_c` be the ten old vertices on its two unselected
parallel lines.  In the 11-vertex component, `infinity` must have degree
five: five copies already contribute at least `5*5=25` incident edges, which
is the full degree in `K_26`.

Let

- `N_c` be the five old neighbours of `infinity` in colour `c`; and
- `M_c=T_c\N_c` be its five old non-neighbours inside the component.

The five sets `N_c` partition `F_5^2`, since the five copies partition all
25 edges incident with `infinity`.

In `H`, the five non-neighbours of a degree-five vertex form a `K_5`.
Indeed, a degree-five vertex lies in one of the size-two blow-up parts next
to the size-three part; its non-neighbours are exactly that size-three part
and the opposite nonadjacent size-two part.  Hence every `M_c` is a
colour-`c` `K_5`.  Pairwise edge-disjointness therefore implies

`|M_c intersection M_d| <= 1`

for distinct colours.

Because `T_c` and `T_d` are unions of two lines in distinct affine
directions, each of the four line pairs meets once and

`|T_c intersection T_d|=4`.

For a colour pair `{c,d}`, the disjointness of `N_c,N_d` gives

`4 = |N_c intersection M_d|`
`  + |M_c intersection N_d|`
`  + |M_c intersection M_d|`.

Sum this identity over the ten unordered colour pairs.  The first two terms
together become

`sum_(c != d) |N_c intersection M_d|`.

Since the `N_c` partition all old vertices and `M_d` is disjoint from
`N_d`, every one of the five points of `M_d` occurs exactly once in this
sum.  Therefore

`sum_(c != d) |N_c intersection M_d| = sum_d |M_d| = 25`.

It follows that

`sum_(c<d) |M_c intersection M_d| = 10*4-25 = 15`.

But there are only ten colour pairs, and every `M_c,M_d` intersection has
size at most one.  Their sum is at most ten, a contradiction.

This rules out the full affine family described above, not merely one
choice of neighbour sets or blow-up labels.  It does not rule out arbitrary
permuted copies of `G61`.
