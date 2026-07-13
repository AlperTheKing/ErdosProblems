import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-!
Temporary Pattern-5 soundness kernels.  This file deliberately does not claim
that a selector with a complete five-pattern matching exists.
-/

namespace CodexTmp.CommonBlueUniversal.Pattern5

open Set
open Erdos23Delta0
open Erdos23Delta0.CertGraph
open Erdos23Delta0.Gamma
open Erdos23Delta0.Gamma.MinimumDemandRowSelection
open Erdos23Delta0.Gamma.CanonicalCollisionHall
open Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-- The owner shore is starved when no quiescent-component boundary vertex is
an eligible active-component row companion of an owner in the shore. -/
def QuiescentBoundaryStarved {Vertex Component Owner : Type*}
    (boundary : Component -> Vertex -> Prop)
    (companion : Owner -> Vertex -> Prop) (shore : Set Owner) : Prop :=
  ∀ component owner, owner ∈ shore ->
    ∀ vertex, boundary component vertex -> ¬companion owner vertex

/-- Abstract owner reach supplied by Pattern 5's two attachment witnesses. -/
def QuiescentAttachmentReach {Vertex Component Owner : Type*}
    (boundary : Component -> Vertex -> Prop)
    (companion : Owner -> Vertex -> Prop) (owner : Owner) : Prop :=
  ∃ left right a b,
    boundary left a ∧ boundary right b ∧
      companion owner a ∧ companion owner b

/-- Boundary starvation kills Pattern-5 reach for every owner in the shore. -/
theorem quiescentAttachmentReach_false_of_starved
    {Vertex Component Owner : Type*}
    {boundary : Component -> Vertex -> Prop}
    {companion : Owner -> Vertex -> Prop} {shore : Set Owner}
    (hstarved : QuiescentBoundaryStarved boundary companion shore)
    {owner : Owner} (howner : owner ∈ shore) :
    ¬QuiescentAttachmentReach boundary companion owner := by
  rintro ⟨left, _right, a, _b, hboundary, _hboundaryRight,
    hcompanion, _hcompanionRight⟩
  exact hstarved left owner howner a hboundary hcompanion

/-- A Pattern-5 source outside the active scope cannot be consumed by the
active-source half-zero reservation. -/
theorem quiescentSource_not_scopedReserved
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (source : FreeHalf G omega)
    (hquiescent : ¬ActiveOwner G c omega source.sourceX) :
    ¬ScopedReserved G c omega source := by
  intro hreserved
  exact hquiescent hreserved.2.2

/-- Switching any union of quiescent components has nonnegative exact loss at
a certified maximum cut.  Component structure is irrelevant to this step. -/
theorem quiescentUnion_sigma_nonneg
    (G : GraphData) (c : CutData) (switchSet : List Nat)
    (hlen : c.side.length = G.n) (hG : checkGraph G = true)
    (hflipLength : (flipCut c switchSet).side.length = G.n)
    (hmax : badCount G c <= badCount G (flipCut c switchSet)) :
    0 <= sigma G c switchSet := by
  exact sigma_nonneg_of_isMaxCut G c switchSet hlen hG hflipLength hmax

end CodexTmp.CommonBlueUniversal.Pattern5

#print axioms CodexTmp.CommonBlueUniversal.Pattern5.quiescentAttachmentReach_false_of_starved
#print axioms CodexTmp.CommonBlueUniversal.Pattern5.quiescentSource_not_scopedReserved
#print axioms CodexTmp.CommonBlueUniversal.Pattern5.quiescentUnion_sigma_nonneg
