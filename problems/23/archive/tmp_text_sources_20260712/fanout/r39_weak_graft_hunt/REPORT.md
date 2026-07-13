# R39 weak-graft adversarial hunt

## Verdict

No positive exact minimum was found.  The distinct family adds triangle-safe,
same-shore distance-four bad atoms to the N20 sigma=1 weak-attachment cage.
The blue graph is fixed, every added atom uses its complete shortest-row
family, and the full P1/P3/P4/P5/common-blue collision Hall defect is minimized
over every row tuple.

There are 30 candidate atoms.  All subsets of one through five atoms were
tested.  Exact maximum-cut filtering was performed by enumerating all `2^19`
cuts once and retaining a subset `A` exactly when

```text
baseCut(C) + |A intersect delta(C)| <= 20
```

for every cut `C`.  Of 174,436 subsets, 174,433 fail this condition.  Exactly
three are triangle-free maximum-cut cages:

```text
added atom   complete family sizes   exact minimum
(2,15)       (2,2,1,1,1)             0
(3,10)       (2,2,1,1,1)             0
(4,7)        (2,2,1,1,1)             0
```

For each survivor the displayed cut has 20 blue edges and exhaustive Gray-code
enumeration proves `MaxCut=20`.  The manifest gives an explicit defect-zero row
tuple, proving the tuple minimum is exactly zero by nonnegativity.  In each
zero tuple the added row disconnects the selected off-support active path, so
the active vertex set is empty.  The raw pair `(0,5)` still has `pairCount=0`
and `(dB,dM,sigma)=(3,2,1)`, but it is no longer a trace exit because active
scope is vacuous.

Thus bad-atom grafting on the fixed N20 blue graph cannot produce the requested
positive weak-free cage through five additions.  The exact obstruction is
stronger than a newly created detour row: max-cut legality leaves only three
single-atom grafts, and every one admits scope vacuation at defect zero.

## Reproduction

```powershell
python tmp/fanout/r39_weak_graft_hunt/search_bad_atom_grafts.py --max-added 5 --tuple-bound 200000
python tmp/fanout/r39_weak_graft_hunt/verify_manifest.py
python -m py_compile tmp/fanout/r39_weak_graft_hunt/search_bad_atom_grafts.py tmp/fanout/r39_weak_graft_hunt/verify_manifest.py
```
