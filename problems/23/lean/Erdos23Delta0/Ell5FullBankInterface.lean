import Erdos23Delta0.RelaxedCoverBanked

/-!
# Full-bank relaxed-cover certificate interface

This module packages the compiled Gap#1 primal object as a first-class Lean
structure.  The remaining open theorem `Ell5FullBankRelaxedCover_exists` can now
be stated as construction of `FullBankRelaxedCoverCert` (or its graph
specialization) for the full ell=5 escape closure.  The soundness theorem here is
only glue: it consumes the package through the already compiled
`RelaxedCoverBanked` algebra.
-/

namespace Erdos23Delta0
namespace Ell5FullBankInterface

open Finset
open BankedCutDominationCore
open RelaxedCoverBanked

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- A finite rational relaxed-cover certificate with legal full-bank routing.
Rows `S` are covered by cuts `K`, support edges `F` have congestion at most one,
and off-support load on `O` is routed through legal bank sinks `J` with capacities
`kap`. -/
structure FullBankRelaxedCoverCert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ) where
  lam : ι → ℚ
  q : E → JT → ℚ
  hlam : ∀ k ∈ K, 0 ≤ lam k
  hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j
  hkap : ∀ j ∈ J, 0 ≤ kap j
  hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0
  hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1
  hroute : ∀ c ∈ O, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j
  hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j
  hqinc : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → inc c j

/-- The packaged primal certificate implies the banked cut-domination theorem. -/
theorem bankedCutDomination_of_cert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap) :
    BankedCutDomination S F O J K sep dB inc kap := by
  exact bankedCutDomination_of_relaxed_cover S F O J K sep dB inc kap cert.lam cert.q
    cert.hlam cert.hq cert.hkap cert.hcov cert.hcong cert.hroute cert.hcap cert.hqinc

/-- The packaged primal certificate excludes every exact rational Farkas dual. -/
theorem no_dualCert_of_cert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap) :
    ¬ ∃ alpha beta gam del, IsDualCert S F O J K sep dB inc kap alpha beta gam del := by
  exact no_dualCert_of_relaxed_cover S F O J K sep dB inc kap cert.lam cert.q
    cert.hlam cert.hq cert.hcov cert.hcong cert.hroute cert.hcap cert.hqinc

/-- Graph-specialized full-bank certificate where the cut family is represented by
vertex sets and `sep`/`dB` are fixed to `deltaM`/`deltaB`. -/
abbrev GraphFullBankRelaxedCoverCert
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet] (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop) (kap : JT → ℚ) :=
  FullBankRelaxedCoverCert S F O J K
    (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
    (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap

/-- Graph-specialized packaged certificate implies graph-level banked domination. -/
theorem graph_bankedCutDomination_of_cert
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop) (kap : JT → ℚ)
    (cert : GraphFullBankRelaxedCoverCert G cut S F O J K Ufam inc kap) :
    BankedCutDomination S F O J K
      (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
      (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap := by
  exact bankedCutDomination_of_cert S F O J K
    (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
    (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap cert

/-- Graph-specialized packaged certificate excludes every exact rational graph-level dual. -/
theorem graph_no_dualCert_of_cert
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop) (kap : JT → ℚ)
    (cert : GraphFullBankRelaxedCoverCert G cut S F O J K Ufam inc kap) :
    ¬ ∃ alpha beta gam del,
      IsDualCert S F O J K
        (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
        (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k))
        inc kap alpha beta gam del := by
  exact no_dualCert_of_cert S F O J K
    (fun k => MaxCutVertexIneq.deltaM G cut (Ufam k))
    (fun k => MaxCutVertexIneq.deltaB G cut (Ufam k)) inc kap cert


end Ell5FullBankInterface
end Erdos23Delta0
