# R29 FullBank semantic audit — Door and boundary routing (child 04)

## Verdict

Production Lean has four distinct Door layers:

1. abstract wall `Sink` with caller-supplied `legal` and `cap`;
2. edge-indexed local FullBank sinks (`Sym2 V`, normally a sum-type right summand) with caller-supplied own-edge incidence/capacity;
3. aggregate legacy ledger tokens tagged `CapKind.door`, with spend bookkeeping but no edge incidence;
4. separate typed sources `CapSource.door edge`, checked against a port edge and embedded into wall sinks only through an explicit adapter.

`Gamma.ActiveScopedMinimumExchange.Available` contains none of them. It relates `Demand` only to `FreeHalf` using `EligibleOwner ∧ ¬ScopedReserved`; it has no Door token/source/sink, boundary predicate, incidence, capacity, token component, source uniqueness, or no-double-spend. The R29 writeup therefore correctly calls the witness a falsifier to FreeHalf matching, not Problem #23, and names “the full-bank capacity that is absent from the active-scoped FreeHalf matching” (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`).

The goal's chain “active-component flow + boundary own-Door routing => ActiveComponentFullBankCert => Checked FullBankGlobalPackage” is partly planned prose (`GOAL_LOOP.md:16`). There is no Lean symbol `ActiveComponentFullBankCert`; compiled active-component constructors return `FullBankRelaxedCoverCert`. The global package is aggregate accounting and does not contain a local certificate's `inc/q` data.

## Exact production semantics

### Abstract and generic sinks

`BankedWallLP` declares abstract `Port` and `Sink`, then

> `legal : Port → Sink → Prop`
>
> `cap : Sink → ℚ`

(`problems/23/lean/Erdos23Delta0/BankedWallLP.lean:32-53`). Its primal has `q : I.Port → I.Sink → ℚ`, requires nonzero `q` to be legal, routes every port load, and enforces `∑ p, q p s ≤ I.cap s` (`problems/23/lean/Erdos23Delta0/BankedWallLP.lean:60-70`). The type itself does not identify Door sinks; its comment puts kind/source labels at the extractor layer (`problems/23/lean/Erdos23Delta0/BankedWallLP.lean:17-20`). Relative to `Available`: **absent**.

`FullBankRelaxedCoverCert` is generic in sink type `JT`, `inc : E → JT → Prop`, and `kap : JT → ℚ`. It stores `q : E → JT → ℚ` and proves routing, per-sink capacity, and positive-flow incidence:

> `hroute : ... load ... ≤ ∑ j ∈ J, q c j`
>
> `hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j`
>
> `hqinc : ... 0 < q c j → inc c j`

(`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:23-40`). Door is a caller specialization, not a constructor. Relative to `Available`: **absent**.

### Edge-indexed local Door sinks

The generic bank-flow sink is

> `abbrev BlockBankSink (JT V : Type*) := JT ⊕ Sym2 V`

(`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-22`). `Sum.inl` is the non-Door pool; `Sum.inr e` is edge `e`'s Door. The executable router is

> `| Sum.inl j => if c ∈ D then 0 else qBase c j`
>
> `| Sum.inr e => if c ∈ D then if c = e then blockLoad ... c else 0 else 0`

(`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:28-38`). Thus a Door edge routes its actual block load only to the identical edge key. The constructor requires `hD : D ⊆ O`, `hincDoor : ∀ e ∈ D, inc e (Sum.inr e)`, and `hdoor : blockLoad ... e ≤ kap (Sum.inr e)` (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:42-67`). All are **absent** from `Available`.

The mixed vertex/Door sink is `V ⊕ Sym2 V`. `mixedDoorVertexQ` sends Doors only to the identical `Sum.inr` edge, while non-Doors split to core vertices (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:481-495`). Its constructor separately assumes `D ⊆ O`, endpoint incidence for `O \ D`, own-Door incidence, vertex capacity, and Door load capacity (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:515-535`). Relative to `Available`: **absent**.

### Aggregate legacy tokens

Spendable kinds are exactly

> `CapKind.door | vertexSlack | c5Base | prune`

with no eta constructor (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31`). A legacy `LedgerToken` has

> `comp : Fin componentCount; kind : CapKind; sourceId : Nat; capQ : ℚ`

(`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-74`). `FullBankGlobalPackage.Checked` requires kind-spend identities, nonnegative spend/caps, per-token `spendOfToken ≤ capQ`, no positive cross-component spend, and uniqueness on `(comp,kind,sourceId)` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:177-209`). This is real aggregate ownership/no-double-spend, but `sourceId : Nat` has no Door edge semantics.

`DoorToken P` is only

> `{t : Fin P.tokenCount // (P.ledger.token t).kind = CapKind.door}`

and its Hall cap is `capQ / 25` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-25,41-49`). The file expressly says:

> `legal edge-to-token incidence is still absent from this package.`
>
> `Thus these finite sinks and capacities do not assert a Hall condition.`

(`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:80-81`). Relative to `Available`, token kind/component/source/cap/spend/uniqueness are **absent**. `ActiveOwner` is only an indirect component notion, not token ownership.

### Typed Door sources

The separate source universe is

> `CapSource.door (edge : ExitEdgeKey)`
>
> `| vertexSlack ... | c5Base ... | prune ...`

(`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`). `TypedLedgerToken` contains `comp`, typed `source`, and `capQ` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:61-67`). `OwnEdgeDoorSourceData` supplies `portEdge`, tokens, and `doorOf : Port → Fin tokenCount` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:91-99`). Its exact checked proposition is

> `Function.Injective D.portEdge ∧`
>
> `(∀ p, (D.token (D.doorOf p)).source = CapSource.door (D.portEdge p)) ∧`
>
> `(∀ p, 25 ≤ (D.token (D.doorOf p)).capQ)`

(`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:108-112`). `doorLegal` is source equality; `doorOf` is proved injective; `hallCapQ t := capQ / 25`, so checked Doors have Hall cap at least one (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:130-159`).

Connection to wall `Sink` is explicitly a separate obligation (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:12-14`). `DoorWallAdapter` gives injective `sinkOf`, maps typed Door legality to wall legality, and equates wall cap with typed Hall cap (`problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean:34-42`). `halfLayerRouted_of_checkedEdgeDoorSources` uses `A.sinkOf (D.doorOf p)` and derives injectivity, legality, and capacity (`problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean:59-85`). This typed data is **not** a field of current `FullBankGlobalPackage`, which still contains legacy `GlobalLedgerData` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:131-143`). Relative to `Available`: **absent**.

## Capacities and scales

- Abstract wall/local certificate: arbitrary exact rational `cap/kap`, subject to nonnegativity and routed-load inequalities (`problems/23/lean/Erdos23Delta0/BankedWallLP.lean:52-70`; `problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:33-40`).
- Typed Door: raw `capQ ≥ 25`; Hall-scale `capQ/25 ≥ 1` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:108-112,151-159`).
- Disjoint-petal own-Door: `door_capacity : ∀ p, 1 ≤ I.cap (door p)` (`problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueeze.lean:100-114`). Load goes only to `door p`, and injectivity prevents another port consuming it (`problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueeze.lean:127-193`).
- Boundary block-singleton Door: exact boundary load `1/2`; required cap `1/2 ≤ kap e` (`problems/23/lean/Erdos23Delta0/Ell5BlockSingleton.lean:308-326,373-386`).
- Endpoint-half all-Doors fast path: every `e ∈ cutEdges G s \ F` needs `inc e e` and `1 ≤ kap e` (`problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean:19-33`). This is stronger than boundary-only half-unit routing.
- Global ledger Door cap: arbitrary nonnegative `capQ`, checked only against total spend and component reserves (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:195-227`); raw 25 is not inferred.

None of these capacities occurs in `Available`.

## Boundary-own-Door routing

The explicit bridge defines

> `O := cutEdges G s \ F`
>
> `D := O.filter fun e => edgeBoundary C e = true`
>
> `I := O.filter fun e => e ∈ C.sym2`

(`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:56-67,101-103`). It does not infer Door availability. The caller must supply

> `hboundaryDoorLegal : ... edgeBoundary C e = true → inc e (Sum.inr e)`
>
> `hboundaryDoorCapacity : ... edgeBoundary C e = true → 1/2 ≤ kap (Sum.inr e)`

(`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:72-100`). Internal non-Doors spend endpoint slack; boundary Doors use their own edge sink (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:104-134`).

Active-component Hall is deliberately only over `E0 O D := {e // e ∈ O ∧ e ∉ D}`. `ActiveComponentBankHall` routes those non-Doors against generic sinks (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:23-64`). Its constructor then separately assumes `incDoor e e` and `blockLoad ... e ≤ kapDoor e` for `e ∈ D`, returning `FullBankRelaxedCoverCert` over the disjoint sink sum (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:107-133`). Boundary own-Doors are supplied after Hall, not discovered by it.

`InactiveComponentBlockChecker.Candidate` stores Boolean `legal` and rational `capacity`; validity tests boundary own-edge legality and cap at least `1/2` (`problems/23/lean/Erdos23Delta0/InactiveComponentBlockChecker.lean:42-75`). Boolean `check` reflects these hypotheses, and `certificate_of_check` returns a local FullBank certificate (`problems/23/lean/Erdos23Delta0/InactiveComponentBlockChecker.lean:77-111`). It checks supplied Door data; it is not an extractor.

## Comparison with `Gamma/ActiveScopedMinimumExchange.Available`

The demand is

> `Demand ... := ActiveCollisionHalf ... ⊕ ActiveHitNeed ...`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106`). The source is `FreeHalf`, and the exact predicate is

> `Available ... d s := EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s`

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). `EligibleOwner` is same-first or row-companion ownership with nonnegative `sigma` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142`). `ScopedReserved` excludes half-zero cells on active edges (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-132`). `Matching` is an injective `Demand → FreeHalf` satisfying `Available` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158`).

| Class/predicate | Status in `Available` |
|---|---|
| `EligibleOwner`, `ScopedReserved` | **Present directly**; they are the whole relation. |
| `ActiveOwner`, `demandOwner` | **Present**, but only demand scope/owner identity; not Door/token ownership. |
| `CapKind.door`, `LedgerToken`, `DoorToken` | **Absent**. |
| `CapSource.door`, `doorOf`, `doorLegal` | **Absent**. |
| wall/local `Sink`, `legal/inc`, `cap/kap`, routed `q` | **Absent**. |
| `edgeBoundary C e`, Door set `D` | **Absent**. |
| own-edge eligibility/source equality | **Absent**. |
| Door capacities (`1/2`, `1`, raw `25`) | **Absent**. |
| token component/source uniqueness/no-cross-spend/no-double-spend | **Absent**. |
| active-component non-Door Hall | **Only indirect**: both scope by active components, but domains/sources/incidence/caps differ. |
| disjoint-petal injective own-Door routing | **Absent**. |

R29's executable reconstruction matches this narrow surface. `owner_sources` emits only `(x,y,h)` FreeHalf triples using same-first/row-companion tests and reserved-half exclusion (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:100-135`); its schema is “ordered FreeHalf source triples” (`tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:153-173`). A scoped search found no Door/FullBank symbol in R29 replay Python. Consequently R29 Door count/capacity cannot be computed without inventing provider data.

## Executable implementations/exporters

Production/kernel-side definitions:

- `OwnEdgeDoorSourceData.checkOwnEdgeDoors`: `Bool := decide D.Checked`, with theorem `checkOwnEdgeDoors = true ↔ D.Checked` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:114-128`). This checks supplied arrays; it is not an extractor.
- `DisjointPetalHalfSqueezeChecker.checkCandidate`: checks disjoint shores, boundary identities, injective Door map, legality, unit cap, and cap nonnegativity (`problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueezeChecker.lean:26-62`). Its header says no real extractor is asserted (`problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueezeChecker.lean:3-9`).
- `InactiveComponentBlockChecker.check`: checks supplied graph/core/block/Door data (`problems/23/lean/Erdos23Delta0/InactiveComponentBlockChecker.lean:77-111`).
- `mixedDoorBlockBankQ`, `mixedDoorVertexQ`, `blockDoorQ`: parameter-driven routing matrices. `blockDoorQ` is boundary-and-same-edge => block load, otherwise zero (`problems/23/lean/Erdos23Delta0/Ell5BlockSingleton.lean:124-133`).

Python/external definitions:

- `_codex_wall_r5_359_gate.py`: `door_sink(port) = ("door", port[0])`; `sink_cap` gives Doors `Fraction(25)`; exact external load is `Fraction(1,2)` (`problems/23/writeup/_codex_wall_r5_359_gate.py:183-212,258-272`). Its result says `"actual_graph_to_bank_constructor_missing": True` (`problems/23/writeup/_codex_wall_r5_359_gate.py:284-313`), so this is fixture evidence, not an exporter.
- `tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py`: exact generic allocator. It accepts kinds `{door,vertexSlack,c5Base,prune}`, keys tokens by `(component,kind,source)`, and uses explicit `allowedTokens` (`tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py:8-15,42-69`). It rejects token capacity lacking an explicit provider assumption (`tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py:53-58`). It allocates supplied tokens but constructs no R29 Door/incidence/capacity.
- `_codex_branchb_door_ownership_gap_audit.py`: explicitly “does not prove the door-ownership certificate” (`problems/23/writeup/_codex_branchb_door_ownership_gap_audit.py:1-10`) and emits `MISSING_MACHINE_CHECKABLE_DOOR_OWNERSHIP` when no explicit hook exists (`problems/23/writeup/_codex_branchb_door_ownership_gap_audit.py:116-150`). It is an absence scanner.

No Python exporter for `CapSource`, `TypedLedgerToken`, `doorOf`, `FullBankGlobalPackage`, or `FullBankRelaxedCoverCert` was found. Scoped command:

```powershell
rg -n --glob '*.py' 'sourceId|tokenCount|spendQ|checkOwnEdgeDoors|TypedLedgerToken|CapSource|doorOf|FullBankGlobalPackage|FullBankRelaxedCoverCert' problems/23/writeup tmp/fanout/r29_gate tmp/fanout/global_min_proof
```

Result: `NO_TYPED_OR_GLOBAL_PACKAGE_EXPORTER_MATCHES`.

R29-only command:

```powershell
rg -n -i --glob '*.py' '\bdoor\b|DoorToken|CapSource|OwnEdgeDoorSourceData|FullBankGlobalPackage|FullBankRelaxedCoverCert|incDoor|kapDoor|doorOf' tmp/fanout/r29_gate tmp/fanout/global_min_proof problems/23/writeup/_claude_r29_2943_structural_gate.py
```

Result: `NO_MATCHES`.

## Contradictions/ambiguities

1. Coordination requested typed sources “replacing sourceId : Nat” (`coordination/CLAUDE_TO_CODEX.md:13787-13789`), but current `FullBankGlobalPackage` still uses legacy `sourceId : Nat` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-74,131-143`). Typed sources are separate.
2. `DoorToken` proves kind only, not own-edge legality; the source says incidence is absent (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-25,80-81`).
3. `ActiveComponentFullBankCert` occurs only in planned writeups (`problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md:34`; `problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:49`). `git grep` found no Lean symbol. Production returns `FullBankRelaxedCoverCert` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean:107-133`).
4. “Door ownership” can mean own-edge incidence, token component/no-double-spend, or Branch-B cactus credit ownership. These are non-equivalent. The cactus map remains absent.
5. Boundary membership is computed, but Door legality/capacity are hypotheses (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:72-100`).
6. Capacity scale depends on constructor: raw 25/Hall 1, boundary half-unit, or all-Doors unit.

## Unresolved gaps

1. No graph-derived R29 provider enumerates boundary Doors, maps them to typed sources, supplies caps, or proves incidence.
2. No adapter embeds typed Door tokens into legacy `FullBankGlobalPackage` with global uniqueness/no-double-spend.
3. No production package joins checked local `FullBankRelaxedCoverCert` (`inc/q/kap`) to checked aggregate `FullBankGlobalPackage`.
4. No Lean `ActiveComponentFullBankCert` type joins active non-Door Hall to boundary Doors.
5. Branch-B cactus door-credit ownership has no machine-checkable map.
6. Exact incremental R29 Door capacity is unresolved, not zero: the provider is absent, so assigning Doors would be speculative.

## Commands run

```powershell
Get-Content (numbered) COMMON.md, GOAL_LOOP.md, coordination/CLAUDE_TO_CODEX.md, R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md, and every cited source
rg/git grep scoped Door/FullBank/Available symbols across production Lean, writeups, and R29 scripts
git grep -n 'ActiveComponentFullBankCert' -- problems/23/lean/**/*.lean problems/23/writeup/*.md
rg -n --glob '*.py' 'sourceId|tokenCount|spendQ|checkOwnEdgeDoors|TypedLedgerToken|CapSource|doorOf|FullBankGlobalPackage|FullBankRelaxedCoverCert' problems/23/writeup tmp/fanout/r29_gate tmp/fanout/global_min_proof
rg -n -i --glob '*.py' '\bdoor\b|DoorToken|CapSource|OwnEdgeDoorSourceData|FullBankGlobalPackage|FullBankRelaxedCoverCert|incDoor|kapDoor|doorOf' tmp/fanout/r29_gate tmp/fanout/global_min_proof problems/23/writeup/_claude_r29_2943_structural_gate.py
Select-String -Pattern '\bsorry\b|native_decide' on all cited Lean files
Get-FileHash -Algorithm SHA256 on every cited source
```

The forbidden-token search had no match. No Lean build was run; this was read-only semantic/signature inspection.

## SHA-256 hashes of every cited source

```text
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
ae5b0716b917265b5cf427557a8ee562d6889286da8c4e104c5a107f6cff6ccb  problems/23/lean/Erdos23Delta0/BankedWallLP.lean
8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104  problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean
f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
793f8b47926dbe93e2b0f476e42ae33a688913faa95e46912205ec69009a4eaa  problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean
2a01e4c4e1a11dc9959582f7e1618dbb417c585d913b69975853cc4ba17f6f84  problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueeze.lean
3832cb92044b89cbd1a27e9044efdf2a912e499925fdf40c282d9502495a2e44  problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueezeChecker.lean
aa06f4008055343b4deb271aa4a461a68b0ef63b8e0e5661942c26f8c7cd565d  problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean
c73c5bf833e439061bcff94a2b9c4a0c05b3c494473a73620792f4a0d4592554  problems/23/lean/Erdos23Delta0/Ell5BlockSingleton.lean
2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048  problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean
506ba26ca167045464c5c5bf45ece250a18a3870e1716e120027cc0a320da8b9  problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean
9e907495d20492505ff85c613c033ee783a288ad790c8682ed575c0c1bec438d  problems/23/lean/Erdos23Delta0/Ell5ActiveComponentBankHall.lean
800547bc53068873072306afba3c9e51000b8f13571ed9d1061e1c13ef43e164  problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean
7273589df3606e90ba0b0bd39b6af42597bb3afb45cc7fa55ff47c5c5a10e609  problems/23/lean/Erdos23Delta0/InactiveComponentBlockChecker.lean
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
c181e1189157785f2ed335ee3ca6c83ab1097e13f65677d396bca0b75ef58200  problems/23/writeup/_codex_wall_r5_359_gate.py
f757e96e8bbe51294958b84c92ba42f2d123987585268a1844249c46757703fe  problems/23/writeup/_codex_branchb_door_ownership_gap_audit.py
8bc975f409136deecd9b4fdf590aef84e1b2805141e850529864d2bd8b558d7f  tmp/fanout/r29_fullbank/C_fullbank/d6_flow/gate.py
bfb75636d5e11b7f3d251cb20a64a5227f5b870938f1d1b715f38d400903adfc  problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md
cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5  problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md
0168e75ea5ca1841208abb2d40d4b17817d8959e404f64d5ec551dce18ae784c  problems/23/writeup/_claude_r29_2943_structural_gate.py
```



