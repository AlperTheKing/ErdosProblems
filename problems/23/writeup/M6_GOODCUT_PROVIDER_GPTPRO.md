# M6 good-cut existence provider — GPT-Pro design (2026-07-08, via user-relay during Chrome outage)

*Reply to the M6 retask (queued during the outage, relayed by the user). Full build-order module plan. Verbatim
structure preserved; Claude annotations as [CLAUDE: ...].*

## 0. Core design decision
Two layers: **GoodCutSelection** (choose a max cut minimizing Γ among B-connected max cuts) +
**GoodCutWithCharge** (attach RowDB + checked `LengthSurplusChargeCertV2`, build `GammaBetaFacts` through
`gammaUpper_from_chargeCertV2`). NEVER call `totalRowSum_le_N2_of_gersh` (the unsatisfiable route). The only
allowed path: all-rows-GERSH + ResidualFormulas F + `checkLengthSurplusChargeCertV2 F cert = true` ⟹
gammaVal ≤ n², via the green `GammaChargeGraft.gammaBetaProvider_of_chargeCert` /
`GammaAggregation.gammaUpper_from_chargeCertV2`. [CLAUDE: matches my wiring-audit constraint exactly.]

## 1. Selection
### 1.1 KEY LEMMA — every max cut is B-connected (per-bad-pair)
`isMaxCut_badEdge_blueConnected`: if bad edge endpoints u,v lie in different blue components, let U = blue
component of u. Then **δB(U) = 0** (U is a blue connected component — no cut edge leaves it) and **δM(U) ≥ 1**
(the bad edge crosses U), so flipping U improves the cut by ≥ 1 — contradicting IsMaxCut. Same local-flip
argument as the compiled vertex inequality, with the stronger fact δB(U)=0. ⟹ **BConnected needs NO
per-K2-component arrangement for the selection**; the component decomposition is for bank/cage arithmetic only.
[CLAUDE: compiled immediately as M6BlueConnectivity.lean — see below; uses my not_isMaxCut_of_improving_flip.]
Caveat noted: if BConnected meant "whole blue graph connected on all vertices" the claim is false; the
interface's per-bad-pair reading is the right one.

### 1.2 GammaMinimalConnected + selection
`GammaMinimalConnected G c := IsMaxCut ∧ BConnected ∧ ∀ c', IsMaxCut → BConnected → badCount c' = badCount c →
gammaOfCut c ≤ gammaOfCut c'` (badCount equality usually derivable since max cuts share cut value; keep if APIs
expect it). Selection = MaxCutSelection.exists_maxCut_argmin with Q := IsMaxCut ∧ BConnected, objective
gammaOfCut; nonemptiness from exists_maxCut + the key lemma.

## 2. RowDB construction
blueGraph/badEdges at GraphData level; per bad edge, `BlueGeodesic` = shortest BluePath. **Use ALL shortest
geodesics** (preferred over one canonical) for the multi-geodesic machinery. Row fields: badId; verts = V(p);
len = p.length + 1 = ell; load5 = indicator len=5 (or ×25 in square units); rowSumQ = Σ_g (1/#geos(g)) ·
Σ_{P ∈ geos(g)} |verts(r) ∩ verts(P)| — computed, not a proof field. `RowDB.ofCut` = Finset.sigma over bad
edges of allShortestBlueGeodesics; finiteness from simple paths (a shortest walk is simple).
`rowsFacts_ofCut`: every row length ≥ 5 from `Distances.badEdge_ell_ge_five`. "No difficult geometry remains."

## 3. GammaBeta instantiation
gammaVal := gammaOfCut = Σ ell²; betaVal := badCount; beta_eq_badCount := rfl (or via badCount =
edgeCount − cutVal). **gammaLower**: 25 ≤ ell² per bad edge, sum ⟹ 25·badCount ≤ Γ
[CLAUDE: = CageSuperadditivity.sum_sq_ge_25_mul_card, compiled]. **ChargeCertProvider** structure = {F :
ResidualFormulas, cert : LengthSurplusChargeCertV2, F_ok, checked} — "this is where the open full-bank Hall /
BankedCutDomination construction ultimately emits data; the GoodCut provider only consumes the checked object."
`gammaBetaFacts_of_chargeCert` assembles GammaBetaFacts with gammaUpper via the graft ONLY.

## 4-5. Provider + existence theorem
`GoodCutExistenceProvider` structure (cut, rows, maxCut, gammaMin, bConnected, rows_eq, rowsFacts, charge) +
`GoodCutData.ofProvider`. Honest existence theorem `exists_goodCutData_of_chargeProvider` CONDITIONAL on the
charge provider for the selected cut; per-instance assembly emits `charge` and Lean checks
`checkLengthSurplusChargeCertV2 = true`.

## 6. Build-order modules
- **M6GoodCut.BlueConnectivity** (imports MaxCutVertexIneq, Distances): blueGraph/badEdges/BConnected +
  isMaxCut_badEdge_blueConnected + isMaxCut_BConnected. [CLAUDE: DONE at SimpleGraph level, M6BlueConnectivity.lean.]
- **M6GoodCut.Selection** (+ MaxCutSelection): gammaOfCut, GammaMinimalConnected,
  exists_gammaMinimalConnected_maxCut.
- **M6GoodCut.RowDBOfCut** (+ Ell5SupportFinset, Ell5AtomGraph): BlueGeodesic, allShortestBlueGeodesics,
  Row.ofGeodesic, RowDB.ofCut, row_len_eq_ell, rowsFacts_ofCut. Remaining = finite enumeration of shortest
  simple blue paths + field simp lemmas + Nat→Rat casts. No hard math.
- **M6GoodCut.GammaBetaCharge** (+ GammaAggregation, GammaChargeGraft): ChargeCertProvider,
  gammaLower_of_rowsFacts, gammaBetaFacts_of_chargeCert.
- **M6GoodCut.Provider** (+ CertGraph): GoodCutExistenceProvider, GoodCutData.ofProvider,
  exists_goodCutData_of_chargeProvider.

## 7. Honest remainder
Bookkeeping only (geodesic enumeration, field equations, casts, badCount = edgeCount − cutVal) — EXCEPT the one
genuine missing mathematical construction: **ChargeCertProvider existence** = the LengthSurplusChargeCertV2 /
full-bank Hall / BankedCutDomination package. Design so that once a checked ChargeCertProvider is emitted,
everything downstream is automatic and axiom-clean.
