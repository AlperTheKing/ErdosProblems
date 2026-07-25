# Objective-9 checkpoint: one-relocation obstruction

Scope: the frozen raw graph
`theory_inputs/unrestricted19-q5-twin-fill-objective9.json`, SHA-256
`32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA`.
This result excludes one fixed-q missing-edge relocation with no additional
arc reversals. It does not exclude coupled relocation-and-reversal surgery.

## Exact twin structure

On the 18 vertices other than 12, the graph is a tournament partitioned into
nine ordered out-twin pairs

`(8,1), (0,15), (16,6), (2,9), (11,18), (7,14), (5,17),`

`(10,4), (3,13)`.

For each `(h,l)`, `h -> l` and `N+(h)=N+(l) union {l}`. The low vertices
`{1,4,6,9,13,14,15,17,18}` are exactly the failing rows, each with penalty
one and unreachable set `{12,h}`. Every high row has `(d+,|N2+|)=(9,8)`;
every low row has `(8,8)`.

Direct reconstruction from the raw adjacency gives the same sorted positive
two-step witness multiplicities in every one of these 18 rows:

`{2,2,4,4,6,6,8,8}`.

In particular, no current second out-neighbor of any non-12 source has a
unique witness.

## The obstruction

A fixed-q relocation fills one missing pair `{12,x}` and deletes one present
arc `a -> b`.

### Outward fill `12 -> x`

Vertex 12 still has no in-neighbor, so the fill can change no non-12
two-step neighborhood. Deleting `a -> b` removes at most one of the at least
two edge-disjoint witness paths to any existing second target. Hence it
removes no existing member of `N2+(v)` for any non-12 row.

If `a` has outdegree 8, the result violates the minimum-outdegree domain. If
`a` has outdegree at least 9, lowering its outdegree cannot reduce any old
penalty, and all nine old failing penalties remain. If `a=12`, the move is a
neutral relocation between two hub pairs. Thus every domain-valid outward
single relocation has objective at least 9.

### Inward fill `x -> 12`

The tournament indegree of `x` is 8 when `x` is a high twin and 9 when it is
a low twin. Every predecessor `v -> x` acquires the new path
`v -> x -> 12`. One deleted arc can destroy this path for at most one
predecessor, namely when that deleted arc itself is `v -> x`.

The deletion cannot remove an old second target from any non-12 row, by the
two-witness calculation above. Therefore at least seven non-12 rows acquire
12 as a new second target. Each such row starts at either `(9,8)` or `(8,8)`,
so its penalty increases by one. Vertex `x` can reduce its own old penalty by
at most one when promoted. Hence an inward single relocation also cannot
lower objective 9.

## Consequence

No single fixed-q missing-edge relocation from this raw graph has objective
below 9. Any further direct surgery must combine a relocation with at least
one additional reversal, and in practice must remove both members of a
two-witness pair while balancing the donor degrees. That larger coupled family
is not excluded here.

## Referee correction

The inward-fill sentence saying each affected penalty increases by one is too strong. The proved statement is that each affected penalty increases by at least one. For example, adding `9 -> 12` and deleting `2 -> 0` changes row 2 from `(9,8,0)` to `(8,10,3)`. The lower bound and the no-improvement conclusion remain valid.

The final scope is also restricted: a successful surgery cannot consist of only one relocation. This note does not prove that an additional reversal is necessary, because two or more coupled relocations without reversals were not analyzed.
