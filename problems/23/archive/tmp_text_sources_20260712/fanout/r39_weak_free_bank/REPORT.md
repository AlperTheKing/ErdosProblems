# R39 weak-free/full-bank audit

## Verdict

**Impossible in the current production interfaces.**  An unreserved free pair
with `sigma = 0` or `sigma = 1` gives two raw `FreeHalf` cells, but it gives no
legal `Door`, `vertexSlack`, `prune`, or `c5Base` bank token.  Its exact
attributable capacity is:

| channel | capacity from one weak free pair |
|---|---:|
| canonical free-half pool | 2 micro-units (one per half) |
| Door | 0 |
| vertexSlack | 0 |
| prune | 0 |
| c5Base | 0 |

The two free units are usable only if a separate production source relation
makes them legal for collision obligations.  They cannot pay retained hit
needs, and in the R36 cage they are not legal for the relevant owner under any
compiled relation.

## Type obstruction

`CheckedFullBankMicroFlow.FullBankMicroFlowData` has two disjoint assignment
maps:

```lean
collisionSource : (Debit x Fin 2) -> FreeHalf
hitBank          : (Hit x Fin 25) -> Term
```

The first spends one raw free unit per collision half.  The second is the only
entry into the bank.  Its term type is classified by `HitBankSource`, whose
constructors are exactly `door`, `vertexSlack`, and `prune`
(`CheckedFullBankMicroFlow.lean`, lines 41-45).  There is no map from
`FreeHalf` to `Term` and no collision-to-bank summand.

The official capacities are (`CheckedFullBankMicroFlow.lean`, lines 124-130):

```text
Door(e)       = 25
vertexSlack(v)= supplied vertexSlackCapQ(v)
prune(r)      = supplied pruneCapQ(r)
```

None is constructed from a free pair.  Moreover the exported production
micro view sets `c5BaseCapQ := 0` definitionally (line 224).  The generic
`CapSource.c5Base` tag in `TypedFullBankSources.lean` is only a typed payload;
that module has no graph-validity or capacity theorem for c5Base.  Attaching a
positive `capQ` to that tag would assume the missing adapter rather than prove
it.  Its only semantic checker is for own-edge Doors (lines 109-112).

Thus:

* Door cannot be used without an actual retained hit and its legal own edge.
* Vertex slack is pre-existing `N-T(v)`-type capacity, not created by `(x,y)`.
* Prune capacity requires an independent prune witness.
* c5Base has no hit-bank constructor and is zero in the production micro view.

## Why common-blue cannot supply the adapter

`CommonBlueOwner` is exactly `CheckedC5BaseTransfer.TerminalData.Valid`
(`CommonBlueExtendedMatching.lean`, lines 37-42).  Validity reserves the two
blue owner edges and requires

```text
dM({x,y}) + 2 <= dB({x,y}), equivalently sigma({x,y}) >= 2.
```

The `two_le_sigma` theorem is explicit in `CheckedC5BaseTransfer.lean`, lines
70-75.  Unreservedness of the free halves concerns the source key; it does not
fund either owner-edge reservation.  Therefore `sigma = 0/1` cannot be routed
by relabelling the pair as common-blue.

The R36 real-graph replay witnesses the live failure at `sigma = 1`:

```text
N=20, |E|=24, maxcut=20, triangle_free=true
owner=7, x=0, y=5
pairCount(0,5)=0, both halves ScopedReserved=false
dB=3, dM=2, sigma=1, commonBlueValid=false
```

For this owner, `x != owner` and `pairCount(7,0)=0`, so the same-owner and
row-companion branches also fail.  Hence the pair supplies zero relation edges
to the relevant collision shore, despite existing as two unreserved cells.

Replay:

```powershell
python tmp/fanout/r36_freepair_proof/verify_counterexample.py
```

## Minimal typed countermodel

`InterfaceCountermodel.lean` instantiates the exact checked interfaces with:

```text
V=Unit, FreeBase=Unit, FreeHalf=Fin 2, Debit=Unit, Comp=Unit
Hit=DoorKey=VertexKey=PruneKey=Term=Empty.
```

The sole debit has two collision halves and `collisionSource` bijects them to
the two canonical free halves.  The reservation ledger is checked, and
`tokenizedSpendQ = 1` for each half, so the exact raw capacity is `2`.
Because `Term=Empty`, no bank source exists, and the checked full-bank view has
all four columns equal to zero.  This is cardinality-minimal at the interface
level: one canonical base necessarily has exactly its two `Fin 2` halves, and
zero terms is the least bank.

Build used:

```powershell
$env:LEAN_PATH=(Resolve-Path tmp/codex_r32_verify/olean).Path
cd formal-conjectures
lake env lean --root=.. --o=../tmp/fanout/r39_weak_free_bank/InterfaceCountermodel.olean ../tmp/fanout/r39_weak_free_bank/InterfaceCountermodel.lean
```

Result: exit 0.  `flow_checked`, `ledger_checked`,
`each_free_half_has_one_raw_unit`, and `bank_columns_are_zero` use only
`propext`, `Classical.choice`, and `Quot.sound`.  Source SHA-256:
`A614B578570473C768A4E0F032BC61DDBBCFCCC2C7C8E092481D3F73708D54D3`.

## Required repair

The local result must retain a fourth outcome:

```text
weakFree(x,y): two unreserved halves, 0 <= sigma(x,y) < 2,
               no owner relation and no bank capacity.
```

A sound continuation needs a genuinely new global lemma that matches those
halves through another compiled source relation or pairs the weak outcome with
independently witnessed Door/vertexSlack/prune capacity.  No positive c5Base
capacity can be claimed without a new reservation-free terminal theorem and a
production adapter proving its exact ledger contribution.
