# Lean dependency-chain audit: real graph data to FullBank endpoints

## Verdict

There is **no compiled theorem or definition in the production sources that constructs either**
`Ell5FullBankInterface.FullBankRelaxedCoverCert` **or**
`Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked` from real graph data.

The repository contains two separate, type-incompatible tracks:

1. a `SimpleGraph V` / Boolean-coloring track whose graph-derived objects are `deltaM` and `deltaB`, and
2. a `CertGraph.GraphData` / `CutData` / `RowDB` aggregate-ledger track.

`CertGraph.graphDataOfSimpleGraph` bridges the underlying graph representations, but no production declaration connects a `FullBankRelaxedCoverCert` (or its fields) to a `FullBankGlobalPackage`, and no declaration constructs `FullBankGlobalPackage.Checked` from the encoding bridge.

The source tree contains compiled `.olean` artifacts for both defining modules under `tmp/` output directories. A fresh source compile could not be run in this shell because `lake env lean` reports `no default toolchain configured`; this audit therefore uses the production declarations and their existing compiled artifacts, not a newly generated probe.

## Track A: real `SimpleGraph` data and `FullBankRelaxedCoverCert`

### Genuine graph-derived chain

- `MaxCutVertexIneq.edgeCut`, `edgeBoundary`: `problems/23/lean/Erdos23Delta0/MaxCutVertexIneq.lean:58`, `:61`.
- `MaxCutVertexIneq.deltaB`, `deltaM`: `MaxCutVertexIneq.lean:83`, `:87`.
- `MaxCutVertexIneq.IsMaxCut`: `MaxCutVertexIneq.lean:105`.
- `MaxCutVertexIneq.deltaM_card_le_deltaB_card`: `MaxCutVertexIneq.lean:109`.

Logical arrow:

`G : SimpleGraph V` + `cut : V -> Bool` + `U : Finset V` + `hmax : IsMaxCut G cut`
`-> |deltaM G cut U| <= |deltaB G cut U|`.

The abstract relaxed-cover theorem is `RelaxedCutCover.relaxed_cutcover_defect_bound` at
`problems/23/lean/Erdos23Delta0/RelaxedCutCover.lean:40`. The real-graph specialization is
`RelaxedCoverGraphBridge.graph_defect_bound` at
`problems/23/lean/Erdos23Delta0/RelaxedCoverGraphBridge.lean:65`; it uses
`deltaB_subset_cutEdges` (`:33`) and discharges only the per-cut cardinal-capacity premise with
`deltaM_card_le_deltaB_card` (`:80`).

Logical arrow:

`G, cut, hmax, S, F, hF, K, Ufam, lam, hlam, hcov, hcong`
`-> graph_defect_bound`.

Thus real graph data supplies the meanings of `deltaM`/`deltaB`; maximum-cut data supplies their cardinal inequality. It does **not** supply the weighted cover.

### Certificate interface

`Ell5FullBankInterface.FullBankRelaxedCoverCert` is declared at
`problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean:27`. Its graph specialization,
`GraphFullBankRelaxedCoverCert`, is only an abbreviation at `:64`; it substitutes
`sep k := deltaM G cut (Ufam k)` and `dB k := deltaB G cut (Ufam k)` (`:69-71`). It is not a constructor or existence theorem.

The compiled algebraic consumption chain is:

`FullBankRelaxedCoverCert`
`-> RelaxedCoverBanked.bankedCutDomination_of_relaxed_cover`
(`problems/23/lean/Erdos23Delta0/RelaxedCoverBanked.lean:32`)
`-> Ell5FullBankInterface.bankedCutDomination_of_cert`
(`Ell5FullBankInterface.lean:43`)
`-> Ell5FullBankInterface.graph_bankedCutDomination_of_cert`
(`Ell5FullBankInterface.lean:74`).

The parallel refutation chain is:

`FullBankRelaxedCoverCert`
`-> RelaxedCoverBanked.no_dualCert_of_relaxed_cover`
(`RelaxedCoverBanked.lean:56`)
`-> Ell5FullBankInterface.no_dualCert_of_cert`
(`Ell5FullBankInterface.lean:53`)
`-> Ell5FullBankInterface.graph_no_dualCert_of_cert`
(`Ell5FullBankInterface.lean:89`).

These soundness arrows consume a certificate. They never derive one from `G`, `cut`, or `hmax`. In particular, `FullBankRelaxedCoverCert` itself has no maximum-cut field, and its soundness proof does not use `deltaM_card_le_deltaB_card`.

### Every certificate hypothesis not supplied by real graph data

Besides choosing the index/data sets `S`, `F`, `O`, `J`, `K`, `Ufam`, legal-incidence relation `inc`, and capacity function `kap`, one must supply:

- `lam : iota -> Q` (`Ell5FullBankInterface.lean:31`);
- `q : E -> JT -> Q` (`:32`);
- `hlam`, nonnegative cut weights (`:33`);
- `hq`, nonnegative routed amounts (`:34`);
- `hkap`, nonnegative bank capacities (`:35`);
- `hcov`, unit coverage of every row in `S` (`:36`);
- `hcong`, support-edge congestion at most one (`:37`);
- `hroute`, every off-support boundary load is routed (`:38`);
- `hcap`, every sink respects its capacity (`:39`);
- `hqinc`, positive flow uses a legal incidence (`:40`).

`Ell5FullBankAssignedSink.cert_of_assignedSink` at
`problems/23/lean/Erdos23Delta0/Ell5FullBankAssignedSink.lean:56` is a convenience constructor, not a graph extractor. It still assumes `lam`, `sink`, `hlam`, `hkap`, `hcov`, `hcong`, `hsink`, `hinc`, and `hcap` (`:60-68`).

`Ell5FullBankWallAdapter.certOfPrimal` at
`problems/23/lean/Erdos23Delta0/Ell5FullBankWallAdapter.lean:115` gives
`Wall.Primal -> FullBankRelaxedCoverCert`; it merely relocates the missing obligation to construction of a `Wall.Primal`.

## Track B: encoded graph data and `FullBankGlobalPackage.Checked`

### Genuine representation bridge

- `CertGraph.GraphData`: `problems/23/lean/Erdos23Delta0/CertGraph.lean:15`.
- `CertGraph.CutData`: `CertGraph.lean:53`.
- `CertGraph.RowDB`: `CertGraph.lean:2453`.
- `CertGraph.graphDataOfSimpleGraph`: `CertGraph.lean:2814`.
- `CertGraph.cutDataOfColoring`: `CertGraph.lean:2822`.
- `CertGraph.SimpleGraphEncodingFacts`: `CertGraph.lean:2847`.
- `CertGraph.simpleGraphEncodingFacts_default`: `CertGraph.lean:3330`.

Logical arrow:

`Gs : SimpleGraph V -> graphDataOfSimpleGraph Gs : GraphData`, with checked encoding and transfer facts.

This arrow transfers the graph/cut representation and counts. It does not construct rows, components, local covers, tokens, spends, or any full-bank certificate.

### Package and soundness chain

`FullBankRelaxedCoverBundleView` is only five rational fields at
`problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean:34`; it does not contain an
`Ell5FullBankInterface.FullBankRelaxedCoverCert`.

`FullBankLocalCover` is declared at `FullBankToLengthSurplusCharge.lean:125`, and
`FullBankGlobalPackage` at `:134`. No field of either structure references
`FullBankRelaxedCoverCert`, `GraphFullBankRelaxedCoverCert`, `deltaM`, `deltaB`, or `Wall.Primal`.

The compiled bookkeeping chain is:

`P : FullBankGlobalPackage G c rows` + `h : P.Checked`
`-> localSurplus_le_localDemand` (`:229`)
`-> localDemand_le_localCap` (`:235`)
`-> localCap_eq_localSpend` (`:242`)
`-> localSpend_eq_tokenSpend` (`:250`)
`-> tokenSpend_le_tokenCap` (`:256`)
`-> componentTokenCap_le_componentResidual` (`:262`)
`-> componentResidual_le_globalResidual` (`:272`)
`-> fullBankGlobalPackage_sound` (`:288`)
`-> gammaUpper_from_fullBankGlobalPackage` (`:311`).

This is a soundness chain from the assumed proposition `P.Checked`, not an existence chain from graph data.

### Every `FullBankGlobalPackage.Checked` hypothesis not supplied by real graph data

First, the package data itself must be independently supplied: `componentCount`, `localCount`, `tokenCount`, `compN`, `componentRowCountQ`, `compOfRow`, `localOfRow`, `localCover`, and `ledger` (`FullBankToLengthSurplusCharge.lean:135-143`). A real `GraphData` value determines none of these.

Then all 19 fields of `FullBankGlobalPackage.Checked` (`:177-227`) remain proof obligations:

1. `rows_length_eq_badCount` (`:178`).
2. `row_length_ge_five` (`:179-180`).
3. `row_local_component` (`:181-182`).
4. `local_view_checked` (`:183-184`), which expands to six further local facts: demand, four cap kinds nonnegative, and demand at most their sum (`:48-54`).
5. `surplusInLocal_le_demand` (`:185-186`).
6. `localCap_eq_kindSpends` (`:187-192`).
7. `localCap_eq_spendOfLocal` (`:193-194`).
8. `spend_nonneg` (`:195-196`).
9. `tokenCap_nonneg` (`:197-198`).
10. `no_double_spend` (`:199-200`).
11. `no_cross_component_spend` (`:201-203`).
12. `token_source_unique` (`:204-209`).
13. `lengthSurplus_eq_localSurplus` (`:210-211`).
14. `tokenCapTotal_eq_componentTokenCapTotal` (`:212-213`).
15. `componentReserveSlack_nonneg` (`:214-215`).
16. `componentReserveIdentity` (`:216-219`).
17. `componentRowCountSum` (`:220-222`).
18. `superadditivitySlack_nonneg` (`:223-224`).
19. `superadditivityIdentity` (`:225-227`).

Even graph validity, cut validity, triangle-freeness, and maximum-cut status are **not fields of `FullBankGlobalPackage.Checked`**. Conversely, the encoding facts do not imply the 19 ledger obligations.

## Missing logical arrows

The actual dependency graph stops at the following gaps:

`real SimpleGraph + maximum cut`
`-> deltaM/deltaB cardinal inequality`
`-/-> FullBankRelaxedCoverCert`.

`FullBankRelaxedCoverCert`
`-/-> FullBankRelaxedCoverBundleView`
`-/-> FullBankLocalCover`
`-/-> FullBankGlobalPackage`
`-/-> FullBankGlobalPackage.Checked`.

`graphDataOfSimpleGraph + cutDataOfColoring + encoding facts`
`-/-> FullBankGlobalPackage.Checked`.

The production countermodel `AggregateLedgerNoIncidenceCounterexample.emptyPackage_checked` at
`problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean:49` confirms the separation: an empty aggregate package satisfies `Checked`, while the file states that `Checked` contains no wall-port/token incidence relation (`:8-16`). Therefore `Checked` cannot by itself recover the missing full-bank routing certificate.

## Audit conclusion

The compiled code proves conditional soundness on both sides, but the requested real-data-to-endpoint dependency chain does not exist. The exact open construction obligations are the ten certificate fields (plus their indexing/capacity data) for `FullBankRelaxedCoverCert`, and the package data plus all 19 `Checked` fields for `FullBankGlobalPackage.Checked`, together with a currently absent typed bridge relating the former certificate's rows/ports/sinks/capacities to the latter local views/tokens/spends.
