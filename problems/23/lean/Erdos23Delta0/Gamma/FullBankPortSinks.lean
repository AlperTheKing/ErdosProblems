import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge

/-!
# Finite full-bank token sinks

This module partitions the finite full-bank token ledger into door and
non-door sinks and records their capacities at hall scale.
-/

namespace Erdos23Delta0
namespace Gamma
namespace FullBankToLengthSurplusCharge
namespace FullBankGlobalPackage

open CertGraph

variable {G : GraphData} {c : CutData} {rows : RowDB}

/-- The finite subtype of ledger tokens whose cap kind is not `door`. -/
def NonDoorToken (P : FullBankGlobalPackage G c rows) :=
  {t : Fin P.tokenCount // (P.ledger.token t).kind != CapKind.door}

/-- The finite subtype of ledger tokens whose cap kind is `door`. -/
def DoorToken (P : FullBankGlobalPackage G c rows) :=
  {t : Fin P.tokenCount // (P.ledger.token t).kind = CapKind.door}

instance nonDoorTokenFintype
    (P : FullBankGlobalPackage G c rows) : Fintype (NonDoorToken P) :=
  Fintype.subtype
    (Finset.univ.filter fun t : Fin P.tokenCount =>
      (P.ledger.token t).kind != CapKind.door)
    (by intro t; simp)

instance doorTokenFintype
    (P : FullBankGlobalPackage G c rows) : Fintype (DoorToken P) :=
  Fintype.subtype
    (Finset.univ.filter fun t : Fin P.tokenCount =>
      (P.ledger.token t).kind = CapKind.door)
    (by intro t; simp)

/-- Hall-scale capacity of a non-door token sink. -/
def nonDoorHallCapQ (P : FullBankGlobalPackage G c rows)
    (t : NonDoorToken P) : ℚ :=
  (P.ledger.token t.1).capQ / 25

/-- Hall-scale capacity of a door token sink. -/
def doorHallCapQ (P : FullBankGlobalPackage G c rows)
    (t : DoorToken P) : ℚ :=
  (P.ledger.token t.1).capQ / 25

theorem nonDoorHallCapQ_nonneg {P : FullBankGlobalPackage G c rows}
    (h : P.Checked) (t : NonDoorToken P) :
    0 ≤ nonDoorHallCapQ P t := by
  exact div_nonneg (h.tokenCap_nonneg t.1) (by norm_num)

theorem doorHallCapQ_nonneg {P : FullBankGlobalPackage G c rows}
    (h : P.Checked) (t : DoorToken P) :
    0 ≤ doorHallCapQ P t := by
  exact div_nonneg (h.tokenCap_nonneg t.1) (by norm_num)

/-- Exact hall-scale form of the checked no-double-spend inequality. -/
theorem spendOfToken_div_twentyFive_le_capQ_div_twentyFive
    {P : FullBankGlobalPackage G c rows} (h : P.Checked)
    (t : Fin P.tokenCount) :
    P.ledger.spendOfToken t / 25 ≤ (P.ledger.token t).capQ / 25 := by
  exact div_le_div_of_nonneg_right (h.no_double_spend t) (by norm_num)

theorem nonDoorSpend_div_twentyFive_le_hallCapQ
    {P : FullBankGlobalPackage G c rows} (h : P.Checked)
    (t : NonDoorToken P) :
    P.ledger.spendOfToken t.1 / 25 ≤ nonDoorHallCapQ P t := by
  exact spendOfToken_div_twentyFive_le_capQ_div_twentyFive h t.1

theorem doorSpend_div_twentyFive_le_hallCapQ
    {P : FullBankGlobalPackage G c rows} (h : P.Checked)
    (t : DoorToken P) :
    P.ledger.spendOfToken t.1 / 25 ≤ doorHallCapQ P t := by
  exact spendOfToken_div_twentyFive_le_capQ_div_twentyFive h t.1

-- Guardrail: legal edge-to-token incidence is still absent from this package.
-- Thus these finite sinks and capacities do not assert a Hall condition.

end FullBankGlobalPackage
end FullBankToLengthSurplusCharge
end Gamma
end Erdos23Delta0
