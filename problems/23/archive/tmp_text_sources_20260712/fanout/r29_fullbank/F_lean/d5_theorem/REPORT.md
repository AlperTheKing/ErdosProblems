# R29-to-FullBank theorem probe

## Signature audit

The real selected-cut surface is `CertGraph.GoodCutData G c rows` (`CertGraph.lean:2673`): it already supplies `IsMaxCut`, `GammaMinimalConnected`, `BConnected`, `RowDBFactsGeneral`, and `GammaBetaFacts`. The R29 finite relation surface is different: `MinimumDemandRowSelection.AllBadsChecked G c bads`, `RowChoice bads`, and `CanonicalCollisionHall.CompleteShortestRowDB G c bads` (`MinimumDemandRowSelection.lean:32`, `MinimumDemandCollisionHall.lean:33`). There is no compiled conversion from `List BadEdgeData` to the selected `RowDB` used by `GoodCutData`.

The first missing FullBank provider is package existence. `FullBankGlobalPackage` is only data (`FullBankToLengthSurplusCharge.lean:134`), and its `Checked` structure (`:177`) includes `local_view_checked`, `demand_le_rhs` transitively, `no_double_spend`, reserve identities, and the global identities. Therefore a theorem taking `P.Checked` as a hypothesis is downstream bookkeeping and circular as an R29 probe. `fullBankGlobalPackage_sound` (`:289`) proves the target inequality only after that hypothesis.

## Candidate 1 (preferred universal provider seam)

```lean
theorem fullBankGlobalPackage_exists_of_goodCut
    {G : CertGraph.GraphData} {c : CertGraph.CutData} {rows : CertGraph.RowDB}
    (hGraph : CertGraph.checkGraph G = true)
    (hCut : CertGraph.checkCut G c = true)
    (hTri : CertGraph.TriangleFree G)
    (hGood : CertGraph.GoodCutData G c rows) :
    ∃ P : FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows,
      FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked P
```

Rationale: this is the smallest honest theorem at the first missing provider boundary. All premises are graph/cut/row facts already produced upstream; none is a FullBank feasibility or inequality assumption. A genuine full-relation construction must build `P` and every checked field. A single R29 instance satisfying the four premises but admitting no checked package falsifies it. `hGraph` and `hCut` are retained because they are the literal certified-data guards used by `erdos23_delta0_graphData_from_good_cut`; `hGood` supplies max-cut, Gamma-minimality, blue connectivity, and row facts.

## Candidate 2 (smallest instance-level falsifier/discharge probe)

```lean
def FullBankProviderProbe
    (G : CertGraph.GraphData) (c : CertGraph.CutData) (rows : CertGraph.RowDB) : Prop :=
  CertGraph.checkGraph G = true ∧
  CertGraph.checkCut G c = true ∧
  CertGraph.TriangleFree G ∧
  Nonempty (CertGraph.GoodCutData G c rows) ∧
  ∃ P : FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows,
    FullBankToLengthSurplusCharge.FullBankGlobalPackage.Checked P
```

Rationale: instantiate this with the canonical R29 `G`, cut, and the actual selected `RowDB`. A full-relation certificate discharges exactly the last conjunct by constructing the package; exact infeasibility falsifies the probe without claiming a counterexample to Erdős #23. This is preferable for artifact checking because it does not quantify over unrelated graphs.

## Required adapter before either candidate can consume the current R29 API

```lean
theorem r29_rows_agree
    {G : CertGraph.GraphData} {c : CertGraph.CutData}
    {rows : CertGraph.RowDB} {bads : List CertGraph.BadEdgeData}
    (hGood : CertGraph.GoodCutData G c rows)
    (hDB : CanonicalCollisionHall.CompleteShortestRowDB G c bads) :
    rows.rowList.length = bads.length
```

Rationale: this is only the weakest necessary coherence probe, not enough to construct FullBank. Its failure proves the current R29 relation is not even indexed by the provider's row database. Its success still requires a stronger value-level bijection preserving bad-edge ownership and row supports before any `RowChoice` full-relation result can populate local covers, tokens, or spends. No existing signature supplies that bridge, so a theorem stated solely from `AllBadsChecked`/`CompleteShortestRowDB` directly to `FullBankGlobalPackage.Checked` would silently assume missing row identity data.
