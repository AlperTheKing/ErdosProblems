# Child 03 — top-level FullBank theorem-chain semantic audit

## Verdict

There is **no compiled end-to-end theorem chain** matching the prose sequence

`CheckedTransferMatching -> banked token families -> EndpointReserveHall -> active-component flow -> ActiveComponentFullBankCert -> FullBankGlobalPackage -> FullBankHall -> Gamma`.

The names `CheckedTransferMatching` and `ActiveComponentFullBankCert` do not occur in production Lean in the scoped search recorded below. They occur only in planned writeup prose (`problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md:31-34`, `problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:48-49`). Production instead contains separate branches:

1. active-scoped `Matching` uses `Available` between `Demand` and `FreeHalf`;
2. residual micro-source tokenization can feed an abstract `CollisionTokenAssignment.Assignment`, which feeds `endpointReserveHallOn`;
3. a different abstract weighted `ActiveComponentBankHall` feeds a `FullBankRelaxedCoverCert`;
4. `Ell5FullBankHall` derives a numeric bank inequality from that local certificate;
5. an unrelated aggregate `FullBankGlobalPackage.Checked` feeds the length-surplus and `gammaOfGD <= n^2` theorems.

No production theorem converts (1)/(2) into (3), converts `FullBankRelaxedCoverCert` into (5), or connects typed wall-port legality to the aggregate package.

The goal prose names the intended chain (`GOAL_LOOP.md:16`, “`CheckedTransferMatching ... => banked token family => compiled EndpointReserveHall => active-component flow ... => ActiveComponentFullBankCert => Checked FullBankGlobalPackage`”), while the coordination log records acceptance of the SPEC-1 **interface** and says the wall is to “construct a Checked FullBankGlobalPackage” (`coordination/CLAUDE_TO_CODEX.md:13651-13654`). This matches the production seam: construction/provider is not supplied.

## Findings: exact production branches

### A. Actual active-scoped predecessor: `Matching`

The demand class is exactly

`Demand G c omega := ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106`). `ActiveCollisionHalf` restricts `CollisionHalf` to owners satisfying `ActiveOwner` (lines 51-54); `ActiveHitNeed` is `Σ v : Fin G.n, Fin (hitNeedUnits ... v)` (lines 80-89). The source class is `FreeHalf G omega` (lines 154-158).

The exact relation is

`Available G c d s := EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s`

(lines 144-147). `EligibleOwner` means either `s.sourceX = owner`, or positive owner co-occurrence with both endpoints plus `0 <= sigma G c [sourceX,sourceY]` (lines 134-142). `ScopedReserved` removes half-zero cells on active-component edges (lines 125-132).

The compiled structure is `Matching.assign : Demand ... -> FreeHalf ...`, with injectivity and `forall d, Available ... d (assign d)` (lines 154-158). The exact theorem is

`Nonempty (Matching G c omega) <-> HallCondition G c omega`

(lines 167-170). It emits no tokens, endpoint reserve, local relaxed-cover certificate, or global package.

The R29 writeup says `HallFailureHasScopedScoreGlobalDescent` remains an abstract Lean interface but its real-graph provider is false (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`). Its exact witness is demand 19953, neighborhood 19925, defect 28 (lines 67-74), and it is explicitly not a falsifier to Erdős #23 (line 12).

### B. Residual tokenization and `EndpointReserveHall`

`ResidualSourceTokenization.Data` carries

`((Debit × Fin 2) ⊕ (Slot × Fin 25)) ↪ (Source × Fin 2)`

plus component maps and a positive rational unit (`problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean:27-42`). Its demand microclasses are debit halves and 25 copies of each need slot; supply is two copies of each abstract source. The existence theorem is only

`2*card Debit + 25*card Slot <= 2*card Source -> Nonempty (((Debit × Fin 2) ⊕ (Slot × Fin 25)) ↪ (Source × Fin 2))`

(lines 46-52). It does not construct graph-semantic `Data`.

For supplied `Data`, `Token := Slot`, legality is `D.owner s ∈ e`, cap is `25 * D.unit`, and `eta x s` is that cap exactly at the owner (lines 59-77). `Data.assignment` constructs `CollisionTokenAssignment.Assignment` (lines 108-116). This module rebuilt in this audit with rc=0; printed axioms were subsets of `{propext, Classical.choice, Quot.sound}`.

`CollisionTokenAssignment.Assignment` is an abstract provider record containing `eta`, nonnegativity, token no-double-spend, payment of need, and endpoint legality (`problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:25-35`). Its theorem concludes

`T.card <= sum_{x in usedEndpoints T} slack x + sum_{t in usedTokens T legal} cap t`

under exact-half, pointwise budget, and supplied assignment (lines 48-56), by calling `endpointReserveHallOn` (lines 58-75). No theorem constructs it from active-scoped `Matching`.

`EndpointReserveHall` treats edges as demands and `V ⊕ JT` as sinks. `endpointReserveInc` is endpoint membership for `Sum.inl x`, or an incident endpoint with positive `eta x t` for `Sum.inr t` (`problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:31-40`). Its exact main conclusion is

`endpointReserveHallOn ... : (T.card : Q) <= (sum x in U, slack x) + sum t in R, cap t`

under the hypotheses listed at lines 145-153 (conclusion lines 144-154). The file says it does not construct the reserve (lines 12-13).

### C. Active-component flow branch

The executable owner map is

`componentOwner comp active x := if active (comp x) then Sum.inl x else Sum.inr (comp x)`

(`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentFlow.lean:21-24`). The flow constructor consumes explicit flow/route/cap/incidence/Door hypotheses and returns `FullBankRelaxedCoverCert ...` (lines 51-79); it wraps block flow rather than proving existence (lines 80-99).

The generic bank variant defines `E0 O D := {e : Sym2 V // e ∈ O ∧ e ∉ D}` and demand as active-component `blockLoad` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:23-33`). The non-Door sink class is arbitrary finite `JT`. `ActiveComponentBankHall` is exactly the weighted subset inequality over `T : Finset (E0 O D)` and filtered `incBase`-neighbor capacities (lines 51-64). This is a provider hypothesis at line 126, not derived from `EndpointReserveHall`.

Given that Hall hypothesis plus graph and Door hypotheses, `certificate_of_activeComponent_mixedDoorBankHall` concludes

`FullBankRelaxedCoverCert S F O univ univ (...) (combinedInc ...) (combinedCap ...)`

(lines 107-133). It obtains a capacitated flow from Hall (lines 142-153) and passes it to block-bank flow (lines 204-228). No `ActiveComponentFullBankCert` symbol exists.

The combined sink class is `BlockBankSink JT V := JT ⊕ Sym2 V`: generic non-Door sinks plus edge-indexed Door sinks (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-22`). `mixedDoorBlockBankQ` sends non-Doors through supplied `qBase` and each Door to its own edge sink (lines 28-38).

### D. Local full-bank certificate and `FullBankHall`

`FullBankRelaxedCoverCert` carries cut weights `lam`, routing `q`, nonnegativity, row coverage, support congestion, off-support routing, capacities, and legal positive incidence (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:23-40`). Its classes are rows `S : Finset R`; cut family `K : Finset ι`; support edges `F`; off-support load edges `O`; and sinks `J : Finset JT`, related by arbitrary `inc`.

Its wrapper concludes `BankedCutDomination ...` (lines 42-50); another excludes an exact rational dual (lines 52-60). The module says full-certificate construction is the remaining open theorem and soundness is glue (lines 6-11).

`Ell5FullBankHall.external_load_le_bank_of_cert` concludes total off-support load is at most total sink capacity (`problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean:28-48`). The numeric theorem is

`hall_bound_of_fullBank_cert ... : 25*|S| <= 25*|F| + 25*sum_{j in J} kap j`

under a supplied cert, `Disjoint F O`, boundary containment, and per-cut cardinal bound (lines 50-66). It does not mention `FullBankGlobalPackage`.

### E. Aggregate package and final Gamma consumer

The cap kinds are exactly `door | vertexSlack | c5Base | prune` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31`). `FullBankRelaxedCoverBundleView` is only five rationals—one demand and four caps (lines 33-45)—not a `FullBankRelaxedCoverCert`.

`LedgerToken` carries `(comp, kind, sourceId, capQ)`; `GlobalLedgerData` carries tokens, a local-by-token spend matrix, component reserve slack, and superadditivity slack (lines 67-82). `FullBankGlobalPackage` contains counts, row ownership maps, rational local covers, and this ledger (lines 124-143).

`FullBankGlobalPackage.Checked` is a provider hypothesis. Fields include local-view checking and surplus/demand inequalities (lines 177-186), local caps equal spends and no-double-spend (lines 187-200), component/source conditions (lines 201-209), the direct identity `lengthSurplusGD rows = P.localSurplusTotal` (lines 210-211), component reserve identities (lines 212-222), and superadditivity identity (lines 223-227).

From supplied `Checked`, the bookkeeping theorem concludes

`lengthSurplusGD rows <= 25 * etaQ G c`

(lines 286-308), and the direct consumer concludes

`gammaOfGD G c rows <= (G.n : Q)^2`

(lines 310-315). `lengthSurplusGD` is exactly the row-list sum of `length^2 - 25` (`problems/23/lean/Erdos23Delta0/GammaAggregation.lean:26-28`); `etaQ = (n^2 - 25*badCount)/25` (`problems/23/lean/Erdos23Delta0/CertGraph.lean:2310-2312`); `gammaOfGD` is the row-list sum of squared lengths (lines 3353-3355). The reduction signature is

`rows.rowList.length = badCount G c -> lengthSurplusGD rows <= 25*etaQ G c -> gammaOfGD G c rows <= n^2`

(`problems/23/lean/Erdos23Delta0/GammaAggregation.lean:47-53`).

The optional charge bridge is not a new provider. It emits zero coefficients and one `.raw` residual equal to `lengthSurplusTarget` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean:41-61`) and proves acceptance by invoking `fullBankGlobalPackage_sound h` (lines 63-80). Its Gamma theorem additionally assumes every row satisfies `RowGershBound` (lines 82-93).

## Source/sink classes versus `ActiveScopedMinimumExchange.Available`

| Layer | Demand/source side | Sink/supply side | Relation to `Available` |
|---|---|---|---|
| Active scoped | `ActiveCollisionHalf ⊕ ActiveHitNeed` | `FreeHalf` | **Present exactly**: `EligibleOwner ∧ ¬ScopedReserved` at `problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`. |
| Residual micro-matching | `(Debit × Fin 2) ⊕ (Slot × Fin 25)` | `Source × Fin 2` | **Only indirectly represented** by injection/component equality; no `EligibleOwner` or `ScopedReserved` (`problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean:27-42`). |
| Collision assignment | endpoint need at `V` through `eta` | token type `JT` | **Only indirectly represented** by provider field `legal_at_endpoint`; no `Available` (`problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:25-35`). |
| Endpoint reserve Hall | selected edges `T ⊆ E` | `V ⊕ JT` | **Absent as a predicate**; `endpointReserveInc` is a different endpoint/positive-eta relation (`problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:31-40`). |
| Active-component bank Hall | non-Door edges `E0 O D` weighted by block load | arbitrary `JT` | **Only indirectly representable** via caller-supplied `incBase`; no specialization to `Available` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:51-64`). |
| Block bank flow | off-support edges | `JT ⊕ Sym2 V` | **Absent**; generic-bank and own-Door summands (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-38`). |
| Local full-bank cert | rows `S`, support `F`, off-support `O`, cuts `K` | `J : Finset JT` | **Only indirectly representable** through arbitrary `inc` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40`). |
| Global ledger | local rational demands/spends | finite `LedgerToken`s in four kinds | **Absent**: no edge/port/source relation is stored (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-82,124-143`). |
| Ledger partition | none newly generated | `NonDoorToken` and `DoorToken` | **Absent**; guardrail says these capacities assert no Hall condition (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-49,80-81`). |
| Typed source keys | ports in `OwnEdgeDoorSourceData` | `CapSource.door/vertexSlack/c5Base/prune` | **Absent for active matching**; only own-Door source equality (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-41,130-149`). |
| All-Door fast path | every off-support edge | its own `Sym2 V` Door sink | **Absent/bypassed**: hypotheses are `inc e e` and `1 <= kap e` (`Ell5SingletonVertexSlack.lean:429-445`). |

## Typed families and explicit adapter gap

`TypedFullBankSources.CapSource` has exactly `.door edge`, `.vertexSlack vertex`, `.c5Base base`, and `.prune prune`, definitionally mapped to the four `CapKind`s (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-41`). `OwnEdgeDoorSourceData.Checked` proves injective port-edge keys, exact Door source equality, and cap at least 25 (lines 108-112); `doorOf_legal` and `doorOf_injective` follow (lines 130-149). The module explicitly says connecting typed tokens to the wall `Sink` is a separate adapter not assumed there (lines 12-14).

`FullBankPortSinks` partitions ledger tokens into `NonDoorToken` and `DoorToken` and divides capacities by 25 (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-49`), but says legal edge-to-token incidence is absent and no Hall condition follows (lines 80-81).

The separation is formally stated by

`checkedAggregatePackage_and_noHalfLayerRouting : emptyPackage.Checked ∧ ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls)`

(`problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean:152-157`). The file states aggregate fields alone cannot derive routing and a typed checked port-to-token adapter is needed (lines 8-16). This source was not in the active olean cache; it is production source, not independently cache-verified here.

## Executable implementations found

1. `tmp/fanout/r29_gate/lead/r29_lead_gate.py` provides `build()` and `scoped_state()`. `build()` constructs exact Python sets/lists/tuples/dicts for `blue`, `bad`, `graph`, `rows`, and selector metadata (`tmp/fanout/r29_gate/lead/r29_lead_gate.py:129-153,223-276`). `scoped_state()` constructs active edges/components and integer collision/hit-need dictionaries (lines 279-338).
2. `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py` implements active scope in `rebuild_scope()` (lines 52-97) and the executable analogue of `EligibleOwner ∧ ¬ScopedReserved` in `owner_sources()`: same-first at lines 110-119, companion/sigma-nonnegative at lines 120-134.
3. `tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py::verify_hall_certificate` deduplicates `(x,y,half)`, builds an owner-mask histogram, recomputes every shore demand/reach/gap, and asserts `[19953,19925,28]` (lines 28-46).
4. `problems/23/writeup/_codex_r29_fullbank_semantic_audit.py` is top-level exact `Fraction` code. It calls `build()` (lines 12-20), constructs `S,rows,C,F,O,J,K` (lines 21-27), defines exact singleton load as endpoint count/2 (lines 35-44), and checks all-Door columns (lines 46-48). This audit returned `|S|=1383`, `|F|=2797`, `|O|=|J|=4242`, `|C|=|K|=2803`, total off-support load 4102, own-Door cap 1, while recording active-scoped defect 28 (lines 50-65).

That executable corresponds to

`certificate_of_singletonCore_allDoors ... : FullBankRelaxedCoverCert S F O O C ...`

under graph/cut facts, `inc e e`, and `1 <= kap e` (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:429-479`). It is a local-certificate bypass of failed active matching on reconstructed R29, not a `FullBankGlobalPackage.Checked` or Gamma proof.

`EndpointHalfDoorComplete` packages rows, support, own-Door incidence, and capacity (`problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean:19-32`); `fullBankBundle_of_endpointHalfDoorComplete` returns local cert, wall primal, and no-strict-dual proof (lines 65-99). The file explicitly says no current bundle carries global-package semantics (lines 34-39). Its audit build failed before elaboration because `Ell5FullBankWallAdapter.olean` was absent from the supplied cache.

No Python/other executable constructs `FullBankGlobalPackage.Checked`, converts `FullBankRelaxedCoverCert` to it, or implements the planned named structures. The scoped command is below.

## Compiled facts versus provider hypotheses

**Cache-attested facts:** active-scoped matching/Hall equivalence; `endpointReserveHallOn`; `hall_of_assignment`; active-component Hall-to-`FullBankRelaxedCoverCert`; block-bank flow; local cert soundness; `Ell5FullBankHall`; typed source and port-cap lemmas; global-package bookkeeping implications; final Gamma consumers. Matching oleans were present under `tmp/claude_lean_o_base_v1`; coordination independently records SPEC-1 accepted (`coordination/CLAUDE_TO_CODEX.md:13648-13654`).

**Independently rebuilt here:** `ResidualSourceTokenization.lean`, rc=0, olean written only to this lane.

**Production source, not independently compiled here:** `EndpointHalfDoorComplete.lean` and `AggregateLedgerNoIncidenceCounterexample.lean`, due missing dependency oleans. The scoped scan found no `sorry`, `admit`, `native_decide`, or `sorryAx` in any cited Lean source.

**Provider hypotheses/open seams:** graph realization of active matching; construction of `ResidualSourceTokenization.Data`; construction of `Assignment`; `ActiveComponentBankHall`; own-Door legality/capacity; general local cert existence; conversion of local cert/typed sources to `FullBankGlobalPackage.Checked`; construction of that checked package for target graphs.

## Contradictions and ambiguities

1. **Prose versus imports.** `EndpointReserveHall` is not imported by `Ell5ActiveComponentBankHall`; its imports are `CapacitatedHallFlow`, `Ell5ActiveComponentFlow`, and `Ell5BlockBankFlow` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:1-3`). The prose arrow is not a compiled dependency.
2. **Three “Hall” meanings.** Active-scoped `HallCondition` is cardinal matching Hall on `Available`; `ActiveComponentBankHall` is weighted Hall on block loads/arbitrary sinks; `hall_bound_of_fullBank_cert` is a numeric consequence of an existing cert. No conversion theorem joins them.
3. **Three similarly named packages/views.** `FullBankRelaxedCoverCert` contains real routing/incidence. `FullBankGlobalPackage` contains aggregate rational ledgers and no port incidence. `FullBankRelaxedCoverBundleView` is five rationals.
4. **R29 matching failure versus all-Door cert.** The same data has active-scoped defect 28 and satisfies a different own-Door local-cert audit. The source/sink relations differ; this neither refutes R29 nor completes Gamma.
5. **Charge “provider”.** `chargeCertProviderOfFullBankLedger` uses a raw residual already proved nonnegative from `P.Checked`; it is a wrapper, not independent certificate generation (`problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean:51-80`).
6. **Gamma naming.** The final consumer here is rational row-data `CertGraph.gammaOfGD` (`problems/23/lean/Erdos23Delta0/CertGraph.lean:3353-3355`), not the separate natural graph-distance `GammaCalc.gammaOf` in `Erdos23Delta0/Gamma.lean`. No graph semantics were inferred from names.

## Unresolved gaps

1. No `Matching -> ResidualSourceTokenization.Data/Assignment` adapter.
2. No endpoint-reserve Hall -> `ActiveComponentBankHall` theorem.
3. No production `ActiveComponentFullBankCert`; actual output is `FullBankRelaxedCoverCert`.
4. No `FullBankRelaxedCoverCert -> FullBankGlobalPackage.Checked` adapter.
5. No checked typed wall-port-to-ledger-token incidence adapter.
6. R29 Python verifies exact data-level all-Door hypotheses but has no 2,943-vertex Lean instantiation/global ledger.
7. No separate active goal attachment was exposed. `GOAL_LOOP.md:9-17` says it reproduces the active `/goal`, so that was used.

## Commands run

All writes were confined to this lane.

```powershell
rg --files | rg "(^|/)(COMMON\.md|GOAL_LOOP\.md|CLAUDE_TO_CODEX\.md|R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER\.md)$|FullBank|EndpointReserveHall|ActiveComponent|CheckedTransferMatching|ActiveScopedMinimumExchange|Gamma"
rg -n "^" tmp/fanout/r29_fullbank_semantics/COMMON.md
rg -n "^" GOAL_LOOP.md
rg -n "^" problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
rg -n -C 5 "CheckedTransferMatching|banked token|EndpointReserveHall|ActiveComponentFullBankCert|FullBankGlobalPackage|FullBankHall|length-surplus|LengthSurplus|ActiveScopedMinimumExchange|R29|FullBank" coordination/CLAUDE_TO_CODEX.md
Get-Content coordination/CLAUDE_TO_CODEX.md  # numbered final 180 lines
Get-ChildItem problems/23/lean/Erdos23Delta0 -Recurse -File -Filter *.lean | Where-Object { excluded O14/Generated and Cert data shards } | Select-String -Pattern 'CheckedTransferMatching|TransferMatching|ActiveComponentFullBankCert'
Get-ChildItem problems/23/lean/Erdos23Delta0 -Recurse -File -Filter *.lean | Where-Object { excluded generated/data shards } | Select-String -Pattern 'FullBankCert|TokenFamily|banked.*family|ActiveComponent.*Bank'
rg -n "^" <each cited Lean/Python source>
Get-ChildItem problems/23/writeup,tmp/fanout/r29_gate,tmp/fanout/global_min_proof,tmp/fanout/r29_fullbank_semantics -Recurse -File -Include *.py,*.cpp,*.rs,*.lean | Select-String -Pattern 'CheckedTransferMatching|ActiveComponentFullBankCert|FullBankGlobalPackage|FullBankRelaxedCoverCert|EndpointReserveHall|ActiveComponentBankHall|ResidualSourceTokenization|NonDoorToken|DoorToken|full.?bank'
rg -n "\bsorry\b|\badmit\b|native_decide|sorryAx" <all cited Lean sources>  # no matches
python problems/23/writeup/_codex_r29_fullbank_semantic_audit.py
lake env lean --root=E:\Projects\ErdosProblems\problems\23\lean -o E:\Projects\ErdosProblems\tmp\fanout\r29_fullbank_semantics\child_03\ResidualSourceTokenization.audit.olean E:\Projects\ErdosProblems\problems\23\lean\Erdos23Delta0\ResidualSourceTokenization.lean
lake env lean ... EndpointHalfDoorComplete.lean  # failed: Ell5FullBankWallAdapter.olean absent
lake env lean ... AggregateLedgerNoIncidenceCounterexample.lean  # parallel batch did not reach a reported result after the other dependency failure
Get-FileHash -Algorithm SHA256 <every cited source>
```

The exact planned-name absence search returned no production Lean matches. The executable search found the four implementations/audits enumerated above, but no global-package constructor or cert-to-global adapter.

## SHA-256 hashes of every cited source

```text
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
bfb75636d5e11b7f3d251cb20a64a5227f5b870938f1d1b715f38d400903adfc  problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md
cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5  problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
9cfa35f2714799ddd4e1a187c2d6d620dae7c15d920f114896b4f30218274440  problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean
a9c4cebee9e5d1d63b4e38ad7203c05d18fdb8f8ef5f41684ebea07340aaa149  problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean
6509c4f9443bebf66a0eea6be7c6dfa03c0dcd3f72a6575c188b191d0253000e  problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean
05501c6d20312eea977a16e3ba9a2fda07cedc612970371f5de8f570523f9eef  problems/23/lean/Erdos23Delta0/Ell5ActiveComponentFlow.lean
9e907495d20492505ff85c613c033ee783a288ad790c8682ed575c0c1bec438d  problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean
aa06f4008055343b4deb271aa4a461a68b0ef63b8e0e5661942c26f8c7cd565d  problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean
8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104  problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean
0ac01cf28b2e7dc6770da7f71b147cedec47671a4c672e1434fd7dc372f1bae1  problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean
f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
8f7941dfa55dc9f5b60bc9666af4cd8d330d4f5d3a03010651d67a3711f50e92  problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean
6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048  problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean
800547bc53068873072306afba3c9e51000b8f13571ed9d1061e1c13ef43e164  problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean
624c56995234f4ef5d68804013ce69d66962cfb2a3230de7c8d601db6870089f  problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean
590b8f0def00520d17dcce54dedfc137989ec482409260630de3c50246e595eb  problems/23/lean/Erdos23Delta0/GammaAggregation.lean
93150a508e19f634d93596b75e9950dc0d0cb72a393efdecb2efda97969bbd31  problems/23/lean/Erdos23Delta0/CertGraph.lean
6d53bfd70568b3554c8c6b9315b919b624f5842106a25d4e0eceb2febbf480dd  problems/23/lean/Erdos23Delta0/Gamma.lean
9d17a2dad9d7775023debc4edd975413920b5ef3fb490cdd08074553a0272ef6  problems/23/writeup/_codex_r29_fullbank_semantic_audit.py
5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6  tmp/fanout/r29_gate/lead/r29_lead_gate.py
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
668f427042c4666e21ec41ee454136aefce789a8cba8adacf703853ef373347c  tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py
```
