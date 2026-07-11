import Erdos23Delta0.CertGraph

/-!
# Checked common-blue C5-base transfer terminal

The 3,892-vertex R19 guardrail refutes the initially proposed
common-bad-neighbour terminal: its remote source pair has a common BLUE
neighbour.  The valid certificate flips the two source vertices and reserves
the two blue source-to-owner edges.  Hence the exact terminal condition is

`dM({x,y}) + 2 <= dB({x,y})`.

This module records and checks precisely that condition on the literal graph
and cut data.  Permanently-Free source ownership and global matching are
separate layers.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedC5BaseTransfer

open CertGraph

/-- Literal source pair and its destination owner. -/
structure TerminalData where
  sourceX : Nat
  sourceY : Nat
  owner : Nat
deriving Repr, DecidableEq

namespace TerminalData

def switch (T : TerminalData) : List Nat := [T.sourceX, T.sourceY]

/-- The graph-computable corrected R19 terminal predicate. -/
def Valid (G : GraphData) (c : CutData) (T : TerminalData) : Prop :=
  T.sourceX < G.n /\
    T.sourceY < G.n /\
    T.owner < G.n /\
    T.sourceX ≠ T.sourceY /\
    blueb G c T.sourceX T.owner = true /\
    blueb G c T.sourceY T.owner = true /\
    dM G c T.switch + 2 <= dB G c T.switch

instance validDecidable (G : GraphData) (c : CutData) (T : TerminalData) :
    Decidable (T.Valid G c) := by
  unfold Valid
  infer_instance

/-- Kernel-replayable checker for one common-blue base terminal. -/
def check (G : GraphData) (c : CutData) (T : TerminalData) : Bool :=
  decide (T.Valid G c)

theorem check_eq_true_iff (G : GraphData) (c : CutData) (T : TerminalData) :
    T.check G c = true <-> T.Valid G c := by
  simp [check]

/-- Exact adjusted switch surplus after reserving the two destination edges. -/
def adjustedSurplus (G : GraphData) (c : CutData) (T : TerminalData) : Int :=
  (dB G c T.switch : Int) - (dM G c T.switch : Int) - 2

theorem adjustedSurplus_nonneg {G : GraphData} {c : CutData} {T : TerminalData}
    (h : T.Valid G c) :
    0 <= T.adjustedSurplus G c := by
  have hbd : dM G c T.switch + 2 <= dB G c T.switch := h.2.2.2.2.2.2
  unfold adjustedSurplus
  omega

/-- In particular, the unadjusted max-cut switch surplus is at least two. -/
theorem two_le_sigma {G : GraphData} {c : CutData} {T : TerminalData}
    (h : T.Valid G c) :
    (2 : Int) <= sigma G c T.switch := by
  have hbd : dM G c T.switch + 2 <= dB G c T.switch := h.2.2.2.2.2.2
  unfold sigma
  omega

end TerminalData

#print axioms TerminalData.check_eq_true_iff
#print axioms TerminalData.adjustedSurplus_nonneg
#print axioms TerminalData.two_le_sigma

end CheckedC5BaseTransfer
end Gamma
end Erdos23Delta0
