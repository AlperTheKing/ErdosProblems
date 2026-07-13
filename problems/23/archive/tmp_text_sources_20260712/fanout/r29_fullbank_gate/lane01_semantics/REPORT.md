# R29 FullBank production-semantics audit

## Verdict

**UNDEFINED.** Production Lean does not define a complete R29 transfer/bank incidence instance. Therefore the auxiliary 28-unit hub-shore defect is not yet either absorbed (PASS) or persistent under every production source class (FAIL).

This is a semantic conclusion, not a numerical extrapolation. The exact demand 19,953, reachable FreeHalf count 19,925, and defect 28 belong to Gamma.ActiveScopedMinimumExchange.Available. Its compiled relation is same-owner/row-companion eligibility after reservations. The authoritative R29 writeup limits the falsifier to the selector/matching route (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96).

build_audit.py does not trust those copied totals: it imports the deterministic cage constructor, rebuilds rows, pair counts, support, active components, collision and HitNeed demand, and owner eligibility through rebuild_owner_hall.py, then asserts N=2943, demand=19953, reach=19925, and defect=28. The exact reconstructed record is in AUDIT_CHECK.json.

## Compiled FullBank contract

Path convention: bare Lean module filenames below are relative to problems/23/lean/Erdos23Delta0; Gamma/... is relative to its Gamma subdirectory. Bare gate/writeup filenames are relative to problems/23/writeup. SEMANTICS.json records every citation with its full workspace-relative path.

FullBankRelaxedCoverCert takes finite rows S, support F, off-support ports O, sinks J, cuts K, sep, dB, an arbitrary incidence predicate inc, and rational capacity kap. Its fields require nonnegative weights, row coverage, support congestion, off-support routing, per-sink capacity, and legal support for every positive flow (problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27-40).

The active-component consumer specializes this to:

- obligations E0 O D = O minus D, weighted by actual blockLoad (Ell5ActiveComponentBankHall.lean:23-33);
- sinks JT plus Sym2 V, separating generic non-Door sinks from edge-indexed Door sinks (Ell5BlockBankFlow.lean:22; Ell5ActiveComponentBankHall.lean:35-49);
- combinedInc incBase incDoor and combinedCap kapBase kapDoor;
- weighted Hall over every subset of E0, using the union of incBase neighborhoods (Ell5ActiveComponentBankHall.lean:51-64);
- one global capacitated flow, so overlapping eligibility cannot duplicate a sink capacity (Ell5ActiveComponentBankHall.lean:142-153,174-186).

The decisive point is that incBase and kapBase remain caller-supplied in both ActiveComponentBankHall and certificate_of_activeComponent_mixedDoorBankHall (Ell5ActiveComponentBankHall.lean:53-59,109-129). No compiled R29 definition supplies them.

The resulting certificate is consumed by:

1. banked cut domination and exact-dual exclusion (Ell5FullBankInterface.lean:42-60);
2. the scaled Hall/bank inequality (Ell5FullBankHall.lean:28-66);
3. the canonical Wall.BankedWallLP primal and strict-dual contradiction (Ell5FullBankWallAdapter.lean:27-49,225-245).

## Gamma ledger does not define incidence

FullBankGlobalPackage is a separate aggregate layer. Its four token kinds are door, vertexSlack, c5Base, and prune (Gamma/FullBankToLengthSurplusCharge.lean:25-31). A token carries component, kind, sourceId, and capQ, while spendQ is indexed only by local cover and token (:67-82).

Checked.no_double_spend sums all local spends into each token and bounds the result by capQ; no_cross_component_spend restricts positive spend by component (:195-209). Thus this layer enforces overlap-free capacity accounting.

However, FullBankGlobalPackage.Checked has no wall port, edge, or legal-incidence argument. Gamma/FullBankPortSinks.lean:80-81 explicitly says its finite sink subtypes do not assert Hall. AggregateLedgerNoIncidenceCounterexample.lean:145-157 proves that aggregate package checking alone cannot create port routing. The ledger consumer is gammaUpper_from_fullBankGlobalPackage (Gamma/FullBankToLengthSurplusCharge.lean:286-315), not an Ell5 FullBank-flow constructor.

Typed keys do not close the gap. CapSource carries typed payloads for all four kinds, and doorLegal implements own-Door equality (Gamma/TypedFullBankSources.lean:23-41,130-132). The same file says connection to the wall Sink is a separate adapter obligation (:12-14). Gamma/TypedOwnDoorHalfLayer.lean:34-42 defines that adapter as input data, not as an extractor from R29 or FullBankGlobalPackage.

## Transfer relations

Compiled:

- SameOwner: sourceX equals owner (Gamma/MinimumDemandCollisionHall.lean:82-87);
- RowCompanion: both coordinates co-occur with the owner and the two-vertex switch has nonnegative sigma (:89-103);
- active-scoped EligibleOwner, merging those cases for collision and HitNeed obligations (Gamma/ActiveScopedMinimumExchange.lean:134-147);
- CheckedC5BaseTransfer.TerminalData.Valid, checking two blue source-owner edges and dM+2 <= dB (Gamma/CheckedC5BaseTransfer.lean:24-43);
- CheckedRowCompanionBaseTransfer.TerminalData.RawValid, checking selected-row witnesses, freeness, switch loss, and active ownership (Gamma/CheckedRowCompanionBaseTransfer.lean:57-85).

The terminal checkers are not wired to a compiled transfer matching or FullBank constructor. The replay search finds no production definition named CheckedTransferMatching, TransferObligation, FreeHalfKey, or CheckedOutsideAttachmentBaseTerminal; see AUDIT_CHECK.json.

The four-pattern Python relation is sameFirst, commonBad, rowCompanion, and outsideAttachment. The exact R23 Python gate implements same-owner at _codex_r23_outside_attachment_full_obligation_gate.py:281-284, positive-cooccurrence row-companion at :286-295, and outside-component attachment at :297-311. The R23 writeup defines pattern 4 at WALL_ATTACK_R23_GPTPRO56.md:7-15. outsideAttachment has no compiled Lean equivalent.

commonBad cannot be identified with one compiled predicate without an adapter proof: the older staged Python gate uses pairs of bad neighbors (_claude_r20_staged_matching_gate.py:163-182), the R23 gate calls it a row-companion subcase, and the compiled C5 terminal checks blue source-owner edges. prune is a token/source label, but no compiled injective slot-transport trace relation was found.

## Data required for a defined R29 test

A production test needs one coherent instance containing:

- the exact finite SimpleGraph V corresponding to reconstructed GraphData, cut coloring, complete row database, and all-anchor choice;
- C, Comp, comp, active, S, F, O, and Door subset D, with the graph/support proofs at Ell5ActiveComponentBankHall.lean:120-129;
- a finite base sink type JT, concrete incBase/kapBase, Door incidence/capacity, and weighted Hall for every E0 shore;
- Gamma component/local/token tables and one overlap-free global spendQ satisfying all FullBankGlobalPackage.Checked fields;
- a typed port-to-token adapter proving that the Ell5 incidence/capacity uses those same ledger tokens.

Lean has a canonical finite SimpleGraph-to-GraphData encoding (CertGraph.lean:2797-2825). It is not a FullBank extractor and points opposite to the supplied R29 Python reconstruction. No canonical extractor currently produces the R29 rows, active partition, ports, typed sinks, incidence, capacities, or checked global package. EndpointHalfDoorComplete.lean:36-38 also records the missing extractor-labelled FullBank bundle.

## Commands

Run from E:\Projects\ErdosProblems:

    python tmp\fanout\r29_fullbank_gate\lane01_semantics\build_audit.py
    python -m json.tool tmp\fanout\r29_fullbank_gate\lane01_semantics\SEMANTICS.json
    python -m json.tool tmp\fanout\r29_fullbank_gate\lane01_semantics\AUDIT_CHECK.json
    python -m json.tool tmp\fanout\r29_fullbank_gate\lane01_semantics\SHA256SUMS.json

SEMANTICS.json is the machine-readable definition map. AUDIT_CHECK.json contains citation-line checks and Lean-tree searches. SHA256SUMS.json is the exact SHA256 manifest for all audited inputs and lane outputs.

## SHA256

Key authoritative hashes:

| File | SHA256 |
|---|---|
| GOAL_LOOP.md | e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b |
| R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md | 5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42 |
| r29_lead_gate.py | 5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6 |
| rebuild_owner_hall.py | a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0 |
| cut_certificate.json | dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce |
| Ell5FullBankInterface.lean | 8d02d032507152301ee7bc01b0a64b7614dfc0c754152be343aa3a3a3a9dd104 |
| Ell5ActiveComponentBankHall.lean | 9e907495d20492505ff85c613c033ee783a288ad790c8682ed575c0c1bec438d |
| Gamma/FullBankToLengthSurplusCharge.lean | f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd |
| Gamma/TypedFullBankSources.lean | 6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd |
| AggregateLedgerNoIncidenceCounterexample.lean | 624c56995234f4ef5d68804013ce69d66962cfb2a3230de7c8d601db6870089f |

SHA256SUMS.json contains the remaining audited sources and the exact hashes of SEMANTICS.json, REPORT.md, build_audit.py, and AUDIT_CHECK.json.
