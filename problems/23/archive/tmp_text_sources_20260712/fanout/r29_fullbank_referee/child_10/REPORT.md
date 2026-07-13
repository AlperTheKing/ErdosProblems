# R29 FullBank Door source-class referee report

## Verdict

The R29 all-anchor FullBank Door audit is **not numerically instantiated in the repository**. No hub-shore Door candidate or capacity can be reported as R29 data without inventing an incidence map. The production Lean tree contains no declaration named `CheckedTransferMatching`; that phrase is goal/design terminology. The concrete checked surfaces are `FullBankGlobalPackage.Checked` and `OwnEdgeDoorSourceData.Checked`, and they are not connected by any R29 provider.

The only value of `FullBankGlobalPackage` found in production is the deliberately empty logical-separation countermodel `AggregateLedgerNoIncidenceCounterexample.emptyPackage`. There is no R29 `FullBankGlobalPackage`, `OwnEdgeDoorSourceData`, `DoorWallAdapter`, or `TypedPetalGeometry` value.

Therefore the claimed active-scoped values (score 23115, demand 19953, FreeHalf reach 19925, defect 28) do not determine whether the real FullBank source class absorbs 28. They contain neither boundary-port enumeration nor typed Door token capacities. No assumptions from those claims were used as Door data.

## Production interface trace

1. `DisjointPetalRouteData` (`DisjointPetalHalfSqueeze.lean:101-115`) starts from graph boundary semantics: `portEdge : I.Port -> Sym2 V` and `port_is_boundary`; it additionally requires an injective `door : I.Port -> I.Sink`, `door_legal`, and capacity `1 <= I.cap (door p)`.
2. `OwnEdgeDoorSourceData` (`TypedFullBankSources.lean:92-98`) is the typed source class: `portEdge`, typed `token`, and `doorOf`.
3. Its `Checked` predicate (`:109-112`) requires exactly: injective `portEdge`; `token (doorOf p).source = CapSource.door (portEdge p)`; and raw `capQ >= 25`. `hallCapQ` is exactly `capQ / 25` (`:152-156`). These facts derive own-Door legality, injectivity, and Hall capacity at least 1.
4. `DoorWallAdapter` (`TypedOwnDoorHalfLayer.lean:35-42`) still must supply `sinkOf`, injectivity, `legal_of_door_source`, exact `I.cap = hallCapQ`, and nonnegative sink capacity.
5. `TypedPetalGeometry` (`:45-57`) must instantiate the all-anchor active component's shore(s), short-edge interpretation, disjointness, and exact short/port boundary equations.
6. `halfLayerRouted_of_checkedEdgeDoorSources` (`:61-85`) is the first production composition point. It needs all four inputs: `D`, `D.Checked`, `DoorWallAdapter D`, and `TypedPetalGeometry D walls`.
7. In contrast, `FullBankGlobalPackage` (`FullBankToLengthSurplusCharge.lean:134-143`) contains only component/local ownership plus an aggregate ledger. Its legacy token has `(comp, kind, sourceId, capQ)` (`:63-68`). Its `Checked` fields (`:177-225`) check spends, kind totals, uniqueness, and residual identities, but have no port, edge-key, `doorOf`, wall sink, or legal-incidence field.
8. `FullBankPortSinks` merely filters aggregate tokens by `kind = door` and defines capacity `capQ/25`; its own guardrail states that legal edge-to-token incidence is absent (`:79-80`). Thus it cannot select the Door belonging to a boundary port.
9. `AggregateLedgerNoIncidenceCounterexample.checkedAggregatePackage_and_noHalfLayerRouting` proves the separation inside Lean: aggregate checking can coexist with absence of any half-layer routing (`AggregateLedgerNoIncidenceCounterexample.lean:155-161`).

## What must be instantiated on the all-anchor active component

For the component containing owners `{0,1,2}`, an honest provider must export:

- the exact component vertex set and graph edge set, hence every crossing boundary edge;
- the finite wall `Port` enumeration and injective canonical `portEdge` map, with completeness relative to the intended boundary-port semantics;
- one typed token per port and an injective `doorOf`, with component ID, source exactly `door(portEdge p)`, and exact rational raw `capQ >= 25`;
- the wall `Sink` image, its injectivity, proof that exact Door-source equality implies `I.legal`, and equality `I.cap(sinkOf t) = capQ(t)/25`;
- the wall cuts/shores and exact `cutPort = boundary indicator` equation (plus short-edge geometry where the half-layer theorem is invoked).

The first three bullets are the smallest **data exporter** needed to enumerate all hub-component Door candidates and capacities. The last two are the smallest **Lean adapter/provider** needed to consume that export in `halfLayerRouted_of_checkedEdgeDoorSources`. Exporting only aggregate `sourceId`, kind, or total Door spend is insufficient.

## Exact exporter and computation

`r29-own-door-v1.schema.json` states the minimal data contract. `check_door_export.py`:

- recomputes all crossing edges using integer set membership;
- requires the port-edge set to equal that boundary set exactly;
- checks port and token injectivity;
- checks exact Door source equality and component ownership;
- parses capacity with `fractions.Fraction`, requires raw `capQ >= 25`, and emits every candidate with exact Hall capacity `capQ/25` and exact totals.

No real R29 export exists, so the R29 candidate count, edge list, and capacities are **undetermined**, not zero. `synthetic_selftest.json` and `door_candidates.json` are explicitly synthetic validator tests and are not theorem evidence about R29.

## Replay

```powershell
python tmp/fanout/r29_fullbank_referee/child_10/audit_sources.py
python tmp/fanout/r29_fullbank_referee/child_10/check_door_export.py tmp/fanout/r29_fullbank_referee/child_10/synthetic_selftest.json
python -m py_compile tmp/fanout/r29_fullbank_referee/child_10/audit_sources.py tmp/fanout/r29_fullbank_referee/child_10/check_door_export.py
```

Observed outputs: `audit_sources.py` returned `provider_missing`; the synthetic validator returned one candidate, raw capacity 25 and Hall capacity 1.

## Artifact SHA256

- `audit_sources.py`: `4d4f40d1f918828331c2cd07700f9c9eda00b88dfdcdfba5241b3aa92fbf5720`
- `audit_sources.json`: `c8e903353acb5979f9f151d3c636786b91de04b5d4cf95f6c0a3eb3855a35980`
- `check_door_export.py`: `bc7025a1cf6f5802f21679a7eb1beab2d620c91a5d31fac1f7a1f28c2d99db1b`
- `r29-own-door-v1.schema.json`: `315bec35464839fdbbd07ace387c0d6c5cb25f63ac067251817ad4e1de7a2174`
- `synthetic_selftest.json`: `e7b84b8a248256ead5ae03f945249e99e7f5a9395785b7221fc385c84f6b1c1d`
- `door_candidates.json` (synthetic): `dcbf654254508092ebd43cac1365d7b226da29ba2606cf58d8852a2e6307e975`

Pinned production hashes are recorded in `audit_sources.json`.
