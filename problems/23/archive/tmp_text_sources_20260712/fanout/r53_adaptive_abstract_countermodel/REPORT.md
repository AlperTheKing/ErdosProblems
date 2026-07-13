# R53 adaptive edge-capacity abstract rotor audit

## Verdict

Adaptive reservation kills the particular two-obligation fixed-reservation
rotor in R53, but it does **not** eliminate positive-defect neutral rotors at
the abstract soft-flow/ledger level.

Take two states `A,B`.  In each state use two collision debits and therefore
four paired half-obligations

```text
d0h0, d0h1, d1h0, d1h1.
```

The state has one active undirected edge and its four physical half keys

```text
(x,y,0), (x,y,1), (y,x,0), (y,x,1).
```

Every obligation is eligible for every key.  Each key has capacity one and
the common active-edge node has aggregate capacity two, exactly as in R53.
Thus the maximum flow has value two and defect two.  State `B` has a disjoint
copy of the four keys and the same four persistent obligations.  Both states
are global minimizers in this two-state universe.

For either transition there is no same-key carry.  The exact ledger values are

```text
born = 0,
brokenLive = 2,
deadUnmatched = 0,
reoptimizedGain = 2.
```

Hence

```text
defect(new)-defect(old)
  = born + brokenLive - deadUnmatched - reoptimizedGain
  = 0.
```

The reverse transition is identical, so this is a neutral positive-defect
two-cycle under adaptive edge capacity.

## Scope

This is not asserted graph-realizable and does not refute
`canonicalSoftEdgeCapFeasibleTuple_exists`.  It proves the narrower point that
adaptive capacity alone does not make the rotor program void.  Any closure
still needs a graph-derived exposure theorem coupling row changes to newly
available keys; fixed-tuple flow integrality plus the defect ledger is
insufficient.

## Replay

```powershell
python tmp/fanout/r53_adaptive_abstract_countermodel/check.py
```

Expected first line:

```text
PASS_ADAPTIVE_ABSTRACT_ROTOR
```
