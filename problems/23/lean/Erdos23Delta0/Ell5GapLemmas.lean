import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.Ell5AtomBase
import Erdos23Delta0.NeutralLensLedger

namespace Erdos23Delta0
namespace Ell5GapLemmas

variable {V : Type*} [DecidableEq V]

/-- An `Ell5Atom` in the blue graph of a triangle-free cut has ambient row length exactly five
    when its endpoints form a bad ambient edge. -/
theorem ell_eq_five_of_ell5Atom (G : SimpleGraph V)
    (c : Distances.Cut V) (htf : G.CliqueFree 3)
    (a : Ell5AtomBase.Ell5Atom (Distances.blueGraph G c))
    (hadj : G.Adj a.u a.v) (hbad : c.side a.u = c.side a.v) :
    Distances.ell G c a.u a.v = 5 := by
  have hconn : (Distances.blueGraph G c).Reachable a.u a.v := a.geo.reachable
  have hlower : 5 <= Distances.ell G c a.u a.v :=
    Distances.badEdge_ell_ge_five G c htf hadj hbad hconn
  have hdist_le : (Distances.blueGraph G c).dist a.u a.v <= 4 := by
    have h := SimpleGraph.dist_le a.geo
    rw [a.len4] at h
    exact h
  have hupper : Distances.ell G c a.u a.v <= 5 := by
    unfold Distances.ell
    omega
  omega

/-- Pure finite-sum surplus split: if `AC` is the disjoint union of `AW`, `AC'`, and
    two boundary atoms with length five, then the boundary atoms contribute zero to
    `ell^2 - 25`. -/
theorem surplus_split {α : Type*} [DecidableEq α] (ellQ : α -> ℚ)
    (AC AW AC' : Finset α) (e f : α)
    (hef : e ≠ f)
    (hpart : AC = (AW ∪ AC') ∪ ({e, f} : Finset α))
    (hWC' : Disjoint AW AC')
    (heW : e ∉ AW) (heC' : e ∉ AC') (hfW : f ∉ AW) (hfC' : f ∉ AC')
    (helle : ellQ e = 5) (hellf : ellQ f = 5) :
    Finset.sum AC (fun h => ellQ h ^ 2 - 25) =
      Finset.sum AW (fun h => ellQ h ^ 2 - 25) +
        Finset.sum AC' (fun h => ellQ h ^ 2 - 25) := by
  subst AC
  have hdisj_pair : Disjoint (AW ∪ AC') ({e, f} : Finset α) := by
    rw [Finset.disjoint_left]
    intro x hx hxpair
    simp only [Finset.mem_union, Finset.mem_insert, Finset.mem_singleton] at hx hxpair
    rcases hxpair with rfl | rfl
    · rcases hx with hxW | hxC'
      · exact heW hxW
      · exact heC' hxC'
    · rcases hx with hxW | hxC'
      · exact hfW hxW
      · exact hfC' hxC'
  rw [Finset.sum_union hdisj_pair, Finset.sum_union hWC']
  have hpair : Finset.sum ({e, f} : Finset α) (fun h => ellQ h ^ 2 - 25) = 0 := by
    simp [hef, helle, hellf]
    norm_num
  rw [hpair]
  ring

/-- Pure ledger-separation assembly: surplus additivity plus bank superadditivity produces
    a `LedgerSep` with remainder `Balance C - Balance C' - Balance W`. -/
theorem pure_lens_ledgerSep {γ : Type*} (Bank Surplus Balance : γ -> ℚ) (Proper : γ -> Prop)
    (C W C' : γ)
    (hBalance : ∀ D, Balance D = Bank D - Surplus D)
    (hWProper : Proper W) (hC'Proper : Proper C')
    (hSurplusSplit : Surplus C = Surplus W + Surplus C')
    (hBankSuper : Bank W + Bank C' <= Bank C) :
    NeutralLensLedger.LedgerSep Balance Proper C W C' (Balance C - Balance C' - Balance W) := by
  refine ⟨hWProper, hC'Proper, ?_, by ring⟩
  have hC := hBalance C
  have hW := hBalance W
  have hC' := hBalance C'
  linarith

/-- A pure lens is impossible in a minimal-negative cage once its ledger-separating
    split has been assembled. -/
theorem no_pure_lens_in_minNeg {γ : Type*} (Balance : γ -> ℚ) (Proper : γ -> Prop)
    (C W C' : γ) (rem : ℚ)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D -> 0 <= Balance D)
    (hLS : NeutralLensLedger.LedgerSep Balance Proper C W C' rem) :
    False := by
  exact NeutralLensLedger.no_ledgerSep_in_minNeg Balance Proper C W C' rem hCneg hMin hLS


end Ell5GapLemmas
end Erdos23Delta0

