import Erdos23Delta0.Gamma.TwoRowRectangleExchange

/-!
# Active-scoped minimum row exchange

This module freezes the scope correction forced by the 89-vertex double-star
falsifier.  Collision and active-endpoint obligations are generated only in
off-support components containing both endpoints of a selected bad atom.
Inactive components have already collapsed to the zero-load branch.

The graph-theoretic frontier is isolated as
`RealActiveScopedHallFailureHasMonotoneOneRowDescent`.  Everything after that
statement, including the finite Hall equivalence and contradiction with the
canonical obligation-score minimum, is proved here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveScopedMinimumExchange

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open TwoRowRectangleExchange

attribute [local instance] Classical.propDecidable

/-- The graph of selected-core blue edges absent from the selected row
support. -/
def activeGraph (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : SimpleGraph (Fin G.n) where
  Adj x y : Prop :=
    x ≠ y ∧ normEdge x.1 y.1 ∈ activeEdges G c omega
  symm := by
    intro x y h
    exact ⟨h.1.symm, by simpa only [normEdge_comm] using h.2⟩
  loopless := by
    intro x h
    exact h.1 rfl

/-- A selected vertex lies in an active component when that off-support
component contains both endpoints of some selected bad atom. -/
def ActiveOwner (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (v : Fin G.n) : Prop :=
  ∃ i : Fin bads.length,
    ∃ hu : (bads.get i).u < G.n,
    ∃ hv : (bads.get i).v < G.n,
      (activeGraph G c omega).Reachable ⟨(bads.get i).u, hu⟩ v ∧
        (activeGraph G c omega).Reachable ⟨(bads.get i).v, hv⟩ v

/-- Collision halves whose owner survives the active-component collapse. -/
abbrev ActiveCollisionHalf (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type :=
  {d : CollisionHalf G omega // ActiveOwner G c omega d.owner}

noncomputable instance activeCollisionHalfFintype
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Fintype (ActiveCollisionHalf G c omega) :=
  Fintype.ofFinite _

noncomputable instance activeCollisionHalfDecidableEq
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : DecidableEq (ActiveCollisionHalf G c omega) :=
  Classical.decEq _

/-- Degree in the active off-support graph, set to zero off active
components. -/
noncomputable def activeDegree (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) (v : Fin G.n) : Nat :=
  if ActiveOwner G c omega v then
    (Finset.univ.filter fun w : Fin G.n =>
      (activeGraph G c omega).Adj v w).card
  else 0

/-- Selected length-five load at a vertex. -/
def selectedLoad {bads : List BadEdgeData} (omega : RowChoice bads)
    (v : Nat) : Nat :=
  5 * pairCount omega v v

/-- Residual endpoint obligations after ordinary vertex slack pays first. -/
noncomputable def hitNeedUnits (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (v : Fin G.n) : Nat :=
  activeDegree G c omega v - (G.n - selectedLoad omega v.1)

/-- One integral endpoint-hit obligation owned by an active vertex. -/
abbrev ActiveHitNeed (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type :=
  Σ v : Fin G.n, Fin (hitNeedUnits G c omega v)

noncomputable instance activeHitNeedFintype
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Fintype (ActiveHitNeed G c omega) := by
  unfold ActiveHitNeed
  infer_instance

noncomputable instance activeHitNeedDecidableEq
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : DecidableEq (ActiveHitNeed G c omega) :=
  Classical.decEq _

/-- Exact active-scoped demand type: repeated-pair halves plus residual
endpoint hits. -/
abbrev Demand (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type :=
  ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega

noncomputable instance demandFintype
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Fintype (Demand G c omega) := by
  unfold Demand
  infer_instance

noncomputable instance demandDecidableEq
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : DecidableEq (Demand G c omega) :=
  Classical.decEq _

def demandOwner {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    Demand G c omega → Fin G.n
  | Sum.inl d => d.1.owner
  | Sum.inr h => h.1

/-- Half-zero cells on active-component edges are consumed by endpoint hits
before collision routing. -/
def ScopedReserved (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (s : FreeHalf G omega) : Prop :=
  s.half.1 = 0 ∧
    (activeGraph G c omega).Adj s.sourceX s.sourceY ∧
    ActiveOwner G c omega s.sourceX

/-- The same-owner or row-companion relation, phrased directly by owner so
it applies uniformly to collision and endpoint-hit obligations. -/
def EligibleOwner (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (owner : Fin G.n) (s : FreeHalf G omega) : Prop :=
  s.sourceX = owner ∨
    (0 < pairCount omega owner.1 s.sourceX.1 ∧
      0 < pairCount omega owner.1 s.sourceY.1 ∧
      0 ≤ sigma G c [s.sourceX.1, s.sourceY.1])

def Available (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (d : Demand G c omega) (s : FreeHalf G omega) : Prop :=
  EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s

noncomputable instance availableDecidable
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} : DecidableRel (Available G c (omega := omega)) :=
  fun _ _ => Classical.propDecidable _

structure Matching (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  assign : Demand G c omega → FreeHalf G omega
  injective : Function.Injective assign
  available : ∀ d, Available G c d (assign d)

def HallCondition (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (Demand G c omega),
    A.card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ A, Available G c d s).card

theorem matching_nonempty_iff_hall
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Nonempty (Matching G c omega) ↔ HallCondition G c omega := by
  let r := Available G c (omega := omega)
  have hHall := Fintype.all_card_le_filter_rel_iff_exists_injective r
  constructor
  · rintro ⟨M⟩
    apply hHall.mpr
    exact ⟨M.assign, M.injective, M.available⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinj, hrel⟩
    exact ⟨⟨assign, hinj, hrel⟩⟩

def replaceOne {bads : List BadEdgeData} (omega : RowChoice bads)
    (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length) : RowChoice bads :=
  replaceTwo omega index index replacement replacement

structure MonotoneOneRowDescent (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  collision_noninc :
    collisionUnits G (replaceOne omega index replacement) ≤
      collisionUnits G omega
  active_drop :
    (activeEdges G c (replaceOne omega index replacement)).length <
      (activeEdges G c omega).length

theorem MonotoneOneRowDescent.score_drop
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (D : MonotoneOneRowDescent G c omega) :
    obligationScore G c (replaceOne omega D.index D.replacement) <
      obligationScore G c omega :=
  obligationScore_lt_of_collision_noninc_active_lt
    D.collision_noninc D.active_drop

/-- Sole graph-exchange frontier in the corrected active scope. -/
def HallFailureHasMonotoneOneRowDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) →
      Nonempty (MonotoneOneRowDescent G c omega)

def RealHallFailureHasMonotoneOneRowDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasMonotoneOneRowDescent G c bads

def MinimumGlobalChoiceActiveScopedHall (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) : Prop :=
  Nonempty (Matching G c (canonicalChoice G c bads h))

/-- The finite-minimum contradiction for the stronger global monotone
exchange statement. -/
theorem minimumGlobalChoiceActiveScopedHall_of_descent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hdescent : HallFailureHasMonotoneOneRowDescent G c bads) :
    MinimumGlobalChoiceActiveScopedHall G c bads hrows := by
  unfold MinimumGlobalChoiceActiveScopedHall
  by_contra hmatching
  obtain ⟨D⟩ := hdescent (canonicalChoice G c bads hrows) hmatching
  have hlt := D.score_drop
  have hmin := canonicalChoice_optimal G c bads hrows
    (replaceOne (canonicalChoice G c bads hrows) D.index D.replacement)
  omega

theorem realMinimumGlobalChoiceActiveScopedHall_of_descent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hdescent : RealHallFailureHasMonotoneOneRowDescent G c bads) :
    MinimumGlobalChoiceActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumGlobalChoiceActiveScopedHall_of_descent
  exact hdescent htri hmax hconn hdb

/-- Exact cardinality of the corrected active-scoped demand type. -/
noncomputable def scopedObligationScore
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) : Nat :=
  Fintype.card (Demand G c omega)

/-- Canonical row tuple minimizing active-scoped demand cardinality itself.
This is distinct from the stronger global collision-plus-active-edge score. -/
noncomputable def minScopedChoice (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) :
    {omega : RowChoice bads // ∀ eta : RowChoice bads,
      scopedObligationScore G c omega ≤ scopedObligationScore G c eta} := by
  letI : Nonempty (RowChoice bads) := ⟨defaultChoice h⟩
  exact chooseFiniteMinimizer (scopedObligationScore G c)

noncomputable def scopedCanonicalChoice (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) : RowChoice bads :=
  (minScopedChoice G c bads h).1

theorem scopedCanonicalChoice_optimal (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads)
    (eta : RowChoice bads) :
    scopedObligationScore G c (scopedCanonicalChoice G c bads h) ≤
      scopedObligationScore G c eta :=
  (minScopedChoice G c bads h).2 eta

/-- Weakest one-row statement sufficient for the corrected scoped selector. -/
structure ScopedScoreOneRowDescent (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  changed : replacement ≠ omega index
  score_drop :
    scopedObligationScore G c (replaceOne omega index replacement) <
      scopedObligationScore G c omega

/-- Number of replacement-row edges that were active before the
replacement. -/
def rowActiveEdgeCount (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) (row : Row5) : Nat :=
  ((rowPathEdges row).filter fun e =>
    decide (e ∈ activeEdges G c omega)).length

/-- R25's geometric atom.  The replacement is an internal alternative row
with at least three old active edges and destroys every active component.
Only `kills_active` is needed by the scoped-score descent; the other fields
are the exact graph-geometric certificate to be constructed. -/
structure ScopedInternalKillerRow (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  changed : replacement ≠ omega index
  internal : ∀ x ∈ ((bads.get index).rows.get replacement).verts,
    x ∈ selectedVertices omega
  three_active : 3 ≤ rowActiveEdgeCount G c omega
    ((bads.get index).rows.get replacement)
  kills_active : ∀ v : Fin G.n,
    ¬ActiveOwner G c (replaceOne omega index replacement) v

/-- Corrected R26 frontier after the order-11 `2A+2S` falsifier.  The
replacement is internal and destroys every active component; no lower bound
on its number of old active edges is imposed. -/
structure ScopedAbsorbingInternalRow (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  changed : replacement ≠ omega index
  internal : ∀ x ∈ ((bads.get index).rows.get replacement).verts,
    x ∈ selectedVertices omega
  kills_active : ∀ v : Fin G.n,
    ¬ActiveOwner G c (replaceOne omega index replacement) v

def ScopedInternalKillerRow.toAbsorbing
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (K : ScopedInternalKillerRow G c omega) :
    ScopedAbsorbingInternalRow G c omega := {
  index := K.index
  replacement := K.replacement
  changed := K.changed
  internal := K.internal
  kills_active := K.kills_active
}

def KillerRawValid (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length) : Prop :=
  replacement ≠ omega index ∧
    (∀ x ∈ ((bads.get index).rows.get replacement).verts,
      x ∈ selectedVertices omega) ∧
    3 ≤ rowActiveEdgeCount G c omega
      ((bads.get index).rows.get replacement) ∧
    ∀ v : Fin G.n,
      ¬ActiveOwner G c (replaceOne omega index replacement) v

noncomputable def semanticCheckScopedInternalKillerRow
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length) : Bool :=
  decide (KillerRawValid G c omega index replacement)

theorem semanticCheckScopedInternalKillerRow_eq_true_iff
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (index : Fin bads.length)
    (replacement : Fin (bads.get index).rows.length) :
    semanticCheckScopedInternalKillerRow G c omega index replacement = true ↔
      KillerRawValid G c omega index replacement := by
  simp [semanticCheckScopedInternalKillerRow]

noncomputable def killer_of_semanticCheck_eq_true
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {index : Fin bads.length}
    {replacement : Fin (bads.get index).rows.length}
    (h : semanticCheckScopedInternalKillerRow
      G c omega index replacement = true) :
    ScopedInternalKillerRow G c omega := by
  have hv := (semanticCheckScopedInternalKillerRow_eq_true_iff
    G c omega index replacement).mp h
  exact ⟨index, replacement, hv.1, hv.2.1, hv.2.2.1, hv.2.2.2⟩

/-- Literal killer-row payload. `labels` is a component-coloring certificate
for the new active graph: active edges preserve labels while every bad atom
has differently labeled endpoints. -/
structure ScopedInternalKillerRowData {bads : List BadEdgeData} where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  labels : List Nat
deriving Repr

def checkScopedInternalKillerRow
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (K : ScopedInternalKillerRowData (bads := bads)) : Bool :=
  let eta := replaceOne omega K.index K.replacement
  decide (K.labels.length = G.n) &&
    decide (K.replacement ≠ omega K.index) &&
    ((bads.get K.index).rows.get K.replacement).verts.all
      (fun x => decide (x ∈ selectedVertices omega)) &&
    decide (3 ≤ rowActiveEdgeCount G c omega
      ((bads.get K.index).rows.get K.replacement)) &&
    (activeEdges G c eta).all (fun e =>
      decide (e.1 < G.n ∧ e.2 < G.n) &&
        decide (K.labels.getD e.1 0 = K.labels.getD e.2 0)) &&
    bads.all (fun b =>
      decide (b.u < G.n ∧ b.v < G.n) &&
        decide (K.labels.getD b.u 0 ≠ K.labels.getD b.v 0))

private theorem label_eq_of_reachable
    {V : Type*} {H : SimpleGraph V} (label : V → Nat)
    (hedge : ∀ x y, H.Adj x y → label x = label y)
    {x y : V} (hxy : H.Reachable x y) : label x = label y := by
  rcases hxy with ⟨walk⟩
  induction walk with
  | nil => rfl
  | cons hadj walk ih =>
      exact (hedge _ _ hadj).trans ih

/-- Soundness of the executable component-label checker. -/
theorem killer_of_checkScopedInternalKillerRow
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    {K : ScopedInternalKillerRowData (bads := bads)}
    (hcheck : checkScopedInternalKillerRow G c omega K = true) :
    Nonempty (ScopedInternalKillerRow G c omega) := by
  classical
  unfold checkScopedInternalKillerRow at hcheck
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hcheck
  rcases hcheck with
    ⟨⟨⟨⟨⟨hlen, hchanged⟩, hinternal⟩, hthree⟩, hedgeLabels⟩, hbadLabels⟩
  let eta := replaceOne omega K.index K.replacement
  have hedge : ∀ x y : Fin G.n,
      (activeGraph G c eta).Adj x y →
        K.labels.getD x.1 0 = K.labels.getD y.1 0 := by
    intro x y hxy
    have hitem := hedgeLabels (normEdge x.1 y.1) hxy.2
    by_cases hlt : x.1 < y.1
    · simpa [normEdge, hlt] using hitem.2
    · simpa [normEdge, hlt] using hitem.2.symm
  have hkills : ∀ v : Fin G.n, ¬ActiveOwner G c eta v := by
    intro v hv
    rcases hv with ⟨i, hu, hv, hreachU, hreachV⟩
    have hlu : K.labels.getD (bads.get i).u 0 = K.labels.getD v.1 0 :=
      label_eq_of_reachable
        (fun x : Fin G.n => K.labels.getD x.1 0) hedge hreachU
    have hlv : K.labels.getD (bads.get i).v 0 = K.labels.getD v.1 0 :=
      label_eq_of_reachable
        (fun x : Fin G.n => K.labels.getD x.1 0) hedge hreachV
    have hbad := hbadLabels (bads.get i) (List.get_mem bads i)
    exact hbad.2 (hlu.trans hlv.symm)
  refine ⟨{
    index := K.index
    replacement := K.replacement
    changed := hchanged
    internal := hinternal
    three_active := hthree
    kills_active := ?_
  }⟩
  simpa only [eta] using hkills

abbrev ScopedAbsorbingInternalRowData {bads : List BadEdgeData} :=
  ScopedInternalKillerRowData (bads := bads)

def checkScopedAbsorbingInternalRow
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (K : ScopedAbsorbingInternalRowData (bads := bads)) : Bool :=
  let eta := replaceOne omega K.index K.replacement
  decide (K.labels.length = G.n) &&
    decide (K.replacement ≠ omega K.index) &&
    ((bads.get K.index).rows.get K.replacement).verts.all
      (fun x => decide (x ∈ selectedVertices omega)) &&
    (activeEdges G c eta).all (fun e =>
      decide (e.1 < G.n ∧ e.2 < G.n) &&
        decide (K.labels.getD e.1 0 = K.labels.getD e.2 0)) &&
    bads.all (fun b =>
      decide (b.u < G.n ∧ b.v < G.n) &&
        decide (K.labels.getD b.u 0 ≠ K.labels.getD b.v 0))

/-- Soundness of the executable corrected absorbing-row checker. -/
theorem absorbing_of_checkScopedAbsorbingInternalRow
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    {K : ScopedAbsorbingInternalRowData (bads := bads)}
    (hcheck : checkScopedAbsorbingInternalRow G c omega K = true) :
    Nonempty (ScopedAbsorbingInternalRow G c omega) := by
  classical
  unfold checkScopedAbsorbingInternalRow at hcheck
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hcheck
  rcases hcheck with
    ⟨⟨⟨⟨hlen, hchanged⟩, hinternal⟩, hedgeLabels⟩, hbadLabels⟩
  let eta := replaceOne omega K.index K.replacement
  have hedge : ∀ x y : Fin G.n,
      (activeGraph G c eta).Adj x y →
        K.labels.getD x.1 0 = K.labels.getD y.1 0 := by
    intro x y hxy
    have hitem := hedgeLabels (normEdge x.1 y.1) hxy.2
    by_cases hlt : x.1 < y.1
    · simpa [normEdge, hlt] using hitem.2
    · simpa [normEdge, hlt] using hitem.2.symm
  have hkills : ∀ v : Fin G.n, ¬ActiveOwner G c eta v := by
    intro v hv
    rcases hv with ⟨i, hu, hv, hreachU, hreachV⟩
    have hlu : K.labels.getD (bads.get i).u 0 = K.labels.getD v.1 0 :=
      label_eq_of_reachable
        (fun x : Fin G.n => K.labels.getD x.1 0) hedge hreachU
    have hlv : K.labels.getD (bads.get i).v 0 = K.labels.getD v.1 0 :=
      label_eq_of_reachable
        (fun x : Fin G.n => K.labels.getD x.1 0) hedge hreachV
    have hbad := hbadLabels (bads.get i) (List.get_mem bads i)
    exact hbad.2 (hlu.trans hlv.symm)
  refine ⟨{
    index := K.index
    replacement := K.replacement
    changed := hchanged
    internal := hinternal
    kills_active := ?_
  }⟩
  simpa only [eta] using hkills

theorem scopedScore_zero_of_no_active_owner
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (hactive : ∀ v : Fin G.n, ¬ActiveOwner G c omega v) :
    scopedObligationScore G c omega = 0 := by
  classical
  apply Fintype.card_eq_zero_iff.mpr
  constructor
  intro d
  cases d with
  | inl collision =>
      exact hactive collision.1.owner collision.2
  | inr hit =>
      rcases hit with ⟨v, copy⟩
      have hdegree : activeDegree G c omega v = 0 := by
        simp [activeDegree, hactive v]
      have hneed : hitNeedUnits G c omega v = 0 := by
        simp [hitNeedUnits, hdegree]
      exact Fin.elim0 (hneed ▸ copy)

theorem ScopedInternalKillerRow.scopedScore_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (K : ScopedInternalKillerRow G c omega) :
    scopedObligationScore G c
      (replaceOne omega K.index K.replacement) = 0 :=
  scopedScore_zero_of_no_active_owner G c
    (replaceOne omega K.index K.replacement) K.kills_active

theorem ScopedAbsorbingInternalRow.scopedScore_zero
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (K : ScopedAbsorbingInternalRow G c omega) :
    scopedObligationScore G c
      (replaceOne omega K.index K.replacement) = 0 :=
  scopedScore_zero_of_no_active_owner G c
    (replaceOne omega K.index K.replacement) K.kills_active

theorem matching_of_scopedScore_zero
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (hzero : scopedObligationScore G c omega = 0) :
    Nonempty (Matching G c omega) := by
  classical
  haveI : IsEmpty (Demand G c omega) :=
    Fintype.card_eq_zero_iff.mp hzero
  refine ⟨{
    assign := fun d => isEmptyElim d
    injective := fun d => isEmptyElim d
    available := fun d => isEmptyElim d
  }⟩

theorem scopedScore_pos_of_matching_failure
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (hfailure : ¬Nonempty (Matching G c omega)) :
    0 < scopedObligationScore G c omega := by
  by_contra hnot
  have hzero : scopedObligationScore G c omega = 0 :=
    Nat.eq_zero_of_not_pos hnot
  exact hfailure (matching_of_scopedScore_zero G c omega hzero)

def HallFailureHasInternalKillerRow
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) →
      Nonempty (ScopedInternalKillerRow G c omega)

def RealHallFailureHasInternalKillerRow
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasInternalKillerRow G c bads

def HallFailureHasAbsorbingInternalRow
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) →
      Nonempty (ScopedAbsorbingInternalRow G c omega)

def RealHallFailureHasAbsorbingInternalRow
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasAbsorbingInternalRow G c bads

def HallFailureHasScopedScoreOneRowDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (Matching G c omega) →
      Nonempty (ScopedScoreOneRowDescent G c omega)

def RealHallFailureHasScopedScoreOneRowDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    HallFailureHasScopedScoreOneRowDescent G c bads

def MinimumActiveScopedHall (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) : Prop :=
  Nonempty (Matching G c (scopedCanonicalChoice G c bads h))

/-- R25's finite-minimum wrapper, now stated against the score it actually
decreases. -/
theorem minimumActiveScopedHall_of_killer
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hkiller : HallFailureHasInternalKillerRow G c bads) :
    MinimumActiveScopedHall G c bads hrows := by
  unfold MinimumActiveScopedHall
  by_contra hmatching
  let omega := scopedCanonicalChoice G c bads hrows
  have hpos := scopedScore_pos_of_matching_failure G c omega hmatching
  obtain ⟨K⟩ := hkiller omega hmatching
  have hzero := K.scopedScore_zero
  have hmin := scopedCanonicalChoice_optimal G c bads hrows
    (replaceOne omega K.index K.replacement)
  change scopedObligationScore G c omega ≤ _ at hmin
  rw [hzero] at hmin
  omega

theorem realMinimumActiveScopedHall_of_killer
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hkiller : RealHallFailureHasInternalKillerRow G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumActiveScopedHall_of_killer
  exact hkiller htri hmax hconn hdb

/-- Corrected finite-minimum wrapper.  The falsified three-active threshold
does not occur in this proof: destroying all active owners is sufficient. -/
theorem minimumActiveScopedHall_of_absorbing
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (habsorbing : HallFailureHasAbsorbingInternalRow G c bads) :
    MinimumActiveScopedHall G c bads hrows := by
  unfold MinimumActiveScopedHall
  by_contra hmatching
  let omega := scopedCanonicalChoice G c bads hrows
  have hpos := scopedScore_pos_of_matching_failure G c omega hmatching
  obtain ⟨K⟩ := habsorbing omega hmatching
  have hzero := K.scopedScore_zero
  have hmin := scopedCanonicalChoice_optimal G c bads hrows
    (replaceOne omega K.index K.replacement)
  change scopedObligationScore G c omega ≤ _ at hmin
  rw [hzero] at hmin
  omega

theorem realMinimumActiveScopedHall_of_absorbing
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (habsorbing : RealHallFailureHasAbsorbingInternalRow G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumActiveScopedHall_of_absorbing
  exact habsorbing htri hmax hconn hdb

/-- Canonical-minimum contradiction from the weakest scoped-score descent
frontier. -/
theorem minimumActiveScopedHall_of_scopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hdescent : HallFailureHasScopedScoreOneRowDescent G c bads) :
    MinimumActiveScopedHall G c bads hrows := by
  unfold MinimumActiveScopedHall
  by_contra hmatching
  let omega := scopedCanonicalChoice G c bads hrows
  obtain ⟨D⟩ := hdescent omega hmatching
  have hmin := scopedCanonicalChoice_optimal G c bads hrows
    (replaceOne omega D.index D.replacement)
  exact (Nat.not_lt_of_ge hmin) D.score_drop

theorem realMinimumActiveScopedHall_of_scopedScoreDescent
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hdescent : RealHallFailureHasScopedScoreOneRowDescent G c bads) :
    MinimumActiveScopedHall G c bads hdb.rowsNonempty := by
  apply minimumActiveScopedHall_of_scopedScoreDescent
  exact hdescent htri hmax hconn hdb

end ActiveScopedMinimumExchange
end Gamma
end Erdos23Delta0
