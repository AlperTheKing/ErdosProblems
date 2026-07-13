# R29 Door-capacity audit

## Verdict: UNDEFINED

The production Door contribution to the R29 HUB shore cannot be evaluated from the implemented repository state. The reconstructed auxiliary shore is exactly `{0,1,2}` with demand `19,953`, ActiveScoped neighborhood `19,925`, and defect `28`, but no implemented R29 value connects wall ports or boundary edges to typed Door tokens. Therefore:

- Door raw reachable token count: **UNDEFINED**.
- Door raw reachable capacity: **UNDEFINED**.
- overlap with the four-pattern transfer sources: **UNDEFINED**.
- incremental Door capacity after overlap removal: **UNDEFINED**.
- post-Door defect: **UNDEFINED**.
- R29 Door no-double-spend check: **not instantiable**.

This is neither PASS nor FAIL. It does not prove that Doors absorb the 28 units, and it does not prove that the 28-unit defect survives production FullBank.

Machine-readable result: `door_audit.json`.

## Exact implemented Door contract

There are three distinct layers in Lean.

1. **Geometric candidate layer.** One bridge defines `O = cutEdges G s \ F` and `D = O.filter (fun e => edgeBoundary C e = true)` (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:101-103`). The same theorem explicitly requires `hboundaryDoorLegal` and `hboundaryDoorCapacity`; it does not infer them (`:72-97`). The all-Door fast path likewise takes `ownDoor_inc` and `ownDoor_capacity` as hypotheses (`EndpointHalfDoorComplete.lean:19-32`).

2. **Typed source layer.** A Door source is `CapSource.door edge` (`Gamma/TypedFullBankSources.lean:23-30`). `OwnEdgeDoorSourceData` requires `portEdge`, a typed token table, and `doorOf` (`:91-99`). Its checked proposition requires injective `portEdge`, exact source equality `token(doorOf p).source = CapSource.door(portEdge p)`, and raw `capQ >= 25` (`:108-120`). Hall-scale capacity is `capQ / 25` (`:151-159`).

3. **Wall routing layer.** `DoorWallAdapter` additionally requires an injective `sinkOf`, a proof that typed source equality implies wall legality, and equality of wall capacity with typed Hall capacity (`Gamma/TypedOwnDoorHalfLayer.lean:34-42`). `TypedPetalGeometry` separately requires actual shores and checked boundary equations (`:44-57`). Only after receiving all these inputs does `halfLayerRouted_of_checkedEdgeDoorSources` build the own-Door routing (`:61-85`).

The aggregate production package is weaker. `LedgerToken` contains only `(comp, kind, sourceId, capQ)` (`Gamma/FullBankToLengthSurplusCharge.lean:67-74`). `FullBankGlobalPackage.Checked` enforces nonnegative spend, per-token no-double-spend, component locality, and aggregate source uniqueness (`:174-209`), but `FullBankPortSinks.lean:80-81` explicitly states that legal edge-to-token incidence is absent and that its finite sinks do not assert Hall.

This logical gap is not merely commentary: `AggregateLedgerNoIncidenceCounterexample.lean:152-157` proves that a checked aggregate package can coexist with failure of half-layer routing. `RootLayerHalfSqueeze.lean:13` also states that no existence theorem for root layers, petal shores, or mandatory Doors is provided.

## R29 reconstruction

`audit_doors.py` imports `tmp/fanout/r29_gate/lead/r29_lead_gate.py`, calls `build()`, replaces all 676 selector rows by their stored anchor rows, and independently rebuilds selected vertices, selected support, off-support active edges, connected components, active components, and the HUB component. It then checks the authoritative owner-Hall certificate.

Exact results:

| Quantity | Value |
|---|---:|
| vertices | 2,943 |
| blue edges | 7,039 |
| bad edges / rows | 1,383 |
| selected vertices | 2,127 |
| selected support edges | 2,797 |
| active edges | 1,370 |
| selected active-graph components | 757 |
| active components | 1 |
| active vertices | 19 |
| demanded active edges | 18 |

The unique active component is the HUB component:

`{0,1,2,55,2762,2763,2764,2765,2766,2771,2772,2773,2774,2780,2781,2782,2783,2929,2930}`.

It contains all three owners in the deficient shore. The reconstructed canonical incidence SHA256 is `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`, exactly matching `cut_certificate.json`.

## Geometric Door diagnostic — not capacity

For audit visibility only, the script feeds the reconstructed 19-vertex active component into the geometric boundary predicate and uses the selected support as `F`:

- blue off-support edges: `4,242`;
- blue off-support edges internal to the HUB component: `18`;
- blue off-support edges crossing the HUB-component boundary: `27`;
- blue off-support edges crossing the full selected-vertex union: `2,760`.

The 27 HUB-boundary pairs are listed in `door_audit.json`. They are **not** counted as Door tokens, are not multiplied by a conjectural unit capacity, and are not compared arithmetically with 28. No implemented R29 `Port`, `portEdge`, typed token table, `doorOf`, `DoorWallAdapter`, petal-shore family, or legal relation licenses that conversion. In particular, the owner shore `{0,1,2}` is a shore of demand owners in `Gamma/ActiveScoped*`; it is not itself an implemented `TypedPetalGeometry.shore`.

## Four-pattern baseline and overlap

The `19,925` sources in `cut_certificate.json` are the auxiliary ActiveScoped `FreeHalf` neighborhood, not a complete production four-pattern bank. The fourth `outsideAttachment` pattern appears as a design and Python gate in `WALL_ATTACK_R23_GPTPRO56.md:7-35` and `_claude_r23_outside_attachment_gate.py`; no `CheckedOutsideAttachment` or `outsideAttachment` definition occurs in the production Lean scan. The third row-companion terminal is compiled in `Gamma/CheckedRowCompanionBaseTransfer.lean:108-165`, but there is no compiled four-pattern-to-FullBank R29 provider.

Consequently even “capacity before Doors” is not a production value in this lane, and there is no common source-identity namespace with which to remove Door/transfer overlap. Assigning `27`, `27/2`, `27*25`, or any other capacity would be speculative and could double-spend tokens.

## Absence audit

The replay parsed 276 non-O14 production Lean files (all top-level files plus `BranchB`, `Cert`, `Ell5`, `Gamma`, `Rows`, and `Toy`) and separately searched all 43,426 generated `O14` Lean files for the relevant FullBank/Door symbols. Total files covered: 43,702.

Results:

- concrete `FullBankGlobalPackage` values found: only the zero-size `emptyPackage` countermodel at `AggregateLedgerNoIncidenceCounterexample.lean:34`;
- concrete `OwnEdgeDoorSourceData` value declarations: none;
- concrete `DoorWallAdapter` value declarations: none;
- `O14` files containing `FullBankGlobalPackage`, `OwnEdgeDoorSourceData`, `DoorWallAdapter`, `CapSource.door`, or `doorHallCapQ`: none;
- compiled `CheckedOutsideAttachment` / `outsideAttachment` occurrences: none.

The exact regex results, line anchors, scan counts, and source hashes are in `door_audit.json` under `source_audit`.

## Minimal missing data

A decisive Door audit needs all of the following, using the same source identifiers as the transfer ledger:

1. A finite R29 wall `Port` enumeration and `portEdge : Port -> Sym2 Vertex`.
2. A typed R29 token table with component and `CapSource` payloads.
3. `doorOf : Port -> token index`, accepted by `checkOwnEdgeDoors`.
4. A `DoorWallAdapter` into the production wall `Sink` type.
5. The actual R29 petal shores/walls and their checked boundary equations.
6. A shared source-identity table relating Door tokens to four-pattern tokens, enabling overlap removal and per-token no-double-spend.

Until those values exist, the decisive question “does complete production FullBank absorb 28?” remains **UNDEFINED** from the Door source class.

## Replay commands

Run from `E:\Projects\ErdosProblems`:

```powershell
python tmp/fanout/r29_fullbank_gate/lane04_doors/audit_doors.py
python tmp/fanout/r29_fullbank_gate/lane04_doors/make_hashes.py
```

Useful independent source checks:

```powershell
rg -n --glob '*.lean' "FullBankGlobalPackage|OwnEdgeDoorSourceData|DoorWallAdapter|doorHallCapQ" problems/23/lean/Erdos23Delta0/Gamma problems/23/lean/Erdos23Delta0/*.lean
rg -l --glob '*.lean' "FullBankGlobalPackage|OwnEdgeDoorSourceData|DoorWallAdapter|CapSource\.door|doorHallCapQ" problems/23/lean/Erdos23Delta0/O14
rg -n --glob '*.lean' "CheckedOutsideAttachment|outsideAttachment" problems/23/lean/Erdos23Delta0
```

A Lean import check was attempted with:

```powershell
lake env lean E:/Projects/ErdosProblems/tmp/fanout/r29_fullbank_gate/lane04_doors/AuditDoorDefinitions.lean
```

It did not start compilation: this workspace contains no `lakefile.*` or `lean-toolchain`, and `elan` reported `no default toolchain configured`. The source-check file is retained; no successful Lean-build claim is made.

## Principal SHA256 hashes

- `r29_lead_gate.py`: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- `rebuild_owner_hall.py`: `a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0`
- `cut_certificate.json`: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`
- `FullBankToLengthSurplusCharge.lean`: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- `FullBankPortSinks.lean`: `ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6`
- `TypedFullBankSources.lean`: `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`
- `TypedOwnDoorHalfLayer.lean`: `793f8b47926dbe93e2b0f476e42ae33a688913faa95e46912205ec69009a4eaa`
- `AggregateLedgerNoIncidenceCounterexample.lean`: `624c56995234f4ef5d68804013ce69d66962cfb2a3230de7c8d601db6870089f`
- `Ell5InternalEndpointSlackFullBank.lean`: `506ba26ca167045464c5c5bf45ece250a18a3870e1716e120027cc0a320da8b9`
- `WALL_ATTACK_R23_GPTPRO56.md`: `45e6533b1cb670ebb8476998bee9904ad0ec8f8943c2753b78a677827358c9d3`
- `_claude_r23_outside_attachment_gate.py`: `6147ac4c7b501f8ab46597ef210838e1138f0b7cb15910a4712dc5efac844cec`

All lane-artifact hashes, including this report, are generated in `HASHES.json`.
