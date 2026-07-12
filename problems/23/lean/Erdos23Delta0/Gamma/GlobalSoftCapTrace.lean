import Erdos23Delta0.Gamma.OptimalGroupedCapPartialFlow
import Erdos23Delta0.Gamma.SoftEdgeCapGraphAdapter

/-!
# Graph-facing trace states for the global soft-cap provider

The older sink/rotor trace is built from active-scoped obligations and a
component-coherent matching.  The theorem-of-record instead uses every
global `CollisionHalf`, no coherence constraint, and aggregate capacity two
on each active four-key block.  This file supplies the corresponding exact
positive-defect payload without changing those semantics.
-/

namespace Erdos23Delta0
namespace Gamma
namespace GlobalSoftCapTrace

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open MinimumCollisionGlobalHallReduction
open OptimalGroupedCapPartialFlow
open SoftEdgeCapGraphAdapter

variable {G : GraphData} {c : CutData} {bads : List BadEdgeData}

/-- Pull the caller's real six-family relation onto the exact edge-capped
physical-key partition. -/
abbrev EligibleAt
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads)
    (Eligible : ∀ omega : RowChoice bads,
      CollisionHalf G omega → FreeHalf G omega → Prop)
    (omega : RowChoice bads) :=
  transportEligible hG htri hchecked omega (Eligible omega)

/-- Exact grouped-cap Hall defect of one real row tuple. -/
noncomputable def groupedDefect
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads)
    (Eligible : ∀ omega : RowChoice bads,
      CollisionHalf G omega → FreeHalf G omega → Prop)
    (omega : RowChoice bads) : Nat :=
  hallDefect (EligibleAt hG htri hchecked Eligible omega)

/-- The first coordinate of the accepted lexicographic selector. -/
def collisionCost (omega : RowChoice bads) : Nat :=
  collisionUnits G omega

/-- Collision-minimal first, then grouped-defect-minimal on that face. -/
structure LexMin
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads)
    (Eligible : ∀ omega : RowChoice bads,
      CollisionHalf G omega → FreeHalf G omega → Prop)
    (omega : RowChoice bads) : Prop where
  collision_min : ∀ eta : RowChoice bads,
    collisionCost (G := G) omega ≤ collisionCost (G := G) eta
  defect_min_on_face : ∀ eta : RowChoice bads,
    collisionCost (G := G) eta = collisionCost (G := G) omega →
      groupedDefect hG htri hchecked Eligible omega ≤
        groupedDefect hG htri hchecked Eligible eta

/-- Exact optimal partial flow at one concrete row tuple. -/
abbrev PartialFlowAt
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads)
    (Eligible : ∀ omega : RowChoice bads,
      CollisionHalf G omega → FreeHalf G omega → Prop)
    (omega : RowChoice bads) :=
  OptimalGroupedCapPartialFlow.Flow
    (EligibleAt hG htri hchecked Eligible omega)

/-- One positive-defect state of the global, coherence-free grouped model. -/
structure Payload
    (hG : checkGraph G = true) (htri : TriangleFree G)
    (hchecked : AllBadsChecked G c bads)
    (Eligible : ∀ omega : RowChoice bads,
      CollisionHalf G omega → FreeHalf G omega → Prop) where
  omega : RowChoice bads
  flow : PartialFlowAt hG htri hchecked Eligible omega
  lexMin : LexMin hG htri hchecked Eligible omega
  root : CollisionHalf G omega
  root_unmatched : root ∉ flow.matched

namespace Payload

variable {hG : checkGraph G = true} {htri : TriangleFree G}
variable {hchecked : AllBadsChecked G c bads}
variable {Eligible : ∀ omega : RowChoice bads,
  CollisionHalf G omega → FreeHalf G omega → Prop}

variable (P : Payload hG htri hchecked Eligible)

def collision : Nat :=
  collisionCost (G := G) P.omega

noncomputable def defect : Nat :=
  groupedDefect hG htri hchecked Eligible P.omega

theorem defect_eq_unmatchedCount :
    P.defect = P.flow.unmatchedCount := by
  exact P.flow.unmatchedCount_eq_hallDefect.symm

theorem defect_pos : 0 < P.defect := by
  rw [P.defect_eq_unmatchedCount,
    OptimalGroupedCapPartialFlow.Flow.unmatchedCount]
  apply Nat.sub_pos_iff_lt.mpr
  exact Finset.card_lt_univ_of_notMem P.root_unmatched

theorem collision_min (eta : RowChoice bads) :
    P.collision ≤ collisionCost (G := G) eta :=
  P.lexMin.collision_min eta

theorem defect_min_on_collision_face
    (eta : RowChoice bads)
    (hcollision :
      collisionCost (G := G) eta = P.collision) :
    P.defect ≤ groupedDefect hG htri hchecked Eligible eta :=
  P.lexMin.defect_min_on_face eta hcollision

/-- Whether one actual proof-carrying free half is occupied by this exact
optimal partial flow. -/
def UsesFreeHalf (s : FreeHalf G P.omega) : Prop :=
  P.flow.Uses
    ((edgeCappedKeyEquivFreeHalf hG htri hchecked P.omega).symm s)

/-- Both physical halves over one proof-carrying ordered free base are used
by this exact optimal flow. -/
def BothHalvesUsed (base : FreeBase G P.omega) : Prop :=
  ∀ half : Fin 2,
    P.UsesFreeHalf
      { sourceX := base.sourceX
        sourceY := base.sourceY
        half := half
        distinct := base.distinct
        free := base.free }

def PositiveUnitDefect : Prop :=
  P.defect = 1

theorem flow_positiveUnitDefect_iff :
    P.flow.PositiveUnitDefect ↔ P.PositiveUnitDefect := by
  change P.flow.unmatchedCount = 1 ↔ P.defect = 1
  rw [P.defect_eq_unmatchedCount]

end Payload

#print axioms Payload.defect_eq_unmatchedCount
#print axioms Payload.defect_pos
#print axioms Payload.flow_positiveUnitDefect_iff

end GlobalSoftCapTrace
end Gamma
end Erdos23Delta0
