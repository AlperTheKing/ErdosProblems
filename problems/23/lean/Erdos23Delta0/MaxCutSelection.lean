import Mathlib
import Erdos23Delta0.MaxCutVertexIneq

/-!
# M6 selection lemmas: a maximum cut exists; refined argmin selection (2026-07-08)

First compiled piece of the M6 good-cut existence provider (the largest missing construction of the certificate
package). Over a finite vertex type the cut-value function has a maximum (`exists_maxCut`), and among the cuts
satisfying any nonempty property one can select one minimizing any ℕ-valued functional (`exists_min_over`) — in
particular a Γ-minimal maximum cut once Γ is wired (`exists_maxCut_argmin`). The B-connectivity refinement slots
in through the same generic `P` (e.g. `P s := IsMaxCut G s ∧ BConnected s`), so the provider's selection step is
fully covered by these lemmas; what remains for M6 is the RowDB construction and the GammaBetaFacts instantiation.
No `sorry`/`admit`/`native_decide`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace MaxCutSelection

open MaxCutVertexIneq

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **A maximum cut exists** (finite argmax of `cutVal` over the cut space `V → Bool`). -/
theorem exists_maxCut (G : SimpleGraph V) [Fintype G.edgeSet] :
    ∃ s : V → Bool, IsMaxCut G s := by
  obtain ⟨s, hs⟩ := Finite.exists_max (fun s : V → Bool => cutVal G s)
  exact ⟨s, hs⟩

/-- **Generic refined selection.** Over a finite type, any nonempty property `P` yields an element minimizing any
    `ℕ`-valued functional `g` among the `P`-satisfiers. -/
theorem exists_min_over {α : Type*} [Finite α] (P : α → Prop) (hne : ∃ a, P a) (g : α → ℕ) :
    ∃ a, P a ∧ ∀ b, P b → g a ≤ g b := by
  classical
  have hne' : {n : ℕ | ∃ a, P a ∧ g a = n}.Nonempty := by
    obtain ⟨a, ha⟩ := hne
    exact ⟨g a, a, ha, rfl⟩
  obtain ⟨a, haP, hgan⟩ : ∃ a, P a ∧ g a = sInf {n : ℕ | ∃ a, P a ∧ g a = n} :=
    Nat.sInf_mem hne'
  refine ⟨a, haP, fun b hb => ?_⟩
  rw [hgan]
  exact Nat.sInf_le ⟨b, hb, rfl⟩

/-- **Γ-minimal maximum cut selection** (generic in the Γ-functional `g` and any extra refinement `Q` that is
    satisfiable among maximum cuts — e.g. B-connectivity): there is a cut that is maximum, satisfies `Q`, and
    minimizes `g` among all maximum cuts satisfying `Q`. -/
theorem exists_maxCut_argmin (G : SimpleGraph V) [Fintype G.edgeSet]
    (Q : (V → Bool) → Prop) (g : (V → Bool) → ℕ)
    (hQ : ∃ s, IsMaxCut G s ∧ Q s) :
    ∃ s, IsMaxCut G s ∧ Q s ∧ ∀ s', IsMaxCut G s' → Q s' → g s ≤ g s' := by
  obtain ⟨s, ⟨hmax, hq⟩, hmin⟩ :=
    exists_min_over (fun s : V → Bool => IsMaxCut G s ∧ Q s) hQ g
  exact ⟨s, hmax, hq, fun s' h1 h2 => hmin s' ⟨h1, h2⟩⟩

#print axioms exists_maxCut
#print axioms exists_min_over
#print axioms exists_maxCut_argmin

end MaxCutSelection
end Erdos23Delta0
