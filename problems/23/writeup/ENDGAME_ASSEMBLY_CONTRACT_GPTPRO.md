# PER-INSTANCE LEAN ENDGAME ASSEMBLY CONTRACT (GPT-Pro MAIN, 2026-07-07)

STATUS: MAIN delivered the full 17594-char contract in the MAIN thread
(https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550, last assistant message; cached window.__ac).
It is the final Lean assembly layer for the certified-per-instance route: every hard object is a checked
artifact with a compiled soundness theorem; no existence theorem assumed except the per-instance cert package.
FULL EXTRACTION + PASTE-BUILD happens at 108/108 (currently 55/108). Thread persists it; re-extract then.

Section headings seen (extract in full at build time):
1. ODL node semantics and core binding (captured below, verbatim decoded)
2. (O14 chart-cover -> odl_full via EQODL1CoverCert; region certs direct|skip|empty; s^11 pullback; height scaling)
3. (odl_full + a1Proper + bank0 -> C5RS trichotomy -> etaNonneg -> gamma squeeze -> beta<=N^2/25)
4. (single top assembly theorem -> erdos23_delta0_simpleGraph -> FC bridge)
[sections 2-4 to be extracted at build time from window.__ac / thread]

## Section 1 (verbatim, decoded) — ODL node semantics + core binding
```lean
namespace Erdos23Delta0
namespace Seed3RouteTree

/-- Per-node ODL core data. Values are emitted but checked by `checkODLRowSemanticsPayload`. -/
structure ODLCoreData
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) : Type where
  support : List Nat
  supportSize : QQ
  supportRowSum : QQ
  supportSize_le_N : supportSize <= (G.n : QQ)

/-- The node-level ODL goal. -/
def CoreODLGoal
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (core : ODLCoreData G c rows Q) : Prop :=
  core.supportRowSum <= core.supportSize + etaQ G c

/-- Core defect. A CONE leaf certifies [continues in-thread ...] -/
```
This aligns with the green ODLFull.lean row-local semantic layer + coreODLGoal_of_coneCert. The CoreODLGoal
matches the NCHMultiTermCert.coreCone consumption: ConeCert proves supportSize + etaQ - supportRowSum >= 0.

NEXT: at 108, extract sections 2-4 fully, then build NCHMultiTermCert wrapper + coverage + top assembly.
