import Erdos23Delta0.Gamma.MinimumDemandRowSelection
import Mathlib.Combinatorics.Hall.Basic

/-!
# The canonical minimum-demand collision Hall frontier

This file states the remaining R20 transfer theorem against the literal
`GraphData` / `BadEdgeData` row database.  Active off-support endpoint hits are
reserved first.  The only remaining demands are the two halves of every
repeated ordered-pair occurrence.  They must inject into permanently free
ordered-pair halves by either same-owner cancellation or the checked
row-companion terminal.

No existence theorem is asserted here.  `MinimumDemandCollisionHall` is the
single graph-exchange statement left by the exact census and blow-up gates.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CanonicalCollisionHall

open CertGraph
open MinimumDemandRowSelection

/-- Canonical undirected key of a listed bad edge. -/
def badEdgeKey (b : BadEdgeData) : Nat × Nat :=
  normEdge b.u b.v

/-- Semantic completeness of the literal all-ell=5 row database.  Validation
alone is insufficient: the exchange proof must know that every bad edge occurs
once and every literal length-four blue path between its endpoints is available
as a row choice. -/
structure CompleteShortestRowDB (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop where
  checked : AllBadsChecked G c bads
  badKeys_nodup : (bads.map badEdgeKey).Nodup
  /-- The row list represents shortest paths as a set.  Multiplicity would
  distort the heat-bath variation and can falsify the transport bound. -/
  rowVerts_nodup : ∀ i : Fin bads.length,
    ((bads.get i).rows.map Row5.verts).Nodup
  covers_bad : ∀ u v : Nat,
    u < G.n → v < G.n → badb G c u v = true →
      ∃ i : Fin bads.length, badEdgeKey (bads.get i) = normEdge u v
  covers_row : ∀ i : Fin bads.length, ∀ verts : List Nat,
    checkRow5 G c (bads.get i).u (bads.get i).v
      { badId := i.1, verts := verts } = true →
      ∃ row ∈ (bads.get i).rows, row.verts = verts

theorem CompleteShortestRowDB.rowsNonempty
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (h : CompleteShortestRowDB G c bads) : RowsNonempty bads :=
  rowsNonempty_of_allBadsChecked h.checked

/-- One half of one repeated ordered-pair collision at an owner.  The dependent
`copy` field has exactly `pairCount owner other - 1` inhabitants. -/
structure CollisionHalf (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) where
  owner : Fin G.n
  other : Fin G.n
  copy : Fin (pairCount omega owner.1 other.1 - 1)
  half : Fin 2
deriving DecidableEq, Fintype

/-- One globally available ordered-pair half.  Freeness is permanent for the
selected row tuple, and the coordinates are distinct. -/
structure FreeHalf (G : GraphData) {bads : List BadEdgeData}
    (omega : RowChoice bads) where
  sourceX : Fin G.n
  sourceY : Fin G.n
  half : Fin 2
  distinct : sourceX ≠ sourceY
  free : pairCount omega sourceX.1 sourceY.1 = 0
deriving DecidableEq, Fintype

/-- The half-zero orientations of an active off-support blue edge are consumed
by its two endpoint hit-needs before collision matching begins. -/
def Reserved (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (s : FreeHalf G omega) : Prop :=
  s.half.1 = 0 ∧
    normEdge s.sourceX.1 s.sourceY.1 ∈ activeEdges G c omega

/-- Same-owner cancellation uses a free source whose first coordinate is the
collision owner. -/
def SameOwner {G : GraphData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (d : CollisionHalf G omega)
    (s : FreeHalf G omega) : Prop :=
  s.sourceX = d.owner

/-- Row-companion cancellation: both source coordinates co-occur with the
owner (not necessarily on the same selected row), the source pair itself is
free, and the literal two-vertex switch has nonnegative max-cut loss. -/
def RowCompanion (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (d : CollisionHalf G omega)
    (s : FreeHalf G omega) : Prop :=
  0 < pairCount omega d.owner.1 s.sourceX.1 ∧
    0 < pairCount omega d.owner.1 s.sourceY.1 ∧
    0 ≤ sigma G c [s.sourceX.1, s.sourceY.1]

/-- The exact source relation used by the clean row-reserved census gate. -/
def Eligible (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (d : CollisionHalf G omega)
    (s : FreeHalf G omega) : Prop :=
  SameOwner d s ∨ RowCompanion G c d s

/-- Matching relation after removing the two oriented active-hit reservations. -/
def Available (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    {omega : RowChoice bads} (d : CollisionHalf G omega)
    (s : FreeHalf G omega) : Prop :=
  Eligible G c d s ∧ ¬Reserved G c omega s

instance availableDecidable (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    DecidableRel (Available G c (omega := omega)) := by
  intro d s
  unfold Available Eligible SameOwner RowCompanion Reserved
  infer_instance

/-- A full collision matching after the active endpoint sources have been
reserved. -/
structure CollisionMatching (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  assign : CollisionHalf G omega → FreeHalf G omega
  injective : Function.Injective assign
  eligible : ∀ d, Eligible G c d (assign d)
  unreserved : ∀ d, ¬ Reserved G c omega (assign d)

/-- Literal finite Hall inequalities for every collision-demand shore. -/
def CollisionHallCondition (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (CollisionHalf G omega),
    A.card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ A, Available G c d s).card

/-- Exact Hall equivalence for the compiled demand/source relation. -/
theorem collisionMatching_nonempty_iff_hall
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    Nonempty (CollisionMatching G c omega) ↔
      CollisionHallCondition G c omega := by
  let r := Available G c (omega := omega)
  have hHall := Fintype.all_card_le_filter_rel_iff_exists_injective r
  constructor
  · rintro ⟨M⟩
    apply hHall.mpr
    exact ⟨M.assign, M.injective, fun d => ⟨M.eligible d, M.unreserved d⟩⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinj, hrel⟩
    exact ⟨{
      assign := assign
      injective := hinj
      eligible := fun d => (hrel d).1
      unreserved := fun d => (hrel d).2
    }⟩

/-- The canonical row tuple selected by the compiled global minimum of
`2 * collisionUnits + 2 * activeEdges.length`. -/
noncomputable def canonicalChoice (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) : RowChoice bads :=
  (minDemandChoice G c bads h).1

/-- Sole R20 combinatorial frontier: the canonical minimum-demand row tuple
admits the reserved-hit / same-owner-or-row-companion collision matching. -/
def MinimumDemandCollisionHall (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) : Prop :=
  Nonempty (CollisionMatching G c (canonicalChoice G c bads h))

/-- Hamming distance between two dependent row-choice tuples. -/
def disagreementCount {bads : List BadEdgeData}
    (omega eta : RowChoice bads) : Nat :=
  (Finset.univ.filter fun i : Fin bads.length => omega i ≠ eta i).card

/-- A failed matching can be repaired by replacing at most two selected rows
and strictly lowering the compiled obligation score. -/
def HasTwoRowImprovement (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∃ eta : RowChoice bads,
    disagreementCount omega eta ≤ 2 ∧
      obligationScore G c eta < obligationScore G c omega

/-- Exchange form of the graph-theoretic wall.  This formulation is stronger
than Hall completeness for the minimizer, but is directly falsifiable on every
finite row database. -/
def TwoRowExchangeComplete (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop :=
  ∀ omega : RowChoice bads,
    ¬Nonempty (CollisionMatching G c omega) →
      HasTwoRowImprovement G c omega

/-- Real graph-derived version of the bounded exchange statement.  These are
the nonvacuous semantic hypotheses exercised by the gate: triangle-free,
connected-blue maximum cut and a complete all-ell=5 row DB. -/
def RealTwoRowExchangeComplete (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) : Prop :=
  TriangleFree G →
    IsMaxCut G c →
    BConnected G c →
    CompleteShortestRowDB G c bads →
    TwoRowExchangeComplete G c bads

theorem canonicalChoice_optimal (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads)
    (eta : RowChoice bads) :
    obligationScore G c (canonicalChoice G c bads h) ≤
      obligationScore G c eta :=
  minDemandChoice_optimal G c bads h eta

theorem minimumDemandCollisionHall_iff (G : GraphData) (c : CutData)
    (bads : List BadEdgeData) (h : RowsNonempty bads) :
    MinimumDemandCollisionHall G c bads h ↔
      Nonempty (CollisionMatching G c (canonicalChoice G c bads h)) := by
  rfl

/-- The finite-minimum argument: a strict row-exchange theorem immediately
forces Hall completeness at the canonical minimum-demand tuple. -/
theorem minimumDemandCollisionHall_of_twoRowExchange
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (hrows : RowsNonempty bads)
    (hexchange : TwoRowExchangeComplete G c bads) :
    MinimumDemandCollisionHall G c bads hrows := by
  unfold MinimumDemandCollisionHall
  by_contra hmatch
  have himprove := hexchange (canonicalChoice G c bads hrows) hmatch
  rcases himprove with ⟨eta, _, hlt⟩
  have hmin := canonicalChoice_optimal G c bads hrows eta
  omega

/-- End-to-end reduction on a real complete row database.  The only missing
input is `RealTwoRowExchangeComplete`; all finite choice and Hall machinery is
discharged here. -/
theorem realMinimumDemandCollisionHall_of_exchange
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (hconn : BConnected G c)
    (hdb : CompleteShortestRowDB G c bads)
    (hexchange : RealTwoRowExchangeComplete G c bads) :
    MinimumDemandCollisionHall G c bads hdb.rowsNonempty := by
  apply minimumDemandCollisionHall_of_twoRowExchange
  exact hexchange htri hmax hconn hdb

#print axioms canonicalChoice_optimal
#print axioms collisionMatching_nonempty_iff_hall
#print axioms minimumDemandCollisionHall_iff
#print axioms minimumDemandCollisionHall_of_twoRowExchange
#print axioms realMinimumDemandCollisionHall_of_exchange

end CanonicalCollisionHall
end Gamma
end Erdos23Delta0
