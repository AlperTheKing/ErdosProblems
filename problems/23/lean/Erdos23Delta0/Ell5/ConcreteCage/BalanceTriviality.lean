import Erdos23Delta0.Ell5.ConcreteCage.BankPrime

/-!
# Structural triviality of the concrete cage balance

`ConcreteCage.Atom (Distances.blueGraph G c)` abbreviates an `Ell5Atom`, so it
contains a blue walk `geo` which is a path and has length four.  The walk gives
blue distance at most four, whether or not it is distance-tight.  Hence every
such atom has `Distances.ell <= 5` and normalized surplus at most zero.

The bank is already nonnegative by `bank_nonneg`.  It follows, without an
all-length-five assumption, that every current `AmbientCage` has nonpositive
surplus, nonnegative `Balance = Bank - Surplus`, and nonpositive
`Defect = Surplus - Bank`.

Consequently a hypothesis `Balance F C < 0` or `0 < Defect F C` on this model
is vacuous.  In particular, the port-Hall minimal-negative object cannot be
represented by the current `AmbientCage` balance/defect.  As noted in
`BankPrime`, no theorem identifies this cage-ledger defect with
`PortHall.deficiencyQ`; such a representation requires a different definition
or an additional semantic bridge that cannot identify these quantities on a
positive port-Hall instance.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

variable {V : Type*}
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- The walk carried by every concrete atom bounds its actual blue distance. -/
theorem atomBlueDist_le_four (a : Atom (Distances.blueGraph G c)) :
    (Distances.blueGraph G c).dist a.u a.v <= 4 := by
  have hdist := SimpleGraph.dist_le a.geo
  rw [a.len4] at hdist
  exact hdist

/-- Every concrete atom has ambient row length at most five. -/
theorem atomEll_le_five (a : Atom (Distances.blueGraph G c)) :
    Distances.ell G c a.u a.v <= 5 := by
  have hdist := atomBlueDist_le_four (G := G) (c := c) a
  unfold Distances.ell
  omega

/-- The rational square of every concrete atom's row length is at most 25. -/
theorem atomEll_sq_le_25 (a : Atom (Distances.blueGraph G c)) :
    atomEll G c a ^ 2 <= 25 := by
  have hnat := atomEll_le_five (G := G) (c := c) a
  have hle : atomEll G c a <= 5 := by
    unfold atomEll
    exact_mod_cast hnat
  have hnonneg : 0 <= atomEll G c a := by
    simp [atomEll]
  have hprod :
      0 <= (5 - atomEll G c a) * (5 + atomEll G c a) :=
    mul_nonneg (sub_nonneg.mpr hle) (add_nonneg (by norm_num) hnonneg)
  nlinarith

/-- Every concrete atom has nonpositive normalized surplus. -/
theorem atomSurplus_nonpos (a : Atom (Distances.blueGraph G c)) :
    atomSurplus G c a <= 0 := by
  unfold atomSurplus
  linarith [atomEll_sq_le_25 (G := G) (c := c) a]

variable [Fintype V]

namespace AmbientCage

/-- Every current ambient cage has nonpositive total surplus. -/
theorem surplus_nonpos (C : AmbientCage G c) : C.Surplus <= 0 := by
  classical
  unfold Surplus
  exact Finset.sum_nonpos fun a _ => atomSurplus_nonpos (G := G) (c := c) a

end AmbientCage

variable [DecidableEq V]
/-- Every current concrete cage balance is nonnegative, with no atom-length
assumption. -/
theorem balance_nonneg (F : BankFrame (V := V)) (C : AmbientCage G c) :
    0 <= Balance F C := by
  rw [balance_eq_bank_sub_surplus]
  linarith [bank_nonneg F C, AmbientCage.surplus_nonpos C]

/-- Every current concrete cage defect is nonpositive, with no atom-length
assumption. -/
theorem defect_nonpos (F : BankFrame (V := V)) (C : AmbientCage G c) :
    Defect F C <= 0 := by
  unfold Defect
  linarith [bank_nonneg F C, AmbientCage.surplus_nonpos C]

/-- A negative concrete balance hypothesis is vacuous. -/
theorem balance_neg_is_vacuous (F : BankFrame (V := V))
    (C : AmbientCage G c) : Not (Balance F C < 0) :=
  not_lt_of_ge (balance_nonneg F C)

/-- A positive concrete defect hypothesis is vacuous. -/
theorem defect_pos_is_vacuous (F : BankFrame (V := V))
    (C : AmbientCage G c) : Not (0 < Defect F C) :=
  not_lt_of_ge (defect_nonpos F C)

/-- There is no minimal-negative candidate at all for the current concrete
balance, independently of any proposed proper-subcage relation. -/
theorem no_negative_balance_cage (F : BankFrame (V := V)) :
    Not (Exists fun C : AmbientCage G c => Balance F C < 0) := by
  rintro ⟨C, hneg⟩
  exact balance_neg_is_vacuous F C hneg

/-- Equivalently, the current concrete defect has no positive instance. -/
theorem no_positive_defect_cage (F : BankFrame (V := V)) :
    Not (Exists fun C : AmbientCage G c => 0 < Defect F C) := by
  rintro ⟨C, hpos⟩
  exact defect_pos_is_vacuous F C hpos


end ConcreteCage
end Ell5
end Erdos23Delta0
