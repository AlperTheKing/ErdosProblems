# Order-19 q=5 twin-fill objective-9 checkpoint

This is a preserved non-certificate derived independently from the verified
objective-10 raw graph. It is not an SSNC counterexample.

## Immutable input and output

- Parent: `unrestricted19-q5-relocation-objective10.json`
- Parent SHA-256:
  `62241FCC69A6D03DAA32A976ADEFB949DFFAE27DBB95470C4492FE85D88389BB`
- Raw output: `unrestricted19-q5-twin-fill-objective9.json`
- Raw-output SHA-256:
  `32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA`

The single fixed-q hole relocation is:

1. fill the missing pair `{7,14}` as `7 -> 14`;
2. delete the existing arc `12 -> 0`.

## Exact witness dependencies

In the parent graph, vertices 7 and 14 are out-twins:

```text
N+(7)=N+(14)={0,2,3,5,9,13,15,17}.
```

The parent row for 7 is

```text
N+(7)  ={0,2,3,5,9,13,15,17},
N2+(7) ={1,4,6,8,10,11,16,18},
W(7)   ={12,14}.
```

After adding `7 -> 14`, vertex 14 moves from `W(7)` to `N+(7)`. Every
two-step target reached from 7 through the new middle 14 is already a direct
out-neighbor of 7, because `N+(14)` is the old `N+(7)`. Hence
`N2+(7)` is unchanged exactly.

The complete set of sources whose second neighborhood could change through
the new final arc `7 -> 14` is

```text
N-(7)={1,4,6,8,10,11,12,16,18}.
```

For sources `1,4,6,8,10,11,16,18`, vertex 14 is already a direct
out-neighbor. For source 12, vertex 14 is already a new second out-neighbor.
Thus the new arc adds no second target to any row other than its already
accounted-for effect on row 7.

Before deleting `12 -> 0`, vertex 12 has no in-neighbor: it points to every
adjacent vertex and is nonadjacent precisely to `9,14,17,18`. Therefore no
row other than row 12 uses a two-step witness of the form `u -> 12 -> 0`.

After deleting `12 -> 0`, the new second target 0 of row 12 has the exact
witness set

```text
{1,2,4,7,8,10}.
```

The four old second targets of row 12 remain, with witness sets among the
remaining out-neighbors of 12:

```text
9:  {1,2,4,6,7,8,10,16}
14: {1,4,6,8,10,11,16}
17: {2,3,5,7,13,15}
18: {2,3,5,11,13,15}
```

Consequently the only changed ledger rows are 7 and 12.

## Exact ledger deltas

Notation is `d=|N+(v)|`, `s=|N2+(v)|`,
`p=max(0,s-d+1)`.

| v | parent `(d,s,p,W)` | output `(d,s,p,W)` | exact set change |
|---:|:---|:---|:---|
| 7 | `(8,8,1,{12,14})` | `(9,8,0,{12})` | `14: W -> N+` |
| 12 | `(14,4,0,{})` | `(13,5,0,{})` | `0: N+ -> N2+` |

Every other row has identical `N+`, `N2+`, and `W` before and after the
relocation.

## Complete output ledger

| v | d | s | p | W |
|---:|---:|---:|---:|:---|
| 0 | 9 | 8 | 0 | `{12}` |
| 1 | 8 | 8 | 1 | `{8,12}` |
| 2 | 9 | 8 | 0 | `{12}` |
| 3 | 9 | 8 | 0 | `{12}` |
| 4 | 8 | 8 | 1 | `{10,12}` |
| 5 | 9 | 8 | 0 | `{12}` |
| 6 | 8 | 8 | 1 | `{12,16}` |
| 7 | 9 | 8 | 0 | `{12}` |
| 8 | 9 | 8 | 0 | `{12}` |
| 9 | 8 | 8 | 1 | `{2,12}` |
| 10 | 9 | 8 | 0 | `{12}` |
| 11 | 9 | 8 | 0 | `{12}` |
| 12 | 13 | 5 | 0 | `{}` |
| 13 | 8 | 8 | 1 | `{3,12}` |
| 14 | 8 | 8 | 1 | `{7,12}` |
| 15 | 8 | 8 | 1 | `{0,12}` |
| 16 | 9 | 8 | 0 | `{12}` |
| 17 | 8 | 8 | 1 | `{5,12}` |
| 18 | 8 | 8 | 1 | `{11,12}` |

The remaining failing vertices are exactly

```text
{1,4,6,9,13,14,15,17,18}.
```

Each has penalty one, so the literal objective is 9.

## Structural invariants

- The fill and deletion preserve 166 arcs and `q=5`.
- The missing pairs are
  `{0,12}`, `{9,12}`, `{12,14}`, `{12,17}`, `{12,18}`.
- No loop or digon is introduced.
- Vertex 7 increases from outdegree 8 to 9.
- Vertex 12 decreases from outdegree 14 to 13.
- All other outdegrees are unchanged, so the minimum outdegree remains 8.

This exact local improvement does not resolve SSNC.
