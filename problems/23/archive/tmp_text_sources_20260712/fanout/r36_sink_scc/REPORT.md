# R36 sink-neutral attachment SCC

## Verdict

No proof of `realSinkNeutralAttachmentClass_hasAugment` was obtained, and the
gate found no real counterexample.  It did find an exact **abstract**
positive-defect sink SCC after retaining every R37 state field: row tuple,
optimal coherent matching, full occurrence/copy/half/component obligation,
and unmatched-root cursor.

Therefore `activeOwner_commonBlue_or_twoEdgeDetour` and
`attachmentStep_total` do not by themselves prove the final theorem.  The
remaining input must be a genuinely global real-graph expansion statement.
The certificate is not a counterexample to the theorem with its `ActiveOwner`
and production source-realization hypotheses.

## R37 alignment

The gate implements the finite object specified in
`WALL_ATTACK_R37_GPTPRO56.md`:

- vertices are defect-minimal row tuples equipped with an optimal coherent
  matching and an unmatched full obligation cursor;
- neutral edges are equal-defect two-edge detours with transported optimal
  matching cursors;
- an augmentation requires a larger coherent matching;
- a leaving trade must be an explicit edge to a state outside the SCC;
- sinkness is checked in the complete declared neutral graph.

R37 supplies no Lean or Python definitions of
`CheckedSinkNeutralAttachmentClass` or `CheckedCoherentAugmentation`; its
section-11 prose specification is therefore the exact available interface.

## Exact sink SCC

Use the anchored complete row family

```text
Q0 = (0,1,2,3,4)
Q1 = (0,1,5,3,4).
```

The probe pair is `(1,3)`, at position separation two.  The forward probe
replaces middle vertex `2` by owner `5`; the reverse probe replaces `5` by
owner `2`.  Thus `attachmentStep_total` returns a detour in both states.

Four additional singleton row families are fixed in both states:

```text
(6,5,1,9,10), (11,5,1,14,15),
(16,2,1,19,20), (21,2,1,24,25).
```

All five atom endpoint pairs are distinct and anchored.  The gate generates
the complete positive-occurrence obligations for active owners `2,5` directly
from the database-ordered selected atoms.  It checks
`occurrence=copy+1` and that `producerAtom` is exactly the atom at that
occurrence.  Each state has 12 such obligations.

There are 11 distinct physical source halves, each with a different base,
eligible for every obligation.  Base/component coherence is automatic because
all obligations have component 7 and no base repeats.  Every cardinality
`0..11` is attained by restriction of the displayed injection; cardinality 12
is impossible with 11 physical keys.  Thus the exact optimum is 11 and the
exact defect is 1.

The corrected state graph is

```text
X0 = (tuple Q0, lex-first 11-key optimal matching, its 12th root unmatched)
X1 = (tuple Q1, lex-first 11-key optimal matching, its 12th root unmatched)
X0 -> X1 -> X0.
```

The matching and unmatched-root cursors both change on traversal; no cursor
projection creates the cycle.  `{X0,X1}` is one SCC and has no outgoing edge.
All 11 sources are matched at both vertices, so no coherent augmentation
exists.  Both possible row states are internal, so no explicit simultaneous
row trade leaves the SCC.  Tuple `Q0` is the canonical rank-zero start.

This is the exact finite obstruction to the proposed inference

```text
attachmentStep_total + finiteness + full matching cursor
  => every positive-defect sink SCC has an escape.
```

## Real-hypothesis audit

The same two rows are the complete shortest-row database for bad atom `(0,4)`
in the six-vertex graph with blue edges

```text
01, 12, 23, 34, 15, 35
```

and bad edge `04`.  Exact enumeration verifies:

```text
triangle-free = true
blue-connected = true
displayed cut = maximum cut = 6
complete shortest rows = {Q0,Q1}
endpoint anchoring = true
```

But at either tuple every blue edge internal to the selected vertices belongs
to the selected row support.  Hence `activeEdges` is empty and bad endpoints
`0,4` are disconnected in `activeGraph`.  `ActiveOwner` is false, the scoped
collision obligation set is empty, and the real defect is zero.  This kills
the embedding exactly; it is why the certificate above is abstract only.

## Boundary

The exact unresolved real statement is narrower than the local dichotomy:
production `ActiveOwner` must force enough source expansion somewhere around
an entire neutral SCC, not merely one outgoing attachment step at each
cursor.  A proof must couple active-component endpoint containment to source
cardinality across all equal-defect detours.  R37's local proof has no such
cross-state inequality.

## Reproduction

```powershell
python tmp/fanout/r36_sink_scc/check_sink_scc.py
python -m py_compile tmp/fanout/r36_sink_scc/check_sink_scc.py
```

Expected summary:

```text
verdict = EXACT_ABSTRACT_POSITIVE_DEFECT_SINK_SCC
defect = 1
sink = true
realCounterexample = false
canonical payload SHA256 = f9c000befc17000907f0cfbe719e7e77b97234c9485d5dd916c7cf08dceaf54e
```

Files:

- `check_sink_scc.py` SHA256
  `1585B4AB03E1D4CDB44525B94A47281D378EF1F3E457772558A428B5A15E671A`
- `result.json` SHA256
  `4B61EAFD3C9B4FD416F494F4AE8FE636F882343B0A1EC0F51911DE5465DB0B17`
