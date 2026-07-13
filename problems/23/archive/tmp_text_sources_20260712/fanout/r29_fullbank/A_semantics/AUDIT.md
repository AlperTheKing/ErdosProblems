# R29 FullBank semantic audit

## Verdict

The exact R29 shore `19925 < 19953` falsifies the compiled ActiveScoped
`Demand -> FreeHalf` matching at the all-anchor tuple. It does not falsify the
real FullBank wall.

The reason is structural, not numerical:

1. `CheckedTransferMatching` has no tracked Lean declaration. R19/R20/R23 use
   it as a prose specification. The claimed four-pattern consumer is absent.
2. Compiled ActiveScoped eligibility has only same-first and row-companion
   branches, followed by a reservation filter. Its unit-capacity sources are
   `FreeHalf` values.
3. The real compiled weighted Hall interface demands rational block load on
   non-Door off-support edges and routes it to generic sinks through `incBase`
   with capacities `kapBase`.
4. `FullBankGlobalPackage` is a different downstream aggregate object. It has
   local rational demands and a four-kind token spend ledger, but no edge/port
   incidence relation. Compiled source kinds are `door`, `vertexSlack`,
   `c5Base`, and `prune`.

Thus an ActiveScoped FreeHalf defect can kill a sufficient selector route, but
it reaches the real wall only after a missing theorem constructs exhaustive
typed sources, eligibility, capacities, and a graph-derived package.

## Exact semantics

### ActiveScoped auxiliary relation

- Demand: `ActiveCollisionHalf` plus `ActiveHitNeed`.
- Source: one `FreeHalf`, an ordered distinct vertex pair, one of two halves,
  and proof that its selected-row pair count is zero.
- Eligibility: first source coordinate equals the owner, or both coordinates
  co-occur with the owner and the two-vertex switch has `sigma >= 0`.
- Reservation: half zero on an active edge in an active component is removed.
- Capacity: one, represented by injectivity of `assign`.
- Score: the cardinality of the ActiveScoped demand type.

There is no compiled `commonBad` branch and no compiled `outsideAttachment`
branch in this relation.

### Real wall relation

`ActiveComponentBankHall` uses:

- Demand objects: non-Door off-support edges `E0 O D`.
- Demand weight: rational active-component `blockLoad`.
- Sources: arbitrary finite sink type `JT`.
- Eligibility: `incBase : Sym2 V -> JT -> Prop`.
- Capacity: `kapBase : JT -> Rat`.
- Hall law: every finite edge shore has total demand at most the capacity of
  all incident sinks.

With separate Door hypotheses, this constructs a
`FullBankRelaxedCoverCert`. That certificate stores rational cut weights and
routing flow and proves coverage, congestion, routing, incidence, and sink
capacity inequalities.

### Global package

`FullBankGlobalPackage` stores local covers and a spend matrix over tokens.
Each token has `(component, kind, sourceId, capQ)`. `Checked` enforces local
cover arithmetic, nonnegative spend, no double spend, no cross-component
spend, source-key uniqueness, and component/global reserve identities.

It does not store an off-support edge or port index, a legal-incidence
predicate, a transport trace, or a source formula. The compiled theorem
`checkedAggregatePackage_and_noHalfLayerRouting` is an exact countermodel to
deriving wall routing from those aggregate fields alone.

### Four source kinds

The global package gives all four kinds arbitrary rational token capacities
subject to its checked ledger laws. `TypedFullBankSources` refines identities
to payloads `ExitEdgeKey`, `VertexKey`, `BaseKey`, and `PruneKey`. Only the Door
kind has compiled semantic eligibility, and even that requires a supplied
`DoorWallAdapter`. The other three graph-derived eligibility/capacity formulas
are absent.

`Ell5.ConcreteCage.LocalBankKind` is another compiled but abstract encoding.
Its `baseLeaf` constructor is not definitionally `c5Base`, and no bridge to the
global package was found.

## Smallest statement

For the deterministic 2943-vertex reconstruction and all-anchor row tuple,
the owner shore `{0,1,2}` has ActiveScoped demand `19953` and ActiveScoped
source neighborhood `19925`. Hence its defect is exactly `28`,
`ScopedOwnerHallCondition` fails, and the compiled equivalence makes
`ActiveScopedMinimumExchange.Matching` empty.

No conclusion about `ActiveComponentBankHall`, existence of a
`FullBankRelaxedCoverCert`, or existence of a checked `FullBankGlobalPackage`
follows without a new bridge theorem.

The additional claim that this tuple is a global scoped-score minimizer is an
exact external certificate claim, not a compiled Lean theorem in the current
tree. The latest coordination block still marks the cell lower-bound
derivation as the remaining formal leg.

## Artifact use

Run:

```powershell
pwsh -NoProfile -File tmp/fanout/r29_fullbank/A_semantics/verify_semantic_map.ps1
```

The verifier checks every declaration anchor in `semantic_map.json`, confirms
that tracked Lean has zero `CheckedTransferMatching` hits, checks the four
compiled global source constructors, and rejects forbidden proof tokens in
this lane.
