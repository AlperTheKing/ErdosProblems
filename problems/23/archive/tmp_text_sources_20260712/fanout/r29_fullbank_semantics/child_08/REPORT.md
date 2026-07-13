# Child 08 — ActiveScoped semantic diff

## Verdict

The production Lean relation is not a FullBank or checked-transfer relation. Its codomain is only `FreeHalf G omega`, and its complete relation is

> `EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). Its proof object is only

> `assign : Demand G c omega → FreeHalf G omega`
>
> `injective : Function.Injective assign`
>
> `available : ∀ d, Available G c d (assign d)`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158`). Thus all four FullBank token classes, rational capacities, component ownership, typed sources, spends, and traces are absent. Direct eligibility has exactly same-first and selected-row companion.

The R29 writeup correctly limits its falsifier to this selector/matching route and says full-bank capacity is absent (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`). `GOAL_LOOP.md:16` instead describes a required `CheckedTransferMatching` chain; the exact scoped search under Commands finds no such production declaration. That name is planned prose, not a compiled API.

## Import boundary

`ActiveScopedMinimumExchange` imports only `TwoRowRectangleExchange` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:1`), which imports `MinimumDemandCollisionHall` (`problems/23/lean/Erdos23Delta0/Gamma/TwoRowRectangleExchange.lean:1`). That imports `MinimumDemandRowSelection` and Hall (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:1-2`). `MinimumDemandRowSelection` imports `CheckedRowCompanionBaseTransfer` (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:1`), which imports `CheckedC5BaseTransfer` (`problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:1`). The terminal checkers are therefore in the environment, but `Available` does not consume their proof objects.

## Exact row and active-scope definitions

The row-choice universe is the dependent product

> `abbrev RowChoice (bads : List BadEdgeData) :=`
>
> `  (i : Fin bads.length) -> Fin (bads.get i).rows.length`

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:23-25`). Selected rows are `(bads.get i).rows.get (omega i)` (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:58-61`). Ordered co-occurrence multiplicity is

> `((selectedRows omega).filter fun row =>`
>
> `  decide (x ∈ row.verts ∧ y ∈ row.verts)).length`

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:78-82`). Selected support is the deduplicated union of consecutive row edges (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:68-76`). `activeEdges` filters graph edges by: both endpoints selected, `blueb = true`, and normalized edge absent from selected support (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:91-101`).

`activeGraph` has adjacency

> `x ≠ y ∧ normEdge x.1 y.1 ∈ activeEdges G c omega`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:28-39`). `ActiveOwner` means there is a listed bad edge whose two in-range endpoints are each reachable to `v` in that graph (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:41-49`). `activeDegree` is noncomputable: filtered adjacency-cardinality if `ActiveOwner`, zero otherwise (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:66-73`).

## Exact demands

The imported collision unit is

> `owner : Fin G.n`
>
> `other : Fin G.n`
>
> `copy : Fin (pairCount omega owner.1 other.1 - 1)`
>
> `half : Fin 2`

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:54-62`). There is no `owner ≠ other` field. Active collision demand is only the subtype

> `{d : CollisionHalf G omega // ActiveOwner G c omega d.owner}`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:51-54`); `other` need not independently be active.

Selected load is exactly `5 * pairCount omega v v` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:75-78`). HitNeed multiplicity uses truncated natural subtraction twice:

> `activeDegree G c omega v - (G.n - selectedLoad omega v.1)`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:80-84`). Its element type is `Σ v : Fin G.n, Fin (hitNeedUnits G c omega v)` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:86-90`).

The complete demand is exactly

> `ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106`). `demandOwner` returns the collision owner or HitNeed vertex (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:119-123`). Availability consequently depends on a demand only through that owner.

## Exact sources, reservations, capacities, and matching

The only source type is

> `sourceX : Fin G.n`
>
> `sourceY : Fin G.n`
>
> `half : Fin 2`
>
> `distinct : sourceX ≠ sourceY`
>
> `free : pairCount omega sourceX.1 sourceY.1 = 0`

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:64-73`). This is an ordered pair: `(x,y,h)` and `(y,x,h)` are distinct values. There is no capacity field. Injectivity makes each half a unit source, hence two units per free ordered pair unless half zero is reserved; the reverse ordered pair has its own two units.

The reservation is exactly

> `s.half.1 = 0 ∧`
>
> `(activeGraph G c omega).Adj s.sourceX s.sourceY ∧`
>
> `ActiveOwner G c omega s.sourceX`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-132`). This is narrower than imported `Reserved`, which is `half=0 ∧ normEdge ... ∈ activeEdges` (`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:75-80`).

For either demand class, eligibility is exactly

> `s.sourceX = owner ∨`
>
> `(0 < pairCount omega owner.1 s.sourceX.1 ∧`
>
> ` 0 < pairCount omega owner.1 s.sourceY.1 ∧`
>
> ` 0 ≤ sigma G c [s.sourceX.1, s.sourceY.1])`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142`). Same-first is literally the first disjunct; selected-row companion is literally the second. Freeness and distinctness come from the `FreeHalf` type. No other pattern occurs.

`HallCondition` quantifies over every finite demand shore and counts the filtered `FreeHalf` neighborhood (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:160-165`). The exact theorem conclusion is

> `Nonempty (Matching G c omega) ↔ HallCondition G c omega`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:167-170`). This is an abstract finite Hall proof, not a Boolean graph checker or a trace-producing theorem.

## Diff against FullBank and checked-terminal classes

“Present” below means the defining predicate literally occurs in `Available`; “indirect” means only a numerical effect or overlapping subcase occurs.

| Class/predicate | Production definition | Status in `Available` | Proof by definition |
|---|---|---|---|
| same-first | `s.sourceX = owner` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:136-142`) | **Present** | Literal first disjunct. |
| selected-row companion | positive `pairCount(owner,x/y)` and `0 ≤ sigma [x,y]` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:136-142`) | **Present** | Literal second disjunct. The executable wrapper checks `RowWitness`, `pairFree`, sigma, and owner activity (`problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:70-85`), but its proof object is not stored in `Matching`. |
| checked common-blue/C5 terminal | `blueb x owner = true ∧ blueb y owner = true ∧ dM [x,y] + 2 ≤ dB [x,y]` (`problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean:35-43`) | **Absent** | `EligibleOwner` has neither `blueb` conjunct nor the `+2` inequality. Overlap with a different disjunct does not represent this predicate. |
| FullBank `door` | `CapKind.door`; typed `CapSource.door edge` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31`; `problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`) | **Absent** | No exit-edge key, port, incidence, component key, or door cap; codomain is `FreeHalf`. |
| FullBank `vertexSlack` | `CapKind.vertexSlack`, `vertexSlackCapQ : ℚ`, `CapSource.vertexSlack` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-39`; `problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`) | **Indirect only** | `G.n - selectedLoad` reduces HitNeed (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:80-84`), but no vertexSlack source, rational cap, or spend exists. |
| FullBank `c5Base` | `CapKind.c5Base`, `c5BaseCapQ : ℚ`, `CapSource.c5Base` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-39`; `problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`) | **Pattern overlap only; capacity absent** | Same-first/row-companion can model some base cancellations, but there is no c5Base constructor, key, `capQ`, or spend. The separate common-blue predicate is absent. |
| FullBank `prune` | `CapKind.prune`, `pruneCapQ : ℚ`, `CapSource.prune` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-39`; `problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`) | **Absent** | No prune key, rank, slot transport, trace, cap, or disjunct occurs. |
| Door/non-Door sinks | token subtypes by `kind = door`/`!= door`, capacity `capQ / 25` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-49`) | **Absent** | No token count, ledger token, rational cap, or sink subtype. |
| typed own-Door incidence | `token (doorOf p)).source = CapSource.door (portEdge p)` and cap at least 25 (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:108-112`) | **Absent** | No port map, typed equality, or cap bound. |
| outside-component attachment | Python uses outside blue components attached to an owner's selected companions and a nonnegative union switch (`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:229-259`, `problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:297-311`) | **Absent** | No outside component or attachment set occurs in `EligibleOwner`; no production Lean declaration exists. |
| checked trace/matching | No production declaration found | **Absent** | `Matching` has only assignment, injectivity, and `Available`; no terminal tag, switch, loss proof, key, or emitted cap (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158`). |

FullBank's exact rational local cap is

> `doorCapQ + vertexSlackCapQ + c5BaseCapQ + pruneCapQ`

(`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:33-45`). A global token is `(comp, kind, sourceId, capQ)` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-74`), and its ledger has a rational local-by-token spend matrix plus reserve slacks (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:76-82`). `Checked` requires spend nonnegativity, per-token no-double-spend, no cross-component spend, and source uniqueness (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:195-209`). None is expressible by unit injection into `FreeHalf`.

`FullBankGlobalPackage.Checked` is an abstract hypothesis structure, not an existence theorem or executable checker: the module says it “does not assert existence” (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:6-9`). From it, the module proves `lengthSurplusGD rows ≤ 25 * etaQ G c` and `gammaOfGD G c rows ≤ (G.n : ℚ)^2` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:286-315`). The consumer does not add FullBank semantics to `Available`. `FullBankPortSinks` explicitly says legal edge-to-token incidence is absent and its sinks/caps do not assert Hall (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:80-81`).

## Executable implementations

The exact R29 implementation is `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py`.

- `rebuild_scope(I)` builds selected rows, ordered-pair `Counter`, support, active components/vertices/degrees, collisions, and truncated HitNeed (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:52-97`). HitNeed is `max(0, degree[v] - max(0, n - 5*load[v]))` (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:93-96`), matching Lean Nat subtraction.
- `owner_sources(I, pair, active_edges, active_vertices)` uses dictionaries `masks`/`reason`, companion sets, and ordered triples `(x,y,h)` (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:100-135`). Same-first is `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:110-119`, row-companion `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:120-134`, and reservation `h == 0 and norm(x,y) in active_edges and x in active_vertices` (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:116`, `tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:130`).
- The emitted schema says `ordered FreeHalf source triples` (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:153-156`). The two reason bits are exactly same-first and row-companion (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:181-186`); no FullBank class is implemented.
- `verify_hall_certificate(cert)` checks triple uniqueness and all owner-shore demand/neighborhood counts, including exact witness `19953,19925,28` (`tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py:28-46`).

The general research executable `problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py` defines `active_scoped_obligation_parts`, `active_scoped_obligation_score`, and `full_owner_flow` (`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:83-150`). It groups an ordered pair's halves into capacity two, or one when half zero is reserved (`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:267-277`), and runs exact integer Dinic flow (`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:29-80`, `problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:313-336`). `include_outside=True` adds outside-attachment arcs (`problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:297-311`). It is not a Lean FullBank ledger or checked-transfer proof object.

`tmp/fanout/global_min_proof/lead/pht_n12_heavy_gate.py` calls it with `scope="active"` and `include_outside=False` (`tmp/fanout/global_min_proof/lead/pht_n12_heavy_gate.py:54-67`). It uses exact `Fraction` residuals (`tmp/fanout/global_min_proof/lead/pht_n12_heavy_gate.py:71-89`); no float is evidence here.

## Contradictions / ambiguities

1. The comment says reserved half-zero cells “are consumed by endpoint hits before collision routing” (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-126`). But `Demand` already contains collision and HitNeed, while `Available` excludes `ScopedReserved` for every demand (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106`, `problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). Compiled `Matching` therefore assigns no reserved cell to HitNeed; HitNeed competes for unreserved cells. The comment describes a staged matcher not defined here.
2. `GOAL_LOOP.md:16` names a checked-transfer/FullBank chain, but no such compiled matching/trace declaration exists. Production ActiveScoped is only FreeHalf Hall.
3. `LedgerToken` still stores untyped `sourceId : Nat` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-74`). `TypedFullBankSources` is a separate replacement and says connection to the wall sink is a separate adapter obligation (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:6-14`). Typed Door legality must not be read into `FullBankGlobalPackage.Checked`.
4. R29 explicitly falsifies only the selector/matching route (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:5-12`), not the abstract FullBank implication.

## Unresolved gaps

- No compiled bridge maps ActiveScoped `Matching` to `FullBankGlobalPackage`, typed `CapSource`, Door incidence, or the length-surplus consumer.
- No production Lean checker chooses same-first/common-blue/row-companion/outside/prune traces and emits typed FullBank tokens.
- Reserved-half staging is unresolved: reserved cells are neither allocated to HitNeed nor exposed by a prior assignment.
- Outside attachment is executable Python only, not a production Lean predicate/disjunct.
- FullBank is an abstract checked-ledger implication; package existence remains external.

## Findings

1. Demand is exactly `ActiveCollisionHalf ⊕ ActiveHitNeed`, all unit elements.
2. Supply is exactly ordered, distinct, selected-row-free `(sourceX,sourceY,half)` values.
3. Capacity is unit/cardinality injection: two halves per free ordered pair, one after the exact half-zero reservation.
4. Availability is exactly same-first or selected-row companion, then scoped-reservation exclusion.
5. All four FullBank cap classes and ledger semantics are absent; vertex slack has only a demand-reduction analogue, and c5Base only overlapping base-pattern analogues.
6. R29's executable reconstruction implements this narrower two-pattern relation, not FullBank.

## Commands run

```powershell
Get-ChildItem -Force
rg --files -g "COMMON.md" -g "GOAL_LOOP.md" -g "CLAUDE_TO_CODEX.md" -g "R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md" -g "ActiveScopedMinimumExchange.lean" -g "*.lean"
rg --files tmp/fanout/r29_fullbank_semantics
Get-Content <context/source> | ForEach-Object { <number and print each line> }
rg -n "^import " problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
rg -n "^import |^(abbrev|def|noncomputable def|structure|inductive|theorem|class) |FreeHalf|CollisionHalf|RowChoice|pairCount|Reserved|Available|Eligible|RowCompanion" <imported Lean sources>
rg -n "CheckedTransferMatching|TransferMatching|CheckedTransfer|TransferTrace|OutsideAttachment|outsideAttachment|prune|c5Base|vertexSlack|door" problems/23/lean/Erdos23Delta0/Gamma
rg -n "ActiveScopedMinimumExchange|ScopedReserved|FreeHalf|full_owner_flow|owner_sources|same-owner|row-companion|outside-attachment|CapKind|CheckedTransferMatching" problems/23/writeup tmp/fanout/r29_gate tmp/fanout/global_min_proof -g "*.py"
Get-FileHash -Algorithm SHA256 -LiteralPath <every cited source>
```

Exact negative Lean search:

```powershell
rg -n "CheckedTransferMatching|TransferTrace|OutsideAttachment|outsideAttachment|prune" problems/23/lean/Erdos23Delta0/Gamma -g "*.lean"
```

It returned only FullBank `prune` declarations; no checked-transfer, trace, or outside-attachment declaration.

## SHA-256 hashes of every cited source

```text
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
6afe14d3a7b69b5c0a8193325896aea2061fb3c54965642b73f8a95200255258  problems/23/lean/Erdos23Delta0/Gamma/TwoRowRectangleExchange.lean
e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean
ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0  problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean
84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean
f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
668f427042c4666e21ec41ee454136aefce789a8cba8adacf703853ef373347c  tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py
83a2c1e97b6c69b0ea876ff6e00eca7b9baabe0a2cab23c2feba45c8a5119292  tmp/fanout/global_min_proof/lead/pht_n12_heavy_gate.py
26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1  problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py
```

