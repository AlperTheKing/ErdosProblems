# R37 sink neutral SCC: exact saturation ledger and obstruction

## Verdict

Structured source saturation by itself does not prove
`realSinkNeutralAttachmentClass_hasAugment`, even when physical two-half bases
and `BaseKeyComponentCoherent` are enforced exactly.  It yields an exact
component-partition identity, but that identity is compatible with positive
defect.  The final lemma therefore still needs a graph-geometric **distinct
base expansion** statement somewhere inside the sink SCC.

This is not a counterexample to the final real-graph lemma.  It is a
counterexample to the proposed saturation-only proof step.

## Exact component ledger

Fix one defect-minimal tuple `omega`, an optimal coherent partial matching
`M`, one unmatched root `o0`, and its ordinary occurrence-level alternating
core.  Write `O` for reached obligations and `S` for reached physical half
keys.  Maximality makes every key in `S` matched.  Alternating-tree
normalization gives a bijection

```text
S  <->  O \ {o0}.
```

For every used physical base `b`, coherence gives a unique label `lambda(b)`:
all obligations assigned to `(b,0)` or `(b,1)` have that component.  Partition
`S` by this base label and `O` by obligation component.  The matching
bijection restricts componentwise, so for every component `c`,

```text
|O_c| = |S_c| + 1[c = component(o0)].                 (1)
```

Let `B_c` be distinct attachment-generated common-blue bases with label `c`
for which both unreserved halves are reached.  Sink saturation puts both
halves in `S_c`; therefore

```text
2 |B_c| <= |S_c| = |O_c| - 1[c = component(o0)].      (2)
```

Thus saturation supplies an upper bound on distinct reached bases.  It does
not supply the reverse strict inequality needed for an augmentation.
Component conflicts do not create extra capacity: a base labelled `c` has
zero usable capacity for another component, exactly as required by
`BaseKeyComponentCoherent`.

## Minimal exact countermodels

The checker exhausts every injective partial assignment in two one-state
models.  Both have one physical base `b`, its honest keys `(b,0),(b,1)`, three
obligations, and complete eligibility to both halves.

1. `single_component`: all three obligations have component `A`.  Two are
   matched, both halves are saturated, coherence holds, and defect is one.
2. `component_conflict`: `x1,x2` have component `A` and `y` has component
   `B`.  The optimum assigns both halves to `x1,x2`; `y` is unmatched and the
   base label is `A`.  Both halves are saturated, coherence holds, and defect
   is one.  Following the conflict cannot change the base label.

Give the sole row state `omega` a neutral self-loop.  Its singleton SCC is a
sink, every physical half is saturated, and no total coherent assignment
exists.  This realizes the matching/coherence/local-probe logic of a closed
neutral class, but deliberately does not realize triangle-free shortest-row
geometry, maximum-cut lock equalities, or the complete six graph relations.

## Exact missing graph statement

A sufficient graph lemma is now numerical and component-correct.  In every
positive-defect sink neutral SCC, there must exist a state, an optimal
matching, its unit-defect alternating core, and a component `c` such that the
attachment probes generate distinct label-compatible two-half bases satisfying

```text
2 |B_c| > |O_c| - 1[c = component(o0)].               (3)
```

Equation (3) contradicts (2), so one generated half is unmatched and gives
the checked coherent augmentation.  An equivalent formulation may count
other reached source families too, but it must count **distinct physical
bases at one state**.  Counts accumulated over different states of the SCC
are invalid because neutral states may reuse the same two half keys with
different optimal matchings.

The known R35 anchored source-floor countermodel rules out deriving (3) from
endpoint diversity or static row incidence alone.  What remains is precisely
a sink-closure/max-cut-lock theorem: repeated reuse of too few bases must
force either a new label-compatible base or a strict-defect detour.  R37
supplies the local probe, but not this global distinctness assertion.

## Reproduction

```powershell
python tmp/fanout/r37_sink_saturation/check_saturation_obstruction.py
```

The script uses only finite enumeration and writes `result.json` with a
canonical payload hash.
