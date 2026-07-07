# BRANCH-B CERTIFIED LEAN LAYERS (GPT-Pro MAIN fresh thread, 2026-07-07) — conjunct 2

STATUS: MAIN delivered the full 32717-char Branch-B Lean layer design (fresh MAIN thread
https://chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61, last assistant message; window.__bb).
This is the CONJUNCT-2 formalization plan (rows with L>5). Full extract + build happens AFTER the 108
Branch-A chart certs (the current fan-out). Thread persists it.

## Dependency chain (build order)
  Dict24 -> CombinedHBD -> CDTelescope -> BankedUPO -> BranchBProvider -> ODLFullProvider.branchB leaf
Per-row certified target: R_Q <= N + eta/2 - SigmaL_Q  (the Banked-UPO per-row bound), consumed by the
already-designed ODLFullProvider through a checker-produced theorem.

## Shared substrate (verbatim head, decoded)
```lean
namespace Erdos23.BranchB
abbrev Q := Rat
abbrev NF := PolyCert.NF
abbrev ConeCert := PolyCert.ConeCert
structure Ctx where
  cg     : CertGraph.Ctx
  poly   : PolyCert.Ctx
  gamma  : GammaAggregation.Ctx
  nRows  : Nat
  N      : Nat
  eta    : Q
-- Branch-B uses the existing exact rational/NF/ConeCert infra (PolyCert); NO floats or proof-fields
-- inside emitted certificate data. rowLen/... are compiled defs, not emitted fields.
```
Layers (each = structure + Bool checker + soundness theorem, checker-produced, per-instance emitted data,
exact rational, no native_decide): (1) Dict24 = the 24-signature dictionary; (2) CombinedHBD = single-spend
HBD ledger; (3) CDTelescope = CD telescope; (4) BankedUPO = per-row R_Q<=N+eta/2-SigmaL_Q; (5) BranchBProvider
composes them; feeds ODLFullProvider.branchB. [FULL 32.7k design in-thread — extract sections 1-5 at build time.]

NEXT: at Branch-B build (post-108), extract the full design + build the 5 layers bottom-up (Dict24 first).

## SELF-REVIEW VERDICT (MAIN, 2026-07-07, 43940-char cleaned build contract in-thread)
Architecture USABLE; no hidden contradiction. Build-time fixes (the first draft had convenience names not in
the green module list):
1. Use Rat (NOT Q) in ALL public certificate structures.
2. Emitted data: Nat + `sig < 24` checker, NOT Fin 24.
3. REMOVE invented PolyCert names (checkNF, denote, NF.add, ...) unless they already exist in green PolyCert.
4. ADD an explicit Branch-B -> ODL BRIDGE THEOREM: without it, the chain R_Q <= N+eta/2-SigmaL_Q -> ODLFull
   .CoreODLGoal is a HAND-WAVE. (retasked MAIN to produce this concretely.)
5. STRENGTHEN CombinedHBD + CDTelescope single-spend checks so row balances can't be reused/double-counted
   across Banked-UPO rows.
6. FIX CD telescope: contiguity alone does NOT prove telescoping unless weights are constant OR coefficient
   cancellation is explicitly checked.
Full cleaned build contract (all 5 layers, corrected) is in the MAIN thread — extract at Branch-B build time.

## BRANCH-B -> ODL BRIDGE THEOREM (MAIN, 2026-07-07, 11920c in-thread) — closes fix #4, conjunct-2 design COMPLETE
The bridge is a PURE SLACK-DECOMPOSITION (exact algebra, zero hand-wave). Goes in Erdos23/BranchB/ODLBridge.lean.
  CoreODLSlack_Q := supportSize_Q + eta - supportRowSum_Q     (this is the ODLFull.CoreODLGoal defect, need >=0)
  R_Q            := N + supportRowSum_Q - supportSize_Q        (BranchB per-row quantity)
  BranchB bound  : R_Q <= N + eta/2 - SigmaL_Q                 (certified by BranchBProvider)
  IDENTITY: CoreODLSlack_Q = (N + eta/2 - SigmaL_Q - R_Q) + (eta/2 + SigmaL_Q)
  Two nonneg inputs:
    (1) BranchBSlack_Q := N + eta/2 - SigmaL_Q - R_Q >= 0   (from BranchBProvider soundness = the Banked-UPO bound)
    (2) Payback_Q      := eta/2 + SigmaL_Q >= 0             (from GammaAggregation: eta>=0 AND SigmaL_Q>=0)
  => CoreODLSlack_Q >= 0 => ODLFull.CoreODLGoal.  theorem branchB_to_coreODLGoal.
  Objects: branchBPaybackNF ctx q := nfAdd (nfConst (eta/2)) (sigmaL_NF ctx q); ODL-slack NF; the two nonneg
  lemmas; the exact NF identity via checkEq. Uses ONLY existing green decls (PolyCert NF/checkEq, GammaAggregation
  eta>=0/SigmaL>=0). => ODLFullProvider.branchB is now checker-PRODUCED, not assumed. CONJUNCT-2 DESIGN COMPLETE
  (5 layers Dict24/CombinedHBD/CDTelescope/BankedUPO/BranchBProvider + self-review 6 fixes + this bridge).
  Full 11920c derivation in MAIN thread; build at Branch-B time.

## SURFACE RECONCILIATION vs REAL GREEN API (Claude, 2026-07-07) — corrects self-review fix #3 concretely
Extracted MAIN's full 43940c build contract (section 0 "Allowed external surface"). GPT's contract
INVENTED a Ctx-based PolyCert API (`PolyCert.Ctx`, `eval ctx : Ctx -> NF -> Rat`,
`checkEq ctx a b`, `checkConeCert_sound`) with `sorry` placeholders. The REAL green surface is
ENV-based (verified in PolyCert.lean, sorry/admit/native_decide count = 0):
  - `NF.eval (env : Var -> Q) (f : NF) : Q`
  - `checkEq (f g : NF) : Bool` ; `checkEq_sound (f g) (h : checkEq f g = true) (env) : f.eval env = g.eval env`  [L284, PROVEN]
  - `structure ConeCert { target base : NF, mults slacks : List NF, hid : checkEq target (comboNF base mults slacks) = true, hbase, hmults }` [L367]
  - `ConeCert.sound (c) (env) (hvars : forall v, 0<=env v) (hslacks : forall s in c.slacks, 0<=NF.eval env s) : 0 <= NF.eval env c.target` [L379, PROVEN]
ANY Branch-B build MUST use this env-based API, NOT GPT's Ctx API (would fail to compile).

## THE BRIDGE IS ALREADY GREEN MACHINERY (major simplification)
ODLFull.lean already provides the bridge pattern (all PROVEN, linarith):
  - `structure ODLCoreData { support : List Nat, supportSize supportRowSum : Q, supportSize_le_N : supportSize <= G.n }` [L28]
  - `CoreODLGoal G c rows Q core := core.supportRowSum <= core.supportSize + etaQ G c` [L36]
  - `coreDefect core := core.supportSize + etaQ G c - core.supportRowSum` [L122]
  - `CoreODLGoal_of_defect_nonneg (core) (h : 0 <= coreDefect core) : CoreODLGoal ...` [L127, PROVEN]
  - `coreODLGoal_of_coneCert (core) (cert : ConeCert) (env) (hvars) (hslacks) (htarget : NF.eval env cert.target = coreDefect core) : CoreODLGoal ...` [L139, PROVEN]
So Branch-B rows enter ODL via EITHER a defect-nonneg proof (linarith from the Banked-UPO bound)
OR a ConeCert whose target NF = coreDefect. No new "bridge layer" needed beyond the slack lemma.

## ODLBridge.lean WRITTEN (Erdos23Delta0/BranchB/ODLBridge.lean) — SOURCE correct, BUILD QUEUED
theorem branchB_to_coreODLGoal {G c rows Q} (core : ODLCoreData G c rows Q) (SigmaL : Q)
  (hEta : 0 <= etaQ G c) (hSigmaL : 0 <= SigmaL)
  (hBankedUPO : (G.n:Q) + core.supportRowSum - core.supportSize <= (G.n:Q) + etaQ G c/2 - SigmaL)
  : CoreODLGoal G c rows Q core := by apply CoreODLGoal_of_defect_nonneg core; unfold coreDefect; linarith
Math verified: hBankedUPO => supportSize-supportRowSum >= SigmaL-eta/2 => coreDefect = (supportSize-supportRowSum)+eta >= SigmaL+eta/2 >= 0. linarith closes.
STATUS: source written, NOT yet honest-green-built (no cached ODLFull.olean; full CertGraph->PolyCert->ODLFull
chain rebuild is multi-minute + CPU-heavy, deferred off the saturated machine). `hBankedUPO` is EXACTLY the
per-row obligation the (still-unbuilt) BankedUPO/BranchBProvider layers must certify per Branch-B row.
NEXT (build tick, CPU free): compile CertGraph+PolyCert+ODLFull+ODLBridge in dep order into a tmp olean
tree; EXIT=0 + empty log + sorry/axiom grep before recording green.

