# Zero-trust audit of the `(12,8,4,0)` hive

This audit does not call the q2 generator/checker or the project hive engine.
`zero_trust_specific_hive.py` reconstructs the standard size-four hive directly
from the three rhombus families and uses only exact `Fraction` arithmetic.

## Boundary and lattice-point count

For

```
lambda = mu = (12,8,4,0),   nu = (18,14,10,6),
```

the boundary values in coordinates `(x,y)`, `x,y >= 0`, `x+y <= 4`, are

```
left:       0,12,20,24,24
bottom:     0,18,32,42,48
hypotenuse: 24,36,44,48,48
```

The three interior coordinates are

```
(h11,h12,h21).
```

Exact vertex enumeration gives 11 vertices, all integral, and direct integer
enumeration in the vertex bounding box gives exactly 50 hive points.  The
independent tableau LR engine also returns

```powershell
python problems_external\ktt_lr_negativity\engine\engineB_lrrule.py `
  "12,8,4,0" "12,8,4,0" "18,14,10,6"
# 50
```

Thus `c=50` is confirmed by both the hive inequalities and an engine that does
not use hives.

## The point `(26,32,38)`

The point satisfies all 18 rhombus inequalities.  Exactly these nine input
inequalities are active:

```
B(0,1):  (-1, 0, 0) . h <= -26
A(0,2):  ( 0,-1, 0) . h <= -32
C(1,0):  (-1, 0, 0) . h <= -26
A(1,1):  ( 1,-1,-1) . h <= -44
B(1,1):  (-1, 1,-1) . h <= -32
C(1,1):  (-1,-1, 1) . h <= -20
C(1,2):  ( 0,-1, 0) . h <= -32
A(2,0):  ( 0, 0,-1) . h <= -38
B(2,1):  ( 0, 0,-1) . h <= -38
```

There are six distinct active input normals.  The three coordinate normals
`-e1,-e2,-e3` are redundant in the tangent cone.  Its three facet normals are

```
( 1,-1,-1), (-1, 1,-1), (-1,-1, 1),   absolute determinant 4.
```

The primitive tangent rays are

```
(0,1,1), (1,0,1), (1,1,0),             absolute determinant 2.
```

Therefore `(26,32,38)` is a vertex and its tangent cone is simplicial but not
unimodular; its lattice multiplicity is 2.

## What the 589M census measured

The vector of nine gap parameters is `(4,4,4,4,4,4,4,4,4)`, so this exact
triple lies inside the `GMAX=10` run.

In `vcheck.cpp`, every nonsingular triple of the 18 *input rows* is solved.
For each feasible solution, lines 86--95 collect every distinct tight input-row
direction in `tdir`.  The vertex denominator is recorded first, but line 102
then executes

```cpp
if (ntd != 3) continue;
```

Only after this test does the code cross the three normals, primitive-normalize
the three rays, and record

```cpp
m = abs(det(primitive tangent rays)).
```

For the audited vertex `ntd=6`, not 3.  Consequently its determinant 2 is
never computed or entered in the histogram.  The reported `m=1:854321098`
means precisely:

> Every feasible row-triple occurrence whose solution had exactly three
> distinct tight **input-row directions** produced primitive-ray determinant
> one.

It does **not** mean that every geometrically simple vertex cone was
unimodular.  Redundant tight inequalities can make `ntd>3` even when the
minimal tangent cone has exactly three facets and three rays, as here.

There is a second counting caveat: the loop has no vertex de-duplication, so
the histogram counts qualifying row-triple occurrences, not necessarily
distinct vertices.  Also `nonempty-row-system polytopes=589487256` is the
source program's label: the counter is incremented after the boundary-row
check, before any feasible vertex has been found.

## Replay

```powershell
python problems_external\ktt_lr_negativity\r4_reeve\zero_trust_specific_hive.py
```

The script terminates with `AUDIT=PASS`.  Its SHA-256 is

```
CE7FFA2C88A0682D1B513981D21854B363701A8D3DD1175D1E5F1DB281F1FA30
```
