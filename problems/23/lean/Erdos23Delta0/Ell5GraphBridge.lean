import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.Ell5CSReduction

/-!
# ell=5 graph bridge: wiring `Distances.ell` to the abstract support-expansion skeleton (2026-07-08)

`Ell5CSReduction` proves the `|S| ≤ 5` base case of `Ell5SupportExpansion` from two abstract graph facts, packaged as
hypotheses `h4` (`|P_e| ≥ 4` for every ell=5 atom) and `hpair` (rigidity: distinct atoms have combined support `≥ 5`).
`Distances` defines the *actual* row length `ell G c u v = (blueGraph G c).dist u v + 1` and proves `badEdge_ell_ge_five`.

This module discharges the FIRST of those two facts at the real `blueGraph` level: an ell=5 bad edge has blue-distance
exactly 4, so a shortest blue geodesic is a length-4 `Path`, whose 4 distinct cut edges lie in the atom's support `P`,
giving `|P| ≥ 4`. Concretely it turns `Distances.ell G c u v = 5` into the `h4` hypothesis of
`Ell5CSReduction.hall_le_five`. (The second fact — `hpair` graph-level rigidity — is a separate, harder lemma and is
NOT proved here; the open research core `BalancedNeutralTheta_book_or_reducible` is downstream of both.)

No `sorry`/`admit`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace Ell5GraphBridge

open Distances

variable {V : Type*} (G : SimpleGraph V)

/-- **`ell = 5 ⟹ blue-distance = 4`.** Definitional unfolding of `ell = dist + 1`. Isolated for reuse: it is the hinge
    that lets the abstract `dist = 4` lemmas of `Ell5CSReduction` fire on the concrete row length. -/
theorem dist_eq_four_of_ell_eq_five (c : Cut V) {u v : V}
    (hell : Distances.ell G c u v = 5) :
    (Distances.blueGraph G c).dist u v = 4 := by
  unfold Distances.ell at hell
  omega

/-- **The `h4` graph fact at the `blueGraph` level: `|P_e| ≥ 4` for an ell=5 atom.** If the bad edge `u,v` is
    blue-connected with row length `ell = 5` (so blue-distance `= 4`), then a shortest blue geodesic is a length-4
    `Path`; its four distinct cut edges lie in `P` (the atom's shortest-geodesic support, hypothesis `hP`: `P` contains
    the edges of every shortest blue path), so `4 ≤ |P|`. This is exactly the `h4` premise of
    `Ell5CSReduction.hall_le_five`, discharged from `Distances.ell`. -/
theorem ell5_support_card_ge_four [DecidableEq V] (c : Cut V) {u v : V}
    (hell : Distances.ell G c u v = 5)
    (hconn : (Distances.blueGraph G c).Reachable u v)
    (P : Finset (Sym2 V))
    (hP : ∀ p : (Distances.blueGraph G c).Walk u v,
            p.IsPath → p.length = 4 → p.edges.toFinset ⊆ P) :
    4 ≤ P.card := by
  have hd : (Distances.blueGraph G c).dist u v = 4 :=
    dist_eq_four_of_ell_eq_five G c hell
  obtain ⟨p, hpath, hlen⟩ := hconn.exists_path_of_dist
  rw [hd] at hlen
  exact Ell5CSReduction.support_card_ge_four p hpath hlen P (hP p hpath hlen)

#print axioms dist_eq_four_of_ell_eq_five
#print axioms ell5_support_card_ge_four

end Ell5GraphBridge
end Erdos23Delta0
