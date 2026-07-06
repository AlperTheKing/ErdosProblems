/-
FC-form bridge: from the package-conditional `erdos23_delta0`
(`(betaSimple Gs : ℚ) ≤ (card V)^2 / 25`) to the official
formal-conjectures `erdos_23` statement shape
(`∃ H ≤ G, H.IsBipartite ∧ (G.edgeFinset \ H.edgeFinset).card ≤ n^2`).

Two steps: (1) the rational-to-Nat arithmetic, card V = 5n ⟹ (5n)^2/25 = n^2,
so `betaSimple Gs ≤ n^2` (Nat); (2) the bipartization identity
`betaSimple Gs = min deletion over bipartite subgraphs`, isolated here as the
single hypothesis `beta_bipartization` (a pure Mathlib SimpleGraph fact,
independent of the #23 argument — the minimizing Boolean coloring yields the
bipartite subgraph whose deleted edges are exactly the monochromatic ones).
-/
import Erdos23Delta0.CertGraph

open SimpleGraph

namespace Erdos23Delta0
namespace CertGraph

/-- FC-FORM (conditional on the bipartization identity). A triangle-free graph
    with a certificate package on `5n` vertices admits a bipartite subgraph
    deleting at most `n^2` edges — the official `erdos_23` shape. -/
theorem erdos23_fcForm_of_bipartization
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (n : ℕ) (hcard : Fintype.card V = 5 * n)
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs)
    (beta_bipartization :
      ∀ K : ℕ, betaSimple Gs ≤ K →
        ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
          (Gs.edgeFinset \ H.edgeFinset).card ≤ K) :
    ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
      (Gs.edgeFinset \ H.edgeFinset).card ≤ n ^ 2 := by
  have hbound : (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 :=
    erdos23_delta0 Gs hTri P
  have hcardQ : (Fintype.card V : ℚ) = 5 * (n : ℚ) := by
    rw [hcard]; push_cast; ring
  rw [hcardQ] at hbound
  have hn2 : ((5 : ℚ) * (n : ℚ)) ^ 2 / 25 = (n : ℚ) ^ 2 := by ring
  rw [hn2] at hbound
  have hbeta_le : betaSimple Gs ≤ n ^ 2 := by exact_mod_cast hbound
  exact beta_bipartization (n ^ 2) hbeta_le

end CertGraph
end Erdos23Delta0

