# C88: exact backbone of the tight C23 image faces

## Verdict

At each known tight cutoff `54, 74, 186, 362`, every zero-slack optimizer
has the same complete healed/unhealed shell pattern.  The source itself is
far from unique: the number of free source membership variables is
respectively `13, 21, 47, 89`.  Thus a proof cannot assume a canonical
source, but a canonical tight shell skeleton survives this exact gate.

This is a finite structural fact, not a proof of C23 for arbitrary cutoffs.

## Method

For each cutoff, C88 rebuilds the exact Boolean source/image model and first
proves that the maximum image excess is zero.  It then fixes the excess to
zero.  For every source variable, image variable, boundary event, unhealed
hard-root event, and healed nonhard-root event, it separately tests
feasibility with that Boolean fixed to `0` and to `1`.

Every query terminates as `FEASIBLE`, `OPTIMAL`, or `INFEASIBLE`; `UNKNOWN`
is rejected.  Model witnesses are checked by the exact Boolean constraints.

## Backbone counts

| X | free source | free image | free boundary | forced unhealed hard | forced healed nonhard |
|---:|---:|---:|---:|---:|---:|
| 54 | 13 | 0 | 0 | 1 | 1 |
| 74 | 21 | 2 | 2 | 2 | 2 |
| 186 | 47 | 1 | 0 | 6 | 6 |
| 362 | 89 | 4 | 0 | 11 | 11 |

The forced shell sets are:

```text
X=54
  unhealed hard:   54
  healed nonhard:  6

X=74
  unhealed hard:   54,74
  healed nonhard:  6,18

X=186
  unhealed hard:   54,74,114,144,174,186
  healed nonhard:  6,18,20,32,38,66

X=362
  unhealed hard:   54,114,144,174,186,234,252,294,318,354,362
  healed nonhard:  6,18,20,30,32,38,60,66,110,120,126
```

The only free image values are `35,62` at `74`, `116` at `186`, and
`188,224,350,356` at `362`.  None changes the shell balance.

## Consequence for proof design

The tight face is not explained by uniqueness or rigidity of the source.
Any valid induction must quotient out large source freedom and act on shell
events or an equivalent boundary object.  Conversely, the exact data do not
show that shell canonicity persists at all future tight cutoffs.

## Reproduction

```powershell
python -O problems/424/compute/wave5/C88_tight_backbone.py `
  --cutoffs 54 74 186 362 --workers 64 --seconds-per-query 30 `
  --output problems/424/compute/wave5/C88_tight_backbone.json
```

An independent second run is byte-identical.

```text
F9C88B9606EC0C37DC1BBBFA150820491243F5D592FA3D89E248BFCAA3192AD5  C88_tight_backbone.py
B3A128A933463CAFC3B2116AC83587D26BCADF9E41586E0AB9C3154F3CA061B7  C88_tight_backbone.json
B3A128A933463CAFC3B2116AC83587D26BCADF9E41586E0AB9C3154F3CA061B7  C88_tight_backbone_replay.json
```
