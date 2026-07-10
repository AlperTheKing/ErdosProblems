import Erdos23Delta0.BankedWallW3Skeleton

/-!
# Bank-prime closed-shore replacement for root locality

The existing W3 route asks broad `PositiveRootBlockClosedExtraction` to turn a
minimal closed Hall deficiency into a unique legal root.  This module records
the weaker split-or-root alternative suggested by the bank-prime argument.

A positive closed shore may fail to be root-local, provided it has two proper
closed children whose inherited-bank defects dominate the parent.  Such a
split is impossible for the minimal closed deficient shore already returned
by `ClosedWeightedHallCompleteness`; both child defects are nonpositive there.
Consequently the root branch suffices for the unchanged closed-cut exchange
identity.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open scoped BigOperators
open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- A proper bank-conserving decomposition of one closed port shore.  Concrete
providers must derive `defect_le` from the checked closed-cut exchange and W1;
the children carry inherited bank through their own `deficiencyQ` values. -/
structure ProperClosedBankSplit (Q : AbstractEscapeQuotient I)
    (L : I.Port → ℚ) (parent : Finset I.Port) where
  left : Finset I.Port
  right : Finset I.Port
  left_closed : ClosedPortSet Q left
  right_closed : ClosedPortSet Q right
  left_proper : left ⊂ parent
  right_proper : right ⊂ parent
  defect_le :
    deficiencyQ I L parent ≤ deficiencyQ I L left + deficiencyQ I L right

/-- Load-specific graph-side classifier required by one W3 application.
Every positive exposed closed shore for this particular almost-squeeze load
either splits with inherited bank, or every legal-component partition already
has one root. -/
def ClosedPositiveSplitOrRootAt (Q : AbstractEscapeQuotient I)
    (L : I.Port → ℚ) : Prop :=
  ∀ U : Finset Q.QComp,
    Q.fullClosure U = U →
      HallDeficient I L (Q.exposedPorts U) →
        Nonempty (ProperClosedBankSplit Q L (Q.exposedPorts U)) ∨
          (∀ D : LegalComponentPartition I (Q.exposedPorts U),
            Fintype.card D.K = 1)

/-- Uniform convenience form.  The W3 conclusion below needs only the weaker
load-specific classifier at `Z.portLoad`. -/
def ClosedPositiveSplitOrRoot (Q : AbstractEscapeQuotient I) : Prop :=
  ∀ L : I.Port → ℚ, ClosedPositiveSplitOrRootAt Q L

/-- A proper bank-conserving split cannot occur inside an inclusion-minimal
closed deficient shore. -/
theorem no_properClosedBankSplit_of_minimal
    (L : I.Port → ℚ) (P : Finset I.Port)
    (hMin : MinimalClosedDeficient Q L P)
    (S : ProperClosedBankSplit Q L P) : False := by
  obtain ⟨_hclosed, hpos, hminimal⟩ := hMin
  have hleft : deficiencyQ I L S.left ≤ 0 :=
    hminimal S.left S.left_closed S.left_proper
  have hright : deficiencyQ I L S.right ≤ 0 :=
    hminimal S.right S.right_closed S.right_proper
  exact (not_lt_of_ge (by linarith [S.defect_le])) hpos

/-- The load-specific bank-prime classifier replaces broad root extraction on
the minimal closed deficient shore. -/
theorem minimalClosedDeficient_has_unique_root_of_splitOrRootAt
    (L : I.Port → ℚ) (hClass : ClosedPositiveSplitOrRootAt Q L)
    (U : Finset Q.QComp)
    (hUclosed : Q.fullClosure U = U)
    (hMin : MinimalClosedDeficient Q L (Q.exposedPorts U)) :
    ∀ D : LegalComponentPartition I (Q.exposedPorts U),
      Fintype.card D.K = 1 := by
  rcases hClass U hUclosed hMin.2.1 with hsplit | hroot
  · obtain ⟨S⟩ := hsplit
    exact False.elim (no_properClosedBankSplit_of_minimal L (Q.exposedPorts U) hMin S)
  · exact hroot

theorem minimalClosedDeficient_has_unique_root_of_splitOrRoot
    (hClass : ClosedPositiveSplitOrRoot Q)
    (L : I.Port → ℚ) (U : Finset Q.QComp)
    (hUclosed : Q.fullClosure U = U)
    (hMin : MinimalClosedDeficient Q L (Q.exposedPorts U)) :
    ∀ D : LegalComponentPartition I (Q.exposedPorts U),
      Fintype.card D.K = 1 :=
  minimalClosedDeficient_has_unique_root_of_splitOrRootAt
    L (hClass L) U hUclosed hMin

/-- Closed weighted-Hall completeness plus the load-specific bank-prime
classifier produces the same unique-root package consumed by W3. -/
theorem uniqueRoot_of_closedWeightedHall_and_splitOrRootAt
    (hHall : ClosedWeightedHallCompleteness Q)
    {d : Dual I} {L : I.Port → ℚ}
    (hClass : ClosedPositiveSplitOrRootAt Q L)
    (hFail : WeightedRoutingFailure d L) :
    ∃ U : Finset Q.QComp,
      Q.fullClosure U = U ∧
        MinimalClosedDeficient Q L (Q.exposedPorts U) ∧
          ∀ D : LegalComponentPartition I (Q.exposedPorts U),
            Fintype.card D.K = 1 := by
  obtain ⟨U, hUclosed, hMin⟩ := hHall hFail
  exact ⟨U, hUclosed, hMin,
    minimalClosedDeficient_has_unique_root_of_splitOrRootAt
      L hClass U hUclosed hMin⟩

theorem uniqueRoot_of_closedWeightedHall_and_splitOrRoot
    (hHall : ClosedWeightedHallCompleteness Q)
    (hClass : ClosedPositiveSplitOrRoot Q)
    {d : Dual I} {L : I.Port → ℚ}
    (hFail : WeightedRoutingFailure d L) :
    ∃ U : Finset Q.QComp,
      Q.fullClosure U = U ∧
        MinimalClosedDeficient Q L (Q.exposedPorts U) ∧
          ∀ D : LegalComponentPartition I (Q.exposedPorts U),
            Fintype.card D.K = 1 :=
  uniqueRoot_of_closedWeightedHall_and_splitOrRootAt hHall (hClass L) hFail

/-- W3 with a load-specific bank-prime classifier in place of broad
root-locality.  Only `Z.portLoad`, not every arbitrary load, is classified. -/
theorem noStrictRestrictedDual_of_closedHall_splitOrRootAt_exchange
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hClass : ClosedPositiveSplitOrRootAt Q Z.portLoad)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap := by
  intro hstrict
  have hFail : WeightedRoutingFailure d Z.portLoad :=
    strictRestrictedDual_gives_weightedRoutingFailure hd Z hstrict
  obtain ⟨U, hUclosed, hMin, hUnique⟩ :=
    uniqueRoot_of_closedWeightedHall_and_splitOrRootAt hHall hClass hFail
  obtain ⟨X, hAllowed, hbad⟩ := hExchange U hUclosed hMin hUnique
  exact not_lt.mpr (hd.d1_allowed X hAllowed) hbad

/-- Uniform-classifier compatibility wrapper. -/
theorem noStrictRestrictedDual_of_closedHall_splitOrRoot_exchange
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hClass : ClosedPositiveSplitOrRoot Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_closedHall_splitOrRootAt_exchange
    hd Z hHall (hClass Z.portLoad) hExchange

/-- All-cut convenience wrapper for the bank-prime W3 route. -/
theorem noStrictDual_of_closedHall_splitOrRoot_exchange
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hClass : ClosedPositiveSplitOrRoot Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_closedHall_splitOrRoot_exchange
    (hd.restrict (Allowed := Allowed)) Z hHall hClass hExchange

/-- All-cut convenience wrapper using only the chosen almost-squeeze load. -/
theorem noStrictDual_of_closedHall_splitOrRootAt_exchange
    {Allowed : I.Cut → Prop} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hClass : ClosedPositiveSplitOrRootAt Q Z.portLoad)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_closedHall_splitOrRootAt_exchange
    (hd.restrict (Allowed := Allowed)) Z hHall hClass hExchange

end ClosedShore
end Wall
end Erdos23Delta0
