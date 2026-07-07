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
