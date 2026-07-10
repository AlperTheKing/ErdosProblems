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

/-- A primal for the canonical subtype wall LP, zero-extended to the ambient
cut, port, and sink types, gives a full-bank relaxed-cover certificate. -/
noncomputable def certOfPrimal
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (P : Wall.Primal (wallLP S F O J K sep dB inc kap)) :
    FullBankRelaxedCoverCert S F O J K sep dB inc kap := by
  classical
  let lam : ι → ℚ := fun k =>
    if hk : k ∈ K then P.lam ⟨k, hk⟩ else 0
  let q : E → JT → ℚ := fun c j =>
    if hc : c ∈ O then
      if hj : j ∈ J then P.q ⟨c, hc⟩ ⟨j, hj⟩ else 0
    else 0
  have hLamSum (a : ι → ℚ) :
      (∑ k : {k // k ∈ K}, P.lam k * a k.1) =
        ∑ k ∈ K, lam k * a k := by
    calc
      (∑ k : {k // k ∈ K}, P.lam k * a k.1) =
          ∑ k : {k // k ∈ K}, lam k.1 * a k.1 := by
        apply Finset.sum_congr rfl
        intro k _
        simp [lam, k.2]
      _ = ∑ k ∈ K, lam k * a k := sum_subtype_mem K (fun k => lam k * a k)
  have hQRow (c : E) (hc : c ∈ O) :
      (∑ j : {j // j ∈ J}, P.q ⟨c, hc⟩ j) = ∑ j ∈ J, q c j := by
    calc
      (∑ j : {j // j ∈ J}, P.q ⟨c, hc⟩ j) =
          ∑ j : {j // j ∈ J}, q c j.1 := by
        apply Finset.sum_congr rfl
        intro j _
        simp [q, hc, j.2]
      _ = ∑ j ∈ J, q c j := sum_subtype_mem J (q c)
  have hQCol (j : JT) (hj : j ∈ J) :
      (∑ c : {c // c ∈ O}, P.q c ⟨j, hj⟩) = ∑ c ∈ O, q c j := by
    calc
      (∑ c : {c // c ∈ O}, P.q c ⟨j, hj⟩) =
          ∑ c : {c // c ∈ O}, q c.1 j := by
        apply Finset.sum_congr rfl
        intro c _
        simp [q, c.2, hj]
      _ = ∑ c ∈ O, q c j := sum_subtype_mem O (fun c => q c j)
  refine
    { lam := lam
      q := q
      hlam := ?_
      hq := ?_
      hkap := ?_
      hcov := ?_
      hcong := ?_
      hroute := ?_
      hcap := ?_
      hqinc := ?_ }
  · intro k hk
    simpa [lam, hk] using P.lam_nonneg ⟨k, hk⟩
  · intro c hc j hj
    simpa [q, hc, hj] using P.q_nonneg ⟨c, hc⟩ ⟨j, hj⟩
  · intro j hj
    have hsum : 0 ≤ ∑ c : {c // c ∈ O}, P.q c ⟨j, hj⟩ :=
      Finset.sum_nonneg fun c _ => P.q_nonneg c ⟨j, hj⟩
    have hcap := P.sinkCapacity ⟨j, hj⟩
    change (∑ c : {c // c ∈ O}, P.q c ⟨j, hj⟩) ≤ kap j at hcap
    exact hsum.trans hcap
  · intro r hr
    have h := P.coverage ⟨r, hr⟩
    change 1 ≤ ∑ k : {k // k ∈ K},
      P.lam k * (if r ∈ sep k.1 then 1 else 0) at h
    calc
      1 ≤ ∑ k : {k // k ∈ K},
          P.lam k * (if r ∈ sep k.1 then 1 else 0) := h
      _ = ∑ k ∈ K, lam k * (if r ∈ sep k then 1 else 0) :=
        hLamSum (fun k => if r ∈ sep k then 1 else 0)
      _ = ∑ k ∈ K, if r ∈ sep k then lam k else 0 := by simp [mul_ite]
  · intro c hc
    have h := P.shortCongestion ⟨c, hc⟩
    change (∑ k : {k // k ∈ K},
      P.lam k * (if c ∈ dB k.1 then 1 else 0)) ≤ 1 at h
    calc
      (∑ k ∈ K, if c ∈ dB k then lam k else 0) =
          ∑ k ∈ K, lam k * (if c ∈ dB k then 1 else 0) := by simp [mul_ite]
      _ = ∑ k : {k // k ∈ K},
          P.lam k * (if c ∈ dB k.1 then 1 else 0) :=
        (hLamSum (fun k => if c ∈ dB k then 1 else 0)).symm
      _ ≤ 1 := h
  · intro c hc
    have h := P.portRouted ⟨c, hc⟩
    change (∑ k : {k // k ∈ K},
      P.lam k * (if c ∈ dB k.1 then 1 else 0)) ≤
        ∑ j : {j // j ∈ J}, P.q ⟨c, hc⟩ j at h
    calc
      (∑ k ∈ K, if c ∈ dB k then lam k else 0) =
          ∑ k ∈ K, lam k * (if c ∈ dB k then 1 else 0) := by simp [mul_ite]
      _ = ∑ k : {k // k ∈ K},
          P.lam k * (if c ∈ dB k.1 then 1 else 0) :=
        (hLamSum (fun k => if c ∈ dB k then 1 else 0)).symm
      _ ≤ ∑ j : {j // j ∈ J}, P.q ⟨c, hc⟩ j := h
      _ = ∑ j ∈ J, q c j := hQRow c hc
  · intro j hj
    have h := P.sinkCapacity ⟨j, hj⟩
    change (∑ c : {c // c ∈ O}, P.q c ⟨j, hj⟩) ≤ kap j at h
    rw [hQCol j hj] at h
    exact h
  · intro c hc j hj hpos
    have hpos' : 0 < P.q ⟨c, hc⟩ ⟨j, hj⟩ := by
      simpa [q, hc, hj] using hpos
    have hlegal := P.q_legal ⟨c, hc⟩ ⟨j, hj⟩ (ne_of_gt hpos')
    change inc c j at hlegal
    exact hlegal

/-- Feasibility of the ambient full-bank certificate is exactly feasibility of
the canonical finite-subtype wall primal. -/
theorem nonempty_cert_iff_nonempty_primal
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ) :
    Nonempty (FullBankRelaxedCoverCert S F O J K sep dB inc kap) ↔
      Nonempty (Wall.Primal (wallLP S F O J K sep dB inc kap)) := by
  constructor
  · rintro ⟨cert⟩
    exact ⟨primalOfCert S F O J K sep dB inc kap cert⟩
  · rintro ⟨P⟩
    exact ⟨certOfPrimal S F O J K sep dB inc kap P⟩

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
