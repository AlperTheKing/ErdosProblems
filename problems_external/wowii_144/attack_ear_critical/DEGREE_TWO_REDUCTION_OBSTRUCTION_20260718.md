# First obstruction to a last-ear degree-two reduction

Date: 2026-07-18.

## Exact failed selection rule

After the proved cycle-rank-two theta case, the most direct open-ear induction
would select an internal vertex of the last nontrivial ear.  Such a vertex has
degree two, its deletion preserves connectivity in a 2-connected graph, and
it lowers cycle rank by one.  The required local assertion would be

```text
some degree-two v has eta(G-v)>=eta(G).                       (D2)
```

Statement (D2) is false for 2-connected graphs of cycle rank at least three.

## First exact obstruction

`find_degree_two_reduction_obstruction.py` exhausts biconnected
girth-at-least-five graphs in graph6 generator order.  The first failure is

```text
graph6: I?`acgwg_
n=10, m=14, beta=5, girth=5,
rad(G)=2, eta(G)=2,
C(G)={2,3,7,9},
degree sequence=(2,2,3,3,3,3,3,3,3,3).
```

Its edges are

```text
04 07 09 15 16 25 28 29 36 37 38 48 57 69.
```

The only degree-two vertices are `1` and `4`.  Both are admissible, preserve
girth five, and lower cycle rank from five to four, but

```text
eta(G-1)=eta(G-4)=1.
```

In both cases the radius remains two and the center expands.  By contrast,
every degree-three vertex except `1,4` is eta-good: deleting any of

```text
0,2,3,5,6,7,8,9
```

leaves eta two.  Those deletions lower cycle rank from five to three.  Hence a
valid induction step may have to delete a branch vertex and remove two units
of cycle rank; it cannot be confined to the internal vertex of the last ear.

The failure occurs after only 40 biconnected cycle-rank-at-least-three graphs
in exact generator order.  The machine-readable record includes every center
and deletion invariant in `degree_two_reduction_obstruction.json`.

## The nearest neighbor repair also fails

The attempted repair

```text
if a degree-two v is bad, one of its two neighbors is admissible and good
```

already fails at cycle rank three:

```text
graph6 H?`@F_], n=9, m=11, beta=3, girth=5,
rad=2, eta=1, C={3,7,8}.
```

Deleting the degree-two vertex `3` raises the radius to three and lowers eta
to zero.  Its neighbors `7,8` are both inadmissible because deleting either
removes every cycle.  Exact data are in
`bad_degree_two_neighbor_exchange_beta3.json`.  Other ears contain good
vertices, so this graph kills the local neighbor exchange, not (EDEL).

## Consequence

The theta theorem is a genuine base case, but it does not extend by simply
removing the internal vertex of a last ear.  The first unsupported higher-ear
step must compare different ears and must allow deletion of a branch vertex.
This is precisely the simultaneous UEP/replacement-path incompatibility
identified in `EAR_CRITICAL_AUDIT_20260718.md`; no degree or location
hierarchy is opened beyond these exact obstructions.
