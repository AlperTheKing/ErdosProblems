# Objective-10 checkpoint: exact block-cycle surgery obstruction

Scope: the frozen raw graph
`theory_inputs/unrestricted19-q5-relocation-objective10.json`, SHA-256
`62241FCC69A6D03DAA32A976ADEFB949DFFAE27DBB95470C4492FE85D88389BB`.
This note does not prove that the unrestricted order-19 instance is UNSAT.

## Exact twin blocks

Write the nine ordered blocks as

`B0=(8,1), B1=(0,15), B2=(16,6), B3=(2,9), B4=(11,18),`

`B5=(14,7), B6=(5,17), B7=(10,4), B8=(3,13)`.

For every `Bi=(h,l)` except `B5`, `h -> l` and
`N+(h)=N+(l) union {l}`. In `B5`, the pair `{14,7}` is missing and
`N+(14)=N+(7)`. Thus the failing vertices are the eight low vertices
`1,15,6,9,18,17,4,13` and both vertices `7,14` of `B5`.

Each failure has penalty one. Its unreachable set is `{12,h}` for an
oriented block and `{12,the other endpoint}` for `B5`.

## Two-witness cycle

For each failing row, every reachable target has at least two witnesses. The
targets of witness count exactly two are:

| source | two-witness targets | the two witnesses |
|---:|:---|:---|
| 1 | `{6,16}` | `{0,15}` |
| 15 | `{2,9}` | `{6,16}` |
| 6 | `{11,18}` | `{2,9}` |
| 9 | `{7,14}` | `{11,18}` |
| 18 | `{5,17}` | `{7,14}` |
| 7 | `{4,10}` | `{5,17}` |
| 14 | `{4,10}` | `{5,17}` |
| 17 | `{3,13}` | `{4,10}` |
| 4 | `{1,8}` | `{3,13}` |
| 13 | `{0,15}` | `{1,8}` |

This is the cyclic rule: low row of `Bi` reaches either vertex of `B(i+2)`
through exactly the two vertices of `B(i+1)` (indices modulo nine), with both
rows of `B5` sharing the same requirement.

Consequently, one arc deletion that does not raise the source degree cannot
repair any row: one of the two displayed paths remains. A repair by promotion
instead transfers one degree unit to the source and removes one from a donor.
The missing bridge is a coupled edit that removes both displayed witnesses
while compensating both degree losses without making a donor fail or using a
new middle that restores an old unreachable target.

## Exact failure of the degree-balanced cycle switch

The canonical simultaneous compensation is to reverse, for every target low
vertex `l_j`, both arcs from `B(j-1)` into `l_j`. These are the 18 arcs

`3->1, 13->1, 8->15, 1->15, 0->6, 15->6, 16->9, 6->9,`

`2->18, 9->18, 11->7, 18->7, 14->17, 7->17, 5->4, 17->4,`

`10->13, 4->13`.

Filling `{7,14}` as `14->7` and moving that hole back to `{0,12}` keeps
`q=5` and minimum outdegree 8. Literal replay gives objective 18: precisely
`{0,2,3,5,8,10,11,14,16}` have `(d+,|N2+|)=(8,9)`, while the nine old low
vertices have `(9,8)`. Thus the all-block switch only transfers the
obstruction and doubles each new row penalty.

The most direct local use of the internal hole also fails. Filling `14->7`,
deleting `14->17`, and reversing `7->17` and `11->7` keeps `q=5` and minimum
outdegree 8, but literal replay gives objective 12. It repairs vertex 17 but
changes vertices 7 and 14 to penalty two and vertex 11 to penalty one.

No explicit degree-balanced two-witness deletion remains after these forced
block compensations. Testing alternative donor choices would be a bounded
neighborhood enumeration with no explicit adjacency bridge, so checkpoint
surgery exits here under the registered direct-route condition.
