/-
Aggregation graft (conjunct-4 gap #1, honest satisfiable route).

The active `CertGraph.gammaBetaProvider_of_rowDB` discharges `GammaBetaFacts.gammaUpper_of_all_rows_gersh`
through `RowDBGammaFacts.totalRowSum_le_N2_of_gersh`, i.e. `Γ ≤ Σ rowSum ≤ N²`. The right conjunct
`Σ rowSum ≤ N²` is UNSATISFIABLE at the extremal (`Σ rowSum` can reach `m(N+η) = N³/25 ≫ N²`), so no real
graph inhabits that field — a latent fake-progress route (grep-confirmed 2026-07-07; GammaAggregation.lean
header declares the two-field route the design bug).

This module provides the SATISFIABLE replacement: it routes `Γ ≤ N²` through the corrected typed
token-charging cert `GammaAggregation.gammaUpper_from_chargeCertV2` (green). The good-cut provider supplies a
per-instance `ResidualFormulas F` + `LengthSurplusChargeCertV2 cert` with `checkLengthSurplusChargeCertV2 = true`
(a real cert CAN inhabit this, unlike `Σ rowSum ≤ N²`). Constructing/proving that cert exists for every good cut,
with the bank-reserve residual nonneg, remains the aggregation-completeness obligation — but this replaces the
dead route with a live one. Additive: does NOT edit CertGraph.
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.GammaAggregation

namespace Erdos23Delta0
namespace GammaChargeGraft

open CertGraph
open GammaAggregation

/-- Satisfiable `GammaBetaFacts` provider via the corrected typed charge certificate. `gammaVal := Γ = Σ ℓ²`,
    and the `Γ ≤ N²` obligation is discharged by `gammaUpper_from_chargeCertV2` (the non-degenerate, compiled
    token-charging route) rather than the unsatisfiable `totalRowSum ≤ N²` field. `hgammaLower : 25·badCount ≤ Γ`
    is supplied by the caller (rows are length ≥ 5 ⟹ Σ ℓ² ≥ 25·#rows = 25·badCount). -/
def gammaBetaProvider_of_chargeCert {G : GraphData} {c : CutData} {rows : RowDB}
    (F : ResidualFormulas G c rows) (cert : LengthSurplusChargeCertV2)
    (hlen : rows.rowList.length = badCount G c)
    (hcheck : checkLengthSurplusChargeCertV2 F cert = true)
    (hgammaLower : 25 * (badCount G c : ℚ) ≤ gammaOfGD G c rows) :
    GammaBetaFacts G c rows where
  gammaVal := gammaOfGD G c rows
  betaVal := (badCount G c : ℚ)
  gammaLower := hgammaLower
  gammaUpper_of_all_rows_gersh := fun hGersh =>
    gammaUpper_from_chargeCertV2 F hlen cert hcheck hGersh
  beta_eq_badCount := rfl

end GammaChargeGraft
end Erdos23Delta0
