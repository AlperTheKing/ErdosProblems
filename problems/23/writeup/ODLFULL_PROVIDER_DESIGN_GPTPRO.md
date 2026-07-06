# ODLFull provider design (GPT-Pro MAIN, 2026-07-06)

TRANSCRIBED from the MAIN GPT-Pro thread (6a450f06), symbol-transform-decoded
(@EQ@→=, @PL@→+, @LT@→<, @GT@→>, @AM@→&). Structural/Lean-code faithful; prose
paraphrased where noted. NOT byte-verbatim. Design gated by Claude for the
BranchAInputs.odlFull obligation (Branch-A full-mask side).

## Decision
`odlFull` is a ROW-LOCAL route/certificate whose leaves cite GLOBAL finite
providers — it is NOT a single global theorem (unlike a1Proper = global six-cone).

    a1Proper = global six-cone uniform theorem.
    odlFull  = row-local ODLFullCert soundness theorem citing global leaf providers.

    BranchAInputs.a1Proper := A1ProperCertBundle.sound ...
    BranchAInputs.odlFull  := ODLFullProvider.sound ...

## Goals
```lean
def ODLFullGoal (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) : Prop :=
  rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c

def CoreODLGoal (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) (S : List Nat) : Prop :=
  supportRowSum G c rows Q S ≤ (S.length : ℚ) + etaQ G c
```
The route-tree theorem proves `CoreODLGoal` at the ROOT support; a root-representation
lemma converts this to `ODLFullGoal`.

## Row certificate (tagged by route type)
```lean
inductive ODLFullRowCert where
  | directCone   (cert : PayloadRef)
  | seed3Route   (tree : Seed3RouteTree.Seed3RouteTreeData)
                 (close : Seed3RouteTree.Seed3LeafCloseData)
  | eqLeaf       (cert : PayloadRef)
  | sibLeaf      (cert : PayloadRef)
  | noOverfull   (cert : PayloadRef)
  | negSwitch    (cert : PayloadRef)
  | fourDoor     (cert : PayloadRef)
  | qlt3         (cert : PayloadRef)
  | nch          (cert : PayloadRef)
```
`seed3Route` is the important constructor: it wraps the route tree already checked by
`checkSeed3RouteTree_sound_from_closeData` (GREEN) but adds the SEMANTIC leaf facts
needed to turn structural coverage into ODL bounds.

## Checker dispatcher
```lean
-- checkODLFullRowCert G c rows Q cert : Bool  dispatches per constructor:
  | .seed3Route T ext C =>
      Seed3RouteTree.checkSeed3RouteTree G c T &&
      Seed3RouteTree.checkSeed3LeafCloseData G c T ext C
  | .eqLeaf ref   => checkEQLeaf G c rows Q ref
  | .sibLeaf ref  => checkSIBLeaf G c rows Q ref
  | .qlt3 ref     => checkTwoDoorODLLeaf G c rows Q ref
  | .fourDoor ref => checkFourDoorODLLeaf G c rows Q ref
  | .nch ref      => checkNCHODLLeaf G c rows Q ref
  -- (directCone / noOverfull / negSwitch leaf checkers analogous — TO SPECIFY)
```

## Provider structure + soundness
```lean
structure ODLFullProvider (G : GraphData) (c : CutData) (rows : RowDB) : Type where
  globals : ODLGlobalProviders G c rows          -- global for graph/cut/rowDB, NOT per row
  rowCert : ∀ Q : RowCert, RowInDB rows Q → Q.length = 5 → ODLFullRowCert
  rowCertCheck : ∀ Q hQ hLen,
      checkODLFullRowCert G c rows Q (rowCert Q hQ hLen) = true
  rowCertSound : ∀ Q hQ hLen,
      checkODLFullRowCert G c rows Q (rowCert Q hQ hLen) = true →
        ODLFullGoal G c rows Q

theorem ODLFullProvider.sound
    (P : ODLFullProvider G c rows) (Q : RowCert)
    (hQ : RowInDB rows Q) (hLen : Q.length = 5) :
    rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c :=
  P.rowCertSound Q hQ hLen
-- This fills BranchAInputs.odlFull.
```

## Semantic Seed3 leaf facts (the hard content)
The green close-data theorem proves STRUCTURAL coverage. For ODL, add a SEMANTIC layer
`Seed3LeafODLFacts` with per-leaf-tag soundness fields, each mapping structural leaf
closure to `resolvedODL n`:
```lean
structure Seed3LeafODLFacts (G c rows Q) (T : Seed3RouteTree...) where
  neg_switch_sound :
    ∀ n ref, n ∈ T.nodes →
      n.kind = Seed3RouteTree.NodeKind.leaf Seed3RouteTree.LeafTag.NEG_SWITCH ref →
      Seed3RouteTree.checkLeafCloseForNode G c T ext C n = true → resolvedODL n
  prunable_sound      : ... LeafTag.PRUNABLE ...      → resolvedODL n
  not_saturated_sound : ... LeafTag.NOT_SATURATED ... → resolvedODL n
  four_door_sound     : ... LeafTag.FOUR_DOOR ...     → resolvedODL n
  -- eq_sound, sib_sound, qlt3_sound, nch_sound analogous
```

## How EQ charts instantiate ODLFull
EQ charts prove ONLY the EQ leaf theorem (a global finite seed theorem), NOT odlFull:
```lean
EQODL1CoverCert.sound + EQPassiveAM.sound + EQIsoCert.sound + ambientEtaBridge
  => EQLeaf.sound              -- one field in Seed3LeafODLFacts.eq_sound
                               -- or one ODLFullRowCert.eqLeaf soundness case
```
where the global cover cert is:
```lean
EQODL1CoverCert.sound :
  checkEQODL1CoverCert cert = true → ∀ w, EQCone w → EQODL1Bound w
```

## ⚠ O14 caveat (gating)
"If the 108 charts are only a partial chart set, they do NOT prove O14. If they are
the complete certified cover after skip/empty/stratum routing, then they give the
global EQ leaf theorem." — Current status 45/108 certified ⟹ the cover is PARTIAL ⟹
**O14 (chart cover) is NOT yet proven**; the full certified cover (all 108 rows,
including the face-split-queue rows) is required for the EQ leaf global theorem.

## Claude build plan
1. Needs leaf checkers (checkEQLeaf, checkSIBLeaf, checkTwoDoorODLLeaf,
   checkFourDoorODLLeaf, checkNCHODLLeaf, + directCone/noOverfull/negSwitch) — NEW defs.
2. `ODLFullProvider.sound := P.rowCertSound` is trivial once the structure + checkers exist.
3. The CONTENT is in `rowCertSound` per constructor = the per-leaf semantic soundness
   (Seed3LeafODLFacts) + EQ/SIB/... leaf global-provider soundness. That is the next
   MAIN design increment (per-family GeomSound lemmas).
4. Blocked on O14: full 108/108 chart cover for the EQ leaf global theorem.

## UPDATE 2026-07-06T23:35Z — MAIN per-leaf reply gated; root-representation BUILT; design CORRECTION
MAIN (thread msg 11) delivered the semantic ODL layer + a design correction. Key points:
- **CORRECTION**: PRUNABLE and NOT_SATURATED are NOT terminal ODL leaves — they are internal
  prune/absorb nodes with child-link inequalities. `checkPrunableTerminalLeaf := fun _ _ => false`,
  `checkNotSaturatedTerminalLeaf := fun _ _ => false`. (Supersedes the ODLFullRowCert `negSwitch`/etc.
  treatment where these appeared as leaves.)
- **Semantic layer** (separate from the STRUCTURAL tree; checkSeed3RouteTree_sound_from_closeData is
  structural only):
  ```lean
  structure ODLCoreData (G c rows Q) where
    support : List Nat ; supportSize : ℚ ; supportRowSum : ℚ ; supportSize_le_N : supportSize ≤ (G.n:ℚ)
  def CoreODLGoal (G c rows Q) (core) : Prop := core.supportRowSum ≤ core.supportSize + etaQ G c
  structure ODLNodeSemantics (G c rows Q) (T) where coreOf : NodeId → ODLCoreData G c rows Q
  def resolvedODL (G c rows Q) (T) (sem) (n : Seed3Node) : Prop := CoreODLGoal (sem.coreOf n.id)
  ```
- **Root-representation (BUILT GREEN, commit c8a7c3157, ODLFull.lean)**:
  ```lean
  structure RootRepresentsRow (G c rows Q) (rootCore) : Prop where
    row_le_support : rowSum G c rows Q ≤ rootCore.supportRowSum
  theorem ODLFull_of_rootCore (hRoot : RootRepresentsRow ...) (hCore : CoreODLGoal ... rootCore) :
      rowSum G c rows Q ≤ (G.n:ℚ) + etaQ G c := by unfold CoreODLGoal at hCore; linarith
  ```
  axioms [propext,Classical.choice,Quot.sound]. This is the root-local-to-row passage that lifts a
  certified root-core bound to BranchAInputs.odlFull.
- **Leaf providers** `Seed3ODLLeafProviders` (structure): checkEQLeaf/checkSIBLeaf/checkNoOverfullLeaf/
  checkNegSwitchLeaf/checkFourDoorLeaf/checkConeLeaf/checkBankBlockLeaf/checkLensGateLeaf/checkSeed10Leaf/
  checkTwoDoorODLLeaf/checkNCHODLLeaf (each Seed3Node→PayloadRef→Bool) + per-tag soundness
  (eq_sound/sib_sound/no_overfull_sound/neg_switch_sound/four_door_sound/cone_sound/bank_block_sound/
  lens_gate_sound/…): n∈T.nodes → n.kind=leaf TAG ref → checkXLeaf n ref=true → resolvedODL n.
- REMAINING odlFull: (a) the ODLNodeSemantics TREE-ASSEMBLY theorem (per-leaf resolvedODL + internal
  prune/absorb child-link inequalities ⟹ root resolvedODL) — the semantic analog of
  checkSeed3RouteTree_sound; (b) the leaf checker Bool defs + soundness (checkEQLeaf etc.); (c) O14 full
  108 cover for the EQ leaf global theorem. MAIN retasked for (a)+(b).

## UPDATE 2026-07-07T00:10Z — MAIN tree-assembly gated; excess-monotonicity link BUILT
MAIN (thread msg 13) delivered the semantic tree assembly. Key design + build status:
- **Internal-node numeric link** (BUILT GREEN, commit 616f7b706, ODLFull.lean): coreExcess(S) :=
  supportRowSum − supportSize; CoreExcessLE parent child := coreExcess parent ≤ coreExcess child;
  `CoreODLGoal_of_excess_le (hlink : CoreExcessLE parent child)(hchild : CoreODLGoal child) :
  CoreODLGoal parent := by unfold; linarith`. Since η is ambient/fixed, parent-excess ≤ child-excess
  propagates the child's ODL bound up. **This is the heart of the tree assembly.** PRUNABLE/NOT_SATURATED
  are internal nodes whose link certificates prove this inequality (NOT terminal leaves).
- **Composition (design, buildable next)**: `resolvedODL := CoreODLGoal (sem.coreOf n.id)`;
  `resolvedODL_of_one_child_excess_link := CoreODLGoal_of_excess_le` (prune/absorb one-child helper);
  `ODLFull_of_resolved_root (hresolved : resolvedODL root)(hrep : RootRepresentsRow (sem.coreOf root.id))
  : rowSum ≤ N+η := ODLFull_of_rootCore hrep hresolved` (resolvedODL root ≡ CoreODLGoal rootCore
  definitionally). Needs Seed3Node/Seed3RouteTreeData (in ns Seed3RouteTree, CertGraph.lean:4582).
- **Recursive checker (design)**: `checkODLResolveNode (fuel)(n) : Bool` — leaf → leafs.sound; internal →
  link check && all children resolve; soundness by fuel induction (mirrors checkSeed3RouteTree_sound,
  using isLeafKind/isInternalKind + List.all_eq_true over childrenOf). Needs Seed3ODLLeafProviders
  (gated on leaf checkers) + Seed3ODLInternalLinks.
- **Composition chain**: checkSeed3ODLSemanticTree_sound ⟹ resolvedODL(root) ≡ CoreODLGoal(rootCore);
  emitted RootRepresentsRow(rootCore) gives row_le_support + supportSize_le_N; ODLFull_of_rootCore ⟹
  rowSum ≤ N+η = BranchAInputs.odlFull.
- REMAINING: leaf checker Bool defs + per-tag soundness (checkEQLeaf/checkSIBLeaf/… ⟹ resolvedODL), the
  Seed3ODLInternalLinks structure + the recursive checker soundness build, and O14 (full 108 cover for the
  EQ leaf). MAIN retasked for the leaf checkers. RootRepresentsRow provenance = structural row/support
  ownership data (emitted per row), not tree-shape alone.

## UPDATE 2026-07-07T04:20Z — coreOf EMISSION design (MAIN) — odlFull provider FULLY DESIGNED
MAIN closed the odlFull recipe. coreOf is emitted PER NODE from a checked per-row core table (NOT inferred
from tree shape):
- ODLRowAtom { v : Nat, num : Int } + denom D; rowSum(Q) = (Sum atoms.num)/D.
- For node support S: supportRowSum(S,Q) = (Sum_{a.v in S} a.num)/D; supportSize(S) = |S| (unweighted graph).
- Emitted core: ODLCoreData.mk (support := S_n) (supportSize := (S_n.length:ℚ)) (supportRowSum := num/D)
  (supportSize_le_N := ...). supportRowSum is RECOMPUTED from atoms, not arbitrary.
- ROOT REPRESENTATION discharge: if root support covers every atom (atomsCoveredByRoot: ∀ atom∈atoms,
  atom.v∈rootSupport), then supportRowSum(root)=rowSum(Q), so row_le_support by le_of_eq. SAFE FALLBACK:
  rootSupport = V(G) => row_le_support automatic, supportSize = N (always sound; larger active closure is
  the tighter option). supportSize_le_N : N<=N.
- INTERNAL LINKS: PRUNE node child removes appendage H\T; coreExcess(parent)-coreExcess(child) =
  s_H(Q∩T) - (|H|-|T|); pruning inequality s_H(Q∩T)<=|H|-|T| => coreExcess(parent)<=coreExcess(child). SPLIT
  node: my internalLinks_of_coreExcess checks coreExcess(parent)<=coreExcess(child) per child (stronger, convenient).
- Per-row payload: ODLRowSemanticsPayload { atoms : List ODLRowAtom, denom : Nat, nodeCores : List
  ODLNodeCorePayload, rootNode : NodeId }.
- CLOSURE RECIPE: emit Seed3RouteTreeData + ODLRowSemanticsPayload; verify checkSeed3RouteTree + core table +
  internal links (exact core-excess) + terminal leaves (concrete providers); checkSeed3ODLSemanticTree_sound =>
  root CoreODLGoal; ODLFull_of_rootCore with RootRepresentsRow => BranchAInputs.odlFull filled for that row.
=> odlFull provider FRAMEWORK (built, 11 green) + DESIGN (coreOf emission) both COMPLETE. Remaining odlFull =
concrete per-row emitted ODLRowSemanticsPayload data (from chart certs + row structure) + O14 EQ-leaf cover.
The coreOf emission is a data-instantiation step (gated on Codex chart certs), not a new theorem.

## UPDATE 2026-07-07T05:00Z — PAYLOAD CHECKER design (MAIN) — odlFull provider DESIGN-COMPLETE
MAIN delivered the concrete per-row payload checker (the emitted-row verifier). Types:
- ODLRowAtom { v : Nat, num : Int }; ODLNodeCorePayload { nodeId : NodeId, support : List Nat, supportSize : ℚ,
  supportRowSum : ℚ }; ODLRowSemanticsPayload { atoms : List ODLRowAtom, denom : Nat, nodeCores : List
  ODLNodeCorePayload, rootNode : NodeId }.
- checkODLSupport (G)(S) := decide S.Nodup && S.all (v < G.n); denomQ P := if denom=0 then 1 else denom.
- checkODLRowSemanticsPayload RECOMPUTES (not trusting payload numerals): supportSize = support.length (guarded
  supportSize<=N); supportRowSum = (atom sum over support)/denom; rowSum Q = (total atom sum)/denom; root
  row_le_support from the root core. semanticsOfPayload uses the RECOMPUTED values.
- semanticsOfPayload : ODLRowSemanticsPayload -> ODLNodeSemantics (coreOf lookup by node id, recomputed cores).
- rootRepresents_of_payload : payload checks + hfind -> RootRepresentsRow (coreOf root.id).
- odlFull_of_rowPayload : (checkODLRowSemanticsPayload) + (checkSeed3ODLSemanticTree with built providers) =>
  rowSum G c rows Q <= (G.n:ℚ) + etaQ G c  [via checkSeed3ODLSemanticTree_sound_exists_root + rootRepresents_of_
  payload + my green ODLFull_of_rootCore]. THIS FILLS BranchAInputs.odlFull for an emitted row.
=> odlFull provider: FRAMEWORK built (11 green) + DESIGN complete (payload checker). Buildable next tick (big
block; ~8k chars). SOUNDNESS-CRITICAL open question (retasked MAIN): does checkODLRowSemanticsPayload bind
rowSum Q to the ACTUAL rowSum G c rows Q (= Q.load5 sum) via decide-equality, or only internal atom consistency?
The former is required for soundness (else the emitter could claim any rowSum). Confirm the exact binding.
