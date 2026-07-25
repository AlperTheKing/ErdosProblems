# Order-19 q=5 two-reversal checkpoint surgery

This is a preserved non-certificate checkpoint. It is not an SSNC
counterexample because nine vertices still fail the strict inequality.

## Immutable inputs and raw output

- Source checkpoint:
  `unrestricted19-best-q5-20260721T221907.json`
- Source SHA-256:
  `71E859E5682CE9E83F47B66A48244A7F27B56C6A7D772A8190FDEB63749B515A`
- Canonical raw candidate:
  `unrestricted19-q5-two-reversal-objective11.json`
- Raw-candidate SHA-256:
  `8E88AA52260A97DA63B7BBC32795CBC3436DC306DE4CA522C00A4D47BA3BE996`

The two legal reversals, in order, are:

1. replace `15 -> 8` by `8 -> 15`;
2. replace `1 -> 3` by `3 -> 1`.

Both edited unordered pairs were oriented in the source. Thus neither reversal
changes the missing-pair set.

Notation below is `A=N+(v)`, `B=N2+(v)`, `W=V-(A union B union {v})`, and
`p=max(0,|B|-|A|+1)`.

## Reversal 1: 15 -> 8 becomes 8 -> 15

The complete set of changed rows is `{3,8,15}`.

### Vertex 3

- Before: `A={5,6,8,11,13,16,17,18}`, `B={0,1,2,4,7,9,10,14}`,
  `W={12,15}`, `(|A|,|B|,p)=(8,8,1)`.
- After: `A={5,6,8,11,13,16,17,18}`,
  `B={0,1,2,4,7,9,10,14,15}`, `W={12}`,
  `(|A|,|B|,p)=(8,9,2)`.

### Vertex 8

- Before: `A={0,1,2,4,7,9,10,14}`,
  `B={3,5,6,11,13,15,16,17,18}`, `W={12}`,
  `(|A|,|B|,p)=(8,9,2)`.
- After: `A={0,1,2,4,7,9,10,14,15}`,
  `B={3,5,6,11,13,16,17,18}`, `W={12}`,
  `(|A|,|B|,p)=(9,8,0)`.

### Vertex 15

- Before: `A={3,5,6,8,11,13,16,17,18}`,
  `B={0,1,2,4,7,9,10,14}`, `W={12}`,
  `(|A|,|B|,p)=(9,8,0)`.
- After: `A={3,5,6,11,13,16,17,18}`,
  `B={1,2,4,7,8,9,10,14}`, `W={0,12}`,
  `(|A|,|B|,p)=(8,8,1)`.

All other rows have identical `A`, `B`, and `W` before and after reversal 1.
The total literal objective remains 13.

## Reversal 2: 1 -> 3 becomes 3 -> 1

The complete set of changed rows, relative to the result of reversal 1, is
`{1,3,13}`.

### Vertex 1

- Before: `A={0,2,3,4,7,9,10,14,15}`,
  `B={5,6,8,11,13,16,17,18}`, `W={12}`,
  `(|A|,|B|,p)=(9,8,0)`.
- After: `A={0,2,4,7,9,10,14,15}`,
  `B={3,5,6,11,13,16,17,18}`, `W={8,12}`,
  `(|A|,|B|,p)=(8,8,1)`.

### Vertex 3

- Before: `A={5,6,8,11,13,16,17,18}`,
  `B={0,1,2,4,7,9,10,14,15}`, `W={12}`,
  `(|A|,|B|,p)=(8,9,2)`.
- After: `A={1,5,6,8,11,13,16,17,18}`,
  `B={0,2,4,7,9,10,14,15}`, `W={12}`,
  `(|A|,|B|,p)=(9,8,0)`.

### Vertex 13

- Before: `A={1,5,6,8,11,16,17,18}`,
  `B={0,2,3,4,7,9,10,14,15}`, `W={12}`,
  `(|A|,|B|,p)=(8,9,2)`.
- After: `A={1,5,6,8,11,16,17,18}`,
  `B={0,2,4,7,9,10,14,15}`, `W={3,12}`,
  `(|A|,|B|,p)=(8,8,1)`.

All other rows have identical `A`, `B`, and `W` before and after reversal 2.
The literal objective changes from 13 to 11.

## Full final raw-adjacency replay

The replay used the literal definition of the new second out-neighborhood:
`w` is included exactly when `w != v`, `v -> w` is absent, and some `u`
satisfies `v -> u -> w`. The objective is the sum of
`max(0,|N2+(v)|-|N+(v)|+1)`.

| v | |N+| | |N2+| | penalty | unreachable W |
|---:|---:|---:|---:|:---|
| 0 | 9 | 8 | 0 | `{12}` |
| 1 | 8 | 8 | 1 | `{8,12}` |
| 2 | 8 | 8 | 1 | `{7,12}` |
| 3 | 9 | 8 | 0 | `{12}` |
| 4 | 8 | 8 | 1 | `{10,12}` |
| 5 | 9 | 8 | 0 | `{12}` |
| 6 | 8 | 8 | 1 | `{12,16}` |
| 7 | 9 | 8 | 0 | `{12}` |
| 8 | 9 | 8 | 0 | `{12}` |
| 9 | 8 | 9 | 2 | `{12}` |
| 10 | 9 | 8 | 0 | `{12}` |
| 11 | 8 | 9 | 2 | `{12}` |
| 12 | 13 | 5 | 0 | `{}` |
| 13 | 8 | 8 | 1 | `{3,12}` |
| 14 | 9 | 8 | 0 | `{12}` |
| 15 | 8 | 8 | 1 | `{0,12}` |
| 16 | 9 | 8 | 0 | `{12}` |
| 17 | 8 | 8 | 1 | `{5,12}` |
| 18 | 9 | 8 | 0 | `{12}` |

The remaining failing vertices are exactly
`{1,2,4,6,9,11,13,15,17}`. Their penalties sum to
`1+1+1+1+2+2+1+1+1=11`.

## Structural audit

- `n=19`.
- Every row is strictly increasing and has no duplicate.
- There are no loops and no digons.
- The raw adjacency has 166 arcs.
- Exactly five of the 171 unordered pairs are missing:
  `{0,12}`, `{9,12}`, `{12,14}`, `{12,17}`, `{12,18}`.
- Hence `q=5` independently from checkpoint metadata.
- The minimum outdegree is exactly 8.
- The literal objective is exactly 11.

This checkpoint is preserved only as an exact surgery frontier. No
counterexample or theorem claim follows from it.
