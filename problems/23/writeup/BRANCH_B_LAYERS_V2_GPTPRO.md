# Branch-B layers 21-26 — GPT-Pro concretization v2 (2026-07-09, post-108 + post-24vtx-falsifier)

*Reply to the conjunct-2 retask; supersedes the layer sketches of BRANCH_B_LEAN_LAYERS_GPTPRO.md where they
conflict. ASCII-sanitized structure; Claude annotations [C: ...].*

## Build order
21 `BranchB.Dict24` → 22 `BranchB.CombinedHBD` → 23 `BranchB.CDTelescope` → 24 `BranchB.PureUPOK0` →
25 `BranchB.BankedUPO` → 26 `BranchB.Provider` → 27 `BranchB.ODLBridge` (already green; remains the ONLY bridge
into `ODLFull.CoreODLGoal` via `branchB_to_coreODLGoal`; new layers only produce the row-level inequality).

## Layer 21 — Dict24 (BOOKKEEPING; deps: Mathlib only)
Typed 24-signature dictionary: `Dict24AtomData` (sig/demand/pure/hbd/cd), `Dict24Checked` (sig<24, all parts ≥ 0,
demand = pure+hbd+cd), theorems `dict24_sum_split`, `dict24_part_sums_nonneg`, `dict24_sig_lt`,
`dict24_demand_sum_nonneg`. Complete Lean text provided (§C). [C: COMPILED as BranchB/Dict24.lean same tick.]

## Layer 22 — CombinedHBD (BOOKKEEPING; deps: Mathlib; token-origin nonneg discharged later by BankL/Bank0Algebra/Bank0 chain)
Single-spend ledger: `HBDChargeData` (demand/cap/q/unused), `HBDLedgerChecked` (all nonneg; demand exactly
charged: demand a = Σ_t q a t; capacity split: cap t = Σ_a q a t + unused t), theorem `hbd_ledger_sound`:
Σ demand ≤ Σ cap. Universal existence of useful ledgers belongs to the row certificate GENERATOR, not here.

## Layer 23 — CDTelescope (BOOKKEEPING; per-step equalities from CDCore/PacketExchange/BankL)
Prefer explicit-endpoint form over list-reverse: `CDTelescopeData` (start/finish/gain), `CDTelescopeChecked`
(0 ≤ gain, start = finish + gain), `cd_telescope_sound`: finish ≤ start.

## Layer 24 — PureUPOK0 (SOUNDNESS = BOOKKEEPING; EXISTENCE = RESEARCH) — **the first real math layer, BANKED**
**Post-24-vtx verdict: Pure-UPO k=0 MUST be banked; a bare/unbanked statement is not safe** — the L>5 regime's
UPO decomposition still creates ell=5 support atoms and escaping/full-closure structures; long-row surplus does
not remove the need for Door/VertexSlack/C5/Prune terms. Shape:
- `PureUPOK0Frame` + `pureUPOK0_of_fullBankCert`: frame + `FullBankRelaxedCoverCert` + checker=true ⟹
  `PureUPOK0Bound` (PureDemand_K0 ≤ PureDoorCap + PureVertexSlackCap + PureC5Cap + PurePruneCap; never η_C).
  A THIN WRAPPER over the compiled banked-Hall soundness (Ell5FullBankInterface / RelaxedCoverGraphBridge
  .graph_hall_absorbed / BankedCutDominationCore + CageSuperadditivity + BankL/Bank0Algebra).
  "PureUPOK0_Banked should not prove a new Hall theorem": (1) construct the atom/bank-token sets for the k=0
  residual, (2) call compiled full-bank soundness, (3) translate.
- **RESEARCH = `pureUPOK0_fullBankCert_exists`**: under IsMaxCut + GammaMinimalConnected + BConnected +
  RowDBFactsGeneral + IsBranchBRow, a frame + checked cert EXISTS. [C: = the Branch-B instance of the same wall
  (Ell5FullBankRelaxedCover_exists); conjunct-2's research core UNIFIES with gap#1's.]

## Layer 25 — BankedUPO (BOOKKEEPING once PureUPOK0 cert available)
`BankedUPOCert` = {dict : Dict24Cert, hbd : CombinedHBDCert, cd : CDTelescopeCert, pure : PureUPOK0Cert} +
checker + `checkBankedUPOCert_sound`: under the five standard hypotheses + check=true ⟹ `BranchBRowBound G c
rows r` = r.rowSumQ + BranchBSigmaL ≤ nRat + etaRat/2 (match the EXACT Prop the compiled bridge expects — do not
redefine if it exists).

## Layer 26 — Provider (BOOKKEEPING)
`BranchBProvider` (checker-friendly: List (Nat × cert) keyed by row index; obligations: valid indices, per-row
check, every Branch-B row exactly once, no EQODL1 row required) + `checkBranchBProvider_sound`: ∀ Branch-B row,
BranchBRowBound. Layer 27's `branchB_to_coreODLGoal` then yields CoreODLGoal per row. Non-Branch-B rows are the
EQODL1 cover module's job (O14 stack).

## §B verbatim core (the research statement)
`PureUPOK0_Banked` (full hypothesis list as in layer 24) with `PureUPOK0Bound` = "the pure UPO k=0 residual of
row r is absorbed by legal Door + VertexSlack + C5/Base + Prune banks, no top η_C." Existence of the certificate
remains THE research obligation — same wall, Branch-B face.

## §C Layer-21 full text
Provided verbatim (Prop-level, Bool checker wrappable later); [C: adapted + compiled as
problems/23/lean/Erdos23Delta0/BranchB/Dict24.lean — see build log].
