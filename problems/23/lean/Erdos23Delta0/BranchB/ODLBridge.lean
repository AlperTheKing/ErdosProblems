/-
Branch-B -> ODL bridge (conjunct 2, self-review fix #4 made concrete against the REAL green API).

MAIN's design contract assumed a `PolyCert.Ctx`/`eval ctx` surface that does NOT exist in the
green modules; the real surface is env-based (`NF.eval env`, `checkEq f g`, `ConeCert.sound` with
`henv`). More importantly, the bridge MAIN designed is already discharged by the existing green
ODL machinery: `ODLFull.CoreODLGoal_of_defect_nonneg` reduces the support-local ODL goal to
`0 <= coreDefect core`, where `coreDefect core = supportSize + etaQ - supportRowSum`.

So the whole Branch-B bridge is a PURE slack-decomposition (exact rational linarith):

  Banked-UPO per-row bound (produced by the Branch-B provider layers, as `hBankedUPO`):
     N + supportRowSum - supportSize  <=  N + eta/2 - SigmaL
  Two nonneg inputs (from GammaAggregation): 0 <= eta,  0 <= SigmaL.
  Identity:  coreDefect = (N + eta/2 - SigmaL - R_Q) + (eta/2 + SigmaL),   R_Q := N + supportRowSum - supportSize
  =>  coreDefect = supportSize + eta - supportRowSum >= SigmaL + eta/2 >= 0
  =>  CoreODLGoal.

This is the glue between the (still-to-be-built) BankedUPO/BranchBProvider layers and the green
ODL core. `hBankedUPO` is exactly the per-row bound those layers must certify per Branch-B row.
-/
import Erdos23Delta0.ODLFull

namespace Erdos23Delta0
namespace BranchB

open CertGraph
open ODLFull

/-- Branch-B -> ODL support-local goal, by slack decomposition. Given the Banked-UPO per-row
    bound `N + supportRowSum - supportSize <= N + eta/2 - SigmaL` (discharged by the Branch-B
    provider layers) together with `0 <= eta` and `0 <= SigmaL`, the core defect is nonnegative,
    so the support-local ODL goal `supportRowSum <= supportSize + eta` holds. Pure `linarith`
    over the exact rationals; reuses only the green `CoreODLGoal_of_defect_nonneg`. -/
theorem branchB_to_coreODLGoal {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (core : ODLCoreData G c rows Q) (SigmaL : ℚ)
    (hEta : 0 ≤ etaQ G c) (hSigmaL : 0 ≤ SigmaL)
    (hBankedUPO : (G.n : ℚ) + core.supportRowSum - core.supportSize
                    ≤ (G.n : ℚ) + etaQ G c / 2 - SigmaL) :
    CoreODLGoal G c rows Q core := by
  apply CoreODLGoal_of_defect_nonneg core
  unfold coreDefect
  linarith

end BranchB
end Erdos23Delta0
