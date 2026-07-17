# C70: arbitrary-shore red team for C66-RANK

## Verdict

No falsifier was found at the exact cutoffs

```text
54, 74, 100, 200, 362, 500, 1000, 2000.
```

For every cutoff `X` and every seed-chain root prefix `R`, CP-SAT minimized

```text
# nonhard exiting chains with root <= R
  - # hard truncated chains with root <= R
```

over **all** Boolean source shores containing every splitless hole and closed
under every infinite unary generated-factor selector. Every optimum was
nonnegative. The calculation therefore tests the missing arbitrary-shore
extension, not merely the canonical residual shore selected in C66.

The minimum objective values at the eight cutoffs were

```text
0, 0, 1, 0, 0, 1, 1, 0.
```

At `X=74`, the tight shore has hard truncated roots `{54,74}` and nonhard
exiting roots `{6,18}`. This is the genuine cross-component compensation from
C62. At `X=200`, a tight shore has hard roots
`{54,74,114,144,174,186}` and exit roots `{6,18,20,38,48,66}`.

Each returned assignment is independently replayed with Python integers:
splitless containment, every unary implication, seed-chain prefix structure,
and the objective identity are asserted under `python -O`.

This is finite evidence only. It does not prove C66-RANK or the C60 arithmetic
cut inequality.

## Reproduction

```powershell
python -O problems/424/fanout/wave5/C70_arbitrary_shore_rank.py
```

