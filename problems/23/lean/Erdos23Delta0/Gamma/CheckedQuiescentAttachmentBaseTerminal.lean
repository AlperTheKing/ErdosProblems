import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
# Checked quiescent-attachment base terminals

Pattern 5 uses a permanently free ordered-pair half whose endpoints lie
outside the active scope.  Each endpoint's component in the blue graph induced
on the quiescent vertices has an active boundary attachment.  The two
attachments and the destination owner lie in one active component and each
attachment is a selected-row companion of the owner.

This file checks exactly that geometric predicate against the current Gamma
APIs.  It proves that the resulting `FreeHalf` is not `ScopedReserved` and that
the union-of-components switch has nonnegative loss at a checked maximum cut.
There is currently no production adapter from this terminal to a typed
`c5Base` ledger token, so the final consumer step is exposed as the explicit
`TerminalConsumerSound` hypothesis below; no bank-incidence theorem is
asserted here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace QuiescentAttachment

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

private theorem blueb_comm (G : GraphData) (c : CutData) (u v : Nat) :
    blueb G c u v = blueb G c v u := by
  unfold blueb
  rw [adjb_comm]
  by_cases h : sideb c u = sideb c v <;> simp [h, Ne.symm]

/-- The literal blue graph of the fixed cut. -/
def blueGraph (G : GraphData) (c : CutData) : SimpleGraph (Fin G.n) where
  Adj x y := blueb G c x.1 y.1 = true
  symm := by
    intro x y hxy
    simpa only [blueb_comm] using hxy
  loopless := by
    intro x hxx
    simp [blueb, adjb] at hxx

/-- The blue graph induced on the complement of the active scope. -/
def quiescentGraph (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    SimpleGraph (Fin G.n) where
  Adj x y :=
    (blueGraph G c).Adj x y ∧
      ¬ActiveOwner G c omega x ∧
      ¬ActiveOwner G c omega y
  symm := by
    intro x y hxy
    exact ⟨(blueGraph G c).symm hxy.1, hxy.2.2, hxy.2.1⟩
  loopless := by
    intro x hxx
    exact (blueGraph G c).loopless x hxx.1

/-- Vertices in the quiescent component of `root`, in canonical `Fin` order. -/
noncomputable def quiescentComponent (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) (root : Fin G.n) :
    List (Fin G.n) := by
  classical
  exact (List.ofFn fun v : Fin G.n => v).filter fun v =>
    decide ((quiescentGraph G c omega).Reachable root v)

/-- An active vertex touches the quiescent component of `root` by a blue edge. -/
def BoundaryWitness (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (root attach : Fin G.n) : Prop :=
  ∃ z : Fin G.n,
    (quiescentGraph G c omega).Reachable root z ∧
      blueb G c z.1 attach.1 = true

/-- Raw finite data for one Pattern-5 source-owner incidence. -/
structure TerminalData (G : GraphData) where
  sourceX : Fin G.n
  sourceY : Fin G.n
  half : Fin 2
  owner : Fin G.n
  attachX : Fin G.n
  attachY : Fin G.n
deriving Repr, DecidableEq

namespace TerminalData

/-- The component union switched by the Pattern-5 certificate. -/
noncomputable def switchVertices (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (T : TerminalData G) : List (Fin G.n) := by
  classical
  exact ((quiescentComponent G c omega T.sourceX) ++
    (quiescentComponent G c omega T.sourceY)).dedup

/-- Literal vertex list supplied to the existing max-cut switch API. -/
noncomputable def switchSet (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (T : TerminalData G) : List Nat :=
  (T.switchVertices G c omega).map Fin.val

/-- The decidable Pattern-5 predicate before conversion to the named checked
proof object.  Its conjuncts match the thirteen fields below. -/
def Valid (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (T : TerminalData G) : Prop :=
  T.sourceX ≠ T.sourceY ∧
    pairCount omega T.sourceX.1 T.sourceY.1 = 0 ∧
    ¬ActiveOwner G c omega T.sourceX ∧
    ¬ActiveOwner G c omega T.sourceY ∧
    ActiveOwner G c omega T.owner ∧
    ActiveOwner G c omega T.attachX ∧
    ActiveOwner G c omega T.attachY ∧
    BoundaryWitness G c omega T.sourceX T.attachX ∧
    BoundaryWitness G c omega T.sourceY T.attachY ∧
    0 < pairCount omega T.owner.1 T.attachX.1 ∧
    0 < pairCount omega T.owner.1 T.attachY.1 ∧
    (activeGraph G c omega).Reachable T.owner T.attachX ∧
    (activeGraph G c omega).Reachable T.owner T.attachY

noncomputable instance validDecidable (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads)
    (T : TerminalData G) : Decidable (T.Valid G c omega) :=
  Classical.propDecidable _

end TerminalData

end QuiescentAttachment

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange
open QuiescentAttachment

/-- Named proof object for the thirteen checked Pattern-5 facts. -/
structure CheckedQuiescentAttachmentBaseTerminal
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (T : TerminalData G) : Prop where
  source_distinct : T.sourceX ≠ T.sourceY
  source_free : pairCount omega T.sourceX.1 T.sourceY.1 = 0
  sourceX_quiescent : ¬ActiveOwner G c omega T.sourceX
  sourceY_quiescent : ¬ActiveOwner G c omega T.sourceY
  owner_active : ActiveOwner G c omega T.owner
  attachX_active : ActiveOwner G c omega T.attachX
  attachY_active : ActiveOwner G c omega T.attachY
  attachX_boundary : BoundaryWitness G c omega T.sourceX T.attachX
  attachY_boundary : BoundaryWitness G c omega T.sourceY T.attachY
  owner_attachX_companion : 0 < pairCount omega T.owner.1 T.attachX.1
  owner_attachY_companion : 0 < pairCount omega T.owner.1 T.attachY.1
  owner_attachX_component :
    (activeGraph G c omega).Reachable T.owner T.attachX
  owner_attachY_component :
    (activeGraph G c omega).Reachable T.owner T.attachY

/-- Semantic owner-source relation contributed by Pattern 5.  Distinctness and
permanent freeness are already carried by `FreeHalf`. -/
def QuiescentAttachmentOwner
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (owner : Fin G.n) (s : FreeHalf G omega) : Prop :=
  ∃ attachX attachY : Fin G.n,
    ¬ActiveOwner G c omega s.sourceX ∧
    ¬ActiveOwner G c omega s.sourceY ∧
    ActiveOwner G c omega owner ∧
    ActiveOwner G c omega attachX ∧
    ActiveOwner G c omega attachY ∧
    BoundaryWitness G c omega s.sourceX attachX ∧
    BoundaryWitness G c omega s.sourceY attachY ∧
    0 < pairCount omega owner.1 attachX.1 ∧
    0 < pairCount omega owner.1 attachY.1 ∧
    (activeGraph G c omega).Reachable owner attachX ∧
    (activeGraph G c omega).Reachable owner attachY

noncomputable instance quiescentAttachmentOwnerDecidable
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) :
    DecidableRel (QuiescentAttachmentOwner G c omega) :=
  fun _ _ => Classical.propDecidable _

/-- Boolean checker for one quiescent-attachment incidence. -/
noncomputable def checkQuiescentAttachment
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (T : TerminalData G) : Bool :=
  decide (T.Valid G c omega)

theorem checkQuiescentAttachment_eq_true_iff
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (T : TerminalData G) :
    checkQuiescentAttachment G c omega T = true ↔ T.Valid G c omega := by
  classical
  simp [checkQuiescentAttachment]

theorem checked_of_valid
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : T.Valid G c omega) :
    CheckedQuiescentAttachmentBaseTerminal G c omega T := by
  rcases h with
    ⟨hxy, hfree, hxq, hyq, ho, hax, hay, hbx, hby, hcx, hcy, hrx, hry⟩
  exact ⟨hxy, hfree, hxq, hyq, ho, hax, hay, hbx, hby, hcx, hcy, hrx, hry⟩

theorem valid_of_checked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    T.Valid G c omega :=
  ⟨h.source_distinct, h.source_free, h.sourceX_quiescent,
    h.sourceY_quiescent, h.owner_active, h.attachX_active,
    h.attachY_active, h.attachX_boundary, h.attachY_boundary,
    h.owner_attachX_companion, h.owner_attachY_companion,
    h.owner_attachX_component, h.owner_attachY_component⟩

theorem checked_of_checkQuiescentAttachment_eq_true
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : checkQuiescentAttachment G c omega T = true) :
    CheckedQuiescentAttachmentBaseTerminal G c omega T :=
  checked_of_valid
    ((checkQuiescentAttachment_eq_true_iff G c omega T).mp h)

theorem checkQuiescentAttachment_eq_true_of_checked
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    checkQuiescentAttachment G c omega T = true :=
  (checkQuiescentAttachment_eq_true_iff G c omega T).mpr
    (valid_of_checked h)

namespace CheckedQuiescentAttachmentBaseTerminal

/-- The actual global source key: the existing permanently free half type. -/
def term
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    FreeHalf G omega where
  sourceX := T.sourceX
  sourceY := T.sourceY
  half := T.half
  distinct := h.source_distinct
  free := h.source_free

theorem owner_relation
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    QuiescentAttachmentOwner G c omega T.owner h.term := by
  exact ⟨T.attachX, T.attachY, h.sourceX_quiescent,
    h.sourceY_quiescent, h.owner_active, h.attachX_active,
    h.attachY_active, h.attachX_boundary, h.attachY_boundary,
    h.owner_attachX_companion, h.owner_attachY_companion,
    h.owner_attachX_component, h.owner_attachY_component⟩

/-- A Pattern-5 source cannot be a half-zero active-edge reservation because
its first endpoint is quiescent. -/
theorem term_unreserved
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    ¬ScopedReserved G c omega h.term := by
  intro hreserved
  exact h.sourceX_quiescent hreserved.2.2

end CheckedQuiescentAttachmentBaseTerminal

/-- Maximum-cut soundness of the computed component-union switch. -/
theorem switchSet_loss_nonneg
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} (T : TerminalData G)
    (hG : checkGraph G = true) (hmax : IsMaxCut G c) :
    0 ≤ sigma G c (T.switchSet G c omega) :=
  sigmaNonneg_of_badCount_min G c hG hmax.valid hmax.min_bad
    (T.switchSet G c omega)

/-- Full proved local soundness surface.  This stops before the absent typed
bank-incidence adapter. -/
theorem quiescentAttachmentTerminal_sound
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (hG : checkGraph G = true) (hmax : IsMaxCut G c)
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T) :
    QuiescentAttachmentOwner G c omega T.owner h.term ∧
      ¬ScopedReserved G c omega h.term ∧
      0 ≤ sigma G c (T.switchSet G c omega) := by
  exact ⟨h.owner_relation, h.term_unreserved,
    switchSet_loss_nonneg T hG hmax⟩

/-- Explicit frontier for a future matching/typed-bank consumer.  Instantiating
`Accepts` with a production terminal relation requires a proof of this
hypothesis; this module does not silently assume one. -/
def TerminalConsumerSound
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (Accepts : Fin G.n → FreeHalf G omega → List Nat → Prop) : Prop :=
  ∀ (T : TerminalData G)
    (h : CheckedQuiescentAttachmentBaseTerminal G c omega T),
      Accepts T.owner h.term (T.switchSet G c omega)

theorem consumer_accepts_of_check
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    {Accepts : Fin G.n → FreeHalf G omega → List Nat → Prop}
    (hconsumer : TerminalConsumerSound (c := c) omega Accepts)
    {T : TerminalData G}
    (hcheck : checkQuiescentAttachment G c omega T = true) :
    ∃ h : CheckedQuiescentAttachmentBaseTerminal G c omega T,
      Accepts T.owner h.term (T.switchSet G c omega) := by
  let h := checked_of_checkQuiescentAttachment_eq_true hcheck
  exact ⟨h, hconsumer T h⟩

theorem checkQuiescentAttachment_sound
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads} {T : TerminalData G}
    (hG : checkGraph G = true) (hmax : IsMaxCut G c)
    (hcheck : checkQuiescentAttachment G c omega T = true) :
    ∃ h : CheckedQuiescentAttachmentBaseTerminal G c omega T,
      QuiescentAttachmentOwner G c omega T.owner h.term ∧
        ¬ScopedReserved G c omega h.term ∧
        0 ≤ sigma G c (T.switchSet G c omega) := by
  let h := checked_of_checkQuiescentAttachment_eq_true hcheck
  exact ⟨h, quiescentAttachmentTerminal_sound hG hmax h⟩

#print axioms checkQuiescentAttachment_eq_true_iff
#print axioms checked_of_checkQuiescentAttachment_eq_true
#print axioms CheckedQuiescentAttachmentBaseTerminal.owner_relation
#print axioms CheckedQuiescentAttachmentBaseTerminal.term_unreserved
#print axioms switchSet_loss_nonneg
#print axioms quiescentAttachmentTerminal_sound
#print axioms consumer_accepts_of_check
#print axioms checkQuiescentAttachment_sound

end Gamma
end Erdos23Delta0
