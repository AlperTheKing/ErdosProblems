# Erdős #23 R29 FullBank semantic audit — child 09 independent referee

## Verdict

The R29 integer 28 is an exact Hall deficiency for the compiled active-scoped relation Erdos23Delta0.Gamma.ActiveScopedMinimumExchange.Available at owner shore {0,1,2}. It is not a deficiency for the compiled FullBank primal relation, whose incidence is an arbitrary parameter, and it is not a verified deficiency for the newer transfer-enriched relation described in GOAL_LOOP.md because that relation has no compiled aggregate definition.

The write-up states the exact witness as demand 19953, source-neighborhood cardinality 19925, and Hall defect 28 (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:24-30, quote: “owner shore A = {0,1,2} ... exact Hall defect 28”). Its consequence is accurately limited: the real-graph provider for the selector score is false, while FullBank capacity is absent from active-scoped FreeHalf matching (same file:91-96).

I treated GOAL_LOOP.md as the active goal because it says the armable /goal is reproduced there (GOAL_LOOP.md:4) and gives the current four conjuncts at :10-17. No separate attachment was exposed.

## Semantic DAG

Legend: EXE = executable/reducible; THM = proved implication; HYP = caller-supplied structure/proposition; MISSING = no compiled bridge found.

    GraphData {n,edges} + CutData {side}                         [EXE]
      -> blueb, badb, sigma, badCount                            [EXE]
      -> BadEdgeData {u,v,rows} + CompleteShortestRowDB          [HYP fields]
      -> RowChoice, one selected row per bad edge                [EXE]
      -> selected rows/vertices/support and pairCount            [EXE]
      -> activeEdges -> activeGraph -> ActiveOwner               [EXE]
      -> ActiveCollisionHalf + ActiveHitNeed = Demand            [EXE types]
      -> FreeHalf                                                [EXE source type]
      -> Available := EligibleOwner and not ScopedReserved       [EXE Prop]
      -> HallCondition iff Nonempty Matching                     [THM]
      -> scopedObligationScore := card Demand; finite minimizer  [EXE/noncomputable]
      -> HallFailureHasScopedScoreGlobalDescent                  [HYP; R29 falsifies]

    R29 build() -> exact graph/cut/rows                           [Python EXE]
      -> scoped_state()/rebuild_scope()                          [Python EXE]
      -> owner_sources() enumerates Available for owners 0,1,2  [Python EXE]
      -> 8 shores; 19953 - 19925 = 28                           [Python EXE]
      -> global certificate: scoped score 23115                  [exact replay]

    Separate FullBank primal, over SimpleGraph
      SimpleGraph + S,F,O,J,K + sep,dB + inc + kap               [HYP inputs]
      -> FullBankRelaxedCoverCert {lam,q,...}                    [HYP structure]
      -> BankedCutDomination                                     [THM]
         sum_S alpha <= sum_F beta + bankCost J kap O inc gamma

    Active-component constructor
      E0 := O minus D (non-Door edge loads), V0 := C (vertex sinks)
      ActiveComponentHall + own-Door incidence/capacity          [HYP]
      -> FullBankRelaxedCoverCert with sinks V ⊕ Sym2 V          [THM]

    Separate aggregate FullBank ledger, over GraphData
      RowDB + arbitrary FullBankGlobalPackage tables             [HYP data]
      -> P.Checked: all local, spend, reserve, global identities [HYP]
      -> surplus <= demand <= cap = spend <= token cap
         <= component residual <= N² - 25 badCount               [THM chain]
      -> lengthSurplusGD <= 25 etaQ -> gammaOfGD <= N²           [THM]

    Missing:
      GraphData/CutData/BadEdgeData <-> SimpleGraph/S,F,O,J,K
      active-scoped Matching -> transfer token family
      transfer tokens -> EndpointReserveHall/ActiveComponentHall hypotheses
      FullBankRelaxedCoverCert -> FullBankRelaxedCoverBundleView
      primal/typed sinks -> FullBankGlobalPackage ledger
      real graph -> Nonempty {P // P.Checked}

## Exact input and active-scoped semantics

GraphData is literally n : Nat and edges : List (Nat × Nat) (problems/23/lean/Erdos23Delta0/CertGraph.lean:15-18). checkGraph is G.edges.all (checkEdge G) && decide G.edges.Nodup (:20-26). CutData is side : List Bool and checkCut only checks its length (:52-58). blueb/badb use side inequality/equality (:64-70); sigma is (dB : Int) - (dM : Int) (:85-87); badCount is a filtered list length (:89-91).

IsMaxCut.min_bad quantifies over every valid cut (:2393-2396). TriangleFree explicitly forbids a triangle (:2399-2402). BConnected only requires a blue path between each bad edge’s endpoints (:2420-2425). These are abstract hypotheses, not consequences of names.

R29 selection uses BadEdgeData.rows : List Row5 (CertGraph.lean:178-187). CompleteShortestRowDB requires checked rows, nodup bad keys, nodup row-vertex lists, every bad edge covered, and every valid row covered (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:29-47). RowChoice is (i : Fin bads.length) -> Fin (bads.get i).rows.length (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:23-25). pairCount counts selected rows containing both ordered coordinates (:78-82). activeEdges are internal selected-vertex blue edges absent from selected row support (:91-101).

CollisionHalf has owner, other, copy : Fin (pairCount - 1), and half : Fin 2 (MinimumDemandCollisionHall.lean:54-62). ActiveCollisionHalf is the subtype whose owner satisfies ActiveOwner (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:51-54). ActiveHitNeed is Σ v, Fin (hitNeedUnits v) (:80-89), with hitNeedUnits = activeDegree - (G.n - selectedLoad) and selectedLoad = 5 * pairCount omega v v (:75-84); Nat subtraction truncates. Demand is ActiveCollisionHalf ⊕ ActiveHitNeed (:102-106).

FreeHalf is an ordered sourceX/sourceY/half triple with distinct coordinates and pairCount = 0 (MinimumDemandCollisionHall.lean:64-73). The exact relation is:

    Available G c d s :=
      EligibleOwner G c (demandOwner d) s ∧
      ¬ScopedReserved G c omega s

(ActiveScopedMinimumExchange.lean:144-147). EligibleOwner is:

    s.sourceX = owner ∨
      (0 < pairCount owner sourceX ∧
       0 < pairCount owner sourceY ∧
       0 ≤ sigma G c [sourceX,sourceY])

(:134-142). ScopedReserved is half zero, activeGraph adjacency, and active first endpoint (:125-132). Matching is an injective assignment of every Demand to FreeHalf satisfying Available (:154-158), and Nonempty Matching iff HallCondition is proved (:167-179).

Available depends only on demandOwner (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean:53-58). Owner-saturated Hall is equivalent to full demand Hall (:114-126), and failure is equivalent to some owner shore with fewer sources than demands (:128-137).

scopedObligationScore is exactly Fintype.card Demand (ActiveScopedMinimumExchange.lean:249-253). HallFailureHasScopedScoreGlobalDescent only says every matching failure has some globally lower-scoring row tuple (:614-620). Its Real wrapper assumes TriangleFree, IsMaxCut, BConnected, and CompleteShortestRowDB and returns that proposition (:622-628); it does not prove the graph provider.

Do not alias this score with the older obligationScore = 2*collisionUnits + 2*activeEdges.length (MinimumDemandRowSelection.lean:103-106).

## R29 executable implementation

The exact implementations are:

- tmp/fanout/r29_gate/lead/r29_lead_gate.py::build constructs dict fields n, blue, bad, graph, side, rows, atoms, and selector metadata (:129-276), asserting n=2943, blue=7039, bad=1383 (:223-230).
- scoped_state uses an ordered Counter, selected support, union-find active components, collision, hit-need, and score (:279-338). Collision is 2*sum(multiplicity-1) (:323-327); hit-need is max(0,degree-max(0,n-5*row_count)) (:328).
- tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py::rebuild_scope independently rebuilds pair/load/support/active state (:52-97).
- owner_sources keys FreeHalf as (x,y,half). Same-first enforces pair-freeness and non-reservation (:110-119). Row-companion enforces both owner co-occurrences, distinctness, pair-freeness, exact nonnegative two-vertex sigma, and non-reservation (:120-134).
- OWNERS is exactly (0,1,2) (:15), and shore enumeration is range(8) (:145-152). Thus “all eight shores” means all subsets of these three owners, not all 2^2943 owner shores. This suffices for a Hall falsifier but does not prove 28 is the global maximum deficiency.
- verify_r29_global_min_hall_falsifier.py::verify_hall_certificate recomputes unique source masks and confirms [19953,19925,28] (:28-46).

The Python relation is extensionally faithful to ActiveScopedMinimumExchange.Available on this tuple: ordered pair counts implement pairCount; component marking implements ActiveOwner; half-zero reservation is ScopedReserved; signed degrees with the internal-edge correction equal sigma [x,y]; source keys enforce all FreeHalf fields. No float is evidence.

Read-only replay returned:

    demand=19953, neighborhood=19925, gap=28, shore=[0,1,2]
    globalScopedScore=23115, hallDefect=28
    phtContradictionNumerator=28*680^676

## Actual FullBank semantics

There are two non-equivalent compiled FullBank objects.

FullBankRelaxedCoverCert is a rational primal over generic row R, edge E, sink JT, and cut index ι. It carries lam and q, with nonnegativity, row coverage, support congestion, off-support routing, capacity, and positive-flow incidence obligations (problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:23-40). The file says Ell5FullBankRelaxedCover_exists remains open (:6-10). bankedCutDomination_of_cert consumes the certificate (:42-50).

BankedCutDomination is a price inequality, not an integral matching. It universally quantifies nonnegative alpha,beta,gam and concludes:

    (∑ r∈S, alpha r) <= (∑ c∈F, beta c) + bankCost J kap O inc gam

subject to per-cut domination (problems/23/lean/Erdos23Delta0/BankedCutDominationCore.lean:68-76). bankCost is sink capacity times the maximum incident off-support price (:28-39).

The active-component adapter has different classes. E0 is {e∈O | e∉D}; V0 is {x∈C}; legalInc is inc e (Sum.inl x) (problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean:14-39). ActiveComponentHall says every edge subset’s rational demand is at most its legal vertex-neighborhood capacity (:41-54). certificate_of_activeComponent_mixedDoorEndpointHall assumes hHall plus own-Door incidence inc e (Sum.inr e) and door capacity, then returns FullBankRelaxedCoverCert (:111-133). None mentions Available.

EndpointReserveHall.endpointReserveHallOn is also conditional: given nonnegative flow, token capacities, per-vertex budget, and explicit endpoint/token supports, it concludes T.card <= sum slack + sum cap (problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean:140-154). It does not construct these hypotheses from R29 matching.

EndpointHalfBoundaryPartition is now compiled. It stores a total port assignment, port loads, and exact aggregation (problems/23/lean/Erdos23Delta0/EndpointHalfRelaxedCutCover.lean:54-68); total_portLoad_eq proves no loss or duplication (:70-110). Its own comment says it contains no Door or graph-existence assertion (:10-12).

The aggregate FullBankGlobalPackage is different again. CapKind has exactly door, vertexSlack, c5Base, prune, with no eta constructor (problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:25-31). FullBankRelaxedCoverBundleView is only demandQ plus four cap rationals; Checked assumes their nonnegativity and demandQ <= rhsQ (:33-54). It has no lam, q, or inc.

LedgerToken is (comp,kind,sourceId,capQ) (:67-74). GlobalLedgerData contains token, spendQ, componentReserveSlackQ, and superadditivitySlackQ (:76-82). FullBankGlobalPackage stores arbitrary counts/tables, row ownership maps, local covers, and ledger (:124-143). P.Checked is a Prop, not a Bool checker. It assumes local checks and surplus-to-demand (:183-186), cap-kind spend equalities (:187-194), nonnegative spend/caps, no-double-spend, no cross-component spend, and key uniqueness (:195-209), plus surplus ownership and reserve/global identities (:210-227).

The theorem chain is exact at :229-284. The final result is lengthSurplusGD rows <= 25*etaQ G c (:286-308), then gammaOfGD <= N² (:310-315). etaQ is explicitly ((N:Q)^2 - 25*badCount)/25 (CertGraph.lean:2311-2312). Thus “eta-free” means no eta token, not absence of etaQ from the conclusion. A literal reading of GOAL_LOOP.md:65 (“NO η anywhere”) exceeds compiled Lean.

FullBankChargeCertProvider is only a wrapper. It creates zero coefficients and one raw residual equal to lengthSurplusTarget (problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean:41-61), and proves the checker passes by first invoking fullBankGlobalPackage_sound (:64-80). Its gamma wrapper additionally assumes all-row GERSH (:82-93). It is not an existence provider.

## Completeness checklist versus ActiveScopedMinimumExchange.Available

| Class/predicate | Status | Exact comparison |
|---|---|---|
| ActiveCollisionHalf | present | Left branch of Demand. |
| ActiveHitNeed | present | Right branch of Demand. |
| FreeHalf | present | Matching codomain. |
| same-first/same-owner | present | sourceX = owner disjunct. |
| row companion | present | co-occurrence/co-occurrence/sigma disjunct. |
| ScopedReserved | present, negated | Removes half-zero active-edge sources. |
| common-blue/C5-base terminal | absent | Standalone Valid requires both source-owner blue edges and dM+2<=dB (problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean:24-43), but it is not an Available disjunct. |
| checked row-companion terminal | indirect | Standalone RawValid has row witnesses, pair-free, sigma, active owner (problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:70-85); no matching assembly consumes it. |
| prune/slot transport | absent | No disjunct or compiled aggregate matching. |
| FullBank S rows | absent | R29 demands are collision/hit units. |
| support edges F | absent | No support capacity in Available. |
| off-support O / E0 | indirect only | Graphically related to activeEdges, but roles/scales differ and no map exists. |
| vertex sinks V0 / Sum.inl | indirect only | Active owners are demand owners, not capacity sinks. |
| own-Door sinks Sum.inr e | absent | R29 reservation is not door flow/capacity. |
| generic JT/inc/kap | absent | Available is never instantiated as inc. |
| CapKind door | absent | No Door token in R29. |
| CapKind vertexSlack | absent | HitNeed subtracts slack numerically but emits no token. |
| CapKind c5Base | absent | Standalone terminal exists; no token emitted. |
| CapKind prune | absent | No active-scoped representation. |
| DoorToken / NonDoorToken | absent | They merely partition ledger indices by kind (problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean:19-25). |
| typed CapSource | absent | Separate four-constructor type (problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:23-41). |
| reserve/superadditivity slack | absent | Aggregate non-spendable ledger fields only. |

## Aliases, double-counting risks, and stale APIs

1. CanonicalCollisionHall.Available is collision-only Eligible ∧ not Reserved (MinimumDemandCollisionHall.lean:99-109). ActiveScopedMinimumExchange.Available is collision-plus-hit and uses EligibleOwner/ScopedReserved. Unqualified Available is unsafe.
2. FullBankRelaxedCoverCert, FullBankRelaxedCoverBundleView, and FullBankGlobalPackage are not aliases. No constructor links them.
3. R29 “sources” are FreeHalf; typed FullBank “sources” are token provenance; primal FullBank routed sources are off-support edges. These roles point in different directions.
4. FreeHalf is ordered and doubled by half. Any conversion to undirected FullBank edges needs a scaling theorem; none exists.
5. P.Checked prevents aggregate double spending only by assumed fields no_double_spend, token_source_unique, componentReserveIdentity, and superadditivityIdentity (FullBankToLengthSurplusCharge.lean:199-227). R29 constructs none.
6. Legacy FullBankGlobalPackage still uses kind plus sourceId : Nat. Typed CapSource/TypedLedgerToken are parallel and not embedded. OwnEdgeDoorSourceData.Checked proves typed door source/capacity (TypedFullBankSources.lean:91-112), but the wall adapter is caller-supplied (problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean:34-42).
7. NonDoorToken merges vertexSlack, c5Base, and prune by kind != door (FullBankPortSinks.lean:19-25). The same file explicitly says legal edge-to-token incidence is absent and no Hall condition is asserted (:80-81).
8. Coordination’s EndpointHalfBoundaryPartition “needed” statement is stale (coordination/CLAUDE_TO_CODEX.md:13764); the type is now compiled.
9. FullBankLPBundleEquivalence remains absent; coordination called it needed (:13767-13770).
10. GOAL_LOOP.md:16’s CheckedTransferMatching and ActiveComponentFullBankCert names are prose only. Coordination still described wiring the standalone row-companion terminal into that future stack (coordination/CLAUDE_TO_CODEX.md:13807-13810).
11. Ell5FullBankRelaxedCover_exists occurs in Lean only in comments describing an open/future theorem (Ell5FullBankInterface.lean:6-10).
12. Coordination’s “interface ... COMPILED end-to-end” is immediately qualified as “wall = construct a Checked FullBankGlobalPackage” (coordination/CLAUDE_TO_CODEX.md:13651-13654). The consumer is compiled; existence is not.
13. R29 coordination reports the narrow relation and then asks for eligibility enrichment beyond same-first/companion (coordination/CLAUDE_TO_CODEX.md:13995-14005), confirming 28 is relation-relative.

## Executable implementation search and unresolved gaps

Present Python: r29_lead_gate.py::build/scoped_state; d09/retry2/verify.py::state (tmp/fanout/r29_gate/d09/retry2/verify.py:45-72); rebuild_owner_hall.py::rebuild_scope/owner_sources; verify_cut_certificate.py; verify_r29_global_min_hall_falsifier.py::verify_hall_certificate/main.

Scoped search:

    rg -n -g "*.py" "FullBankGlobalPackage|FullBankRelaxedCoverCert|ActiveComponentHall|BankedCutDomination|CheckedTransferMatching" tmp/fanout/r29_gate tmp/fanout/global_min_proof problems/23/writeup

returned no matches. There is no Python FullBank implementation in that scope.

Unresolved production gaps:

1. Define compiled CheckedTransferMatching with sameFirst/commonBad/rowCompanion/prune and its exact legal relation.
2. Prove how it compares with ActiveScopedMinimumExchange.Available.
3. Construct transfer tokens and derive EndpointReserveHall/ActiveComponentHall hypotheses with exact orientation/scaling.
4. Define graph-derived FullBank inc and kap.
5. Bridge GraphData/CutData/complete rows to SimpleGraph/S,F,O,J,K.
6. Convert FullBankRelaxedCoverCert to bundle views, typed tokens, spends, reserves, and P.Checked.
7. Migrate typed CapSource into FullBankGlobalPackage or prove a lossless adapter.
8. Prove real-graph existence of a checked FullBankGlobalPackage.
9. If defect 28 is claimed for the enriched relation, build a new exact enumerator; current code proves it only for Available.

## Commands run

Key searches/reads:

    Get-Content -Raw COMMON.md, GOAL_LOOP.md, coordination/CLAUDE_TO_CODEX.md, R29 write-up
    rg -n for Available, HallFailureHasScopedScoreGlobalDescent, FullBank names, target APIs
    rg -n --max-depth 1 and Gamma searches for CheckedTransferMatching,
      ActiveComponentFullBankCert, FullBankLPBundleEquivalence,
      EndpointHalfBoundaryPartition, Ell5FullBankRelaxedCover_exists
    rg -n "\bsorry\b|\badmit\b|native_decide|sorryAx" <cited Lean sources>
    Get-FileHash -Algorithm SHA256 <every cited source>

No sorry/admit/native_decide/sorryAx hit was found in cited Lean sources.

Exact read-only replays:

    python -B tmp/fanout/r29_gate/d05/retry2/verify_cut_certificate.py
    python -B tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py

No production, Lean, coordination, progress, or sibling-lane file was edited.

## SHA-256 of every cited source

    49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
    e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
    6ce365ff45578dbbadb238f691700012df52ddb1afa82331027b0e51aff6a614  coordination/CLAUDE_TO_CODEX.md
    5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
    93150a508e19f634d93596b75e9950dc0d0cb72a393efdecb2efda97969bbd31  problems/23/lean/Erdos23Delta0/CertGraph.lean
    590b8f0def00520d17dcce54dedfc137989ec482409260630de3c50246e595eb  problems/23/lean/Erdos23Delta0/GammaAggregation.lean
    e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean
    ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
    6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
    6a4d47533d10e4b04eb19cda0d0554658abd434c94c04566a01916708a90e8f0  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedOwnerHallReduction.lean
    12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0  problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean
    84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean
    4edf663b6d0e1949561d9eed0dd81b51e84c4e18880290787487ea80dc138e6e  problems/23/lean/Erdos23Delta0/BankedCutDominationCore.lean
    8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104  problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean
    180f362f8d0ba889c485385703c713e619d22c5f1ab5b4e15cba60d54ffb197f  problems/23/lean/Erdos23Delta0/Ell5ActiveComponentHall.lean
    9cfa35f2714799ddd4e1a187c2d6d620dae7c15d920f114896b4f30218274440  problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean
    bfb51085e469bb0011e5ec861ff99cbde3d45e2bdaca75686bbf10fa7c3fa13a  problems/23/lean/Erdos23Delta0/EndpointHalfRelaxedCutCover.lean
    f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd  problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean
    ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6  problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean
    8f7941dfa55dc9f5b60bc9666af4cd8d330d4f5d3a03010651d67a3711f50e92  problems/23/lean/Erdos23Delta0/Gamma/FullBankChargeCertProvider.lean
    6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd  problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean
    793f8b47926dbe93e2b0f476e42ae33a688913faa95e46912205ec69009a4eaa  problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean
    5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6  tmp/fanout/r29_gate/lead/r29_lead_gate.py
    e2958cea60a225b0af89dcfcf5db0c054dea188e305dfb012bbee7b454337d20  tmp/fanout/r29_gate/d09/retry2/verify.py
    a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
    31ce4c7f531076e40dda41d0344b78eae4b9c0d2e5fd2ad968edcfcc6823be04  tmp/fanout/r29_gate/d05/retry2/verify_cut_certificate.py
    668f427042c4666e21ec41ee454136aefce789a8cba8adacf703853ef373347c  tmp/fanout/global_min_proof/lead/verify_r29_global_min_hall_falsifier.py

## Final finding

R29 is a valid, exact falsifier of the current active-scoped selector/matching provider. It is not a FullBank falsifier. The compiled end point is only the conditional implication P.Checked -> lengthSurplusGD <= 25*etaQ -> gammaOfGD <= N². The production gap is constructing P.Checked from real graph data through the not-yet-compiled transfer relation and missing representation/ledger adapters.

