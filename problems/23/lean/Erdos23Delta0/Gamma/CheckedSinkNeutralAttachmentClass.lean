import Erdos23Delta0.Gamma.CanonicalCollisionGraphSelection
import Erdos23Delta0.Gamma.LiveDetourEndpointSource

/-!
# Checked sink-neutral attachment classes

This is the production-typed R37/R38 finite interface.  Its states use the
literal `CollisionDefectGraphAdapter` row choices, active collision
obligations, source relation, and honest collision defect.  A trace payload
stores an optimal coherent partial matching and the least unmatched root; a
trace state adds the current alternating cursor.

The neutral graph has exactly the three archived edge forms:

* following a matched physical source half;
* following a base-key component conflict;
* replacing one selected row by a checked live two-edge detour while staying
  among global defect minimizers.

`SinkNeutralAttachmentClassData.check` reflects the finite sink-SCC
conditions.  This module does **not** assert that a class has positive
exposure, that it has an augmentation, or that no positive-defect class
exists.  Those are the missing graph theorems consumed downstream.
-/

namespace Erdos23Delta0
namespace Gamma

open CertGraph
open MinimumDemandRowSelection
open ActiveScopedMinimumExchange
open CheckedCollisionDefectTrade
open CanonicalCollisionProgress
open CollisionDefectGraphAdapter
open CanonicalCollisionGraphSelection
open LiveDetourEndpointSource

attribute [local instance] Classical.propDecidable

noncomputable section

/-- The existing D05 graph-facing defect engine, named locally for the
sink/rotor interface. -/
abbrev AttachmentDefectData
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) :=
  defectData G c bads R

/-- A deterministic audit order on the fixed production obligation carrier.
It is used only to make the unmatched root canonical inside one matching. -/
noncomputable def collisionObligationAuditCode
    (G : GraphData) (bads : List BadEdgeData) :
    CollisionObligation G bads → Nat :=
  fun d => (Fintype.equivFin (CollisionObligation G bads) d).1

/-- One defect-minimal row tuple with an exact optimal coherent matching and
its least unmatched obligation.  Consequently these payloads exist only at
positive defect. -/
structure CollisionTracePayload
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) where
  omega : RowChoice bads
  matching : CoherentPartialMatching (AttachmentDefectData G c bads R) omega
  matching_optimal :
    (AttachmentDefectData G c bads R).collisionDefect omega =
      matching.unmatchedCount
  defect_minimal : ∀ eta : RowChoice bads,
    (AttachmentDefectData G c bads R).collisionDefect omega ≤
      (AttachmentDefectData G c bads R).collisionDefect eta
  root : CollisionObligation G bads
  root_unmatched : root ∈ matching.unmatched
  root_least : ∀ d : CollisionObligation G bads,
    d ∈ matching.unmatched →
      collisionObligationAuditCode G bads root ≤
        collisionObligationAuditCode G bads d

namespace CollisionTracePayload

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}

/-- The exact positive defect carried by a trace payload. -/
def defect (P : CollisionTracePayload G c bads R) : Nat :=
  (AttachmentDefectData G c bads R).collisionDefect P.omega

theorem defect_eq_unmatchedCount
    (P : CollisionTracePayload G c bads R) :
    P.defect = P.matching.unmatchedCount :=
  P.matching_optimal

theorem defect_pos (P : CollisionTracePayload G c bads R) :
    0 < P.defect := by
  rw [P.defect_eq_unmatchedCount,
    CoherentPartialMatching.unmatchedCount]
  exact Finset.card_pos.mpr ⟨P.root, P.root_unmatched⟩

theorem root_mem_obligations (P : CollisionTracePayload G c bads R) :
    P.root ∈ (AttachmentDefectData G c bads R).obligations P.omega := by
  exact (Finset.mem_sdiff.mp P.root_unmatched).1

end CollisionTracePayload

/-- One occurrence-level alternating state.  The cursor may be matched; its
root remains the least unmatched obligation of the fixed optimal matching. -/
structure CollisionTraceState
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) where
  payload : CollisionTracePayload G c bads R
  cursor : CollisionObligation G bads
  cursor_mem :
    cursor ∈ (AttachmentDefectData G c bads R).obligations payload.omega
  cursor_component :
    (AttachmentDefectData G c bads R).component payload.omega cursor =
      (AttachmentDefectData G c bads R).component payload.omega payload.root

namespace CollisionTraceState

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}

abbrev omega (S : CollisionTraceState G c bads R) : RowChoice bads :=
  S.payload.omega

abbrev matching (S : CollisionTraceState G c bads R) :
    CoherentPartialMatching (AttachmentDefectData G c bads R) S.omega :=
  S.payload.matching

def defect (S : CollisionTraceState G c bads R) : Nat :=
  S.payload.defect

theorem defect_pos (S : CollisionTraceState G c bads R) :
    0 < S.defect :=
  S.payload.defect_pos

/-- Any two production trace states carry the same global minimum defect. -/
theorem defect_eq (S T : CollisionTraceState G c bads R) :
    S.defect = T.defect := by
  apply Nat.le_antisymm
  · exact S.payload.defect_minimal T.omega
  · exact T.payload.defect_minimal S.omega

end CollisionTraceState

/-- Follow a concrete source half used by the current cursor to the matched
obligation occupying that same physical half.  The row tuple, optimal
matching, and least unmatched root are unchanged. -/
structure CheckedMatchedSourceStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) where
  payload_eq : T.payload = S.payload
  source : SourceBase G × Fin 2
  source_realized :
    (AttachmentDefectData G c bads R).sourceRealized
      S.omega S.cursor source
  target : {d // d ∈ S.matching.matched}
  target_uses_source : S.matching.assign target = source
  target_cursor : T.cursor = target.1

namespace CheckedMatchedSourceStep

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}
  {S T : CollisionTraceState G c bads R}

theorem omega_eq (E : CheckedMatchedSourceStep S T) :
    T.omega = S.omega :=
  congrArg CollisionTracePayload.omega E.payload_eq

theorem defect_eq (E : CheckedMatchedSourceStep S T) :
    T.defect = S.defect := by
  rw [CollisionTraceState.defect, CollisionTraceState.defect,
    E.payload_eq]

theorem target_mem_matching (E : CheckedMatchedSourceStep S T) :
    E.target.1 ∈ S.matching.matched :=
  E.target.2

end CheckedMatchedSourceStep

/-- Follow a source whose base key is already owned by a different active
component.  The matched target may occupy either half of that base. -/
structure CheckedBaseConflictStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) where
  payload_eq : T.payload = S.payload
  source : SourceBase G × Fin 2
  source_realized :
    (AttachmentDefectData G c bads R).sourceRealized
      S.omega S.cursor source
  target : {d // d ∈ S.matching.matched}
  same_base : (S.matching.assign target).1 = source.1
  different_component :
    (AttachmentDefectData G c bads R).component S.omega target.1 ≠
      (AttachmentDefectData G c bads R).component S.omega S.cursor
  target_cursor : T.cursor = target.1

namespace CheckedBaseConflictStep

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}
  {S T : CollisionTraceState G c bads R}

theorem omega_eq (E : CheckedBaseConflictStep S T) :
    T.omega = S.omega :=
  congrArg CollisionTracePayload.omega E.payload_eq

theorem defect_eq (E : CheckedBaseConflictStep S T) :
    T.defect = S.defect := by
  rw [CollisionTraceState.defect, CollisionTraceState.defect,
    E.payload_eq]

theorem target_mem_matching (E : CheckedBaseConflictStep S T) :
    E.target.1 ∈ S.matching.matched :=
  E.target.2

end CheckedBaseConflictStep

/-- A production live R37 detour: one selected row
`a-x-m-y-b` is replaced by `a-x-v-y-b`, with `x-v` active and
`v-y` already in selected support.  The target payload independently carries
its own exact optimal matching. -/
structure CheckedTwoEdgeDetour
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) where
  index : Fin bads.length
  replacement : Fin (bads.get index).rows.length
  a : Fin G.n
  x : Fin G.n
  m : Fin G.n
  y : Fin G.n
  b : Fin G.n
  v : Fin G.n
  geometry : LiveDetourData G c S.omega index replacement a x m y b v
  active_left : normEdge x.1 v.1 ∈ activeEdges G c S.omega
  support_right : normEdge v.1 y.1 ∈ selectedSupport S.omega
  target_omega : T.omega = geometry.postChoice

namespace CheckedTwoEdgeDetour

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}
  {S T : CollisionTraceState G c bads R}

theorem defect_eq (_E : CheckedTwoEdgeDetour S T) :
    T.defect = S.defect :=
  CollisionTraceState.defect_eq T S


end CheckedTwoEdgeDetour

/-- The complete neutral attachment edge relation archived in R37/R38. -/
inductive CheckedNeutralAttachmentStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads} :
    CollisionTraceState G c bads R →
      CollisionTraceState G c bads R → Type
  | matchedSource {S T} (cert : CheckedMatchedSourceStep S T) :
      CheckedNeutralAttachmentStep S T
  | baseConflict {S T} (cert : CheckedBaseConflictStep S T) :
      CheckedNeutralAttachmentStep S T
  | equalDefectDetour {S T} (cert : CheckedTwoEdgeDetour S T) :
      CheckedNeutralAttachmentStep S T

namespace CheckedNeutralAttachmentStep

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}
  {S T : CollisionTraceState G c bads R}

theorem defect_eq (E : CheckedNeutralAttachmentStep S T) :
    T.defect = S.defect := by
  cases E with
  | matchedSource cert => exact cert.defect_eq
  | baseConflict cert => exact cert.defect_eq
  | equalDefectDetour cert => exact cert.defect_eq

end CheckedNeutralAttachmentStep

/-- Reflect the matched-source edge predicate. -/
noncomputable def checkMatchedSourceStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) : Bool := by
  classical
  exact decide (Nonempty (CheckedMatchedSourceStep S T))

theorem checkMatchedSourceStep_eq_true_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) :
    checkMatchedSourceStep S T = true ↔
      Nonempty (CheckedMatchedSourceStep S T) := by
  classical
  simp [checkMatchedSourceStep]

/-- Reflect the base-conflict edge predicate. -/
noncomputable def checkBaseConflictStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) : Bool := by
  classical
  exact decide (Nonempty (CheckedBaseConflictStep S T))

theorem checkBaseConflictStep_eq_true_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) :
    checkBaseConflictStep S T = true ↔
      Nonempty (CheckedBaseConflictStep S T) := by
  classical
  simp [checkBaseConflictStep]

/-- Reflect the equal-defect live-detour edge predicate. -/
noncomputable def checkTwoEdgeDetour
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) : Bool := by
  classical
  exact decide (Nonempty (CheckedTwoEdgeDetour S T))

theorem checkTwoEdgeDetour_eq_true_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) :
    checkTwoEdgeDetour S T = true ↔
      Nonempty (CheckedTwoEdgeDetour S T) := by
  classical
  simp [checkTwoEdgeDetour]

/-- Reflect the union of the three neutral edge kinds. -/
noncomputable def checkNeutralAttachmentStep
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) : Bool := by
  classical
  exact decide (Nonempty (CheckedNeutralAttachmentStep S T))

theorem checkNeutralAttachmentStep_eq_true_iff
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {R : NoCommonBlueSourceRelations G c bads}
    (S T : CollisionTraceState G c bads R) :
    checkNeutralAttachmentStep S T = true ↔
      Nonempty (CheckedNeutralAttachmentStep S T) := by
  classical
  simp [checkNeutralAttachmentStep]

/-- Serialized finite candidate for one sink SCC.  `edge` is required by the
checker to be exactly the production neutral-step relation restricted to the
listed states. -/
structure SinkNeutralAttachmentClassData
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) where
  stateCount : Nat
  state : Fin stateCount → CollisionTraceState G c bads R
  edge : Fin stateCount → Fin stateCount → Bool
  defect : Nat

namespace SinkNeutralAttachmentClassData

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}

variable (D : SinkNeutralAttachmentClassData G c bads R)

/-- Reachability in the serialized directed graph. -/
def Reachable (i j : Fin D.stateCount) : Prop :=
  Relation.ReflTransGen (fun x y => D.edge x y = true) i j

/-- The exact proposition reflected by `check`.  Sink closure quantifies over
the full production neutral relation, not merely the marked adjacency table. -/
structure Checked : Prop where
  nonempty : 0 < D.stateCount
  state_injective : Function.Injective D.state
  edge_exact : ∀ i j,
    D.edge i j = true ↔
      Nonempty (CheckedNeutralAttachmentStep (D.state i) (D.state j))
  strongly_connected : ∀ i j, D.Reachable i j
  sink : ∀ i (T : CollisionTraceState G c bads R),
    Nonempty (CheckedNeutralAttachmentStep (D.state i) T) →
      ∃ j, T = D.state j
  common_defect : ∀ i, (D.state i).defect = D.defect

/-- Kernel-decidable checker for a fixed serialized candidate.  It makes no
existence claim and invokes no native evaluator. -/
noncomputable def check : Bool := by
  classical
  exact decide D.Checked

theorem check_eq_true_iff : D.check = true ↔ D.Checked := by
  classical
  simp [check]

/-- Semantic view exported to downstream M2/M3 consumers. -/
structure Sound : Prop where
  nonempty : 0 < D.stateCount
  state_injective : Function.Injective D.state
  edge_iff_neutral : ∀ i j,
    D.edge i j = true ↔
      Nonempty (CheckedNeutralAttachmentStep (D.state i) (D.state j))
  strongly_connected : ∀ i j, D.Reachable i j
  closed_under_neutral_steps :
    ∀ i (T : CollisionTraceState G c bads R),
      Nonempty (CheckedNeutralAttachmentStep (D.state i) T) →
        ∃ j, T = D.state j
  common_defect : ∀ i, (D.state i).defect = D.defect

theorem sound_of_check_eq_true (hcheck : D.check = true) : D.Sound := by
  have h := D.check_eq_true_iff.mp hcheck
  exact
    { nonempty := h.nonempty
      state_injective := h.state_injective
      edge_iff_neutral := h.edge_exact
      strongly_connected := h.strongly_connected
      closed_under_neutral_steps := h.sink
      common_defect := h.common_defect }

theorem edge_preserves_defect (h : D.Sound) {i j : Fin D.stateCount}
    (hedge : D.edge i j = true) :
    (D.state j).defect = (D.state i).defect := by
  obtain ⟨step⟩ := (h.edge_iff_neutral i j).mp hedge
  exact step.defect_eq

theorem neutral_successor_mem (h : D.Sound) (i : Fin D.stateCount)
    (T : CollisionTraceState G c bads R)
    (hstep : Nonempty (CheckedNeutralAttachmentStep (D.state i) T)) :
    ∃ j, T = D.state j :=
  h.closed_under_neutral_steps i T hstep

end SinkNeutralAttachmentClassData

/-- A checked nonempty sink SCC of the production neutral attachment graph. -/
structure CheckedSinkNeutralAttachmentClass
    (G : GraphData) (c : CutData) (bads : List BadEdgeData)
    (R : NoCommonBlueSourceRelations G c bads) where
  data : SinkNeutralAttachmentClassData G c bads R
  check_eq_true : data.check = true

namespace CheckedSinkNeutralAttachmentClass

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}
  {R : NoCommonBlueSourceRelations G c bads}

variable (C : CheckedSinkNeutralAttachmentClass G c bads R)

def sound : C.data.Sound :=
  C.data.sound_of_check_eq_true C.check_eq_true

abbrev stateCount : Nat := C.data.stateCount

abbrev state (i : Fin C.stateCount) : CollisionTraceState G c bads R :=
  C.data.state i

abbrev defect : Nat := C.data.defect

theorem stateCount_pos : 0 < C.stateCount :=
  C.sound.nonempty

theorem state_defect_eq (i : Fin C.stateCount) :
    (C.state i).defect = C.defect :=
  C.sound.common_defect i

theorem defect_pos : 0 < C.defect := by
  let i : Fin C.stateCount := ⟨0, C.stateCount_pos⟩
  rw [← C.state_defect_eq i]
  exact (C.state i).defect_pos

theorem edge_iff_neutral (i j : Fin C.stateCount) :
    C.data.edge i j = true ↔
      Nonempty (CheckedNeutralAttachmentStep (C.state i) (C.state j)) :=
  C.sound.edge_iff_neutral i j

theorem stronglyConnected (i j : Fin C.stateCount) :
    C.data.Reachable i j :=
  C.sound.strongly_connected i j

theorem sink_closed (i : Fin C.stateCount)
    (T : CollisionTraceState G c bads R)
    (hstep : Nonempty (CheckedNeutralAttachmentStep (C.state i) T)) :
    ∃ j, T = C.state j :=
  C.sound.closed_under_neutral_steps i T hstep

/-- The exact class-level augmentation target.  No inhabitant is constructed
in M1; the missing real graph theorem must provide one. -/
structure Augmentation : Type where
  stateIndex : Fin C.stateCount
  cert : CheckedCoherentAugmentation
    (AttachmentDefectData G c bads R) (C.state stateIndex).omega

end CheckedSinkNeutralAttachmentClass

#print axioms CollisionTracePayload.defect_pos
#print axioms CollisionTraceState.defect_eq
#print axioms CheckedMatchedSourceStep.defect_eq
#print axioms CheckedBaseConflictStep.defect_eq
#print axioms CheckedTwoEdgeDetour.defect_eq
#print axioms CheckedNeutralAttachmentStep.defect_eq
#print axioms checkNeutralAttachmentStep_eq_true_iff
#print axioms SinkNeutralAttachmentClassData.sound_of_check_eq_true
#print axioms SinkNeutralAttachmentClassData.edge_preserves_defect
#print axioms CheckedSinkNeutralAttachmentClass.defect_pos

end

end Gamma
end Erdos23Delta0
