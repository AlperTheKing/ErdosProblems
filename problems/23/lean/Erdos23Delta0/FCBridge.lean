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

/-- FC-FORM (unconditional). A triangle-free graph with a certificate package on
    `5n` vertices has a bipartite subgraph deleting at most `n^2` edges — the
    official `erdos_23` shape. The bipartization identity is now discharged by the
    proven `SimpleGraphBridge.beta_bipartization`. -/
theorem erdos23_fcForm_of_bipartization
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (n : ℕ) (hcard : Fintype.card V = 5 * n)
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs) :
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
  exact SimpleGraphBridge.beta_bipartization Gs (n ^ 2) hbeta_le

/-- Official-form wrapper from the remaining generic package provider.

This is the final bookkeeping shape for the `formal-conjectures` theorem: once
the delta=0 assembly constructs a `SimpleGraphCertificatePackage` for every
finite triangle-free graph, the displayed Erdős #23 statement follows. -/
theorem erdos23_fcForm_of_packageProvider
    (packageProvider :
      ∀ {V : Type*} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (n : ℕ) (V : Type*) [Fintype V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V), Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2 := by
  intro n V _ hcard Gs hTri
  classical
  letI : DecidableEq V := Classical.decEq V
  letI : DecidableRel Gs.Adj := Classical.decRel Gs.Adj
  obtain ⟨P⟩ := packageProvider Gs hTri
  exact erdos23_fcForm_of_bipartization Gs n hcard hTri P

end CertGraph
end Erdos23Delta0
