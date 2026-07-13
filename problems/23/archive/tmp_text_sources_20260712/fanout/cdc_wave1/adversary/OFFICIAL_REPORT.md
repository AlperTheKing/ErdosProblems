# CDC Wave 1 Official Selector Adversary

## Verdict

No real graph-derived counterexample was found under the official
coherence-free six-relation model with unscoped `P4_outsideAttachment`.
All acceptance computations use integers only.

The earlier strict-P4 deficits are a diagnostic scope fork, not
counterexamples to this official selector.  Direct official replay gives:

| Fixture | Row product | Min collision | Flow | Defect |
|---|---:|---:|---:|---:|
| N24 singleton | 1 | 156 | 312/312 | 0 |
| N89 singleton | 1 | 388 | 776/776 | 0 |
| R35 N24 | 91125000000000 | 82 | 164/164 | 0 |

R35's minimum `collisionUnits = 82` is globally
proved by integer CP-SAT (`OPTIMAL`) over row-family radices
`[10, 10, 10, 10, 10, 10, 10, 10, 10, 45, 45, 45]`.  Its first optimum choice
`[0, 6, 8, 5, 7, 3, 9, 2, 4, 36, 40, 44]` passes Hall.

## Bounded Stress

Random connected triangle-free `geng` sample counters:
`{"PASS_SOME_MINIMUM_TUPLE": 91, "PASS_fixedTuple": 91, "allEllFiveGammaMinCuts": 91, "gammaMinCuts": 101, "graphsAvailable": 11479, "graphsSampled": 90, "noConnectedNonbipartiteGammaMinCut": 54, "rowProductsExhausted": 91}`.

C5 blow-up counters:
`{"FAIL_fixedTuple": 19, "PASS_SOME_MINIMUM_TUPLE": 33, "PASS_fixedTuple": 14, "rowProductsExhausted": 33}`.

Fixed-tuple failures, when present, are not promoted to selector failures:
the minimum-collision row product is exhausted (or an exact minimum witness is
found) before classification.  Full graph6 strings, rows, choices, exact Hall
shores, source hashes, and per-case coverage are in `official_coverage.json`.
