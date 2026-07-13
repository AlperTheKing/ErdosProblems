Role: exact four-pattern transfer gate.

Read `../COMMON.md`. Reconstruct the R29 all-anchor tuple and implement, from the
definitions/specs actually used in R19-R23 gates, the full staged transfer relation:
same-first/same-owner, commonBad, rowCompanion, and outside-component attachment.
For hub shore `{0,1,2}`, report demand and cumulative unique reachable source slots
after each class, with overlaps and reservations handled exactly. Verify every arc's
structural predicate and switch-loss predicate. Emit `verify.py`, `RESULT.json`,
`REPORT.md`, and hashes. If one class is prose-only or lacks an operational predicate,
say UNDEFINED rather than inventing it.

