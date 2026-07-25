# Order-19 q=5 star-breaking objective-10 checkpoint

This is a preserved non-certificate. Both frozen exhaustive verifiers return
`VALID_GRAPH_NOT_COUNTEREXAMPLE`.

## Immutable raw adjacency

- File: `unrestricted19-q5-relocation-objective10.json`
- SHA-256:
  `62241FCC69A6D03DAA32A976ADEFB949DFFAE27DBB95470C4492FE85D88389BB`
- Parent: `unrestricted19-q5-two-reversal-objective11.json`
- Parent SHA-256:
  `8E88AA52260A97DA63B7BBC32795CBC3436DC306DE4CA522C00A4D47BA3BE996`

Applied to the parent, the exact legal edits are:

1. reverse `7 -> 11` to `11 -> 7`;
2. reverse `18 -> 2` to `2 -> 18`;
3. fill missing pair `{0,12}` as `12 -> 0` and delete `14 -> 7`.

Thus the final missing pairs are
`{7,14}, {9,12}, {12,14}, {12,17}, {12,18}`. There are
166 arcs, no loop, no digon, `q=5`, and minimum outdegree 8.

## Frozen dual replay

The frozen scalar-set and C++ bitset verifiers independently replayed the
unchanged raw file. Both returned `VALID_GRAPH_NOT_COUNTEREXAMPLE`, agreed on
every ledger row, and reported literal objective 10 with failing set
`{1,4,6,7,9,13,14,15,17,18}`.

Notation: `d=|N+(v)|`, `s=|N2+(v)|`,
`p=max(0,s-d+1)`, and `W` is the unreachable set. The raw adjacency fixes
`N+(v)`; consequently `N2+(v)=V-({v} union N+(v) union W)` exactly.

| v | d | s | p | W |
|---:|---:|---:|---:|:---|
| 0 | 9 | 8 | 0 | `{12}` |
| 1 | 8 | 8 | 1 | `{8,12}` |
| 2 | 9 | 8 | 0 | `{12}` |
| 3 | 9 | 8 | 0 | `{12}` |
| 4 | 8 | 8 | 1 | `{10,12}` |
| 5 | 9 | 8 | 0 | `{12}` |
| 6 | 8 | 8 | 1 | `{12,16}` |
| 7 | 8 | 8 | 1 | `{12,14}` |
| 8 | 9 | 8 | 0 | `{12}` |
| 9 | 8 | 8 | 1 | `{2,12}` |
| 10 | 9 | 8 | 0 | `{12}` |
| 11 | 9 | 8 | 0 | `{12}` |
| 12 | 14 | 4 | 0 | `{}` |
| 13 | 8 | 8 | 1 | `{3,12}` |
| 14 | 8 | 8 | 1 | `{7,12}` |
| 15 | 8 | 8 | 1 | `{0,12}` |
| 16 | 9 | 8 | 0 | `{12}` |
| 17 | 8 | 8 | 1 | `{5,12}` |
| 18 | 8 | 8 | 1 | `{11,12}` |

The penalties sum to 10. No counterexample or theorem claim follows from this
checkpoint.
