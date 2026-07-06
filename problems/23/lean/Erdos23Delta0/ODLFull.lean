/-
ODLFull provider — stage 1: the semantic core layer + the root-representation passage.
Per GPT-Pro MAIN (ODLFULL_PROVIDER_DESIGN + per-leaf correction): the Seed3 route tree's
STRUCTURAL coverage (checkSeed3RouteTree_sound_from_closeData, already green) must be
followed by a SEMANTIC layer whose node resolution is a support-local ODL bound
`CoreODLGoal`. The root-representation theorem `ODLFull_of_rootCore` lifts the root core's
support-local bound to the row-level goal `rowSum ≤ N + η` that fills BranchAInputs.odlFull.

This file builds the cone/tree-INDEPENDENT part: ODLCoreData + CoreODLGoal +
RootRepresentsRow + ODLFull_of_rootCore. The per-leaf ODL providers (checkEQLeaf, …) and
the ODLNodeSemantics table are a separate stage (gated on the leaf checkers + O14 cover).
Honest build. NOTE (MAIN correction): PRUNABLE and NOT_SATURATED are NOT terminal ODL
leaves — they are internal prune/absorb links, so the terminal-leaf provider set excludes
them.
-/
import Erdos23Delta0.CertGraph

namespace Erdos23Delta0
namespace ODLFull

open CertGraph

/-- Support-local ODL data attached to a route-tree node: a vertex support with its size
    (≤ N) and the row mass carried on it. -/
structure ODLCoreData (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) : Type where
  support : List Nat
  supportSize : ℚ
  supportRowSum : ℚ
  supportSize_le_N : supportSize ≤ (G.n : ℚ)

/-- The support-local ODL goal: the row mass on the support is at most the support size
    plus the η budget. -/
def CoreODLGoal (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (core : ODLCoreData G c rows Q) : Prop :=
  core.supportRowSum ≤ core.supportSize + etaQ G c

/-- The root core represents the whole row: the full row sum is bounded by the root
    support's row mass. -/
structure RootRepresentsRow (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (rootCore : ODLCoreData G c rows Q) : Prop where
  row_le_support : rowSum G c rows Q ≤ rootCore.supportRowSum

/-- Root-representation passage: from the root core's support-local ODL bound and the
    root-represents-row fact, derive the row-level ODL goal `rowSum ≤ N + η`. This is the
    step that turns the route tree's certified core bound into `BranchAInputs.odlFull`.
    Pure rational linear arithmetic (chain: rowSum ≤ supportRowSum ≤ supportSize + η ≤ N + η). -/
theorem ODLFull_of_rootCore {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {rootCore : ODLCoreData G c rows Q}
    (hRoot : RootRepresentsRow G c rows Q rootCore)
    (hCore : CoreODLGoal G c rows Q rootCore) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c := by
  unfold CoreODLGoal at hCore
  have h1 := hRoot.row_le_support
  have h2 := rootCore.supportSize_le_N
  linarith

end ODLFull
end Erdos23Delta0
