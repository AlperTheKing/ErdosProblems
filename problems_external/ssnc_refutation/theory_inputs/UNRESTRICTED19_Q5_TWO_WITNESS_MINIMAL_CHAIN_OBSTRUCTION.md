# Two-witness minimal compensation-chain obstruction

## Scope

Work from `unrestricted19-q5-twin-fill-objective9.json`, SHA-256
`32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA`.
Keep the quotient-block orientation fixed except for the two witness arcs and
one degree-compensating arc per witness donor.  Relocate the two resulting
holes only to the five pairs currently missing at vertex 12.  This note proves
that this smallest coupled repair cannot lower the objective while preserving
minimum outdegree eight.

Longer chains that alter additional quotient-block arcs are outside this
statement.

## The exact unique-witness cycle

Use the ordered blocks

```text
A=(8,1), B=(10,4), C=(16,6), D=(2,9), E=(3,13),
F=(7,14), G=(0,15), H=(5,17), I=(11,18),
```

where the first vertex is high and the second is low.  For every block there
is one second-neighbour block reached through exactly one intermediate block,
hence through exactly its two vertices.  The nine triples are

```text
A -> G -> C
B -> E -> A
C -> D -> I
D -> I -> F
E -> A -> G
F -> H -> B
G -> C -> D
H -> B -> E
I -> F -> H.
```

Their intermediate map is the directed nine-cycle

```text
A -> G -> C -> D -> I -> F -> H -> B -> E -> A.
```

## Concrete first repair

Choose the failing low vertex 1 in block `A`.  Its second-neighbour block `C`
is reached only through block `G`.  For either `x=16` or `x=6`, the complete
two-step witness set is exactly

```text
{m : 1 -> m -> x} = {0,15}.
```

Delete both `0 -> x` and `15 -> x`.  Then `x` leaves `N2+(1)`, changing row 1
from `(8,8)` to `(8,7)`.  The same deletion removes `x` from `N2+(8)`, so the
high vertex 8 changes from `(9,8)` to `(9,7)`.

The two witness donors change as follows.

- Vertex 15 falls from outdegree eight to seven.
- Vertex 0 falls from outdegree nine to eight.  The deleted target `x` is
  still a second out-neighbour of 0; for example block `E` supplies a path
  `0 -> 3 -> x`.  Thus row 0 becomes `(8,9)` before compensation.

The deletion creates two new missing pairs.  Filling any two of the original
12-star holes restores `q=5`, but only the hole `{0,12}` is incident with a
witness donor.  Filling it as `0 -> 12` restores the degree of 0 while leaving
`x` in its second neighbourhood, so row 0 is still a failing `(9,9)` row.
No original hole is incident with vertex 15.

## Why one compensation step for vertex 15 cannot close the repair

There are only two one-arc ways to restore the lost outdegree of vertex 15.

### Reverse `12 -> 15`

Changing it to `15 -> 12` restores `d+(15)=8`, but vertex 1 already has
`1 -> 15`.  Consequently

```text
1 -> 15 -> 12
```

makes 12 a new second out-neighbour of vertex 1.  This exactly replaces the
removed target `x`, returning row 1 to `(8,8)`.  The proposed repair vanishes
before any collateral rows are counted.

### Reverse `y -> 15`

The possible high donors are `y in {8,10,2,7}`, the highs of the four blocks
that dominate `G`.  A low donor would immediately fall from degree eight to
seven.

For every high donor, deleting `y -> 15` leaves 15 reachable in two steps:
`y` points to its own low partner, which still points to 15.  Hence 15 changes
from a direct target to a new second target of `y`.

- For `y=8`, the earlier loss of `x` from `N2+(8)` is exactly offset by the
  new target 15.  Its degree falls to eight and its second degree returns to
  eight, so it fails by equality.
- For `y in {10,2,7}`, target `x` retains other two-step witnesses.  The new
  target 15 therefore raises the second degree to nine while the direct degree
  falls to eight.

Thus every one-arc internal compensation for vertex 15 creates a donor
failure.  Independently, vertex 0 still requires more than the single
available star fill: `0 -> 12` gives equality, while a one-arc transfer
`y -> 0` makes 0 a new second target of the donating high through its low
partner (and a low donor violates the degree bound).

## Conclusion

The smallest repair consisting of

1. the two exact witness deletions for one unique next block;
2. two fills of old 12-star holes; and
3. at most one degree-compensating reversal for each witness donor

cannot produce a valid objective below nine.  Either vertex 1 returns to
equality, a donor becomes a new failing row, or a donor has outdegree seven.
Escaping this obstruction requires a longer chain that changes another
quotient-block relation; repeating a different member of the same nine-cycle
is algebraically equivalent.

