# R38 weak-free canonical cage hunt

## Verdict

No decisive weak-free dead-end cage was found in the bounded balanced-deletion
family.  The exact N20 replay confirms the new obstruction to R37:
`pairCount(0,5)=0`, both halves are unreserved, and `sigma({0,5})=1`, while
the production common-blue terminal requires `sigma>=2`.

The 24-vertex search then tested 5,000 deterministic balanced mutations:

- all 600 choices deleting one optional blue edge and one bad atom;
- the first 4,400 choices deleting two optional blue edges and two bad atoms.

Every mutation retained a connected blue graph, all displayed anchored rows,
and nonempty complete shortest-row families.  Every one had exact full-relation
collision defect zero at the displayed tuple under
P1/P3/strict-P4/P5/common-blue.  Since defect is nonnegative, that displayed
tuple is already a proof that the global minimum is zero.  Therefore none can
contain the requested positive-defect weak-free dead end at an exact
defect-minimizing tuple.

Exact result:

```text
variants                         5000
displayed defect-zero            5000
positive exact minima               0
weak-free canonical witnesses       0
verdict            BOUNDED_ZERO_FAILURE
```

This is a bounded family verdict, not a proof of the repaired wall.  In
particular, adding new bad atoms, grafting the N20 weak attachment onto a
collision-loaded core, and later two-lock combinations are outside this
manifest.  R37 dead-end elimination remains invalid.

## Reproduction

```powershell
python tmp/fanout/r36_freepair_proof/verify_counterexample.py
python tmp/fanout/r38_weak_attachment_hunt/balanced_mutation_gate.py --variant-offset 0 --variant-limit 5000 --tuple-bound 250000 --beam-budget 5000
python tmp/fanout/r38_weak_attachment_hunt/verify_manifest.py
python -m py_compile tmp/fanout/r38_weak_attachment_hunt/balanced_mutation_gate.py tmp/fanout/r38_weak_attachment_hunt/verify_manifest.py
```
