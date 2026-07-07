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
MAIN retasked to adversarially self-review this design.
