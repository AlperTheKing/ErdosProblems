import Erdos23Delta0.BankedWallLP
import Erdos23Delta0.Ell5FullBankInterface

/-!
# Full-bank relaxed-cover certificates as banked wall primals

This module gives the canonical finite-subtype presentation of a
`FullBankRelaxedCoverCert` as a `Wall.BankedWallLP`, and transports the
certificate's weights and routing flow to a `Wall.Primal`.
-/

namespace Erdos23Delta0
namespace Ell5FullBankWallAdapter

open scoped BigOperators

open Ell5FullBankInterface

variable {R E JT ι : Type} [DecidableEq R] [DecidableEq E]

private theorem sum_subtype_mem {α M : Type*} [AddCommMonoid M]
    (s : Finset α) (f : α → M) :
    (∑ x : {x // x ∈ s}, f x.1) = ∑ x ∈ s, f x := by
  rw [Finset.univ_eq_attach]
  exact Finset.sum_attach s f

/-- The canonical wall LP carried by finite relaxed-cover data. -/
noncomputable def wallLP
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ) : Wall.BankedWallLP := by
  classical
  exact
    { Cut := {k // k ∈ K}
      Atom := {r // r ∈ S}
      Short := {c // c ∈ F}
      Port := {c // c ∈ O}
      Sink := {j // j ∈ J}
      cutFintype := inferInstance
      atomFintype := inferInstance
      shortFintype := inferInstance
      portFintype := inferInstance
      sinkFintype := inferInstance
      cov := fun k r => if r.1 ∈ sep k.1 then 1 else 0
      useShort := fun k c => if c.1 ∈ dB k.1 then 1 else 0
      cutPort := fun k c => if c.1 ∈ dB k.1 then 1 else 0
      legal := fun c j => inc c.1 j.1
      legalDecidable := fun _ _ => Classical.propDecidable _
      cap := fun j => kap j.1 }

/-- A full-bank relaxed-cover certificate, transported to the canonical wall LP. -/
noncomputable def primalOfCert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap) :
    Wall.Primal (wallLP S F O J K sep dB inc kap) := by
  classical
  refine
    { lam := fun k => cert.lam k.1
      q := fun c j => cert.q c.1 j.1
      lam_nonneg := ?_
      q_nonneg := ?_
      q_legal := ?_
      coverage := ?_
      shortCongestion := ?_
      portRouted := ?_
      sinkCapacity := ?_ }
  · exact fun k => cert.hlam k.1 k.2
  · exact fun c j => cert.hq c.1 c.2 j.1 j.2
  · intro c j hq
    apply cert.hqinc c.1 c.2 j.1 j.2
    exact lt_of_le_of_ne (cert.hq c.1 c.2 j.1 j.2) (Ne.symm hq)
  · intro r
    change 1 ≤ ∑ k : {k // k ∈ K},
      cert.lam k.1 * (if r.1 ∈ sep k.1 then 1 else 0)
    calc
      1 ≤ ∑ k ∈ K, if r.1 ∈ sep k then cert.lam k else 0 := cert.hcov r.1 r.2
      _ = ∑ k : {k // k ∈ K},
          cert.lam k.1 * (if r.1 ∈ sep k.1 then 1 else 0) := by
        simpa [mul_ite] using
          (sum_subtype_mem K (fun k => if r.1 ∈ sep k then cert.lam k else 0)).symm
  · intro c
    change (∑ k : {k // k ∈ K},
      cert.lam k.1 * (if c.1 ∈ dB k.1 then 1 else 0)) ≤ 1
    calc
      (∑ k : {k // k ∈ K},
          cert.lam k.1 * (if c.1 ∈ dB k.1 then 1 else 0)) =
          ∑ k ∈ K, if c.1 ∈ dB k then cert.lam k else 0 := by
        simpa [mul_ite] using
          sum_subtype_mem K (fun k => if c.1 ∈ dB k then cert.lam k else 0)
      _ ≤ 1 := cert.hcong c.1 c.2
  · intro c
    change (∑ k : {k // k ∈ K},
      cert.lam k.1 * (if c.1 ∈ dB k.1 then 1 else 0)) ≤
        ∑ j : {j // j ∈ J}, cert.q c.1 j.1
    calc
      (∑ k : {k // k ∈ K},
          cert.lam k.1 * (if c.1 ∈ dB k.1 then 1 else 0)) =
          ∑ k ∈ K, if c.1 ∈ dB k then cert.lam k else 0 := by
        simpa [mul_ite] using
          sum_subtype_mem K (fun k => if c.1 ∈ dB k then cert.lam k else 0)
      _ ≤ ∑ j ∈ J, cert.q c.1 j := cert.hroute c.1 c.2
      _ = ∑ j : {j // j ∈ J}, cert.q c.1 j.1 :=
        (sum_subtype_mem J (fun j => cert.q c.1 j)).symm
  · intro j
    change (∑ c : {c // c ∈ O}, cert.q c.1 j.1) ≤ kap j.1
    calc
      (∑ c : {c // c ∈ O}, cert.q c.1 j.1) =
          ∑ c ∈ O, cert.q c j.1 := sum_subtype_mem O (fun c => cert.q c j.1)
      _ ≤ kap j.1 := cert.hcap j.1 j.2

/-- Every checked dual of the canonical wall instance has no strict gap. -/
theorem noStrictDualOfCert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap)
    (d : Wall.Dual (wallLP S F O J K sep dB inc kap))
    (hd : d.Checked) : ¬ d.StrictGap :=
  Wall.noStrictDual_of_primal hd (primalOfCert S F O J K sep dB inc kap cert)

end Ell5FullBankWallAdapter
end Erdos23Delta0
