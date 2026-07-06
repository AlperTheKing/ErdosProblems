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
import Erdos23Delta0.PolyCert

namespace Erdos23Delta0
namespace ODLFull

open CertGraph
open PolyCert

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

/-- The support excess: how far the support row mass exceeds the support size. The
    support-local ODL goal is exactly `coreExcess ≤ η`. -/
def coreExcess {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (core : ODLCoreData G c rows Q) : ℚ :=
  core.supportRowSum - core.supportSize

/-- Internal-link relation: the parent's excess is at most the child's. This is the
    reusable numeric link a prune/absorb internal node certifies. -/
def CoreExcessLE {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (parent child : ODLCoreData G c rows Q) : Prop :=
  coreExcess parent ≤ coreExcess child

/-- Internal-node monotonicity (the heart of the semantic tree assembly): since η is
    ambient and fixed, a parent whose excess is ≤ a child's inherits the child's
    support-local ODL bound. Composed up the route tree, this propagates the terminal
    leaves' certified ODL bounds to the root. -/
theorem CoreODLGoal_of_excess_le {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {parent child : ODLCoreData G c rows Q}
    (hlink : CoreExcessLE parent child)
    (hchild : CoreODLGoal G c rows Q child) :
    CoreODLGoal G c rows Q parent := by
  unfold CoreODLGoal at hchild ⊢
  unfold CoreExcessLE coreExcess at hlink
  linarith

/-- Semantic ODL data over a route tree: each node id carries a support-local core. -/
structure ODLNodeSemantics (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTree.Seed3RouteTreeData) : Type where
  coreOf : Seed3RouteTree.NodeId → ODLCoreData G c rows Q

/-- A route-tree node is ODL-resolved iff its core meets the support-local ODL goal. -/
def resolvedODL (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTree.Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T)
    (n : Seed3RouteTree.Seed3Node) : Prop :=
  CoreODLGoal G c rows Q (sem.coreOf n.id)

/-- One-child prune/absorb helper: if the internal parent's core excess is ≤ its child's
    and the child resolves, the parent resolves. (Composed over the tree by the recursive
    checker.) -/
theorem resolvedODL_of_one_child_excess_link {G : GraphData} {c : CutData} {rows : RowDB}
    {Q : RowCert} {T : Seed3RouteTree.Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {parent child : Seed3RouteTree.Seed3Node}
    (hlink : CoreExcessLE (sem.coreOf parent.id) (sem.coreOf child.id))
    (hchild : resolvedODL G c rows Q T sem child) :
    resolvedODL G c rows Q T sem parent :=
  CoreODLGoal_of_excess_le hlink hchild

/-- Composition: if the ROOT node is ODL-resolved and its core represents the row, the
    row-level odlFull goal `rowSum ≤ N + η` holds. This is where the semantic tree assembly
    (root resolvedODL) meets the root-representation certificate to fill BranchAInputs.odlFull. -/
theorem ODLFull_of_resolved_root {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTree.Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3RouteTree.Seed3Node}
    (hresolved : resolvedODL G c rows Q T sem root)
    (hrep : RootRepresentsRow G c rows Q (sem.coreOf root.id)) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c :=
  ODLFull_of_rootCore hrep hresolved

/-- The core defect: `supportSize + η − supportRowSum`. A leaf checker certifies its target
    equals this defect for the node's emitted core; nonnegativity of the defect is exactly
    the support-local ODL goal. (Per MAIN: `coreOf` is emitted per node in `ODLNodeSemantics`;
    a leaf checker does NOT reconstruct the core from the graph.) -/
def coreDefect {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (core : ODLCoreData G c rows Q) : ℚ :=
  core.supportSize + etaQ G c - core.supportRowSum

/-- Defect nonnegativity is the support-local ODL goal. -/
theorem CoreODLGoal_of_defect_nonneg {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (core : ODLCoreData G c rows Q) (h : 0 ≤ coreDefect core) :
    CoreODLGoal G c rows Q core := by
  unfold CoreODLGoal coreDefect at *
  linarith

/-- ConeCert-backed leaf soundness (the CONE / scalar-bank leaf pattern): a `ConeCert` whose
    target evaluates (under a nonnegative environment with nonnegative slacks) to the node's
    core defect certifies `CoreODLGoal` for that core. This is the odlFull leaf analog of the
    a1Proper cone-bridge (`canonicalCone_bound`), reusing `PolyCert.ConeCert.sound` directly.
    The concrete leaf checkers (checkConeLeaf / checkBankBlockLeaf / …) supply `cert`, `env`,
    and the target identity. -/
theorem coreODLGoal_of_coneCert {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (core : ODLCoreData G c rows Q) (cert : ConeCert) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hslacks : ∀ s ∈ cert.slacks, 0 ≤ NF.eval env s)
    (htarget : NF.eval env cert.target = coreDefect core) :
    CoreODLGoal G c rows Q core := by
  have h0 : 0 ≤ NF.eval env cert.target := ConeCert.sound cert env hvars hslacks
  rw [htarget] at h0
  exact CoreODLGoal_of_defect_nonneg core h0

end ODLFull
end Erdos23Delta0
