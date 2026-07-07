# CONJUNCT-4 PACKAGE-OBLIGATION AUDIT (adversarial workflow, 2026-07-07) — the definitive Lean gap ledger

6-agent adversarial audit (wf_39d022d1-cae) mapping every `SimpleGraphCertificatePackage` field to its
discharging module + flagging stubs/gaps. Full JSON: tasks/wx0g960by.output. Grep-CONFIRMED by Claude where noted.

## Verdict per package obligation
- **enc (SimpleGraphEncodingFacts)** = PROVEN GREEN. `simpleGraphEncodingFacts_default` total, no sorry (CertGraph.lean:3330-3344).
- **good : GoodCutData (M6 existence)** = STRUCTURE-STUB. No `∀ tri-free G, ∃ GoodCutData`. The 3 providers
  (GammaMinSelectionProvider, ConnectedMaxCutImpliesBConnected, ExistsGoodCutConnectedProvider) are UNINHABITED
  structs, instantiated only in Toy/OddCyclePackingC5. RowDB is never GENERATED (no emitter). NOT 108-gated.
- **delta.branchA** = AT-RISK GAP, 108-gated. `ConcreteODLLeafChecks` (ODLFull.lean:349-366) never instantiated;
  EQ/SIB dispatch hard-returns false (ODLFull.lean:394-395); no O14 module/dir exists; ODLFullProvider (28) unbuilt.
- **delta.branchB** = STRUCTURE-STUB. Modules 21-26 DESIGNED (MAIN thread) but NOT WRITTEN; only ODLBridge (27)
  exists and it only ASSUMES hBankedUPO. NOT 108-gated (checker layer); per-row DATA (35-38) is 108-gated.
- **AGGREGATION** = AT-RISK GAP + INTEGRATION BROKEN (**Claude grep-CONFIRMED**):
  CertGraph.lean imports NOTHING from GammaAggregation (0 `import Erdos23Delta0.*`); active
  `gammaBetaProvider_of_rowDB` (L3414, used L3618) -> `gammaUpper_from_all_rows_gersh` (L3407) ->
  `totalRowSum_le_N2_of_gersh` FIELD (L3367) = the route GammaAggregation.lean:4-14 declares UNSATISFIABLE at
  extremal (Σ rowSum = N^3/25 > N^2). Corrected `gammaUpper_from_chargeCertV2` (GammaAggregation.lean:266) is
  green but ORPHANED (0 uses in CertGraph). => erdos23_delta0 compiles green but its package is un-constructible
  via the active aggregation route for extremal graphs.

## Ranked remaining gaps (most-critical first)
1. AGGREGATION INTEGRATION BROKEN — graft GammaAggregation.gammaUpper_from_chargeCertV2 into CertGraph, replacing
   the buggy RowDBGammaFacts/totalRowSum_le_N2_of_gersh route in gammaBetaProvider_of_rowDB. Both already compiled.
2. M6 good-cut existence unbuilt — the largest single missing construction; gates any UNCONDITIONAL result.
3. Branch-A concrete leaf checkers absent (CONE/NO_OVERFULL/NEG_SWITCH/BANK_BLOCK/LENS_GATE + EQ/SIB) + O14 cover.
4. Branch-B provider stack (21-26) not written; nothing emits the per-row Banked-UPO bound.
5. Coverage not structural — rowList_length_eq_badCount is a hypothesis field, not a compiled all-edges-covered theorem.
6. Residual nonnegativity (lrsVal/cauchyVal/bankReserveVal) has no universal compiled 0<= proof.

## deepest_open_node
Branch-B per-row Banked-UPO emission (modules 21-26): a compiled provider certifying rowSum <= N + eta/2 - rho(L)
for EVERY long row via Dict24->CombinedHBD->CDTelescope->BankedUPO w/ single-spend + CD-contiguity. ODLBridge only
assumes it (hBankedUPO). Hardest research core (Pure-UPO at k=0).

## buildable NOW (no 108): DAG 19-30 + the GammaAggregation->CertGraph graft.
## gated on 108: DAG 31-45 (O14 emitted DATA + final data-consuming assembly).

## HONEST P(Lean) RECALIBRATION
The axiom-clean chain (base + FC bridge + ODLBridge, [propext,Classical.choice,Quot.sound]) is real but CONDITIONAL
on the certificate package. The package CONSTRUCTION (M6 existence + Branch-A leaves + Branch-B stack + aggregation
wiring + structural coverage) is largely UNBUILT. Prior memory "P(Lean)~97" reflects the conditional framework, NOT
the sorry-free unconditional proof. Honest P(Lean complete) ~= 30-40%: framework solid, hard constructions remain.
