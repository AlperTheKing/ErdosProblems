import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.Ell5AtomBase
import Erdos23Delta0.Ell5GraphBridge

/-!
# The multi-geodesic support `P_e` as a concrete `Finset` (2026-07-08)

Until now the FULL shortest-geodesic support of an ell=5 atom existed only as a hypothesis (`hP` of
`Ell5GraphBridge.ell5_support_card_ge_four`), and the compiled `|S| ≤ 5` base case
(`Ell5AtomBase.ell5_base_case`) bounded `|S|` by the union of ONE canonical geodesic support per atom. This module
closes both gaps:

* `geodesicSupport H u v` — the union of the edges of ALL shortest geodesics between `u` and `v`, as a `Finset`
  (classical filter over `Finset.univ`; needs `[Fintype V]`);
* `edges_toFinset_subset_geodesicSupport` — discharges the `hP` hypothesis by construction;
* `four_le_geodesicSupport_card` — the `h4` graph fact `|P_e| ≥ 4` for a real ell=5 bad edge of `blueGraph`,
  now with NO support hypothesis;
* `Eshort` — the real multi-geodesic `E_short(S)` = `⋃_{a ∈ S} P_a`;
* `ell5_base_case_Eshort` / `ell5_base_case_Eshort_of_ell` — the `|S| ≤ 5` base case of `Ell5SupportExpansion`
  transferred to the TRUE `E_short` (monotonicity: each canonical support is a subset of the atom's full `P_e`),
  stated end-to-end from the actual row length `Distances.ell = 5`.

No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace Ell5SupportFinset

open SimpleGraph Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

open Classical in
/-- **The full multi-geodesic support `P_e`.** All edges lying on SOME shortest geodesic path from `u` to `v`
    (length = graph distance), as a concrete `Finset (Sym2 V)`. -/
noncomputable def geodesicSupport (H : SimpleGraph V) (u v : V) : Finset (Sym2 V) :=
  Finset.univ.filter fun e => ∃ p : H.Walk u v, p.IsPath ∧ p.length = H.dist u v ∧ e ∈ p.edges

theorem mem_geodesicSupport {H : SimpleGraph V} {u v : V} {e : Sym2 V} :
    e ∈ geodesicSupport H u v ↔
      ∃ p : H.Walk u v, p.IsPath ∧ p.length = H.dist u v ∧ e ∈ p.edges := by
  classical
  simp only [geodesicSupport, Finset.mem_filter, Finset.mem_univ, true_and]

/-- Any shortest geodesic path's edges land in `geodesicSupport` — the `hP` hypothesis, discharged by construction. -/
theorem edges_toFinset_subset_geodesicSupport {H : SimpleGraph V} {u v : V}
    (p : H.Walk u v) (hp : p.IsPath) (hlen : p.length = H.dist u v) :
    p.edges.toFinset ⊆ geodesicSupport H u v := by
  intro e he
  rw [List.mem_toFinset] at he
  exact mem_geodesicSupport.mpr ⟨p, hp, hlen, he⟩

/-- **`h4` with a REAL `P_e`, no hypothesis:** an ell=5 blue-connected bad edge has `|geodesicSupport| ≥ 4`. -/
theorem four_le_geodesicSupport_card (G : SimpleGraph V) (c : Distances.Cut V) {u v : V}
    (hell : Distances.ell G c u v = 5)
    (hconn : (Distances.blueGraph G c).Reachable u v) :
    4 ≤ (geodesicSupport (Distances.blueGraph G c) u v).card := by
  refine Ell5GraphBridge.ell5_support_card_ge_four G c hell hconn _ ?_
  intro p hpath hlen
  have hd : (Distances.blueGraph G c).dist u v = 4 :=
    Ell5GraphBridge.dist_eq_four_of_ell_eq_five G c hell
  exact edges_toFinset_subset_geodesicSupport p hpath (hlen.trans hd.symm)

/-- The canonical one-geodesic support of an `Ell5Atom` sits inside the atom's full `P_e`
    (whenever the carried geodesic is genuinely shortest, i.e. `dist = 4`). -/
theorem atom_support_subset_geodesicSupport {H : SimpleGraph V}
    (a : Ell5AtomBase.Ell5Atom H) (hd : H.dist a.u a.v = 4) :
    a.support ⊆ geodesicSupport H a.u a.v := by
  show a.geo.edges.toFinset ⊆ _
  exact edges_toFinset_subset_geodesicSupport a.geo a.isPath (a.len4.trans hd.symm)

/-- **The real `E_short(S)`:** the union over the atoms of `S` of their FULL multi-geodesic supports. -/
noncomputable def Eshort (H : SimpleGraph V) (S : Finset (Ell5AtomBase.Ell5Atom H)) : Finset (Sym2 V) :=
  S.biUnion fun a => geodesicSupport H a.u a.v

/-- **`|S| ≤ 5` base case at the TRUE `E_short`.** The compiled base case bounds `|S|` by the union of canonical
    supports; monotonicity (each canonical support ⊆ full `P_e`) transfers it to the multi-geodesic `E_short`. -/
theorem ell5_base_case_Eshort {H : SimpleGraph V} (S : Finset (Ell5AtomBase.Ell5Atom H))
    (hInj : ∀ a ∈ S, ∀ b ∈ S, s(a.u, a.v) = s(b.u, b.v) → a = b)
    (hgeo : ∀ a ∈ S, H.dist a.u a.v = 4)
    (hS : S.card ≤ 5) :
    S.card ≤ (Eshort H S).card := by
  have hbase := Ell5AtomBase.ell5_base_case S hInj hS
  refine le_trans hbase (Finset.card_le_card ?_)
  intro x hx
  rw [Finset.mem_biUnion] at hx
  obtain ⟨a, ha, hxa⟩ := hx
  unfold Eshort
  rw [Finset.mem_biUnion]
  exact ⟨a, ha, atom_support_subset_geodesicSupport a (hgeo a ha) hxa⟩

/-- **End-to-end `|S| ≤ 5` base case from the actual row length.** For a finset of ell=5 atoms of the blue graph of a
    cut (distinct bad edges), with every atom's row length `Distances.ell = 5`, the support-expansion Hall bound holds
    at the true multi-geodesic `E_short`. -/
theorem ell5_base_case_Eshort_of_ell (G : SimpleGraph V) (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (hInj : ∀ a ∈ S, ∀ b ∈ S, s(a.u, a.v) = s(b.u, b.v) → a = b)
    (hell : ∀ a ∈ S, Distances.ell G c a.u a.v = 5)
    (hS : S.card ≤ 5) :
    S.card ≤ (Eshort (Distances.blueGraph G c) S).card :=
  ell5_base_case_Eshort S hInj
    (fun a ha => Ell5GraphBridge.dist_eq_four_of_ell_eq_five G c (hell a ha)) hS


end Ell5SupportFinset
end Erdos23Delta0
