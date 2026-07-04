/-
Erdős #23 δ=0 — L1: Γ, the CutState hypothesis bundle, and ν_K ≥ 0.
Per LEAN_BRANCHB_BLUEPRINT_GPTPRO.md §1.2/§1.4: gammaOf = Σ ℓ² over bad edges;
CutState packages max-cut + B-connectedness + gamma-minimality; SwitchCert carries
the σ ledger for a flip; nuK_nonneg is the everywhere-used switch inequality
(σ = 0 via gammaMin, σ ≥ 1 via ν ≥ −K). Self-contained module; unified at PR assembly.
-/

import Mathlib

namespace Erdos23Delta0
namespace GammaCalc

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A two-sided cut. -/
structure Cut (V : Type*) where
  side : V → Bool

/-- Flip the side of every vertex in `S`. -/
def flip (c : Cut V) (S : Finset V) : Cut V :=
  ⟨fun v => if v ∈ S then !(c.side v) else c.side v⟩

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The blue (bichromatic) subgraph of a cut. -/
def blueGraph (c : Cut V) : SimpleGraph V where
  Adj u v := G.Adj u v ∧ c.side u ≠ c.side v
  symm := fun _ _ ⟨ha, hs⟩ => ⟨ha.symm, Ne.symm hs⟩
  loopless := fun _ ⟨_, hs⟩ => hs rfl

/-- Symmetric same-side predicate on unordered edges. -/
def sameSide (s : V → Bool) : Sym2 V → Bool :=
  Sym2.lift ⟨fun a b => s a == s b,
    fun a b => by cases ha : s a <;> cases hb : s b <;> simp [ha, hb]⟩

/-- Bad (monochromatic) edges. -/
def badEdges (c : Cut V) : Finset (Sym2 V) :=
  G.edgeFinset.filter (fun e => sameSide c.side e = true)

/-- Bad-edge count. -/
def badCount (c : Cut V) : ℕ := (badEdges G c).card

/-- Row length of an unordered edge: blue distance + 1 (symmetric lift). -/
noncomputable def ellEdge (c : Cut V) : Sym2 V → ℕ :=
  Sym2.lift ⟨fun u v => (blueGraph G c).dist u v + 1,
    fun u v => by
      show (blueGraph G c).dist u v + 1 = (blueGraph G c).dist v u + 1
      rw [SimpleGraph.dist_comm]⟩

/-- Γ = Σ ℓ² over bad edges. -/
noncomputable def gammaOf (c : Cut V) : ℕ :=
  ∑ e ∈ badEdges G c, (ellEdge G c e) ^ 2

/-- Hypothesis bundle: a B-connected gamma-minimal maximum cut.
    (`maxCut` = bad count is minimal; `gammaMin` = Γ minimal among B-connected
    cuts with the same bad count.) -/
structure CutState where
  cut : Cut V
  maxCut : ∀ c' : Cut V, badCount G cut ≤ badCount G c'
  bconn : (blueGraph G cut).Connected
  gammaMin : ∀ c' : Cut V, badCount G c' = badCount G cut →
    (blueGraph G c').Connected → gammaOf G cut ≤ gammaOf G c'

/-- Switch certificate: the σ ledger for flipping `S` on a `CutState`,
    with the flip staying B-connected. -/
structure SwitchCert (st : CutState G) where
  S : Finset V
  bconn' : (blueGraph G (flip st.cut S)).Connected
  sigma : ℤ
  hsigma : (badCount G (flip st.cut S) : ℤ) = badCount G st.cut + sigma

/-- σ ≥ 0 is forced by max-cut maximality. -/
theorem SwitchCert.sigma_nonneg {st : CutState G} (C : SwitchCert G st) :
    0 ≤ C.sigma := by
  have h := st.maxCut (flip st.cut C.S)
  have := C.hsigma
  omega

/-- ν(S) = Γ(flip) − Γ(cut). -/
noncomputable def SwitchCert.nu {st : CutState G} (C : SwitchCert G st) : ℤ :=
  (gammaOf G (flip st.cut C.S) : ℤ) - gammaOf G st.cut

/-- K = Γ(cut). -/
noncomputable def SwitchCert.K {st : CutState G} (_C : SwitchCert G st) : ℤ :=
  (gammaOf G st.cut : ℤ)

/-- THE SWITCH INEQUALITY: ν_K = ν + K·σ ≥ 0.
    σ = 0: the flip is a B-connected max cut, so gamma-minimality gives ν ≥ 0.
    σ ≥ 1: ν ≥ −K since Γ(flip) ≥ 0, and then ν + Kσ ≥ K(σ−1) ≥ 0. -/
theorem SwitchCert.nuK_nonneg {st : CutState G} (C : SwitchCert G st) :
    0 ≤ C.nu + C.K * C.sigma := by
  have hK0 : (0:ℤ) ≤ C.K := by
    unfold SwitchCert.K; exact_mod_cast Nat.zero_le _
  rcases eq_or_lt_of_le (C.sigma_nonneg G) with h0 | hpos
  · -- σ = 0
    have hbc : badCount G (flip st.cut C.S) = badCount G st.cut := by
      have h := C.hsigma
      omega
    have hg := st.gammaMin (flip st.cut C.S) hbc C.bconn'
    have hnu : (0:ℤ) ≤ C.nu := by
      unfold SwitchCert.nu
      have : (gammaOf G st.cut : ℤ) ≤ (gammaOf G (flip st.cut C.S) : ℤ) := by
        exact_mod_cast hg
      linarith
    rw [← h0]
    simpa using hnu
  · -- σ ≥ 1
    have hnu : -C.K ≤ C.nu := by
      unfold SwitchCert.nu SwitchCert.K
      have hz : (0:ℤ) ≤ (gammaOf G (flip st.cut C.S) : ℤ) := by
        exact_mod_cast Nat.zero_le _
      linarith
    have h1 : (1:ℤ) ≤ C.sigma := hpos
    nlinarith [mul_nonneg hK0 (by linarith : (0:ℤ) ≤ C.sigma - 1)]

end GammaCalc
end Erdos23Delta0
