# Lead C referee: R29 scoped invariance and production FullBank audit

## Verdict

The R29 all-anchor tuple is an exact, selector-uniform falsifier of the
auxiliary `ActiveScoped` source relation:

```text
hub-shore demand = 19953
ActiveScoped reach = 19925
defect = 28.
```

It is **not** a falsifier of the intended production transfer relation.
`Gamma/CheckedC5BaseTransfer.lean` contains a concrete corrected
common-blue terminal omitted by the auxiliary relation and by the stale
common-bad prose model. Replaying its literal predicate

```text
blue(x,owner) and blue(y,owner) and dM({x,y}) + 2 <= dB({x,y})
```

on the all-anchor R29 cage gives 216 new, nonoverlapping `FreeHalf` keys.
Thus the hub neighborhood becomes

```text
19925 + 216 = 20141 >= 19953
```

with exact margin 188.

More strongly, `r29_extended_owner_matching.json` is a complete injection of
all 23,115 all-anchor demands into 23,115 distinct source keys using only:

```text
sameFirst       19595
rowCompanion     3308
checkedC5Base     212
```

The separate verifier replays every FreeHalf, reservation, owner eligibility,
switch-surplus inequality, and source uniqueness check.

This does **not** finish the FullBank theorem. There is no compiled
`CheckedTransferMatching`, `CheckedPruneStep`, or
`Ell5FullBankRelaxedCover_exists` definition/provider in the current tree.
The checked common-blue terminal repairs R29, but the graph-to-
`FullBankGlobalPackage` construction remains open.

## Independent reconstruction

`lead/r29_referee_gate.py` contains a standalone constructor; it imports no
Lead B script, JSON, or module. Its canonical graph-and-baseline-row hash is

```text
fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f
```

The exact structural output is:

```text
N = 2943
|B| = 7039
|M| = 1383
|E| = 8422
Gamma = 1383*25 = 34575
row families = 707 of size 1, 676 of size 680
total shortest rows = 460387
selector space = 680^676.
```

The script checks blue connectivity, the displayed cut, triangle-freeness,
blue distance exactly four for all 1,383 bad edges, and every one of the
459,680 selector rows.

### Exact maximum-cut certificate

The edge set is partitioned into five disjoint classes:

| class | edges | upper bound | displayed cut |
|---|---:|---:|---:|
| locked double-star | 4786 | 4110 | 4110 |
| selector C5s | 3380 | 2704 | 2704 |
| three seed C5s | 15 | 12 | 12 |
| 28/27 circuit | 235 | 207 | 207 |
| cable | 6 | 6 | 6 |

The locked class is exhausted by the `16*27*27 = 11664` core/count quotient.
The selector and seed classes have respectively 676 and 3 edge-disjoint odd
cycles. The circuit has 28 edge-disjoint private 7-cycles, forcing at least 28
uncut edges. Summing the five exact upper bounds gives 7,039, attained by the
displayed cut. Triangle-freeness plus cut parity gives ell at least five for
every bad edge, while the displayed cut has ell exactly five, proving the
Gamma minimum.

## Selector-universe invariant

This is a universal finite certificate, not a random sample.

The complete shortest-row enumeration proves simultaneously:

1. Every one of the 459,680 selector rows avoids vertices `0..54`.
2. Every selector support avoids the six cable edges and the rigid circuit
   active path.
3. The 676 rigid traffic rows therefore fix every pair count involving hubs
   `0,1,2` and fix their companion set to `0..54`.
4. Rigid traffic support consumes every non-cable blue edge incident with a
   hub. The three invariant active hub edges are
   `(0,55)`, `(1,2929)`, `(2,2930)`.
5. Cable plus rigid circuit active edges put all hubs in an active component
   containing the fixed bad edge `(2762,2766)` for every selector tuple.

For each hub, the fixed collision demand is

```text
2 * (3*(676-1) + 26*(26-1) + 26*(26-1)) = 6650.
```

Its selected load is `5*676 = 3380 > 2943` and its active degree is one, so
HitNeed is one. Hence each hub owns 6,651 demands and the shore owns 19,953.

The exact source quotient is:

```text
sameFirst:
  3 * (2*(2943-55) - 1 reservation) = 17325

rowCompanion:
  2 * (26*25 + 26*25) = 2600

total = 19925.
```

These formulas use only the five fixed structural facts above, so they hold
for all `680^676` selector choices. The gate also checks several extreme
tuples, but those samples are not used to justify the universal claim.

## Production source audit

| class | all-anchor hub effect | selector behavior | referee result |
|---|---:|---|---|
| `sameFirst` | 17,325 | invariant | exact |
| stale `commonBad` | 0 | invariant; hubs have no bad neighbors | exact |
| `rowCompanion` | 2,600 | invariant at this shore | exact |
| `outsideAttachment` | 0 | variable; lex-all-local has 60 keys | exact samples show variation |
| corrected common-blue `CheckedC5BaseTransfer` | +216 new | invariant at this shore | exact, absorbs defect |
| Door | not a CollisionHalf source | boundary set varies | separate off-support load class |
| vertexSlack | zero at all three hubs | endpoint-local | cannot pay collision defect |
| prune | not instantiated | unknown | unnecessary for this R29 injection |

The corrected common-blue count decomposes as follows:

```text
owner 0: 4 valid ordered terminals, 8 halves, 4 new halves
owner 1: 704 valid ordered terminals, 1408 halves, 106 new halves
owner 2: 704 valid ordered terminals, 1408 halves, 106 new halves

unique halves = 2824
overlap with ActiveScoped = 2608
new halves = 216.
```

Every selector row meets the common-blue source-vertex pool in at most one
vertex, so freeness of all these keys is selector-invariant. A common-blue
source pair is nonadjacent by triangle-freeness, hence no half-zero key is
removed by `ScopedReserved`.

The full injection uses only 212 of the 216 new keys because four keys valid
for owner 0 are already consumed as owner-55 `sameFirst` keys. The remaining
source allocation is:

```text
hubs:
  owner 0 = 5775 sameFirst + 876 rowCompanion
  owner 1 = 5775 sameFirst + 770 rowCompanion + 106 checkedC5Base
  owner 2 = 5775 sameFirst + 770 rowCompanion + 106 checkedC5Base

owner 55:
  1812 sameFirst + 892 rowCompanion

13 positive circuit owners:
  all 488 demands use owner-private sameFirst keys.
```

### Door and vertexSlack are not additive to 19,925

The compiled block constructors route off-support blue-edge load. They do not
add `FreeHalf` neighbors to the collision matching. Under the diagnostic
choice `C = selectedVertices` and `F = selectedSupport`, the all-anchor tuple
has 2,760 boundary Door edges, 18 positive internal block edges, and three
positive internal hub edges. The baseline tuple instead has 56 boundary edges
and 4,074 positive internal block edges, demonstrating selector dependence.

At each hub, `max(0,N-selectedLoad)=max(0,2943-3380)=0`; vertexSlack is exactly
zero. The three endpoint obligations already appear as the three HitNeed
units. Neither Door nor vertexSlack can be reclassified as collision sources.

## Interface audit

`lead/interface_audit.py` checks the current production tree exactly:

- the four `CapKind`s are `door`, `vertexSlack`, `c5Base`, `prune`;
- `FullBankGlobalPackage.Checked` has spend, uniqueness, ownership, and reserve
  fields, but no wall-port incidence field;
- `TypedFullBankSources.lean` explicitly leaves the Sink adapter separate;
- `FullBankPortSinks.lean` explicitly leaves legal edge-to-token incidence
  absent;
- `AggregateLedgerNoIncidenceCounterexample.lean` compiles the logical
  separation theorem `checkedAggregatePackage_and_noHalfLayerRouting`;
- no definition of `CheckedTransferMatching`, `CheckedPruneStep`, or
  `Ell5FullBankRelaxedCover_exists` exists in the production Lean tree.

Therefore the exact conclusion is:

> R29's known 28-unit shore is absorbed by an existing graph-checkable
> common-blue terminal, so R29 is not the decisive FullBank falsifier. The
> complete real FullBank provider is nevertheless still missing.

## Child fanout reconciliation

Nine disjoint child lanes were launched; all exited with code zero. The lead
accepted only claims it independently replayed.

- Child 02 independently derived demand 19,953 and separated its symbolic
  proof from sample checks.
- Child 03 derived the generic Boolean reach quotient and correctly warned
  that generic definitions alone do not imply invariance; the lead's complete
  R29 row enumeration supplies the missing instance-specific facts.
- Child 07 independently obtained zero hub vertexSlack.
- Child 09 independently isolated the missing typed incidence adapter.
- Child 01 correctly noted that the short R29 prose archive alone omits enough
  formulas for a canonical constructor.
- Other child reports were not used as acceptance evidence where output paths
  were misplaced or no lane-local report was emitted.

The common-blue repair was found and verified by the lead after the child
fanout; no child claim was used to infer its 216-key count.

## Exact replay

From `E:\Projects\ErdosProblems`:

```powershell
python tmp\fanout\r29_fullbank_referee\lead\r29_referee_gate.py
python tmp\fanout\r29_fullbank_referee\lead\verify_extended_matching.py
python tmp\fanout\r29_fullbank_referee\lead\interface_audit.py

python tmp\fanout\r29_fullbank_referee\child_02\gate.py
python tmp\fanout\r29_fullbank_referee\child_03\reach_quotient.py
python tmp\fanout\r29_fullbank_referee\child_07\audit_vertex_slack.py
python tmp\fanout\r29_fullbank_referee\child_09\quotient_gate.py
```

The lead verifier returns:

```text
PASS assignments=23115
relations={checkedC5Base:212,rowCompanion:3308,sameFirst:19595}
canonical certificate content SHA256=
c76ec29432f68d1ec2d8dd55a5cef0dcb3787630442f03f3868ca151144cbace
```

File hashes are recorded in `SHA256SUMS.txt`.

