import Erdos23Delta0.ClosedShoreProperSplit

/-!
# Exact finite checker for proper closed-shore splits

This module reflects the abstract closed-shore and proper-partition conditions
to finite Boolean searches.  The definitions are `noncomputable` because the
compiled port-Hall API supplies classical equality on ports and sinks, and
`legalNbr` is itself noncomputable.  Nevertheless, every quantifier searched
here is explicitly bounded by a finite powerset, and the reflection theorems
identify the Boolean results with the original propositions exactly.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- Check whether `P` is exposed by some full-escape-closed quotient shore. -/
noncomputable def checkClosedPortSet
    (Q : AbstractEscapeQuotient I) (P : Finset I.Port) : Bool :=
  decide (∃ U ∈ (Finset.univ : Finset Q.QComp).powerset,
    Q.fullClosure U = U ∧ Q.exposedPorts U = P)

/-- Exact reflection of the finite closed-shore search. -/
theorem checkClosedPortSet_eq_true_iff
    (Q : AbstractEscapeQuotient I) (P : Finset I.Port) :
    checkClosedPortSet Q P = true ↔ ClosedPortSet Q P := by
  rw [checkClosedPortSet, decide_eq_true_iff]
  constructor
  · rintro ⟨U, _hU, hclosed, hexposed⟩
    exact ⟨U, hclosed, hexposed⟩
  · rintro ⟨U, hclosed, hexposed⟩
    exact
      ⟨U, Finset.mem_powerset.mpr (Finset.subset_univ U),
        hclosed, hexposed⟩

/-- The port-level conditions recognized for a proper closed-bank partition. -/
def ProperClosedBankPartitionCandidate
    (Q : AbstractEscapeQuotient I) (parent left right : Finset I.Port) : Prop :=
  ClosedPortSet Q left ∧
    ClosedPortSet Q right ∧
      left ⊂ parent ∧
        right ⊂ parent ∧
          Disjoint left right ∧
            left ∪ right = parent ∧
              Disjoint (legalNbr I left) (legalNbr I right)

/-- Boolean reflection of one proposed proper closed-bank partition. -/
noncomputable def checkProperClosedBankPartitionCandidate
    (Q : AbstractEscapeQuotient I) (parent left right : Finset I.Port) : Bool :=
  checkClosedPortSet Q left && (
    checkClosedPortSet Q right &&
      decide
        (left ⊂ parent ∧
          right ⊂ parent ∧
            Disjoint left right ∧
              left ∪ right = parent ∧
                Disjoint (legalNbr I left) (legalNbr I right)))

/-- Exact reflection of the candidate predicate. -/
theorem checkProperClosedBankPartitionCandidate_eq_true_iff
    (Q : AbstractEscapeQuotient I) (parent left right : Finset I.Port) :
    checkProperClosedBankPartitionCandidate Q parent left right = true ↔
      ProperClosedBankPartitionCandidate Q parent left right := by
  simp [checkProperClosedBankPartitionCandidate,
    ProperClosedBankPartitionCandidate, checkClosedPortSet_eq_true_iff]

/-- Search all pairs of subsets of `parent` for a proper closed-bank partition. -/
noncomputable def checkProperClosedBankPartition
    (Q : AbstractEscapeQuotient I) (parent : Finset I.Port) : Bool :=
  decide (∃ left ∈ parent.powerset, ∃ right ∈ parent.powerset,
    checkProperClosedBankPartitionCandidate Q parent left right = true)

/-- Bounded form of the positive reflection theorem. -/
theorem checkProperClosedBankPartition_eq_true_iff_bounded
    (Q : AbstractEscapeQuotient I) (parent : Finset I.Port) :
    checkProperClosedBankPartition Q parent = true ↔
      ∃ left ∈ parent.powerset, ∃ right ∈ parent.powerset,
        ProperClosedBankPartitionCandidate Q parent left right := by
  rw [checkProperClosedBankPartition, decide_eq_true_iff]
  constructor
  · rintro ⟨left, hleft, right, hright, hcandidate⟩
    exact
      ⟨left, hleft, right, hright,
        (checkProperClosedBankPartitionCandidate_eq_true_iff
          Q parent left right).1 hcandidate⟩
  · rintro ⟨left, hleft, right, hright, hcandidate⟩
    exact
      ⟨left, hleft, right, hright,
        (checkProperClosedBankPartitionCandidate_eq_true_iff
          Q parent left right).2 hcandidate⟩

/-- A positive result is equivalent to the existence of a qualifying pair.
The explicit powerset bounds disappear because strict properness already
places each child inside `parent`. -/
theorem checkProperClosedBankPartition_eq_true_iff
    (Q : AbstractEscapeQuotient I) (parent : Finset I.Port) :
    checkProperClosedBankPartition Q parent = true ↔
      ∃ left right, ProperClosedBankPartitionCandidate Q parent left right := by
  rw [checkProperClosedBankPartition_eq_true_iff_bounded]
  constructor
  · rintro ⟨left, _hleft, right, _hright, hcandidate⟩
    exact ⟨left, right, hcandidate⟩
  · rintro ⟨left, right, hleftClosed, hrightClosed, hleftProper,
      hrightProper, hports, hcover, hnbrs⟩
    exact
      ⟨left,
        Finset.mem_powerset.mpr
          (Finset.ssubset_iff_subset_ne.mp hleftProper).1,
        right,
        Finset.mem_powerset.mpr
          (Finset.ssubset_iff_subset_ne.mp hrightProper).1,
        hleftClosed, hrightClosed, hleftProper, hrightProper,
        hports, hcover, hnbrs⟩

/-- A negative result is equivalent to the absence of every qualifying pair. -/
theorem checkProperClosedBankPartition_eq_false_iff
    (Q : AbstractEscapeQuotient I) (parent : Finset I.Port) :
    checkProperClosedBankPartition Q parent = false ↔
      ∀ left right, ¬ ProperClosedBankPartitionCandidate Q parent left right := by
  constructor
  · intro hfalse left right hcandidate
    have htrue : checkProperClosedBankPartition Q parent = true :=
      (checkProperClosedBankPartition_eq_true_iff Q parent).2
        ⟨left, right, hcandidate⟩
    simp [hfalse] at htrue
  · intro hnone
    apply Bool.eq_false_of_not_eq_true
    intro htrue
    obtain ⟨left, right, hcandidate⟩ :=
      (checkProperClosedBankPartition_eq_true_iff Q parent).1 htrue
    exact hnone left right hcandidate

/-- A checked partition constructs the existing proper split at the same load. -/
theorem nonempty_properClosedBankSplit_of_checkProperClosedBankPartition
    (L : I.Port → ℚ) (parent : Finset I.Port)
    (hcheck : checkProperClosedBankPartition Q parent = true) :
    Nonempty (ProperClosedBankSplit Q L parent) := by
  obtain ⟨left, right, hleftClosed, hrightClosed, hleftProper,
      hrightProper, hports, hcover, hnbrs⟩ :=
    (checkProperClosedBankPartition_eq_true_iff Q parent).1 hcheck
  exact
    ⟨properClosedBankSplitOfDisjointNeighbors (Q := Q) L
      hports hcover hleftClosed hrightClosed hleftProper hrightProper hnbrs⟩

end ClosedShore
end Wall
end Erdos23Delta0
