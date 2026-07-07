# AGGREGATION-COMPLETENESS DESIGN (GPT-Pro MAIN, 2026-07-07, 16811c in-thread) — closes audit gap #1

MAIN's design for the #1 gap. INDEPENDENTLY CONFIRMS Claude's GammaChargeGraft approach (additive module,
gammaUpper_from_chargeCertV2 route, drop the unsatisfiable totalRowSum route). Adds the missing cert-existence piece.

## Correct route (verbatim head)
NOT `Σ rowSum <= N^2` from per-row GERSH (structurally false at the extremal scale). Instead:
  all-row GERSH  +  checked reserve residual nonnegativity  +  checked LengthSurplusChargeCertV2 over ResidualFormulas F
  -> GammaAggregation.gammaUpper_from_chargeCertV2  -> Γ <= N².

## Module structure
- NEW module `CertGraphGammaCharge.lean` (does NOT edit CertGraph; final assembly imports it instead of the old
  active theorem). [= Claude's Erdos23Delta0/GammaChargeGraft.lean, already BUILT green+axiom-clean.]
- "1. Do not use the old route gammaBetaProvider_of_rowDB" (CONFIRMS the audit).
- "2. New provider: checked charge route" `namespace CertGraphGammaCharge` [= gammaBetaProvider_of_chargeCert, DONE].

## 2.1 Reserve token-bank certificate (THE NEW / crux piece)
  structure ReserveTokenCert ...
  structure ReserveBankCert { tokens : Array ReserveTokenCert }
  def reserveResidualNFOfRowDB (gd) (rowDB) : NF   -- COMPILED structural token-bank residual for this good cut/rowDB
The reserve residual is NOT stored/supplied per-instance; it is a COMPILED STRUCTURAL FUNCTION of the good cut,
appended to ResidualFormulas as the extra residual source. Its NONNEGATIVITY must be PROVEN (a theorem of code) —
this is the extra nonneg term that row-GERSH slacks alone do NOT provide (slacks give only Γ <= N(N+η)).
"If the actual types are not named GammaData and RowDB, use the exact types already in gammaBetaProvider_of_rowDB."

## STATUS / what remains
- Claude's GammaChargeGraft.gammaBetaProvider_of_chargeCert already provides the provider skeleton (green, axiom-clean).
- REMAINING crux = build `reserveResidualNFOfRowDB` + PROVE its nonnegativity structurally, and show the resulting
  LengthSurplusChargeCertV2 passes checkLengthSurplusChargeCertV2 for every good cut. That nonneg proof is the open
  research core of gap #1 (the "bank-reserve" the memory flagged). Full 16.8k detail in MAIN thread — extract when building.
- CROSS-CHECK: SIBLING was tasked with the same theorem in math prose (may be depleted per user 2026-07-07).
