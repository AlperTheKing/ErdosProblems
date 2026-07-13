# R58 positive-defect compiled-interface countermodel

## Verdict

The 16-vertex R57 graph with nine checked copies of its sole `s-t` bad atom is
an exact countermodel to the compiled-interface bridge.  The selected tuple
uses four left rows and five right rows.  It is lex-minimal, has positive exact
grouped defect, saturates both first-divergence halves in an optimum, and has a
positive residual unit core.  No graph-only mask pair is four-corner
overweight, and neither class of one-row replacement lowers collision or
defect.

This is not a counterexample to a theorem explicitly assuming
`CompleteShortestRowDB.badKeys_nodup`: all nine listed atoms have the same one
graph bad-edge key.

## One-command replay

From `E:\Projects\ErdosProblems`:

```powershell
python -B tmp/fanout/r58_positive_defect_interface_countermodel/verify.py
```

Default mode rebuilds every check in memory and verifies `result.json` and
`REPORT.md` byte-for-byte.  `--write` is the explicit deterministic refresh
mode and writes only those two files in this directory.

## Exact arithmetic

- Signed cut engine: `fractions.Fraction`; floating point used: `false`.
- Switch masks checked: 65536.
- Row-union mask pairs checked: 65536.
- Four-corner identities checked: 65536.
- Minimum switch loss: 0.
- Minimum four-corner margin: 0.
- All observed Fraction denominators equal one: `true`.

## Full row-tuple census

All `512` choices in `{P,Q}^9` are listed in
`result.json`.

| Quantity | Exact value |
|---|---:|
| Collision minimum | 179 |
| Defect minimum on the collision face | 50 |
| Lex-minimal tuples | 420 |
| Positive lex payloads | 420 |
| Lex tuples with both fork halves saturable | 420 |

Metric histogram: `{"179,106": 18, "179,50": 420, "179,76": 72, "200,50": 2}`.

## Selected state and forced core

- Choice: `[0, 0, 0, 0, 1, 1, 1, 1, 1]`.
- Collision/defect: `(179, 50)`.
- Total demand / maximum flow: `358 / 308`.
- Ordered relation bases: `154`.
- Forced assignment cardinality: `308`.
- Residual root: `[4, 3, 1, 0]`.
- Unit core: `|O_K|=293`, `cap(S_K)=292`.
- Fork halves reached and matched: `true`.
- Successors lie in the core and the residual sink is unreachable:
  `true`.

The core owner set is `['s', 't', 'a1', 'a2', 'a3', 'b1', 'b2']` and satisfies

```text
N*|A| = 112
shoreSelectedLoad(A) + internalActive(A) = 200
2*shoreCollision(A) = 318
p1GroupedCapacity(A) = 142
```

## One-row replacements

- Four `P_to_Q` replacements have metric
  `[179, 50]`.
- Five `Q_to_P` replacements have metric
  `[179, 50]`.
- Every one-coordinate replacement preserves `(collision, defect)`:
  `true`.

## SHA-256

```text
verify.py            8E2306126EC05536B2C1193AB2BCEE7AAD9E6D3FE49B24FDDF8E87CEE62ED9D7
result.json          47E947866132084E6AF7D116F45A74A0F41B26B2A8F67414277E4EB81C421A48
census records       ED4B8E54C6A89D383453605D500E1AB946B86E2D674BB591887FB2A3B5367977
relation             87B6AB18D0C3CD08C8CBD4F5D93EA5F54B03BE4E5B80FF6C7D87204C5FC9B334
forced assignment    88D83DCFA202A2978EA7F50A4A03068E1BB29B434102870D91ECB7F5E1AD87B1
unit core            9B2E9BD93F38535F5AD82752014294B567400CF71FAF9DDC4DE3F18C919B6D80
```
