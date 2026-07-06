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
open CertGraph.Seed3RouteTree

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

/-! ### Semantic tree assembly (GPT-Pro MAIN): recursive ODL resolution over the route tree.
Opaque leaf/internal providers (`Seed3ODLLeafProviders`, `Seed3ODLInternalLinks`) plug in the
concrete per-family leaf checkers and the excess-monotonicity links; the recursive checker
propagates `resolvedODL` from terminal leaves to the root, which `ODLFull_of_rootCore` lifts to
`odlFull`. Reuses the green `checkSeed3RouteTree` (structural coverage). -/

/-- Terminal-leaf semantic provider: a Bool leaf checker with a soundness field giving
    `resolvedODL` at each leaf it accepts. -/
structure Seed3ODLLeafProviders
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T) : Type where
  checkLeaf : Seed3Node → Bool
  sound : ∀ n : Seed3Node,
    isLeafKind n.kind = true →
    checkLeaf n = true →
      resolvedODL G c rows Q T sem n

/-- Internal-node link provider: a Bool link checker whose soundness turns children's
    `resolvedODL` into the parent's (via the excess-monotonicity link). -/
structure Seed3ODLInternalLinks
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T) : Type where
  checkLink : Seed3Node → Bool
  sound : ∀ n : Seed3Node,
    isInternalKind n.kind = true →
    checkLink n = true →
    (∀ child : Seed3Node, child ∈ childNodes T n → resolvedODL G c rows Q T sem child) →
      resolvedODL G c rows Q T sem n

/-- Fuel-bounded recursive semantic checker: a leaf resolves via its leaf checker; an internal
    node resolves if its link check passes and all children resolve. -/
def checkODLResolveNode
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T)
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem) :
    Nat → Seed3Node → Bool
  | 0, _ => false
  | fuel + 1, n =>
      if isLeafKind n.kind then
        leafs.checkLeaf n
      else
        links.checkLink n &&
          (childNodes T n).all (fun child => checkODLResolveNode T sem leafs links fuel child)

/-- Soundness of the recursive semantic checker: a checked node is ODL-resolved. -/
theorem checkODLResolveNode_sound
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem) :
    ∀ (fuel : Nat) (n : Seed3Node),
      checkODLResolveNode T sem leafs links fuel n = true →
        resolvedODL G c rows Q T sem n := by
  intro fuel
  induction fuel with
  | zero =>
      intro n h
      simp [checkODLResolveNode] at h
  | succ fuel ih =>
      intro n h
      by_cases hleaf : isLeafKind n.kind = true
      · simp [checkODLResolveNode, hleaf] at h
        exact leafs.sound n hleaf h
      · have hleafFalse : isLeafKind n.kind = false := by
          cases hb : isLeafKind n.kind <;> simp_all
        simp [checkODLResolveNode, hleafFalse] at h
        rcases h with ⟨hlink, hchildren⟩
        have hinternal : isInternalKind n.kind = true := by
          cases hk : n.kind <;> simp [isLeafKind, isInternalKind, hk] at hleafFalse ⊢
        exact links.sound n hinternal hlink
          (by
            intro child hchild
            exact ih child (hchildren child hchild))

/-- Root semantic checker: resolve the root with fuel `|nodes|+1`. -/
def checkODLResolveRoot
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T)
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem) : Bool :=
  match findNode? T T.root with
  | some root => checkODLResolveNode T sem leafs links (T.nodes.length + 1) root
  | none => false

theorem checkODLResolveRoot_sound
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hroot : checkODLResolveRoot T sem leafs links = true) :
    ∃ root : Seed3Node,
      findNode? T T.root = some root ∧
      resolvedODL G c rows Q T sem root := by
  unfold checkODLResolveRoot at hroot
  cases hfind : findNode? T T.root with
  | none => simp [hfind] at hroot
  | some root =>
      simp [hfind] at hroot
      have hres : resolvedODL G c rows Q T sem root :=
        checkODLResolveNode_sound leafs links (T.nodes.length + 1) root hroot
      exact ⟨root, by first | exact hfind | rfl, hres⟩

/-- Full semantic tree checker: structural coverage (`checkSeed3RouteTree`, green) plus root
    ODL resolution. -/
def checkSeed3ODLSemanticTree
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (T : Seed3RouteTreeData) (sem : ODLNodeSemantics G c rows Q T)
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem) : Bool :=
  checkSeed3RouteTree G c T && checkODLResolveRoot T sem leafs links

theorem checkSeed3ODLSemanticTree_sound_exists_root
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hcheck : checkSeed3ODLSemanticTree T sem leafs links = true) :
    ∃ root : Seed3Node,
      findNode? T T.root = some root ∧
      resolvedODL G c rows Q T sem root := by
  unfold checkSeed3ODLSemanticTree at hcheck
  rw [Bool.and_eq_true] at hcheck
  exact checkODLResolveRoot_sound leafs links hcheck.2

theorem checkSeed3ODLSemanticTree_sound
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3Node}
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hfind : findNode? T T.root = some root)
    (hcheck : checkSeed3ODLSemanticTree T sem leafs links = true) :
    resolvedODL G c rows Q T sem root := by
  rcases checkSeed3ODLSemanticTree_sound_exists_root leafs links hcheck with ⟨root', hfind', hres⟩
  rw [hfind] at hfind'
  simp only [Option.some.injEq] at hfind'
  subst hfind'
  exact hres

/-- The odlFull provider theorem from the semantic tree: if the semantic tree checks and the
    root core represents the row, then `rowSum ≤ N + η` = `BranchAInputs.odlFull`. This closes
    the odlFull ASSEMBLY modulo the concrete per-family leaf checkers (Seed3ODLLeafProviders)
    and the internal links (Seed3ODLInternalLinks). -/
theorem ODLFull_of_semantic_tree
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} {sem : ODLNodeSemantics G c rows Q T}
    {root : Seed3Node}
    (leafs : Seed3ODLLeafProviders G c rows Q T sem)
    (links : Seed3ODLInternalLinks G c rows Q T sem)
    (hfind : findNode? T T.root = some root)
    (hcheck : checkSeed3ODLSemanticTree T sem leafs links = true)
    (hrep : RootRepresentsRow G c rows Q (sem.coreOf root.id)) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c := by
  have hres := checkSeed3ODLSemanticTree_sound leafs links hfind hcheck
  exact ODLFull_of_rootCore hrep hres

/-! ### Concrete internal-node links from emitted core-excess (GPT-Pro MAIN instantiation).
For PRUNE/ABSORB/SPLIT internal nodes the emitted child core satisfies
`coreExcess(parent) ≤ coreExcess(child)`; the link checker verifies this (decidably) for each
child, and soundness lifts any one resolved child to the parent via `CoreODLGoal_of_excess_le`. -/

/-- Decidable parent→child excess-link check on the emitted cores. -/
def checkCoreExcessLE {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} (sem : ODLNodeSemantics G c rows Q T)
    (parent child : Seed3Node) : Bool :=
  decide (coreExcess (sem.coreOf parent.id) ≤ coreExcess (sem.coreOf child.id))

/-- Internal-node link checker: the node has at least one child and every child satisfies the
    excess link. -/
def checkInternalCoreExcessLinks {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} (sem : ODLNodeSemantics G c rows Q T)
    (n : Seed3Node) : Bool :=
  match childNodes T n with
  | [] => false
  | childs => childs.all (fun child => checkCoreExcessLE sem n child)

/-- The concrete internal-links provider. -/
def internalLinks_of_coreExcess {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    {T : Seed3RouteTreeData} (sem : ODLNodeSemantics G c rows Q T) :
    Seed3ODLInternalLinks G c rows Q T sem where
  checkLink := checkInternalCoreExcessLinks sem
  sound := by
    intro n _hInternal hcheck hchildren
    unfold checkInternalCoreExcessLinks at hcheck
    cases hkids : childNodes T n with
    | nil => simp [hkids] at hcheck
    | cons child rest =>
        simp only [hkids, List.all_cons, Bool.and_eq_true, checkCoreExcessLE] at hcheck
        have hchildResolved : resolvedODL G c rows Q T sem child :=
          hchildren child (by rw [hkids]; simp)
        have hlink := of_decide_eq_true hcheck.1
        exact CoreODLGoal_of_excess_le hlink hchildResolved

end ODLFull
end Erdos23Delta0
