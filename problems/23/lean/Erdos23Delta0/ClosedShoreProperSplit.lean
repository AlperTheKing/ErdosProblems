import Erdos23Delta0.ClosedShoreBankPrime

/-!
# Proper closed-shore splits from port partitions

This module is a generic adapter from port-Hall uncrossing to
`ProperClosedBankSplit`.  A disjoint partition of the parent ports has exactly
additive deficiency when the capacity of the children’s common legal sink
neighborhood is zero.  Literal disjointness of those neighborhoods is the main
special case.

The adapter does not supply any root-corner geometry.  A concrete application
must still prove that the two child port sets partition the parent, are proper
and closed, and have disjoint legal sink neighborhoods (or zero-capacity
overlap).  In particular, these hypotheses are not identified with, and do not
follow here from, `ConcreteCage.Balance`.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP} {Q : AbstractEscapeQuotient I}

/-- Deficiency is additive across a disjoint port partition when the capacity
of the overlap of the two legal sink neighborhoods is zero. -/
theorem deficiencyQ_eq_add_of_partition_of_overlap_cap_zero
    (L : I.Port → ℚ) {parent left right : Finset I.Port}
    (hports : Disjoint left right) (hcover : left ∪ right = parent)
    (hoverlap : capQ I (legalNbr I left ∩ legalNbr I right) = 0) :
    deficiencyQ I L parent = deficiencyQ I L left + deficiencyQ I L right := by
  rw [← hcover, deficiencyQ_union_of_disjoint_ports L hports, hoverlap, add_zero]

/-- Deficiency is additive across a disjoint port partition whose legal sink
neighborhoods are disjoint. -/
theorem deficiencyQ_eq_add_of_disjoint_neighbor_partition
    (L : I.Port → ℚ) {parent left right : Finset I.Port}
    (hports : Disjoint left right) (hcover : left ∪ right = parent)
    (hnbrs : Disjoint (legalNbr I left) (legalNbr I right)) :
    deficiencyQ I L parent = deficiencyQ I L left + deficiencyQ I L right := by
  rw [← hcover]
  exact deficiencyQ_disjoint_neighbor_split L hports hnbrs

/-- Build a proper closed-bank split from a proper closed port partition with
zero-capacity legal-neighborhood overlap. -/
noncomputable def properClosedBankSplitOfOverlapCapZero
    (L : I.Port → ℚ) {parent left right : Finset I.Port}
    (hports : Disjoint left right) (hcover : left ∪ right = parent)
    (hleftClosed : ClosedPortSet Q left)
    (hrightClosed : ClosedPortSet Q right)
    (hleftProper : left ⊂ parent) (hrightProper : right ⊂ parent)
    (hoverlap : capQ I (legalNbr I left ∩ legalNbr I right) = 0) :
    ProperClosedBankSplit Q L parent where
  left := left
  right := right
  left_closed := hleftClosed
  right_closed := hrightClosed
  left_proper := hleftProper
  right_proper := hrightProper
  defect_le :=
    (deficiencyQ_eq_add_of_partition_of_overlap_cap_zero
      L hports hcover hoverlap).le

/-- Build a proper closed-bank split from a proper closed port partition whose
legal sink neighborhoods are disjoint. -/
noncomputable def properClosedBankSplitOfDisjointNeighbors
    (L : I.Port → ℚ) {parent left right : Finset I.Port}
    (hports : Disjoint left right) (hcover : left ∪ right = parent)
    (hleftClosed : ClosedPortSet Q left)
    (hrightClosed : ClosedPortSet Q right)
    (hleftProper : left ⊂ parent) (hrightProper : right ⊂ parent)
    (hnbrs : Disjoint (legalNbr I left) (legalNbr I right)) :
    ProperClosedBankSplit Q L parent where
  left := left
  right := right
  left_closed := hleftClosed
  right_closed := hrightClosed
  left_proper := hleftProper
  right_proper := hrightProper
  defect_le :=
    (deficiencyQ_eq_add_of_disjoint_neighbor_partition
      L hports hcover hnbrs).le

end ClosedShore
end Wall
end Erdos23Delta0
