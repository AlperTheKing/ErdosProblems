# Literal-objective versus smooth-energy divergence at the q=5 frontier

## Scope

This is a heuristic audit, not an SSNC result and not a defect in the exact hit
predicate. The running engine's smooth energy is zero exactly at a literal hit,
but it ranks preserved best checkpoints only by smooth energy.

## Frozen comparison

Source checkpoint:

- file: `unrestricted19-best-q5-20260721T221907.json`
- SHA-256: `71E859E5682CE9E83F47B66A48244A7F27B56C6A7D772A8190FDEB63749B515A`
- literal objective: 13
- failing vertices: 9
- smooth witness energy: 14

Two-reversal checkpoint:

- file: `unrestricted19-q5-two-reversal-objective11.json`
- SHA-256: `8E88AA52260A97DA63B7BBC32795CBC3436DC306DE4CA522C00A4D47BA3BE996`
- edits: `15->8` becomes `8->15`, then `1->3` becomes `3->1`
- literal objective: 11
- failing vertices: 9
- smooth witness energy: 16

Both the independent scalar verifier and the independent C++ bitset verifier
returned `VALID_GRAPH_NOT_COUNTEREXAMPLE` with the same failing set
`{1,2,4,6,9,11,13,15,17}`.

## Exact energy replay

For each vertex of outdegree `d`, the native score sorts the two-step witness
multiplicities of all non-direct targets and sums the smallest
`max(0,19-2d)` entries. Replaying that definition row by row gives total 14 on
the frozen source and total 16 on the two-reversal graph. Replaying the literal
penalty `max(0,d2-d+1)` gives 13 and 11 respectively.

The native best-checkpoint comparator in `unrestricted19_stochastic.cpp` lines
797-815 accepts a new global best only when smooth energy strictly decreases.
Therefore the exact literal improvement above is intentionally not retained as
a best checkpoint. This does not invalidate the active search or its zero-score
contract, but it is a concrete heuristic blind spot to address only after the
frozen eight-hour run reaches its registered exit.
