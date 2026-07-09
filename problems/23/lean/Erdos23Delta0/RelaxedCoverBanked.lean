import Erdos23Delta0.RelaxedCoverDuality
import Erdos23Delta0.BankedCutDominationCore
import Erdos23Delta0.MaxCutVertexIneq

/-!
# Relaxed-cover primal certificates imply banked cut domination

This is a small interface layer for Gap#1.  The duality module proves that a
relaxed cut-cover with routed off-support load is incompatible with any
Farkas dual certificate.  The banked-domination core proves that the absence
of such a dual certificate is equivalent to `BankedCutDomination`.

The theorem below packages those two compiled facts into the exact form the
future `Ell5FullBankRelaxedCover_exists` construction should consume: once a
cover and legal bank-routing flow are built, the banked domination inequality
follows without re-opening Farkas algebra.
-/

namespace Erdos23Delta0
namespace RelaxedCoverBanked

open Finset
open RelaxedCoverDuality
open BankedCutDominationCore


variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- A relaxed-cover primal certificate, with the flow support routed only
through legal bank incidences, implies the δ-eliminated banked cut-domination
inequality. -/
theorem bankedCutDomination_of_relaxed_cover
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop)
    (kap : JT → ℚ) (lam : ι → ℚ) (q : E → JT → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hroute : ∀ c ∈ O, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j)
    (hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j)
    (hqinc : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → inc c j) :
    BankedCutDomination S F O J K sep dB inc kap := by
  by_contra hnot
  obtain ⟨alpha, beta, gam, del, hcert⟩ :=
    (dualCert_iff_not_bankedCutDomination S F O J K sep dB inc kap hkap).mpr hnot
  rcases hcert with ⟨halpha, hbeta, hgam, hdel, hD1, hD2, hD3⟩
  exact relaxed_cover_weak_duality S F O J K sep dB lam q alpha beta gam del kap
    hlam halpha hbeta hgam hdel hq hcov hcong hroute hcap
    (fun c hc j hj hpos => hD2 c hc j hj (hqinc c hc j hj hpos))
    hD1 hD3

/-- Explicit refutation-facing form: a relaxed-cover primal certificate rules
out every exact rational Farkas dual certificate. -/
theorem no_dualCert_of_relaxed_cover
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop)
    (kap : JT → ℚ) (lam : ι → ℚ) (q : E → JT → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hroute : ∀ c ∈ O, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j)
    (hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j)
    (hqinc : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → inc c j) :
    ¬ ∃ alpha beta gam del, IsDualCert S F O J K sep dB inc kap alpha beta gam del := by
  rintro ⟨alpha, beta, gam, del, hcert⟩
  rcases hcert with ⟨halpha, hbeta, hgam, hdel, hD1, hD2, hD3⟩
  exact relaxed_cover_weak_duality S F O J K sep dB lam q alpha beta gam del kap
    hlam halpha hbeta hgam hdel hq hcov hcong hroute hcap
    (fun c hc j hj hpos => hD2 c hc j hj (hqinc c hc j hj hpos))
    hD1 hD3
/-- Graph-instantiated form of `bankedCutDomination_of_relaxed_cover`, with the
cut family represented by vertex sets and the row/boundary maps fixed as
`deltaM` and `deltaB`. -/
theorem graph_bankedCutDomination_of_relaxed_cover
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop)
    (kap : JT → ℚ) (lam : ι → ℚ) (q : Sym2 V → JT → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤
      ∑ k ∈ K, if r ∈ MaxCutVertexIneq.deltaM G cut (Ufam k) then lam k else 0)
    (hcong : ∀ c ∈ F,
      (∑ k ∈ K, if c ∈ MaxCutVertexIneq.deltaB G cut (Ufam k) then lam k else 0) ≤ 1)
    (hroute : ∀ c ∈ O,
      (∑ k ∈ K, if c ∈ MaxCutVertexIneq.deltaB G cut (Ufam k) then lam k else 0) ≤
        ∑ j ∈ J, q c j)
    (hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j)
    (hqinc : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → inc c j) :
    BankedCutDomination S F O J K
      (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
      (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap := by
  exact bankedCutDomination_of_relaxed_cover S F O J K
    (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
    (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap lam q
    hlam hq hkap hcov hcong hroute hcap hqinc
/-- Graph-instantiated no-dual form for exact regression tests: a graph-level
relaxed-cover primal certificate excludes every exact rational dual
certificate for the same `deltaM`/`deltaB` family. -/
theorem graph_no_dualCert_of_relaxed_cover
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop)
    (kap : JT → ℚ) (lam : ι → ℚ) (q : Sym2 V → JT → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤
      ∑ k ∈ K, if r ∈ MaxCutVertexIneq.deltaM G cut (Ufam k) then lam k else 0)
    (hcong : ∀ c ∈ F,
      (∑ k ∈ K, if c ∈ MaxCutVertexIneq.deltaB G cut (Ufam k) then lam k else 0) ≤ 1)
    (hroute : ∀ c ∈ O,
      (∑ k ∈ K, if c ∈ MaxCutVertexIneq.deltaB G cut (Ufam k) then lam k else 0) ≤
        ∑ j ∈ J, q c j)
    (hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j)
    (hqinc : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → inc c j) :
    ¬ ∃ alpha beta gam del,
      IsDualCert S F O J K
        (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
        (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k))
        inc kap alpha beta gam del := by
  exact no_dualCert_of_relaxed_cover S F O J K
    (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
    (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap lam q
    hlam hq hcov hcong hroute hcap hqinc

end RelaxedCoverBanked
end Erdos23Delta0
