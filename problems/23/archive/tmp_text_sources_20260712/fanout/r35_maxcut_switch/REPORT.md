# CANONICAL COVERAGE-OR-TRADE: exact refutation of the lex-rotation mechanism

## Verdict

The proposed statement is **false at the stated interface** if its trade
branch is supposed to follow from orienting a reversible vertex switch or row
rotation.  A neutral exchange orbit has a least tuple-rank element, and at
that element every nontrivial orientation is rank-increasing.  Thus
max-cut-valid reversible geometry does not imply an explicit simultaneous
lex trade.

This does **not** refute the stronger, subsequently isolated statement
`realSinkNeutralAttachmentClass_hasAugment`.  That statement adds the missing
claim that a positive-defect sink neutral class has an augmentation somewhere
inside the whole class.  The present result says that lexicographic
orientation cannot prove it.

## Exact three-state countermodel

Take three row coordinates, each with three choices.  Use the injective
mixed-radix rank

```text
rank(r0,r1,r2) = r0 + 3 r1 + 9 r2.
```

Let a reversible neutral row rotation have the orbit

```text
omega0 = (0,0,0),
omega+ = (1,1,1),
omega- = (2,2,2),
```

where the two orientations from `omega0` are `omega+` and `omega-`.  Suppose
the transported coherent matching has the same unmatched count at all three
states.  This is exactly the neutral closed-rotation case left by R34.

Integer evaluation gives

```text
rank(omega0) = 0,
rank(omega+) = 13,
rank(omega-) = 26.
```

Hence neither orientation is a `CheckedCollisionLexTrade` from `omega0`:
both violate the required field

```text
rowCode newState < rowCode oldState.
```

The defect branch also does not fire because the rotation was assumed
neutral.  Reversibility merely says that the inverse move decreases rank
when started at `omega+` or `omega-`; it supplies no decreasing move at the
orbit minimum.  The same argument works for every finite exchange orbit and
every injective well-order: choose the least orbit element.

## Formal consequence of the compiled modules

`CheckedCollisionLexTrade.false_of_lexMinimal` proves that an explicit lex
trade at a lex-minimal state is impossible.  The newer
`CanonicalCollisionLexSelection.no_checked_trade_at_canonical` specializes
this to the selected canonical state.  Therefore a proof by contradiction
must construct a trade carrying an independently checked strict rank
decrease; no theorem can infer that field from reversibility, cycle closure,
or the existence of two orientations.

Likewise, `collisionDefect` is the minimum unmatched count over coherent
partial matchings.  Once the trace starts from an optimal matching, an
ordinary matching augmentation is impossible unless graph geometry first
produces a genuinely new realized source or a state change with smaller true
defect.  A closed matching rotation alone does neither.

## Real max-cut geometry check

The 24-vertex fixture from `r35_endpoint_diversity` verifies all of the
following with integer arithmetic:

```text
vertices = 24, edges = 82, triangles = 0,
maximum cut = 70,
12 bad edges, all blue distance 4,
Gamma = 300,
complete anchored shortest-row families of sizes 10 (nine atoms)
and 45 (three atoms).
```

At the displayed anchored state, owner `7` has 72 active collision halves
and only 48 no-common-blue P1/P3 source halves; strict P4 and P5 are empty.
Thus the exact central Hall defect is 24.  The first selected main row is row
index 0,

```text
(0,6,7,8,3),
```

while the explicit alternative

```text
(0,9,12,8,3)
```

is row index 2.  The change lowers the owner's raw obligation count from 72
to 62 but **increases** that row coordinate.  This is a concrete instance of
the distinction the abstract countermodel exposes: useful graph switches and
lex-decreasing switches are different notions.

There is also a solver-independent positive raw-collision lower bound across
all row choices of this fixture.  Each of the nine main rows contains vertex
`8`, and its preceding vertex is one of only `{7,12,13}`.  If the three
multiplicities are `n_7,n_12,n_13`, then

```text
sum_z max(n_z-1,0) >= 9-3 = 6,
```

so every tuple has at least 12 raw collision halves.  The accompanying script
checks these row-family facts exactly.  Its MILP additionally finds raw
minimum 46, but that numerical optimum is diagnostic only and is not used as
an exact certificate.

## Why the graph adapter cannot state the requested theorem

`CollisionDefectGraphAdapter.NoCommonBlueSourceRelations` contains four
caller-supplied propositions `p1`, `p3`, `strictP4`, and `p5`.  The adapter
does not derive them from `TriangleFree`, `IsMaxCut`, or
`CompleteShortestRowDB`.  It also defines no closed-trace, vertex-switch, row
rotation, or augmentation object.  Consequently the requested implication is
not presently expressible, much less provable, from that module's hypotheses.

For example, setting all four caller-supplied relations to `False` is legal at
the adapter interface even on the verified 24-vertex graph.  This observation
is an interface countermodel, not a counterexample to the intended production
relations.  Any exact graph theorem must first replace those arbitrary fields
by checked graph-derived predicates and introduce the corrected
occurrence-level trace surface from R34.

## Correct replacement

The lex branch is sound only in the following explicit form:

```text
strict defect decrease
OR checked coherent augmentation using a newly realized source
OR checked lex trade carrying tupleRank(new) < tupleRank(old)
OR neutral transition retained inside the state graph.
```

Neutral transitions must be closed under reachability and condensed into sink
SCCs.  The remaining exact statement is therefore not
CANONICAL COVERAGE-OR-TRADE by row orientation, but:

```text
realSinkNeutralAttachmentClass_hasAugment:
every positive-defect sink SCC of defect-minimal row states and optimal
coherent matchings contains a checked coherent augmentation.
```

That is the place where max-cut and triangle-free shortest-row geometry still
has mathematical work to do.  Static source counts and lex orientation do not
settle it.

## Reproduction

```powershell
python tmp/fanout/r35_endpoint_diversity/check_real_endpoint_floor_obstruction.py
python tmp/fanout/r35_maxcut_switch/check_min_pair_collision.py
```

The second script's SHA-256 is
`6958B214DC50AD0A881BE95366199027BBA70EAA61079A3A17576C91C2400631`.
