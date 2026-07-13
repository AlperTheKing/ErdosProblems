# Child 05 semantic audit: `vertexSlack` and internal-endpoint slack

## Executive verdict

Production has several distinct objects that must not be identified.

1. The concrete singleton-cover `vertexSlack` sink is a vertex `x : V`. Its fixed route sends `1/2` of an off-support edge to every incident core endpoint: `endpointQ e x := if x ∈ e then 1 / 2 else 0` (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:165-167`). The vertex-only certificate requires `((O.filter fun e => x ∈ e).card : ℚ) / 2 ≤ kap x` (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:384-399`).
2. The mixed internal-endpoint bridge uses sink type `V ⊕ Sym2 V`: `Sum.inl x` is vertex slack and `Sum.inr e` is the edge's own Door (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:75-82`). Boundary edges use own Doors; only non-boundary/internal incidence consumes vertex capacity (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:481-495`; `problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:101-127`).
3. Generic bank sinks are type parameters (`JT`) with no vertex meaning absent an incidence adapter. `BlockBankSink JT V := JT ⊕ Sym2 V` (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-22`).
4. The global bookkeeping layer has `.vertexSlack` aggregate data but no wall-port incidence. `CapKind` is exactly `door | vertexSlack | c5Base | prune` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31`), while `NonDoorToken` is every token not of kind `door` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-25`). That file states: `legal edge-to-token incidence is still absent from this package` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:80-81`).
5. `ActiveScopedMinimumExchange.Available` is not a bank relation. Its complete definition is `EligibleOwner ... ∧ ¬ScopedReserved ...` with right object `s : FreeHalf G omega` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). It has no capacity, flow, Door, `CapKind`, or vertex-slack token. Ordinary slack is represented only indirectly by subtracting `G.n - selectedLoad` before residual `ActiveHitNeed` units are formed (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:75-89`).

The internal-endpoint constructor is compiled but conditional: it does not derive `slack`, `kap`, or legal incidence from graph data. The current R29 executable audit records `compiled_incidence_licensed_from_graph_data:false` and `numeric_vertexSlack_feasible:false` (`tmp/fanout/r29_fullbank/E_source_search/vertex_slack/result.json:1`).

## Exact production semantics

### Token and sink types

The vertex-only constructor uses `JT = V`, `J = C`, and returns:

> `FullBankRelaxedCoverCert S F O C C ... inc kap`

(`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:384-399`). A sink is literally a core vertex, not a `CapKind` or a `FreeHalf`.

The mixed constructor uses `V ⊕ Sym2 V` and all sinks:

> `FullBankRelaxedCoverCert S F O Finset.univ C ... inc kap`

(`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:515-537`). `Sum.inl x` receives `endpointQ c x` exactly when `c ∉ D` and `x ∈ C`; `Sum.inr e` receives the full singleton load exactly when `c ∈ D` and `c = e` (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:484-495`). Thus a Door-routed edge does not also spend vertex slack.

The typed source universe is:

> `CapSource ExitEdgeKey VertexKey BaseKey PruneKey`
> with `.door (edge : ExitEdgeKey)`, `.vertexSlack (vertex : VertexKey)`,
> `.c5Base (base : BaseKey)`, `.prune (prune : PruneKey)`.

(`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-30`). `CapSource.kind` maps `.vertexSlack _` definitionally to `.vertexSlack` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:36-49`). A typed token has `comp`, `source`, and `capQ` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:61-67`); its ledger requires injectivity of `(comp, source)` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:81-89`).

No vertex-slack incidence checker is defined there. The Boolean `checkOwnEdgeDoors` checks only Door-source equality and `25 ≤ capQ` (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:108-126`). Connecting typed tokens to wall `Sink` is explicitly a separate, unassumed adapter (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:12-14`).

Legacy `LedgerToken` instead has `comp`, `kind`, `sourceId : Nat`, `capQ : ℚ` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:67-74`), so it does not expose a vertex payload. `NonDoorToken P := {t // token.kind != CapKind.door}` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-21`) includes vertex-slack, c5Base, and prune tokens. Its capacity is only `(token t).capQ / 25` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:41-44`).

### Capacity definitions

`halfWeight` is exactly `1/2`, and `endpointQ` is half at each incident endpoint (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:163-167`). The proved column sum is:

> `∑ e ∈ O, endpointQ e x = ((O.filter fun e => x ∈ e).card : ℚ) / 2`.

(`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:219-228`). The vertex-only constructor accepts arbitrary `kap : V → ℚ`; it assumes nonnegativity and this incidence-degree bound, rather than defining capacity from `N` or row load (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:384-396`).

For internal endpoint slack:

> `O := cutEdges G s \ F`,
> `D := O.filter fun e => edgeBoundary C e = true`,
> `I := O.filter fun e => e ∈ C.sym2`.

(`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:56-67`, `problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:101-103`). At core vertex `x`, non-Door incident members of `O` equal internal incident members of `I` (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:33-40`). The exact assumed chain is:

> `(((I.filter fun e => x ∈ e).card : ℚ) / 2) ≤ slack x`
> and `slack x ≤ kap (Sum.inl x)`.

(`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:88-93`). Neither `slack` nor `kap` is graph-derived, and equality is not required. Every boundary edge requires own-Door legality and `(1 / 2 : ℚ) ≤ kap (Sum.inr e)` (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:94-97`).

`EndpointReserveHall` uses another mixed sink, `V ⊕ JT`, with vertex capacity `slack x` and token capacity `cap t` (`problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:31-40`). A token is incident when `∃ x, x ∈ e ∧ 0 < eta x t` (`problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:33-36`). Here `eta : V → JT → ℚ` is an allocation matrix, not the forbidden eta token. `CapKind` indeed has no eta constructor (`GOAL_LOOP.md:12-16`; `problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31`).

`CollisionTokenAssignment.Assignment` has `eta`, `eta_nonneg`, `no_double_spend`, `pays_need`, and `legal_at_endpoint`; its exact inequalities and incidence conclusion are at `problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:25-35`. The module explicitly does not assert provider existence (`problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:6-11`).

`FullBankRelaxedCoverBundleView` stores `demandQ`, `doorCapQ`, `vertexSlackCapQ`, `c5BaseCapQ`, and `pruneCapQ` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:33-40`). Its RHS is the four-cap sum, and `Checked` assumes nonnegativity plus `demandQ ≤ rhsQ` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:42-54`). Thus `vertexSlackCapQ` is an asserted aggregate, not a definition `max(0,N-T(v))`. It is linked to the ledger only by `view.vertexSlackCapQ = ledger.spendOfKindLocal l CapKind.vertexSlack` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:187-192`).

### Routing, cover certificates, and soundness

`FullBankRelaxedCoverCert` has data `lam : ι → ℚ` and `q : E → JT → ℚ`, with proof fields `hlam`, `hq`, `hkap`, row coverage `hcov`, support congestion `hcong`, per-port routing `hroute`, per-sink capacity `hcap`, and positive-flow legality `hqinc` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40`). In particular:

> `hroute : ∀ c ∈ O, load(c) ≤ ∑ j ∈ J, q c j`
> and `hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j`.

This is a rational flow certificate, not a matching into `FreeHalf`.

The deterministic wrapper defines `assignedSinkQ ... sink c j := if sink c = j then load(c) else 0` (`problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean:32-36`) and constructs a certificate from explicit coverage, congestion, legal assignment, and capacity hypotheses (`problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean:55-85`).

`certificate_of_internalEndpointSlack_boundaryDoors` returns:

> `FullBankRelaxedCoverCert S F (cutEdges G s \ F) Finset.univ C ... inc kap`.

(`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:75-100`). It calls the mixed Door/vertex count constructor (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:101-105`), uses count normalization plus the slack inequalities for vertex capacity (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:125-127`), and proves boundary Door load `1/2` before applying Door capacity (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:128-134`). Its docstring says, `No endpoint or Door existence is inferred by this bridge` (`problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:72-74`).

The endpoint-reserve Hall theorem assumes:

> `hcap : ∀ t, (∑ x, eta x t) ≤ cap t`
> and `hbudget : ∀ x, halfDegree E x ≤ slack x + ∑ t, eta x t`,

plus containment hypotheses, and concludes:

> `(T.card : ℚ) ≤ (∑ x ∈ U, slack x) + ∑ t ∈ R, cap t`.

(`problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:140-154`). `CollisionTokenAssignment.hall_of_assignment` gives the same form from an abstract `Assignment` (`problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:46-59`).

The active-component endpoint Hall wrapper remains conditional. It defines non-Door edges `E0 O D`, core-vertex sinks `V0 C`, actual block demand, and capacity `kap (Sum.inl x)` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean:14-54`). `certificate_of_activeComponent_mixedDoorEndpointHall` assumes this Hall condition and Door legality/capacity, then returns `FullBankRelaxedCoverCert` (`problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean:111-133`). The generic bank version assumes arbitrary `qBase`, routing, capacity, and incidence for `JT` (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-64`). Nothing identifies `JT` with vertices.

From any full-bank certificate, production proves:

- `BankedCutDomination ...` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:42-50`).
- `¬ ∃ alpha beta gam del, IsDualCert ...` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:52-60`).
- Total off-support load at most total sink capacity (`problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean:28-48`).
- Under disjointness, support, and per-cut cardinal hypotheses, `25 * |S| ≤ 25 * |F| + 25 * ∑ kap` (`problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean:50-66`).

From a checked global package, production proves `lengthSurplusGD rows ≤ 25 * etaQ G c` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:286-308`) and `gammaOfGD G c rows ≤ (G.n : ℚ)^2` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:310-315`). These consume asserted checks; they do not construct wall flow.

### Package fields and missing adapter

`FullBankGlobalPackage` fields are exactly `componentCount`, `localCount`, `tokenCount`, `compN`, `componentRowCountQ`, `compOfRow`, `localOfRow`, `localCover`, and `ledger` (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:131-143`). `GlobalLedgerData` has `token`, `spendQ`, component-reserve slack, and superadditivity slack (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:76-82`).

Relevant `Checked` fields are local-view checks and kind-spend equalities, nonnegative spend/caps, no double spend, no cross-component spend, and `(comp,kind,sourceId)` uniqueness (`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:177-209`). There is no port type, `inc`, `q`, or positive-spend legality field.

This is formally separated: `AggregateLedgerNoIncidenceCounterexample` proves:

> `emptyPackage.Checked ∧ ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls)`.

(`problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean:145-157`). It states no theorem can derive `HalfLayerRouted` from present aggregate-package fields alone (`problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean:8-16`).

Coordination called the exporter future work: `I will spec+build the real multi-sink (door,vertexSlack,c5Base,prune) incidence/capacity exporter` (`coordination/CLAUDE_TO_CODEX.md:13858-13861`). A scoped search found no declaration named `ActiveComponentFullBankCert`; `GOAL_LOOP.md` uses that phrase only in pipeline prose (`GOAL_LOOP.md:16`). Present compiled objects are conditional constructors returning `FullBankRelaxedCoverCert`.

## Comparison with `ActiveScopedMinimumExchange.Available`

`FreeHalf` has exact fields:

> `sourceX : Fin G.n`, `sourceY : Fin G.n`, `half : Fin 2`,
> `distinct : sourceX ≠ sourceY`,
> `free : pairCount omega sourceX sourceY = 0`.

(`problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:64-73`). ActiveScoped demand is `ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106`). Its endpoint residual is `hitNeedUnits ... v := activeDegree ... v - (G.n - selectedLoad omega v)` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:75-89`).

`ScopedReserved` requires `half = 0`, an active-graph edge, and active first endpoint (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-132`). `EligibleOwner` is same-first-owner or row-companion pair-count/sigma eligibility (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142`). The complete relation is:

> `EligibleOwner G c (demandOwner d) s ∧ ¬ ScopedReserved G c omega s`.

(`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). `Matching` assigns every demand injectively to a `FreeHalf` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158`); `Nonempty (Matching ...) ↔ HallCondition ...` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:160-179`).

| Semantic object | In `ActiveScoped.Available`? | Exact status |
|---|---:|---|
| `FreeHalf` source | Present | Right-hand object and matching codomain (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-158`). |
| Same-owner/row-companion eligibility | Present | Directly in `EligibleOwner` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-147`). |
| Ordinary slack `N-selectedLoad` | Indirect only | Reduces `hitNeedUnits` before demand is formed (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:75-106`). |
| Vertex sink keyed by `v` | Absent | Codomain is `FreeHalf`, not `V` or `VertexKey` (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-158`). |
| Internal count `|I incident x|/2` | Absent | No `C,D,I`, count, or rational division; these occur in `problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:56-97`. |
| Boundary own-Door | Absent | No Door summand or own-edge equality; mixed Door routing is `problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:484-495`. |
| c5Base/prune token | Absent | No `CapKind`, token, `capQ`, or allocation matrix (`problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147`). |
| Generic bank sink `JT` | Absent | Generic routing is separate (`problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean:21-64`). |
| Rational capacity/flow | Absent | ActiveScoped has a discrete injection; full bank uses `q` and `kap` (`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40`). |
| Endpoint reserve assignment | Absent | Only in `problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:31-54` and `problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean:25-35`. |

This matches the R29 writeup: the selector/matching falsifier is not a falsifier of Erdős #23, and the live wall needs `the full-bank capacity that is absent from the active-scoped FreeHalf matching` (`problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96`).

## Executable implementations

### Lean

- `halfWeight`, `endpointQ`, `mixedDoorVertexQ`, `endpointReserveCap`, and `endpointReserveInc` execute arithmetic/dispatch but do not derive graph capacities (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:163-167`, `problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:484-495`, `problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:33-40`).
- `certificate_of_singletonCore_vertexSlack`, `certificate_of_singletonCore_mixedDoorVertex`, `certificate_of_internalEndpointSlack_boundaryDoors`, and Hall-to-certificate constructors are `noncomputable def`s: proof constructors from hypotheses, not finite input checkers (`problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:384`, `problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean:515`; `problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean:75`; `problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean:113`).
- `checkOwnEdgeDoors` is Boolean but checks only Doors (`problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:108-128`).
- Exact fixtures exist. `Wall24PrimalFixture` defines `assignedVertexSlack`, equality-based `legalVertexSlack`, constant cap `9`, and a certificate (`problems/23/lean/Erdos23Delta0/Wall24PrimalFixture.lean:52-73`, `problems/23/lean/Erdos23Delta0/Wall24PrimalFixture.lean:137-176`). `Wall359PrimalFixture` analogously uses cap `314` (`problems/23/lean/Erdos23Delta0/Wall359PrimalFixture.lean:60-89`, `problems/23/lean/Erdos23Delta0/Wall359PrimalFixture.lean:154-197`). These are fixtures, not a general extractor.

### Python/current audit data

1. `_codex_singleton_vertexslack_gate.py:subset_record` constructs `C`, shortest support, outside/internal/boundary edges (`problems/23/writeup/_codex_singleton_vertexslack_gate.py:42-64`), then uses exact `Fraction` capacity `max(0,n-T[v])`, fixed split `degree/2`, and internal-only `internal_degree/2` (`problems/23/writeup/_codex_singleton_vertexslack_gate.py:66-99`). This is a Python policy, not the Lean constructor's definition.
2. `_codex_internal_offsupport_gate.py:endpoint_flow_hall_margin` sets `caps[v]=max(0,ambient_n-loads[v])` and scans all vertex masks for `capacity-|E[U]|` (`problems/23/writeup/_codex_internal_offsupport_gate.py:63-84`). This tests existence of arbitrary incident-endpoint flow, not fixed `endpointQ` splitting.
3. `_codex_r23_double_star_fullbank_audit.py` defines `build`, `literal_audit`, and `formula_audit` (`problems/23/writeup/_codex_r23_double_star_fullbank_audit.py:31`, `problems/23/writeup/_codex_r23_double_star_fullbank_audit.py:83`, `problems/23/writeup/_codex_r23_double_star_fullbank_audit.py:176`). `literal_audit` computes outside degree, fixed half-load, `max(0,N-load)` capacity, and exact coverage/congestion/off-load with `Fraction` (`problems/23/writeup/_codex_r23_double_star_fullbank_audit.py:139-158`). It is an audit, not a Lean provider.
4. Current R29 `tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py` constructs `C,F,S,O`, partitions internal/boundary/disjoint edges, computes `T=5*row_incidence`, and evaluates `cap=max(0,n-T[v])`, `load=Fraction(O_incidence,2)` (`tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py:13-36`). Source keys are `(edge endpoints, incident core vertex)` (`tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py:38-45`), and it emits `compiled_incidence_licensed_from_graph_data: False` (`tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py:57-66`). Exact output has margins `-1/2` at vertices 0,1,2 and `-2` at vertex 55, with `numeric_vertexSlack_feasible:false` (`tmp/fanout/r29_fullbank/E_source_search/vertex_slack/result.json:1`). This refutes vertexSlack-only fixed splitting on that tuple, not the full bank or conditional constructor.

No named general vertex-slack/internal-endpoint checker was found. Exact scoped command:

```powershell
rg -n -S "check.*[Vv]ertex.*[Ss]lack|[Vv]ertex.*[Ss]lack.*check|check.*[Ii]nternal.*[Ee]ndpoint|check.*[Ee]ndpoint.*[Rr]eserve" problems/23/lean problems/23/writeup tmp/fanout/r29_fullbank --glob '*.lean' --glob '*.py' --glob '*.cpp' --glob '*.json' --glob '!**/result.json' --glob '!**/events*.jsonl'
```

It returned two prose-only script matches and no named checker declaration.

## Commands run

All commands were read-only except creation of this report. Exact substantive commands (PowerShell, cwd `E:\Projects\ErdosProblems`) were:

```powershell
Get-ChildItem -Force
rg --files | rg "(^|/|\\)(COMMON\.md|GOAL_LOOP\.md|CLAUDE_TO_CODEX\.md|R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER\.md)$|vertexSlack|ActiveScopedMinimumExchange|FullBank|FreeHalf|Available"
rg --files tmp/fanout/r29_fullbank_semantics problems/23 coordination . | rg "COMMON\.md$|goal|Goal|GOAL"
rg -n --hidden -S "vertexSlack|internal[- ]endpoint|InternalEndpoint|FreeHalf|Available|bank sink|BankSink" problems/23/lean problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md coordination/CLAUDE_TO_CODEX.md GOAL_LOOP.md tmp/fanout/r29_fullbank_semantics
rg -n -S "vertexSlack|internal[- ]endpoint|InternalEndpoint|EndpointReserve|FullBank|FreeHalf|R29" coordination/CLAUDE_TO_CODEX.md
rg -n -S "certificate_of_internalEndpointSlack_boundaryDoors|certificate_of_singletonCore_vertexSlack|certificate_of_singletonCore_mixedDoorVertexCount|endpointReserveHallOn|FullBankGlobalPackage|CapSource.vertexSlack|nonDoorHallCapQ" problems/23/lean --glob '*.lean' --glob '!**/Generated/**' --glob '!**/ChartPayloads/**' --glob '!**/Proofs/**'
rg -n -S --glob '*.py' --glob '*.cpp' --glob '*.cc' --glob '*.cxx' --glob '*.json' --glob '*.jsonl' --glob '*.toml' --glob '*.yaml' --glob '*.yml' "vertexSlack|vertex_slack|vertex slack|internalEndpoint|internal_endpoint|internal endpoint slack|endpointReserve|endpoint_reserve|EndpointReserve|assignedVertexSlack|legalVertexSlack" problems/23 tmp/fanout coordination tools
rg -l -S --glob '*.py' --glob '*.cpp' --glob '*.cc' --glob '*.cxx' --glob '*.json' --glob '*.jsonl' --glob '*.toml' --glob '*.yaml' --glob '*.yml' "vertexSlack|vertex_slack|vertex slack|internalEndpoint|internal_endpoint|internal endpoint slack|endpointReserve|endpoint_reserve|EndpointReserve|assignedVertexSlack|legalVertexSlack" problems/23 tmp/fanout coordination tools
rg -n -S "check.*[Vv]ertex.*[Ss]lack|[Vv]ertex.*[Ss]lack.*check|check.*[Ii]nternal.*[Ee]ndpoint|check.*[Ee]ndpoint.*[Rr]eserve" problems/23/lean problems/23/writeup tmp/fanout/r29_fullbank --glob '*.lean' --glob '*.py' --glob '*.cpp' --glob '*.json' --glob '!**/result.json' --glob '!**/events*.jsonl'
Get-Content -LiteralPath <source> | ForEach-Object { <emit numbered requested slice> }
Get-FileHash -Algorithm SHA256 -LiteralPath <every cited source>
Get-Content -Raw -LiteralPath tmp/fanout/r29_fullbank/E_source_search/vertex_slack/result.json | ConvertFrom-Json
```

Two initial broad recursive `rg` calls over all `Erdos23Delta0` Lean files were terminated/timed out before a complete result. Subsequent file-filtered/glob-excluded searches completed. Two Windows `Gamma/*.lean` invocations failed with OS error 123 and were replaced by searches with Gamma as cwd. No conclusion relies on an incomplete search.

## Exact SHA-256 hashes for every cited source

```text
49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
cd536b9edf3a4b1ba9e0e79754c0daa780c68b98f5f4c06da84e279b6d2c20f2  coordination/CODEX_GOAL.md
e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
6ce365ff45578dbbadb238f691700012df52ddb1afa82331027b0e51aff6a614  coordination/CLAUDE_TO_CODEX.md
5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104  problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean
3fa9278b724453364532e7f36cc7f5b67ecd3f035957b7f6632a2835df6379d3  problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean
0ac01cf28b2e7dc6770da7f71b147cedec47671a4c672e1434fd7dc372f1bae1  problems/23/lean/Erdos23Delta0/Ell5FullBankHall.lean
2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048  problems/23/lean/Erdos23Delta0/Ell5SingletonVertexSlack.lean
506ba26ca167045464c5c5bf45ece250a18a3870e1716e120027cc0a320da8b9  problems/23/lean/Erdos23Delta0/Ell5InternalEndpointSlackFullBank.lean
aa06f4008055343b4deb271aa4a461a68b0ef63b8e0e5661942c26f8c7cd565d  problems/23/lean/Erdos23Delta0/Ell5BlockBankFlow.lean
180f362f8d0ba889c485385703c713e619d22c5f1ab5b4e15cba60d54ffb197f  problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean
9cfa35f2714799ddd4e1a187c2d6d620dae7c15d920f114896b4f30218274440  problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean
a9c4cebee9e5d1d63b4e38ad7203c05d18fdb8f8ef5f41684ebea07340aaa149  problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean
624c56995234f4ef5d68804013ce69d66962cfb2a3230de7c8d601db6870089f  problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean
ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
188e5d5096020941728f20c240247d0e669887736d4d14f322ea684114210362  problems/23/lean/Erdos23Delta0/Wall24PrimalFixture.lean
020399ad070c497b54725544a7726109086b3de80de3743c2da70cc962666cde  problems/23/lean/Erdos23Delta0/Wall359PrimalFixture.lean
c933cd768bd972130c5cefad3df15185a045b92a57c96091dc092c9cdbd72f8e  problems/23/writeup/_codex_singleton_vertexslack_gate.py
ebe194c5c08eee10473304a6ab6cbdc70fb3fb249ed02d02d069b7f3ef2dd47c  problems/23/writeup/_codex_internal_offsupport_gate.py
846a4cb388de50913da35753c012a2d9d29dddbc5725a74c2251084dae72e84c  problems/23/writeup/_codex_r23_double_star_fullbank_audit.py
587ed8c4e5d7b30e660036ce1a3b2e0221f96618f3491202f24fdf944b0c1179  tmp/fanout/r29_fullbank/E_source_search/vertex_slack/replay.py
9458645fdca1b005123faea41db00a61c3709b7e3a955238b542cb7c70e77a66  tmp/fanout/r29_fullbank/E_source_search/vertex_slack/result.json
```

`coordination/CODEX_GOAL.md` was the accessible goal-attachment candidate and was read; its opening mission predates transfer-matching-era `GOAL_LOOP.md`, so no current semantic conclusion relies on it.

## Findings

1. Production `vertexSlack` has three representations: concrete vertex sink (`V`), typed ledger source `.vertexSlack vertex`, and legacy aggregate kind/spend. Only the first has routing semantics; only the typed source carries a vertex payload; the aggregate package has neither ports nor incidence.
2. Internal-endpoint slack is exactly half the internal off-support incidence count at each core vertex. Boundary off-support edges are excluded and routed to own edge Doors.
3. The internal bridge is conditional. Graph-derived existence of slack, capacity, endpoint legality, and Door legality/capacity are hypotheses, not outputs.
4. `EndpointReserveHall` and `CollisionTokenAssignment` prove subset Hall inequalities from an abstract reserve provider; neither constructs a c5Base/prune provider.
5. Generic bank sinks must not be read as vertex sinks. `JT` is unconstrained, and `NonDoorToken` combines three kinds.
6. `ActiveScoped.Available` contains `FreeHalf` and owner eligibility only. Vertex slack is indirect through residual-demand subtraction; internal endpoint counts, Doors, bank tokens, capacities, and rational routing are absent.
7. The current R29 exact replay fails vertexSlack-only fixed splitting and separately records unlicensed compiled incidence. It does not test or falsify the full four-kind bank.

## Contradictions and ambiguities

1. **Prose pipeline versus declarations.** `GOAL_LOOP.md:16` names `ActiveComponentFullBankCert`, but no declaration with that name exists in the scoped search. Closest production semantics are conditional constructors returning `FullBankRelaxedCoverCert`.
2. **“Compiled FullBankGlobalPackage” can be misread.** The aggregate structure and soundness theorem compile, but port-to-token incidence is absent; `checkedAggregatePackage_and_noHalfLayerRouting` formally proves aggregate checking cannot create routing.
3. **Capacity formula ambiguity.** Python gates choose `max(0,N-T(v))`; general Lean singleton/internal constructors accept arbitrary `slack` and `kap`. ActiveScoped Nat subtraction is a demand calculation, not a rational sink-capacity definition.
4. **`eta` name collision.** `EndpointReserveHall.eta` is endpoint-to-token mass, not the forbidden top-cage eta token.
5. **Fixed split versus free endpoint flow.** `certificate_of_singletonCore_vertexSlack` fixes half to each endpoint. `endpoint_flow_hall_margin` and active-component Hall permit arbitrary fractional routing. Their pass/fail results are not equivalent.
6. **Legacy versus typed uniqueness.** `FullBankGlobalPackage.Checked` uses `(comp,kind,sourceId : Nat)` while `TypedGlobalLedgerData` uses payload-typed sources. No compiled adapter connects typed sources to wall sinks.

## Unresolved gaps

1. No graph-derived production provider constructs `slack x`, proves `slack x ≤ kap (Sum.inl x)`, and licenses every internal `(edge,endpoint)` incidence required by `certificate_of_internalEndpointSlack_boundaryDoors`.
2. No compiled adapter maps `CapSource.vertexSlack v` (or c5Base/prune) to concrete `JT`/wall sinks and proves legal port incidence.
3. No production checker exports a full `door + vertexSlack + c5Base + prune` incidence/capacity instance from R29 graph data; coordination records this exporter as planned.
4. No provider constructs `CollisionTokenAssignment.Assignment`; its existence remains the c5Base/prune collision-reserve obligation.
5. The R29 replay establishes failure of fixed vertexSlack-only routing, but neither supplies nor refutes full-bank flow using remaining token kinds.




