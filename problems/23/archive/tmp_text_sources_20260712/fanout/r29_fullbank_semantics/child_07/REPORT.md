# R29 FullBank semantic audit — child 07 executable implementation mapping

Snapshot: 2026-07-11T18:07:40.8202505+03:00. Read-only source audit; no production, Lean, coordination, progress, or sibling-lane file was edited.

## Executive verdict

The exact current relation is `Gamma.ActiveScopedMinimumExchange.Available`, not a symbol named `CheckedTransferMatching`:

> `EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s`

with `EligibleOwner` exactly

> `s.sourceX = owner ∨ (0 < pairCount ... owner ... sourceX ∧ 0 < pairCount ... owner ... sourceY ∧ 0 ≤ sigma ... [sourceX, sourceY])`.

These are defined at `problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:136` and `:144`. Thus current `Available` directly contains same-first (spelled `s.sourceX = owner`) and row-companion; common-bad is only an indirect row-companion subcase; outside-attachment, common-blue `c5Base`, Door, prune, and rational sink capacities are absent. Vertex slack appears only upstream in demand generation as

> `activeDegree G c omega v - (G.n - selectedLoad omega v.1)`

at `ActiveScopedMinimumExchange.lean:81`, not as an `Available` source.

`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py` is the faithful executable implementation for the all-anchor R29 instance. `rebuild_scope` reconstructs active components and demand (`:52-97`); `owner_sources` implements same-first, row-companion, and half-zero reservation (`:100-135`). It asserts demand 19,953, reach 19,925, defect 28 at `:177-187`.

Two audit-only executable extensions independently remove the defect:

* `tmp/fanout/r29_fullbank_gate/verify.py:198` adds outside-attachment and asserts max flows `[17325,17325,19925,19953]` at `:518-522`.
* `tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py:192` adds exact `CheckedC5BaseTransfer.Valid` common-blue terminals; it finds 216 new keys and a 28-key absorber at `:263-293`.

Neither extension is current Lean `Available`. The c5Base executable explicitly says the repair “creates no FullBank token spend” at `r29_c5base_absorber.py:372-377`. Outside-attachment theorem names occur only as planned prose at `coordination/CLAUDE_TO_CODEX.md:13898-13901`; no Lean definition was found.

“FullBank” denotes two different compiled APIs:

1. `Ell5FullBankInterface.FullBankRelaxedCoverCert` is a generic rational routing certificate with `lam`, `q`, and abstract `inc`, `kap`; obligations are `hroute`, `hcap`, `hqinc` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40`).
2. `Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked` is an aggregate token/spend ledger (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:177-227`) with no port-to-token relation. `FullBankPortSinks.lean:80-81` says “legal edge-to-token incidence is still absent from this package.” The compiled countermodel concludes

   > `emptyPackage.Checked ∧ ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls)`

   at `problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean:152-157`.

Therefore no Python/C++/JSON artifact is a faithful end-to-end executable R29 `FullBankGlobalPackage.Checked` provider with graph-derived typed incidence. The R29 gate records `UNDEFINED_WITHOUT_REAL_GRAPH_DERIVED_PROVIDER` at `tmp/fanout/r29_fullbank_gate/verify.py:416-443`.

## Commands run

All commands ran from `E:\Projects\ErdosProblems`.

```powershell
rg --files -g "COMMON.md" -g "GOAL_LOOP.md" -g "CLAUDE_TO_CODEX.md" -g "R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md" -g "*goal*" -g "*GOAL*"
rg --files tmp/fanout/r29_fullbank_semantics | rg "COMMON\.md$"
Get-Content GOAL_LOOP.md
Get-Content tmp/fanout/r29_fullbank_semantics/COMMON.md
Get-Content problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
Get-Content coordination/CLAUDE_TO_CODEX.md | Out-Null
Get-Content GOAL_CODEX.md | Out-Null
rg -n -i -C 3 "R29|FullBank|CheckedTransferMatching|sameFirst|commonBad|rowCompanion|outsideAttachment|EndpointReserve|off-support|sink capacit|vertexSlack|c5Base|ActiveScopedMinimumExchange|Available" coordination/CLAUDE_TO_CODEX.md
git grep -l -i -E "CheckedTransferMatching|sameFirst|commonBad|rowCompanion|outsideAttachment|EndpointReserve|FullBank|off[-_ ]support|sink capacit|vertexSlack|c5Base|prune|Door|ActiveScopedMinimumExchange|Available" -- "problems/23/**/*.lean" "problems/23/**/*.py" "problems/23/**/*.cpp" "problems/23/**/*.json"
git grep -n -E "(structure|abbrev|def) FreeHalf|def pairCount|def activeEdges|def selectedVertices" -- "problems/23/**/*.lean"
git grep -n "CheckedC5BaseTransfer\|TerminalData.adjustedSurplus\|CapSource.c5Base" -- "problems/23/**/*.lean"
git grep -n -E "PruneKey|CapKind\.prune|pruneCapQ|pruneIdentity|prune.*provider|prune.*token" -- "problems/23/**/*.lean"
git grep -n "Ell5FullBankRelaxedCover_exists\|checkedBaseCorridorPruneMatching_to_activeFullBank\|checkedMatching_withOutsideAttachment_sound" -- "problems/23/**/*.lean" "problems/23/**/*.md"
rg -n -F --glob '*.lean' --glob '*.py' --glob '*.cpp' --glob '*.json' CheckedTransferMatching problems/23/lean problems/23/writeup tmp/fanout/r29_fullbank tmp/fanout/r29_fullbank_gate tmp/fanout/r29_fullbank_lean tmp/fanout/r29_gate tmp/fanout/global_min_proof
rg -n -F --glob '*.lean' --glob '*.py' --glob '*.cpp' --glob '*.json' EndpointReserve problems/23/lean problems/23/writeup tmp/fanout/r29_fullbank tmp/fanout/r29_fullbank_gate tmp/fanout/r29_fullbank_lean tmp/fanout/r29_gate tmp/fanout/global_min_proof
rg --files <same scopes> | rg '\.(c|cc|cpp|cxx|h|hpp)$'
rg -n --glob '*.json' '"\$schema"|"type"\s*:\s*"object"|"required"\s*:' <same scopes>
rg -n "\bsorry\b|native_decide" <all cited Lean sources>
Get-FileHash -Algorithm SHA256 -LiteralPath <each cited source>
```

The first unrestricted scans over `.`/the full Lean tree were terminated after generated trees dominated runtime. Absence claims are limited to the explicit production/R29 scopes above. `CheckedTransferMatching` had no hit. `EndpointReserve` returned only Lean namespace/import hits. Nine C++ files exist in scope, but none contains the requested vocabulary. No formal JSON-Schema marker was found.


## Exact SHA-256 hashes for every cited source

Lowercase SHA-256 of file bytes at snapshot time:

```text
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
21bfc871fa147e131e8699b75079ab24690961a8359c6cf12dbac3b27350da26  GOAL_CODEX.md
387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
93150a508e19f634d93596b75e9950dc0d0cb72a393efdecb2efda97969bbd31  problems/23/lean/Erdos23Delta0/CertGraph.lean
e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean
ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0  problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean
84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean
f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
793f8b47926dbe93e2b0f476e42ae33a688913faa95e46912205ec69009a4eaa  problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean
9cfa35f2714799ddd4e1a187c2d6d620dae7c15d920f114896b4f30218274440  problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean
a9c4cebee9e5d1d63b4e38ad7203c05d18fdb8f8ef5f41684ebea07340aaa149  problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean
8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104  problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean
2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048  problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean
506ba26ca167045464c5c5bf45ece250a18a3870e1716e120027cc0a320da8b9  problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean
82da759aeb837967d293e57f58cabe5bf51198e5c2abc6f8c88a407c5ada22ba  problems/23/lean/Erdos23Delta0/NeutralLensLedger.lean
624c56995234f4ef5d68804013ce69d66962cfb2a3230de7c8d601db6870089f  problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean
5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6  tmp/fanout/r29_gate/lead/r29_lead_gate.py
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
018836f5df6459ccdd413e4dde3a31f52ec7cdc209759e587e4f5755c1d8c902  tmp/fanout/r29_fullbank_gate/verify.py
73e5d8d9ffd0e11a02428cc9b8df3943bdd77884ed18c277a1f7c1f04006cb0c  tmp/fanout/r29_fullbank_gate/RESULT.json
3d9ae4475a6cee19294a93ee1aa877719c79889d1aedf8c1abeff46284f55b64  tmp/fanout/r29_fullbank/B_fourpattern/verify_fourpattern.py
653663a87635db27854a1cacb58497370faee9215b7547b46fa39771d5e57f9f  tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py
15c15a07fd30c8a5d2431dbf7059f29acbef104b1cdbbcc7bb8dedec13c44e46  tmp/fanout/r29_fullbank/E_source_search/doors/audit_doors.py
587ed8c4e5d7b30e660036ce1a3b2e0221f96618f3491202f24fdf944b0c1179  tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py
7bd32c87ed879d3fcb3bf63b231738da2547c8986e7dca69176abdf7fa3a192f  tmp/fanout/r29_fullbank/E_source_search/flow_dual/check_certificate.py
3ff3db60553da97e581d42d42344f3626c2a3629638933390cb646fd781c5465  tmp/fanout/r29_fullbank/E_source_search/flow_dual/flow_instance.json
6ef8a3af62b615791ccaf4e17bd1def4aeec59ec5dea8a975a0ae5891d4a2338  problems/23/writeup/_claude_r20_staged_matching_gate.py
6147ac4c7b501f8ab46597ef210838e1138f0b7cb15910a4712dc5efac844cec  problems/23/writeup/_claude_r23_outside_attachment_gate.py
26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1  problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py
846a4cb388de50913da35753c012a2d9d29dddbc5725a74c2251084dae72e84c  problems/23/writeup/_codex_r23_double_star_fullbank_audit.py
d2b06fe7f9f017707fe8db76e70cba97204d2239d65eb0b4604db01cf46319aa  tmp/fanout/r29_fullbank/C_fullbank/d4_c5base/audit_c5base.py
ebbccece440ec3659858b35f43d109df3a45c45d0e2b2d41ae94b2f4176f8f72  tmp/fanout/r29_fullbank/C_fullbank/d5_prune/replay.py
8bc975f409136deecd9b4fdf590aef84e1b2805141e850529864d2bd8b558d7f  tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py
3d763d47710edb4d60748b75d03317a4b007f9ab3203fe8794612bd5fea27c83  tmp/fanout/r29_fullbank/C_fullbank/d6_flow/input.json
```


## Findings

### Production matching baseline

FreeHalf is ordered (sourceX, sourceY, half), with distinct coordinates and exact pairCount = 0 (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:66-73). Active demand is ActiveCollisionHalf ⊕ ActiveHitNeed (ActiveScopedMinimumExchange.lean:102-106). ScopedReserved removes only half zero of an active edge with active first coordinate (:127-132). Matching is an injective function into FreeHalf satisfying Available (:154-158): unit-cardinality Hall, not capacitated FullBank routing.

The Python match is clause-for-clause:

* active edges/components: rebuild_owner_hall.py:52-97;
* collision 2 * sum(max(0,pair[v,y]-1)): :93, matching CollisionHalf's Fin(pairCount-1) and Fin 2 at MinimumDemandCollisionHall.lean:54-62;
* HitNeed with two truncated subtractions: rebuild_owner_hall.py:94-96, matching ActiveScopedMinimumExchange.lean:81-84;
* same-first, row-companion, and reservation: rebuild_owner_hall.py:110-134.

### Concept-by-concept executable mapping and comparison with Available

| Concept | Exact file:function/data structure | Current Available status |
|---|---|---|
| CheckedTransferMatching | No Python/C++/JSON/Lean symbol in scoped search. Closest compiled object: ActiveScopedMinimumExchange.Matching at ActiveScopedMinimumExchange.lean:154-158. Name is planned prose in GOAL_LOOP.md:16 and coordination/CLAUDE_TO_CODEX.md:13807-13810. | **Absent as named object.** No trace, terminal-kind tag, or FullBank output. |
| sameFirst | rebuild_owner_hall.py:100 owner_sources, branch :110-119; duplicate r29_fullbank_gate/verify.py:231-243; cell version B_fourpattern/verify_fourpattern.py:237-240. | **Present under another name:** first EligibleOwner disjunct “s.sourceX = owner” (ActiveScopedMinimumExchange.lean:136-142). |
| commonBad | Explicit branch in r29_fullbank_gate/verify.py:245-256 and B_fourpattern/verify_fourpattern.py:242-246; older aggregate gate _claude_r20_staged_matching_gate.py:163-183. | **Indirect only.** No named Lean branch. Bad neighbors co-occur with owner on selected rows, so this is row-companion when pair-free and sigma ≥ 0. Adds zero unique R29 keys (verify.py:518-520). |
| rowCompanion | Faithful R29 code rebuild_owner_hall.py:120-134; gate verify.py:258-272; duplicate B_fourpattern/verify_fourpattern.py:248-253. Separate Boolean checker TerminalData.check at CheckedRowCompanionBaseTransfer.lean:94-105. | **Present:** positive owner/source co-occurrence twice plus sigma ≥ 0 (ActiveScopedMinimumExchange.lean:136-142). Separate RawValid (:70-85) is not consumed by Available. |
| outsideAttachment | r29_fullbank_gate/verify.py:167-195 builds components; staged_sources admits pairs at :274-314. Independent implementation B_fourpattern/verify_fourpattern.py:134-170,255-264. Older full-obligation gate _codex_r23_outside_attachment_full_obligation_gate.py:229-311. | **Absent.** No Lean definition/theorem. Strict extension: 912,600 half slots; max flow 19,925→19,953 (verify.py:518-522,538). |
| Door | CapKind.door at FullBankToLengthSurplusCharge.lean:25-31; CapSource.door at TypedFullBankSources.lean:23-41; conditional checkOwnEdgeDoors at :108-128; adapter fields TypedOwnDoorHalfLayer.lean:34-42; generic certificate_of_singletonCore_allDoors at Ell5SingletonVertexSlack.lean:429-479. | **Absent.** FullBank sink, not FreeHalf eligibility. Typed realization requires supplied data/adapter. |
| vertexSlack | Correct all-anchor audit E_source_search/vertex_slack/replay.py:17-46, testing cap=max(0,n-T[v]) against half incidence at :27-36. Production constructor at Ell5SingletonVertexSlack.lean:381-420. Double-star executable _codex_r23_double_star_fullbank_audit.py:124-158. | **Indirect only:** slack is subtracted in HitNeed, not an Available sink. Lean constructor takes abstract kap/hinc. R29 code finds four negative margins and records compiled graph incidence false (replay.py:46-66). |
| c5Base | TerminalData.Valid requires two blue source-owner edges and dM([x,y])+2 ≤ dB([x,y]) (CheckedC5BaseTransfer.lean:35-43); checker :50-56. Exact R29 c5base_source_masks at r29_c5base_absorber.py:192-223, repair :263-293. Typed source only at TypedFullBankSources.lean:23-41. | **Absent, but exact executable extension exists.** 216 new keys (r29_c5base_absorber.py:271-274). No Lean adapter to Available or unique bank-token incidence. |
| prune | Abstract kind/cap fields FullBankToLengthSurplusCharge.lean:25-54; typed constructor TypedFullBankSources.lean:23-41; abstract LedgerSep.pruneIdentity NeutralLensLedger.lean:21-28. Audit C_fullbank/d5_prune/replay.py:30-49 checks no provider fragments and sets justified token/capacity zero at :60-88. | **Absent.** No prune eligibility/slot transport in Available; no graph-to-token constructor. |
| EndpointReserve | No Python/C++/JSON implementation by literal search. Lean endpointReserveInc/cap at EndpointReserveHall.lean:31-40; endpointReserveHallOn consumes eta, cap, budget, sets at :144-154. CollisionTokenAssignment.Assignment packages eta/capacity/need/legality at CollisionTokenAssignment.lean:25-35; hall_of_assignment concludes subset Hall at :48-56. | **Absent/separate.** Provider-consuming theorem, not FreeHalf Available; no provider existence/external executable. |
| FullBank | Generic FullBankRelaxedCoverCert (Ell5FullBankInterface.lean:27-40); aggregate GlobalLedgerData/FullBankGlobalPackage (FullBankToLengthSurplusCharge.lean:78-83,134-143); partial JSON flow gate C_fullbank/d6_flow/gate.py:42-94. | **Absent/separate.** Soundness concludes “lengthSurplusGD rows ≤ 25 * etaQ G c” only from supplied P.Checked (FullBankToLengthSurplusCharge.lean:286-315). No R29 constructor. |
| off-support routing | Generic q obligations hroute/hcap/hqinc (Ell5FullBankInterface.lean:31-40). mixedDoorVertexQ sends Door edges to own sink and others to endpoints (Ell5SingletonVertexSlack.lean:481-495). Boundary/internal bridge assumes legality/capacity (Ell5InternalEndpointSlackFullBank.lean:72-100). Python sets F, O=blue-F at vertex_slack/replay.py:20-26. | **Indirect only.** Available reserves one FreeHalf orientation; it does not route off-support load. |
| sink capacities | Matching.assign is injective (ActiveScopedMinimumExchange.lean:154-158). LedgerToken.capQ at FullBankToLengthSurplusCharge.lean:67-74; spendOfToken ≤ capQ at :199-200; Hall cap capQ/25 at FullBankPortSinks.lean:41-49; typed Door requires raw capQ ≥ 25 at TypedFullBankSources.lean:108-112. Four-pattern cell cap is 1 on reserved active cell, 2 otherwise (B_fourpattern/verify_fourpattern.py:224-226). Rational flow gate scales denominators (C_fullbank/d6_flow/gate.py:60-94). | **Absent as rational capacity.** Python 1/2 values count FreeHalf slots, not LedgerToken.capQ or wall-sink capacity. |

### Python/JSON/C++ status

No formal JSON Schema exists in scope; formats use ad hoc version strings and hand-coded parsers.

* Owner-Hall records emitted at rebuild_owner_hall.py:153-174 are {x,y,half,owner_mask,reason_mask}: closest serialized current Available.
* tmp/fanout/r29_fullbank_gate/RESULT.json:219 is R29_FULLBANK_GATE_V1; row-companion and outside max flows are at :487-499,581-593. It is output, not an input schema/kernel checker.
* C_fullbank/d6_flow/gate.py:42-94 hand-validates locals {id,component,demandQ,allowedTokens} and tokens {id,component,kind,source,capacityQ,provider.assumed}. Shipped input.json:8-19 has tokens=[] and labels demands as probes. It omits row ownership, local-view equalities, reserve identities, and superadditivity from Lean Checked.
* E_source_search/flow_dual/check_certificate.py:25-75 validates r29_fullbank_residual_flow_v1; its instance has no proved tokens/arcs and marks Door, vertexSlack, c5Base incidence unknown (flow_instance.json:19-52). It predates c5Base terminal enumeration; the terminal-to-bank-token adapter remains missing.
* c5Base absorber JSON has no schema field; producer structure is at r29_c5base_absorber.py:323-381.
* No relevant C/C++ implementation was found.

### Context status

GOAL_LOOP.md:1-4 self-identifies v6.1/current and names the desired architecture at :12-17. GOAL_CODEX.md was readable as a candidate attachment, but no distinct active-attachment handle/path was exposed; it did not override newer GOAL_LOOP.md. The R29 writeup correctly says the descent interface remains abstract while full-bank capacity is absent from active-scoped FreeHalf matching (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96).


## Contradictions and ambiguities

1. **The current gate's “r29IsFullBankFalsifier: false” exceeds compiled evidence.** tmp/fanout/r29_fullbank_gate/RESULT.json:597-599 simultaneously says compiled end-to-end instantiation is UNDEFINED_WITHOUT_REAL_GRAPH_DERIVED_PROVIDER, the operational four-pattern relation passes, and r29IsFullBankFalsifier is false. Source explicitly separates those questions (verify.py:1-10). Defensible conclusion: not a falsifier of that operational relation; compiled FullBank status unresolved.

2. **Door census is labeled all-anchor but executes baseline rows.** tmp/fanout/r29_fullbank/E_source_search/doors/audit_doors.py:28 sets rows = d["rows"]. Constructor forms those with displayed selector rows (tmp/fanout/r29_gate/lead/r29_lead_gate.py:158-192,252-272) and calls data["rows"] the baseline with score 30,811 (:399-400). All-anchor requires replacing every selector with anchorRow (:402-405; also r29_fullbank_gate/verify.py:107-111). Door census reports core 2,803 (audit_doors.py:36), but correct all-anchor gate asserts 2,127 selected vertices (verify.py:527). Its 56-exit/load-28 result is stale for the assigned tuple.

3. **commonBad has incompatible readings.** R20/R23 gates use two bad-edge neighbors plus pair loss ≥ 0 (verify.py:245-256). CheckedC5BaseTransfer instead checks two blue neighbors and stronger sigma ≥ 2 (CheckedC5BaseTransfer.lean:35-43). Current Available names neither: bad-neighbor commonBad is absorbed by row-companion; common-blue c5Base is absent and adds new R29 keys.

4. **Older c5Base “relabeling” audit is stale as matching evidence but valid as ledger warning.** C_fullbank/d4_c5base/audit_c5base.py:41-45 only relabels existing FreeHalf keys and fixes independent_base_keys empty. New executable finds 216 new common-blue keys (r29_c5base_absorber.py:263-274). It still creates no FullBank token spend (:372-377), so “no concrete R29 full-bank c5Base ledger” remains true.

5. **Compiled FullBank APIs are not interchangeable.** FullBankRelaxedCoverCert includes q/inc/kap routing; FullBankGlobalPackage.Checked has aggregate spend but no port incidence. AggregateLedgerNoIncidenceCounterexample.lean:145-157 formally blocks deriving half-layer routing from the latter.

6. **Capacity units are conflated in prose/artifacts.** FreeHalf slots are integers; relaxed-cover kap is Hall-scale rational; LedgerToken.capQ is raw length-surplus scale; FullBankPortSinks divides by 25. Python four-pattern capacities 1/2 are slot multiplicities, not capQ.

7. **Planned names are not production symbols.** CheckedTransferMatching, checkedBaseCorridorPruneMatching_to_activeFullBank, and checkedMatching_withOutsideAttachment_sound occur in goal/coordination/writeup prose but no Lean declaration. Ell5FullBankRelaxedCover_exists is also only described as remaining open prose at Ell5FullBankInterface.lean:7-11; scoped production search found no declaration.

## Unresolved gaps

1. Missing compiled extension of ActiveScopedMinimumExchange.Available consuming CheckedC5BaseTransfer.TerminalData.Valid, despite exact 28-key R29 witness.
2. Missing compiled outside-attachment predicate/checker/soundness theorem.
3. Missing CheckedTransferMatching trace/certificate structure and theorem mapping an extended injective matching to ActiveComponentFullBankCert or FullBankGlobalPackage.Checked.
4. Missing graph-derived R29 typed token ledger with unique Door/vertexSlack/c5Base/prune keys, capacities, and legal port incidence. FullBankPortSinks supplies only subtypes and capQ/25.
5. Missing graph-to-prune provider connecting LedgerSep.pruneIdentity to PruneKey, nonnegative capacity, incidence, and no-double-spend.
6. EndpointReserveHall and CollisionTokenAssignment remain provider-consuming; no Python or Lean provider constructs eta for R29.
7. Correct all-anchor Door/off-support census must replace baseline rows. Correct vertexSlack audit shows boundary count 2,760 and four negative N-T endpoint margins, but no mixed Door/vertex/c5Base/prune provider is tested.
8. c5Base repair proves a matching fact, not FullBank. An adapter must decide whether FreeHalf keys are matching slots, typed BaseKey tokens, or both, and prove deduplication if both consume them.
9. No formal JSON Schema exists for current certificate formats; version strings do not ensure compatibility with Lean structures.

