import Erdos23Delta0.CertGraph
import Erdos23Delta0.BranchB.Dict24
import Erdos23Delta0.BranchB.CombinedHBD
import Erdos23Delta0.BranchB.CDTelescope
import Erdos23Delta0.BranchB.PureUPOK0

/-!
# Branch-B layer 25: Banked UPO bookkeeping combiner

This layer does not prove any graph-theoretic existence statement.  It combines
the already-checked Branch-B subledgers:

* `Dict24`: total demand splits into pure / HBD / CD parts;
* `PureUPOK0`: the pure part is paid by legal k=0 banks;
* `CombinedHBD`: HBD demand is paid by HBD token capacities;
* `CDTelescope`: CD finish mass is paid by CD start mass.

The result is the exact rational row-bound shape consumed by the Branch-B
provider layer and by `CertGraph.BranchBInputs`.
-/

namespace Erdos23Delta0
namespace BranchB
namespace BankedUPO

open Finset
open CertGraph

variable {α τ : Type*} [DecidableEq τ]

/-- Numeric target frame for a Branch-B banked-UPO row inequality. -/
structure BankedUPOFrame where
  rowExpr : ℚ
  base : ℚ
  target : ℚ

/-- The row-bound proposition proved by this layer. -/
def BankedUPORowBound (fr : BankedUPOFrame) : Prop :=
  fr.rowExpr ≤ fr.target

/-- A checker-friendly package of the four subcertificates. -/
structure BankedUPOCert (α τ : Type*) where
  dict : Dict24.Dict24AtomData α
  hbd : CombinedHBD.HBDChargeData α τ
  cd : CDTelescope.CDTelescopeData α
  pure : PureUPOK0.PureUPOK0Frame

/-- Total legal bank made available to this Branch-B row. -/
def legalBank (A : Finset α) (T : Finset τ) (C : BankedUPOCert α τ) : ℚ :=
  PureUPOK0.totalBank C.pure + (∑ t ∈ T, C.hbd.cap t) + (∑ a ∈ A, C.cd.start a)

/-- Checked consistency between the four Branch-B subledgers.  The two binding
conditions identify the HBD and CD components of the dictionary with the
corresponding downstream ledgers. -/
def BankedUPOChecked (A : Finset α) (T : Finset τ) (C : BankedUPOCert α τ) : Prop :=
  Dict24.Dict24Checked A C.dict ∧
  CombinedHBD.HBDLedgerChecked A T C.hbd ∧
  CDTelescope.CDTelescopeChecked A C.cd ∧
  PureUPOK0.PureUPOK0Bound C.pure ∧
  C.pure.pureDemand = (∑ a ∈ A, C.dict.pure a) ∧
  (∀ a ∈ A, C.hbd.demand a = C.dict.hbd a) ∧
  (∀ a ∈ A, C.cd.finish a = C.dict.cd a)

/-- Soundness of a checked Banked-UPO certificate.  The row-specific obligations
are kept explicit:

* `hRow`: the row expression is bounded by `base + total demand`;
* `hBudget`: the base plus legal banks fit under the final target.
-/
theorem checkBankedUPOCert_sound (A : Finset α) (T : Finset τ)
    (fr : BankedUPOFrame) (C : BankedUPOCert α τ)
    (hC : BankedUPOChecked A T C)
    (hRow : fr.rowExpr ≤ fr.base + (∑ a ∈ A, C.dict.demand a))
    (hBudget : fr.base + legalBank A T C ≤ fr.target) :
    BankedUPORowBound fr := by
  rcases hC with ⟨hDict, hHBD, hCD, hPure, hPureBind, hHBDBind, hCDBind⟩
  have hSplit := Dict24.dict24_sum_split A C.dict hDict
  have hPureBound : C.pure.pureDemand ≤ PureUPOK0.totalBank C.pure := by
    exact (PureUPOK0.pureUPOK0Bound_iff C.pure).mp hPure
  have hPurePart : (∑ a ∈ A, C.dict.pure a) ≤ PureUPOK0.totalBank C.pure := by
    linarith
  have hHBDEq :
      (∑ a ∈ A, C.dict.hbd a) = ∑ a ∈ A, C.hbd.demand a := by
    exact Finset.sum_congr rfl fun a ha => (hHBDBind a ha).symm
  have hHBDPart : (∑ a ∈ A, C.dict.hbd a) ≤ ∑ t ∈ T, C.hbd.cap t := by
    have hSound := CombinedHBD.hbd_ledger_sound A T C.hbd hHBD
    linarith
  have hCDEq :
      (∑ a ∈ A, C.dict.cd a) = ∑ a ∈ A, C.cd.finish a := by
    exact Finset.sum_congr rfl fun a ha => (hCDBind a ha).symm
  have hCDPart : (∑ a ∈ A, C.dict.cd a) ≤ ∑ a ∈ A, C.cd.start a := by
    have hSound := CDTelescope.cd_telescope_sound A C.cd hCD
    linarith
  have hDemandBank :
      (∑ a ∈ A, C.dict.demand a) ≤ legalBank A T C := by
    unfold legalBank
    linarith
  unfold BankedUPORowBound
  linarith

/-- The exact row-bound shape expected by `CertGraph.BranchBInputs`. -/
def BranchBRowBound (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) : Prop :=
  rowSum G c rows Q ≤ (G.n : ℚ) + etaQ G c / 2 - rhoQ Q.length

/-- Package a proved Banked-UPO row bound into the abstract Branch-B input
record consumed by the existing GERSH bridge. -/
theorem branchBInputs_of_bankedUPO {G : GraphData} {c : CutData}
    {rows : RowDB} {Q : RowCert}
    (hLen : 5 < Q.length)
    (hBankL : 2 * rhoQ Q.length ≤ etaQ G c)
    (hBound : BranchBRowBound G c rows Q) :
    BranchBInputs G c rows Q :=
  { hLen := hLen
    bankL := hBankL
    bankedUPO := hBound }


end BankedUPO
end BranchB
end Erdos23Delta0
