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

## RED-TEAM SELF-REVIEW (MAIN, 2026-07-07, 20388 chars in-thread) — BOTTOM LINE
Contract is SOUND as a per-instance certified assembly plan; no hidden algebraic contradiction in the
row-to-beta chain. But several names were PLACEHOLDERS, not green decls. Build-time hazards (fix ALL before
paste-building; full type/name audit + dependency-sorted BUILD ORDER in-thread, extract at 108):
1. QQ vs ℚ/Rat — use ONE rational type consistently (my modules use ℚ).
2. ODLFullProvider.sound MUST be produced from checkODLFullRowCert / the green semantic-tree checker — NOT an
   arbitrary structure field (else the provider is an unproven assumption).
3. O14 coverage MUST be ALL-OR-NOTHING: 45/108 or ANY partial chart list gives NO EQ leaf theorem. (confirms
   the all-or-nothing gate — the 108 must be COMPLETE for odl_full to hold.)
4. Seed3RouteTree STRUCTURAL coverage is NOT enough for ODL: every leaf must be SEMANTICALLY resolved
   (NCHMultiTermCert / EQ-leaf / M6), not just structurally present.
5. Gamma aggregation MUST use the V2 length-surplus charge cert (checkLengthSurplusChargeCertV2), NOT the old
   totalRowSum.
6. SimpleGraphCertificatePackage proves a CONDITIONAL certified theorem UNLESS package existence is built for
   the target graph/class — this is the certified-per-instance caveat (theorem conditional on package supply).
7. Assembly must be typed with these EXACT provider boundaries.
DEEPEST hazards = #2 + #4 (ODLFullProvider must be checker-produced with every leaf semantically resolved) —
retasked MAIN to design the concrete ODLFullProvider construction next.

## ODLFullProvider DESIGN — LANDED (MAIN, 2026-07-07, 15335 chars)
MAIN delivered the concrete ODLFullProvider construction (checker-produced soundness, per-leaf semantic
witnesses EQ/NCH/M6/NO_OVERFULL/NEG_SWITCH, ODLFull->odl_full all-or-nothing indexing, build order). Full
text is IN THE OLD MAIN THREAD (https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550, last assistant
message) — that thread is being RETIRED (bloated, per user 2026-07-07) but persists as an ARCHIVE; extract the
ODLFullProvider + full assembly self-review type/name audit + build order from it AT 108 build time.
OLD THREAD ARCHIVE URLs (all Lean design lives here — assembly contract, self-review, ODLFullProvider):
  MAIN-old = https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550
  SIBLING-old = https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526 (paper sections)
