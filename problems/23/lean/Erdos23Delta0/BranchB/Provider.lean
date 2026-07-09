import Erdos23Delta0.BranchB.BankedUPO

/-!
# Branch-B layer 26: provider surface

This is the final bookkeeping layer above `BankedUPO`: a provider supplies,
for every Branch-B row in a row database, the two abstract facts needed by
`CertGraph.BranchBInputs`:

* the Bank-L reserve inequality;
* the Banked-UPO row bound.

No existence theorem is asserted here.  The research obligation is exactly the
construction of such a provider from the FullBank/lens machinery.
-/

namespace Erdos23Delta0
namespace BranchB
namespace Provider

open CertGraph

/-- Prop-level Branch-B provider for one selected cut and row database. -/
structure BranchBProvider (G : GraphData) (c : CutData) (rows : RowDB) : Prop where
  bankL : ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
    2 * rhoQ Q.length ≤ etaQ G c
  bankedUPO : ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
    BankedUPO.BranchBRowBound G c rows Q

/-- A provider discharges the abstract `BranchBInputs` obligation rowwise. -/
theorem branchBInputs_of_provider {G : GraphData} {c : CutData} {rows : RowDB}
    (P : BranchBProvider G c rows)
    (Q : RowCert) (hQ : RowInDB rows Q) (hLen : 5 < Q.length) :
    BranchBInputs G c rows Q :=
  BankedUPO.branchBInputs_of_bankedUPO hLen
    (P.bankL Q hQ hLen) (P.bankedUPO Q hQ hLen)

/-- Package a provider row into the `BranchBCertBundle` extension point. -/
theorem branchBCertBundle_of_provider {G : GraphData} {c : CutData} {rows : RowDB}
    (P : BranchBProvider G c rows)
    (Q : RowCert) (hQ : RowInDB rows Q) (hLen : 5 < Q.length) :
    BranchBCertBundle G c rows Q :=
  { inputs := branchBInputs_of_provider P Q hQ hLen }

/-- The Branch-B half of `Delta0CertBundles`, as a reusable family theorem. -/
theorem branchB_bundle_family_of_provider {G : GraphData} {c : CutData} {rows : RowDB}
    (P : BranchBProvider G c rows) :
    ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
      BranchBCertBundle G c rows Q :=
  fun Q hQ hLen => branchBCertBundle_of_provider P Q hQ hLen


end Provider
end BranchB
end Erdos23Delta0
