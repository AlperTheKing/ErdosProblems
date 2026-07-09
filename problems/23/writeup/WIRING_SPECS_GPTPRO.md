# The two critical wiring specs — GPT-Pro (2026-07-09, NEW thread, relayed verbatim by user)

*Fills the architecture audit's MISSING-SPEC 1 & 2 (+4 folded in). Everything in `Rat`, all caps in
length-surplus units (ell²−25). TYPE-LEVEL GUARANTEE: no local/cage η token exists anywhere — spendable kinds
are exactly door / vertexSlack / c5Base / prune.*

## ⚠ HEADLINE — THE WALL'S REQUIRED STATEMENT IS REFINED
A bare `Ell5FullBankRelaxedCover_exists : ∀ obstruction, ∃ cover, check = true` is **NOT sufficient** to feed
`gammaUpper_from_chargeCertV2`. The required strengthening:

```
theorem Ell5FullBankRelaxedCover_globalPackage_exists
    (G cut rows) (hRows : RowsAreAllShortestBlueGeodesics) (hMax) (hGammaMin) (hBConnected)
    (hWall : ∀ obs : MinimalFullClosureObstruction, ∃ b, checkFullBankRelaxedCoverBundle obs b = true) :
    ∃ pkg : FullBankGlobalPackage G cut rows, checkFullBankGlobalPackage G cut rows pkg = true
```
If the bundle already carries globally labelled sink/source IDs + reserve identities ⟹ repackaging theorem;
if it only carries local BankedCutDomination ⟹ **genuine strengthening of the wall interface**. Extra data:
(1) flattened global index of local cage/prefix cover uses; (2) global token ledger, kinds EXCLUDE η;
(3) per-local spend matrices; (4) component reserve identities vs N_c²−25m_c; (5) global superadditivity
reserve identity vs N²−ΣN_c²; (6) row-to-local ownership.

## SPEC 1 — Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge (structure summary; full Lean in the relay)
- `FullBankRelaxedCoverBundleView` (bundle + demandQ/doorCapQ/vertexSlackCapQ/c5BaseCapQ/pruneCapQ; NO etaQ
  field exists) + `check` (bundle checks; five quantities nonneg; demandQ ≤ rhsQ = door+vs+c5+prune) +
  `check_sound` [BOOKKEEPING].
- Ledger types: `CapKind` (door|vertexSlack|c5Base|prune — deliberately NO η constructor), `LedgerToken`
  (comp, kind, sourceId, capQ; (comp,kind,sourceId) injective), `GlobalLedgerData` (token array, spendQ :
  local×token→Q, componentReserveSlackQ, superadditivitySlackQ — the two slack families are NON-SPENDABLE),
  `FullBankLocalCover` (comp + audit keys + view), `FullBankGlobalPackage` (componentCount/localCount/
  tokenCount, compN, compOfRow, localOfRow, local, ledger; every row exactly one component + one local owner;
  spends legal only within component).
- Derived: rowEll := verts.length; rowGammaQ = ell²; rowSurplusQ = ell²−25; gammaRowsQ; lengthSurplusQ;
  per-local caps/demands; spendOfToken/Local(Kind); tokenCapInComponent; componentResidualCapQ = N_c²−25·rows_c;
  componentGammaQ = 25·rows_c + surplus_c; token/localDemand/localCap slacks; reserveIdentityLhs/Rhs (= N²−Γ).
- `Checked` (the exact Prop; all finite/decidable): rows.length = badCount; ∀i 5 ≤ ell; row-ownership respects
  components; every local view checks; surplusInLocal ≤ localDemand ≤ localCap; the four cap quantities EQUAL
  the four kind-spends; nonneg tokens/spends; **no double-spend** (spendOfToken ≤ tokenCap); **no cross-component
  spends**; **token source uniqueness**; **component reserve identity** (tokenCapInComp + reserveSlack_c =
  N_c²−25m_c, slack ≥ 0); **global superadditivity identity** (Σ N_c² + superSlack = N², slack ≥ 0).
- `fullBankGlobalPackage_sound : checked → lengthSurplusQ rows ≤ N² − 25·badCount` — 12-step BOOKKEEPING plan
  (local: surplus ≤ demand ≤ cap = Σkind-spends = spendOfLocal; per-component sum + swap + no-double-spend ⟹
  surplus_c ≤ tokenCapInComp_c; + reserve identity ⟹ componentGamma_c ≤ N_c²; sum + superadditivity ⟹
  Γ ≤ N²; convert; equivalently lengthSurplus ≤ 25η). Corollary gammaRows_le_N_sq (sanity only).
- Provider: `LengthSurplusChargeCertV2.ofFullBankLedger` (pure data translation from the listed arrays) +
  `residualFormulasOfRows` (canonical) + `chargeCertProvider_of_fullBankPackage` +
  `..._ok : checkLengthSurplusChargeCertV2 out.1 out.2 = true` (checker obligations a-i map 1:1 to Checked
  fields; only nontrivial step = Σ_i rowSurplus = Σ_j surplusInLocal, isolate as
  sum_surplus_eq_sum_surplusInLocalQ) + `gammaUpper_from_fullBankPackage_via_chargeCertV2` (THE route; full
  expected hypothesis list given incl GraphData.Valid/CutData.Valid/RowDB.Sound/rows.length=badCount; the
  algebraic provider needs NO IsMaxCut/GammaMin/BConnected — those live upstream).
- CLASSIFICATION — bookkeeping: checker soundness, sum rearrangements, Γ = 25·len + surplus, η conversion,
  provider_ok, routing. **Harder/WALL-side: existence of FullBankGlobalPackage; globally unique token source
  IDs; local quantities = the banked Hall quantities; no token duplication across cages/prefixes; component
  reserve identities from the real decomposition.**

## SPEC 2 — Row partition (Erdos23Delta0.Rows.RowPartition)
**KEY CORRECTION: EQODL1 is a COMPONENT-level equal-length condition, not row-level ell=5. A row with ell=5 in
a mixed component is BranchB.**
- `K2ComponentData` (componentCount + compOfRow table; data because the provider needs a decidable dispatch) +
  `Sound` (compOfRow i = compOfRow j ⟺ RowsK2Connected i j — must be THE SAME component notion used by both
  branches, else the partition is unsound) + checker.
- `ComponentAllL5 c := ∀ i, compOfRow i = c → rowEll i = 5`; `ComponentBranchB := ¬AllL5`;
  `IsEQODL1Row i := ComponentAllL5 (compOfRow i)`; `IsBranchBRow i := ComponentBranchB (compOfRow i)`;
  `IsOtherGreenLeafRow` = diagnostic only (provably uninhabited).
- Theorems (proofs given, essentially complete): `nonEQ_L5_row_is_BranchB` (the anti-bug theorem);
  `BranchB_component_contains_long_row` (guardrail; needs ∀i 5 ≤ ell + finite not-forall);
  `rowCoverage : ∀ i, ExactlyOne (IsEQODL1Row i) (IsBranchBRow i)` (pure case split);
  `noOtherGreenLeafRows`.
- Provider-facing: `RowClass` (eqodl1|branchB), `ODLFullRowPartitionView` (k2 + classOf + per-component
  Option certs) + checker (k2 sound; classOf matches ComponentAllL5 semantically; eqodl1 components have
  checked EQODL1ComponentCert; branchB components have checked BranchBComponentCert) +
  `ODLFullRowPartitionView_sound` + `rowBound_of_partitioned_provider` (dispatch: EQ rows via chartOf/registry;
  BranchB rows via BranchBRowBound — **the BranchB theorem must be COMPONENT-SCOPED: it applies to every row in
  a BranchB component INCLUDING its ell=5 rows**).
- Placement: definitions + exhaustiveness EXTERNAL (Rows.RowPartition); computable dispatch table INSIDE the
  ODLFull provider checker (prevents import cycles).
- THE GUARDRAIL (verbatim): `IsEQODL1Row_wrong (i) := rowEll i = 5` is WRONG; correct is
  `ComponentAllL5 (compOfRow i)` — "That single distinction is what makes non-EQ length-5 rows go to BranchB
  rather than leaking out of the partition."
- CLASSIFICATION — bookkeeping: all partition defs/theorems + provider dispatch. Harder/branch-owned: 108-chart
  registry soundness; BranchB 21-26 soundness (compiled); K2 decomposition checker vs the graph relation.

## [CLAUDE actions on receipt]
1. Partition core COMPILED immediately (RowPartitionCore.lean — defs + the four theorems, K2 relation
   abstracted as a parameter until the graph-level RowsK2Connected is fixed).
2. WALL PACKAGE UPDATED: the refined statement (globalPackage_exists + the 6 data classes) propagated to the
   escalation brief — GPT-5.6 must prove the wall WITH global accounting, or the bundle must carry it.
3. SPEC-1 module = Codex lane (data plumbing + checker + the 12-step bookkeeping proofs).
