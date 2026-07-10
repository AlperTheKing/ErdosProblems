import Erdos23Delta0.BankedWallHornQuotient
import Erdos23Delta0.ClosedShoreProperSplit

/-!
# Direct Horn-closed shore split checker

This module avoids two unnecessary assumptions in the closed-shore wall route:

* it does not identify Horn-closed shores with unions of an undirected
  coupling graph;
* it does not search the full powerset for witnesses whose quotient shores
  are already supplied by a concrete extractor.

A candidate consists of two explicit quotient shores.  The checker scans the
finite Horn rule list, checks the induced exposed-port partition and legal
sink separation, and constructs the existing same-load
`ProperClosedBankSplit`.

No theorem here asserts that a concrete extractor supplies such shores.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Executable closedness check for one supplied Horn shore.  Unlike
`hornClosure`, this scans only the finite rule list and does not enumerate
all quotient shores. -/
def checkHornClosed (S : HornEscapeSurface I) (U : Finset S.QComp) : Bool :=
  S.ruleList.all fun r => decide (r.pre ⊆ U → r.post ∈ U)

/-- Exact reflection of the finite Horn-rule scan. -/
theorem checkHornClosed_eq_true_iff
    (S : HornEscapeSurface I) (U : Finset S.QComp) :
    checkHornClosed S U = true ↔ HornClosed S.rules U := by
  simp only [checkHornClosed, List.all_eq_true, decide_eq_true_eq,
    HornClosed, HornEscapeSurface.rules]

/-- Two supplied quotient shores form a proper closed-bank partition of
`parent` when they are Horn-closed, expose a strict disjoint port partition,
and have disjoint legal sink neighborhoods. -/
def HornClosedSplitCandidate
    (S : HornEscapeSurface I) (parent : Finset I.Port)
    (leftU rightU : Finset S.QComp) : Prop :=
  HornClosed S.rules leftU ∧
    HornClosed S.rules rightU ∧
      S.exposedPorts leftU ⊂ parent ∧
        S.exposedPorts rightU ⊂ parent ∧
          Disjoint (S.exposedPorts leftU) (S.exposedPorts rightU) ∧
            S.exposedPorts leftU ∪ S.exposedPorts rightU = parent ∧
              Disjoint
                (legalNbr I (S.exposedPorts leftU))
                (legalNbr I (S.exposedPorts rightU))

/-- Linear-in-the-rule-list checker for one supplied pair of Horn shores. -/
noncomputable def checkHornClosedSplitCandidate
    (S : HornEscapeSurface I) (parent : Finset I.Port)
    (leftU rightU : Finset S.QComp) : Bool :=
  checkHornClosed S leftU && (
    checkHornClosed S rightU &&
      decide
        (S.exposedPorts leftU ⊂ parent ∧
          S.exposedPorts rightU ⊂ parent ∧
            Disjoint (S.exposedPorts leftU) (S.exposedPorts rightU) ∧
              S.exposedPorts leftU ∪ S.exposedPorts rightU = parent ∧
                Disjoint
                  (legalNbr I (S.exposedPorts leftU))
                  (legalNbr I (S.exposedPorts rightU))))

/-- Exact reflection of the direct split checker. -/
theorem checkHornClosedSplitCandidate_eq_true_iff
    (S : HornEscapeSurface I) (parent : Finset I.Port)
    (leftU rightU : Finset S.QComp) :
    checkHornClosedSplitCandidate S parent leftU rightU = true ↔
      HornClosedSplitCandidate S parent leftU rightU := by
  simp [checkHornClosedSplitCandidate, HornClosedSplitCandidate,
    checkHornClosed_eq_true_iff]

/-- A direct Horn-closed child witness constructs the existing same-load
proper split. -/
noncomputable def properClosedBankSplitOfHornClosedCandidate
    (S : HornEscapeSurface I) (L : I.Port → ℚ)
    (parent : Finset I.Port) (leftU rightU : Finset S.QComp)
    (h : HornClosedSplitCandidate S parent leftU rightU) :
    ProperClosedBankSplit S.toQ L parent := by
  rcases h with ⟨hleftClosed, hrightClosed, hleftProper, hrightProper,
    hports, hcover, hnbrs⟩
  exact properClosedBankSplitOfDisjointNeighbors (Q := S.toQ) L
    hports hcover
    (S.closedPortSet_of_hornClosed leftU hleftClosed)
    (S.closedPortSet_of_hornClosed rightU hrightClosed)
    hleftProper hrightProper hnbrs

/-- Positive checker result, with no component-union or block-saturation
hypothesis, is a kernel-checked proper closed-bank split. -/
theorem nonempty_properClosedBankSplit_of_checkHornClosedSplitCandidate
    (S : HornEscapeSurface I) (L : I.Port → ℚ)
    (parent : Finset I.Port) (leftU rightU : Finset S.QComp)
    (hcheck : checkHornClosedSplitCandidate S parent leftU rightU = true) :
    Nonempty (ProperClosedBankSplit S.toQ L parent) :=
  ⟨properClosedBankSplitOfHornClosedCandidate S L parent leftU rightU
    ((checkHornClosedSplitCandidate_eq_true_iff
      S parent leftU rightU).1 hcheck)⟩

#print axioms checkHornClosed_eq_true_iff
#print axioms checkHornClosedSplitCandidate_eq_true_iff
#print axioms properClosedBankSplitOfHornClosedCandidate
#print axioms nonempty_properClosedBankSplit_of_checkHornClosedSplitCandidate

end ClosedShore
end Wall
end Erdos23Delta0
