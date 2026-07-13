# R29 exact FullBank gate synthesis

## Verdict

The R29 all-anchor hub shore is **not a decisive falsifier of the intended
FullBank architecture**.  It is a decisive falsifier of the smaller compiled
`ActiveScopedMinimumExchange.Available` relation: demand is 19,953, reachable
capacity is 19,925, and the exact Hall defect is 28.

The literal compiled predicate
`CheckedC5BaseTransfer.TerminalData.Valid` supplies 216 new ordered
`(sourceX, sourceY, half)` identities after deduplication against same-owner and
row-companion sources.  Adding those identities gives reach 20,141 and exact
maximum flow 19,953; all seven nonempty owner shores pass.  An explicit
28-source repair is

```text
(x, 2930, h),  x = 29,...,42,  h in {0,1},  owner = 2.
```

For every one of these sources, both source vertices are blue-adjacent to
owner 2, `pairCount = 0`, switch loss is 3, and the compiled adjusted surplus
is `3 - 2 = 1`.

This is a **conditional owner-Hall pass**, not an end-to-end production
FullBank certificate.  The checked C5 module explicitly leaves permanently
free source ownership and global matching to separate layers.  No compiled
definition constructs the R29 base-sink incidence/capacity, global matching,
typed token spend, or port-to-token adapter.  Therefore the complete production
FullBank verdict is **UNDEFINED**.

## Exact reconstruction

The lead replay independently verifies:

| Quantity | Exact value |
|---|---:|
| vertices | 2,943 |
| graph edges | 8,422 |
| blue/cut edges | 7,039 |
| bad edges | 1,383 |
| maximum cut | 7,039 |
| Gamma | 34,575 |
| shortest-row family histogram | 707 of size 1; 676 of size 680 |
| all-anchor selected vertices | 2,127 |
| active vertices | 19 |
| active edges | 1,370 |
| demanded active edges | 18 |
| demand per hub | 6,650 collision + 1 HitNeed = 6,651 |
| hub-shore demand | 19,953 |

Triangle-freeness, blue connectivity, distance 4 for every bad edge, row
noduplication, and the five-class maximum-cut decomposition are checked by
integer arithmetic.  The cut classes total
`4110 + 2704 + 12 + 207 + 6 = 7039`.

## Incremental source accounting

Source identities are deduplicated before owner masks are unioned.  Capacities
are never added by prose label.

| Stage | Raw keys | New unique | Union reach | Full-shore defect | Max flow |
|---|---:|---:|---:|---:|---:|
| same-first / same-owner | 17,325 | 17,325 | 17,325 | 2,628 | 17,325 |
| common-bad | 0 | 0 | 17,325 | 2,628 | 17,325 |
| row-companion | 2,600 | 2,600 | 19,925 | 28 | 19,925 |
| compiled common-blue C5 terminal | 2,824 | 216 | 20,141 | -188 | 19,953 |
| component-scoped outside attachment | 0 | 0 | 20,141 | -188 | 19,953 |

After the common-blue stage, the seven nonempty owner-shore defects are
`-1732, -1832, -960, -1832, -960, -1064, -188`; hence all Hall cuts pass.
The complete list of 28 repair identities and their literal validity witnesses
is in `RESULT.json` under `commonBlueC5Terminal`.

## Outside-attachment correction

The 816 outside vertices form 704 blue components: 676 singleton components
and 28 components of size 5.  The R23 prose condition requires the attachment
and owner to lie in the same selected active component.  Under that condition,
all three hubs have zero eligible outside vertices and the class contributes
zero sources.

The archived R23 Python gate omitted that component equality.  Its unscoped
relation manufactures 912,600 half-slots and passes Hall, but that result is not
the stated component-scoped relation and is rejected as production evidence.

## FullBank class audit

| Class | R29 status |
|---|---|
| door | Boundary geometry is computable, but no R29 typed Door provider or legal port incidence is instantiated. |
| vertexSlack | Hub-owner residual slack is exactly 0; non-owner/component slack has no compiled legal route to these obligations. |
| c5Base | Literal common-blue terminal validity is compiled and yields 216 new identities conditionally; global ownership/matching and sink conversion are absent. |
| prune | A typed label exists, but no graph-derived prune transition, injective slot transport, or provider exists. |

The rational singleton LP requirement on the 19-vertex hub component is exact:
12 internal support edges define `F`; `O = B \\ F` has 18 internal unit-load
ports and 1,441 boundary half-load ports, totaling

```text
18 + 1441/2 = 1477/2.
```

This is required load, not available capacity.  It is ill-typed to compare
`1477/2` with the integral defect 28 until the missing ActiveScoped-to-FullBank
adapter fixes the scaling and incidence.

## Compiled-surface result

The production sources establish all of the following on replay:

- `Ell5FullBankRelaxedCover_exists` remains the named open existence theorem.
- `FullBankPortSinks` explicitly says legal edge-to-token incidence is absent.
- `FullBankGlobalPackage` takes door, vertexSlack, c5Base, and prune capacities
  as supplied rational data.
- `TypedFullBankSources` leaves the wall-sink adapter separate.
- `CheckedC5BaseTransfer` and `CheckedRowCompanionBaseTransfer` leave source
  ownership/global matching separate.
- no compiled `CheckedTransferMatching` or `outsideAttachment` definition is
  present.

Thus R29 proves neither a production FullBank pass nor a production FullBank
failure.  It isolates the exact missing bridge: construct graph-derived source
ownership, one overlap-safe global matching, and the typed port-to-token sink
adapter.  Once that bridge is supplied, the 216 common-blue identities show
that this particular 28-unit obstruction is numerically absorbable.

## Fanout adjudication

Nine disjoint lanes were run and then replayed by the lead.

| Lane | Accepted result |
|---|---|
| 01 semantics | end-to-end production relation UNDEFINED; abstract capacities are not supply |
| 02 transfer | common-blue increment 216 accepted; its unscoped outside-attachment PASS rejected because component equality was omitted |
| 03 reconstruction | all structural and auxiliary 28-defect invariants pass |
| 04 doors | geometry computed; production door capacity UNDEFINED |
| 05 vertexSlack | owner slack 0; incremental legal capacity UNDEFINED/0 |
| 06 c5Base | component-scoped four-pattern defect 28; no token/provider conversion |
| 07 prune | no operational provider; no attributable source capacity |
| 08 weighted LP | exact `1477/2` requirement; 12 provider fields missing |
| 09 referee | independently confirms defect 28, common-blue +216, final reach 20,141, production UNDEFINED |

## Replay

Run from `E:\Projects\ErdosProblems`:

```powershell
python -B tmp/fanout/r29_fullbank_gate/verify.py > tmp/fanout/r29_fullbank_gate/verify_stdout.json
python -B tmp/fanout/r29_fullbank_gate/lane01_semantics/build_audit.py
python -B tmp/fanout/r29_fullbank_gate/lane03_reconstruct/verify.py
python -B tmp/fanout/r29_fullbank_gate/lane04_doors/audit_doors.py
python -B tmp/fanout/r29_fullbank_gate/lane05_vertexslack/replay_vertexslack_audit.py
python -B tmp/fanout/r29_fullbank_gate/lane06_c5base/audit_c5base.py
python -B tmp/fanout/r29_fullbank_gate/lane07_prune/audit_prune.py
python -B tmp/fanout/r29_fullbank_gate/lane07_prune/verify_audit.py
python -B tmp/fanout/r29_fullbank_gate/lane08_fullbank_lp/verify.py
python -B tmp/fanout/r29_fullbank_gate/lane09_referee/audit_r29_fullbank.py
```

No float, `sorry`, or `native_decide` is used by the lead gate.  Input and
artifact hashes are recorded in `RESULT.json` and `SHA256SUMS.txt`.

## Key authoritative hashes

```text
5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6  r29_lead_gate.py
fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f  canonical R29 payload
93d5d64c55338186603b718b5d6bb162d907c4fc868ce276808e01822c395901  advertised all-anchor tuple file
dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce  auxiliary Hall certificate
12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0  CheckedC5BaseTransfer.lean
84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  CheckedRowCompanionBaseTransfer.lean
```
