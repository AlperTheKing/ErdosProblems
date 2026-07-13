# Corrected R37 weak-free dead-end gate

## Verdict

The production common-blue threshold is `sigma({x,y}) >= 2`, not merely
max-cut nonnegativity. The exact N=20 witness from `r36_freepair_proof` was
replayed: `dB=3`, `dM=2`, `sigma=1`, and the production common-blue terminal
is invalid.

The corrected census regenerated every connected triangle-free graph through
N=12, selected the exact connected Gamma-minimum maximum cut, retained the
all-length-five complete-row cages, and chose the lexicographically first
minimum collision-defect tuple. The source relation used P1/P3/strict-P4/P5,
a subset of the production relation. A checked defect-zero assignment in this
subset proves the production minimum is zero.

All 992,618 eligible canonical states have collision defect zero. Therefore
there is no canonical positive-defect state on which a weak-free outcome can
be a dead end, and no occurrence-level dead-end witness exists in this census.

## Attachment classification

Every canonical attachment probe `(owner, active neighbor, support neighbor)`
was classified exactly:

```text
sigma = 0       55
sigma = 1      174
sigma >= 2    8509
detour         1027
invalid           0
```

Thus 229 genuine weak-free probes occur even though the canonical states have
zero defect. They confirm that the sigma gap is not confined to the N=20
construction. Since no canonical positive-defect state exists through N=12,
the requested fallback checks for another source, detour, or strict trade are
vacuous on this census.

## Scope

This is a zero-failure falsifier manifest, not a proof of the corrected global
dead-end exclusion. The driver contains the positive-defect branch: it counts
other P1/P3/P4/P5 owner arcs, enumerates detours, and tests every one-row strict
defect trade. That branch was not reached by any N<=12 canonical state.

## Replay

```powershell
python tmp/fanout/r36_freepair_proof/verify_counterexample.py
python tmp/fanout/r36_freepair_search/verify_weakfree_manifest.py
python -m py_compile tmp/fanout/r36_freepair_search/r37_weakfree_deadend_gate.py tmp/fanout/r36_freepair_search/verify_weakfree_manifest.py
```
