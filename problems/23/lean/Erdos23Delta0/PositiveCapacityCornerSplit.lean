import Erdos23Delta0.NoMixedCornerPortComponent

/-!
# Capacity-sensitive corner-component split

The all-sink coupling relation in `NoMixedCornerPortComponent` is stronger
than deficiency additivity requires.  Two child shores may share legal sinks
of zero capacity: their common-neighborhood capacity is still zero, so
`properClosedBankSplitOfOverlapCapZero` applies.

This module rebuilds the same component partition after restricting legal
sink coupling to sinks of strictly positive capacity.  It proves that a
no-mixed-component certificate for this smaller graph yields a proper closed
bank split.  The only open geometric statement left by this reduction is the
real-extractor alternative for a mixed *positive-capacity* component.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- The same LP with legal arcs restricted to positive-capacity sinks. -/
noncomputable def positiveCapacityLP (I : BankedWallLP) : BankedWallLP where
  Cut := I.Cut
  Atom := I.Atom
  Short := I.Short
  Port := I.Port
  Sink := I.Sink
  cutFintype := I.cutFintype
  atomFintype := I.atomFintype
  shortFintype := I.shortFintype
  portFintype := I.portFintype
  sinkFintype := I.sinkFintype
  cov := I.cov
  useShort := I.useShort
  cutPort := I.cutPort
  legal := fun p s => I.legal p s ∧ 0 < I.cap s
  legalDecidable := by
    classical
    intro p s
    infer_instance
  cap := I.cap

@[simp] theorem positiveCapacityLP_legal (p : I.Port) (s : I.Sink) :
    (positiveCapacityLP I).legal p s ↔ I.legal p s ∧ 0 < I.cap s :=
  Iff.rfl

@[simp] theorem positiveCapacityLP_cap (s : I.Sink) :
    (positiveCapacityLP I).cap s = I.cap s :=
  rfl

/-- Parent ports in a positive-capacity coupling component meeting `seedR`. -/
noncomputable def positiveRightPorts
    (primitive : I.Port → I.Port → Prop)
    (parent seedR : Finset I.Port) : Finset I.Port :=
  rightPorts (I := positiveCapacityLP I) primitive parent seedR

/-- All remaining parent ports. -/
noncomputable def positiveLeftPorts
    (primitive : I.Port → I.Port → Prop)
    (parent seedR : Finset I.Port) : Finset I.Port :=
  leftPorts (I := positiveCapacityLP I) primitive parent seedR

/-- No positive-capacity coupling component meets both corner seeds. -/
def NoMixedPositiveCapacityComponent
    (I : BankedWallLP) (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port) : Prop :=
  NoMixedCornerPortComponent (positiveCapacityLP I) primitive parent seedL seedR

theorem positiveRightPorts_subset_parent
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    positiveRightPorts (I := I) primitive parent seedR ⊆ parent :=
  rightPorts_subset_parent (I := positiveCapacityLP I) primitive parent seedR

theorem positiveLeftPorts_subset_parent
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    positiveLeftPorts (I := I) primitive parent seedR ⊆ parent :=
  leftPorts_subset_parent (I := positiveCapacityLP I) primitive parent seedR

theorem positiveLeft_right_disjoint
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    Disjoint (positiveLeftPorts (I := I) primitive parent seedR)
      (positiveRightPorts (I := I) primitive parent seedR) :=
  left_right_disjoint (I := positiveCapacityLP I) primitive parent seedR

theorem positiveLeft_union_right
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    positiveLeftPorts (I := I) primitive parent seedR ∪
      positiveRightPorts (I := I) primitive parent seedR = parent :=
  left_union_right (I := positiveCapacityLP I) primitive parent seedR

theorem positiveRightPorts_ssubset_parent
    (primitive : I.Port → I.Port → Prop)
    {parent seedR : Finset I.Port} (hseedRne : seedR.Nonempty)
    (hseedR : seedR ⊆ parent) :
    positiveLeftPorts (I := I) primitive parent seedR ⊂ parent :=
  leftPorts_ssubset_parent (I := positiveCapacityLP I)
    primitive hseedRne hseedR

theorem positiveLeftSeed_forces_rightProper
    (primitive : I.Port → I.Port → Prop)
    {parent seedL seedR : Finset I.Port} (hseedLne : seedL.Nonempty)
    (hseedL : seedL ⊆ parent)
    (hNMC : NoMixedPositiveCapacityComponent I primitive parent seedL seedR) :
    positiveRightPorts (I := I) primitive parent seedR ⊂ parent :=
  rightPorts_ssubset_parent (I := positiveCapacityLP I)
    primitive hseedLne hseedL hNMC

theorem positiveRightPorts_primitiveBlockSaturated
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    PrimitiveBlockSaturatedIn primitive parent
      (positiveRightPorts (I := I) primitive parent seedR) := by
  intro p q hp hq hpq
  apply rightPorts_closed_under_coupled
    (I := positiveCapacityLP I) primitive hp
  exact ⟨positiveRightPorts_subset_parent primitive parent seedR hp,
    hq, Or.inl hpq⟩

theorem positiveLeftPorts_primitiveBlockSaturated
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port) :
    PrimitiveBlockSaturatedIn primitive parent
      (positiveLeftPorts (I := I) primitive parent seedR) := by
  intro p q hp hq hpq
  apply leftPorts_closed_under_coupled
    (I := positiveCapacityLP I) primitive hp
  exact ⟨positiveLeftPorts_subset_parent primitive parent seedR hp,
    hq, Or.inl hpq⟩

theorem positiveRightPorts_closed
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port)
    (hblocks : PrimitiveBlockClosureExactOn Q primitive parent) :
    ClosedPortSet Q (positiveRightPorts (I := I) primitive parent seedR) :=
  (hblocks _ (positiveRightPorts_subset_parent primitive parent seedR)).2
    (positiveRightPorts_primitiveBlockSaturated primitive parent seedR)

theorem positiveLeftPorts_closed
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port)
    (hblocks : PrimitiveBlockClosureExactOn Q primitive parent) :
    ClosedPortSet Q (positiveLeftPorts (I := I) primitive parent seedR) :=
  (hblocks _ (positiveLeftPorts_subset_parent primitive parent seedR)).2
    (positiveLeftPorts_primitiveBlockSaturated primitive parent seedR)

/-- A sink shared by the two positive-component shores cannot have positive
capacity; nonnegativity therefore makes its capacity exactly zero. -/
theorem sharedSink_cap_eq_zero
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port)
    (hcap : ∀ s : I.Sink, 0 ≤ I.cap s)
    {s : I.Sink}
    (hs : s ∈ legalNbr I (positiveLeftPorts (I := I) primitive parent seedR) ∩
      legalNbr I (positiveRightPorts (I := I) primitive parent seedR)) :
    I.cap s = 0 := by
  classical
  rcases Finset.mem_inter.mp hs with ⟨hsL, hsR⟩
  rcases mem_legalNbr.mp hsL with ⟨p, hpL, hps⟩
  rcases mem_legalNbr.mp hsR with ⟨q, hqR, hqs⟩
  have hnotpos : ¬0 < I.cap s := by
    intro hpos
    have hqp : Coupled (positiveCapacityLP I) primitive parent q p :=
      ⟨positiveRightPorts_subset_parent primitive parent seedR hqR,
        positiveLeftPorts_subset_parent primitive parent seedR hpL,
        Or.inr ⟨s, ⟨hqs, hpos⟩, ⟨hps, hpos⟩⟩⟩
    have hpR := rightPorts_closed_under_coupled
      (I := positiveCapacityLP I) primitive hqR hqp
    exact (mem_leftPorts (I := positiveCapacityLP I) primitive).mp hpL |>.2 hpR
  exact le_antisymm (not_lt.mp hnotpos) (hcap s)

theorem positiveComponent_overlap_cap_zero
    (primitive : I.Port → I.Port → Prop) (parent seedR : Finset I.Port)
    (hcap : ∀ s : I.Sink, 0 ≤ I.cap s) :
    capQ I
      (legalNbr I (positiveLeftPorts (I := I) primitive parent seedR) ∩
        legalNbr I (positiveRightPorts (I := I) primitive parent seedR)) = 0 := by
  classical
  unfold capQ
  apply Finset.sum_eq_zero
  intro s hs
  exact sharedSink_cap_eq_zero primitive parent seedR hcap hs

/-- Capacity-sensitive replacement for the all-sink NMC split theorem. -/
noncomputable def properClosedBankSplitOfNoMixedPositiveCapacityComponent
    (L : I.Port → ℚ) (primitive : I.Port → I.Port → Prop)
    (parent seedL seedR : Finset I.Port)
    (hseedLne : seedL.Nonempty) (hseedRne : seedR.Nonempty)
    (hseedL : seedL ⊆ parent) (hseedR : seedR ⊆ parent)
    (hNMC : NoMixedPositiveCapacityComponent I primitive parent seedL seedR)
    (hblocks : PrimitiveBlockClosureExactOn Q primitive parent)
    (hcap : ∀ s : I.Sink, 0 ≤ I.cap s) :
    ProperClosedBankSplit Q L parent :=
  properClosedBankSplitOfOverlapCapZero L
    (positiveLeft_right_disjoint primitive parent seedR)
    (positiveLeft_union_right primitive parent seedR)
    (positiveLeftPorts_closed primitive parent seedR hblocks)
    (positiveRightPorts_closed primitive parent seedR hblocks)
    (positiveRightPorts_ssubset_parent primitive hseedRne hseedR)
    (positiveLeftSeed_forces_rightProper primitive hseedLne hseedL hNMC)
    (positiveComponent_overlap_cap_zero primitive parent seedR hcap)

#print axioms sharedSink_cap_eq_zero
#print axioms positiveComponent_overlap_cap_zero
#print axioms properClosedBankSplitOfNoMixedPositiveCapacityComponent

end ClosedShore
end Wall
end Erdos23Delta0
