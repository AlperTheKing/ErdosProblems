import Erdos23Delta0.RelaxedCoverGraphBridge
import Erdos23Delta0.Ell5FullBankAssignedSink

namespace Erdos23Delta0
namespace SingletonProbe

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink

variable {V : Type*} [DecidableEq V]

theorem boundary_mk_iff (u v x : V) :
    edgeBoundary ({x} : Finset V) s(u, v) = true ↔ (u = x) != (v = x) := by
  simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk]

theorem half_singleton_boundary_sum_eq (C : Finset V) {u v : V}
    (hne : u ≠ v) :
    (∑ x ∈ C,
      if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        (if u ∈ C then (1 / 2 : ℚ) else 0) +
          (if v ∈ C then (1 / 2 : ℚ) else 0) := by
  have hpoint : ∀ x ∈ C,
      (if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        (if x = u then (1 / 2 : ℚ) else 0) +
          (if x = v then (1 / 2 : ℚ) else 0) := by
    intro x _hx
    by_cases hxu : x = u
    · simp [boundary_mk_iff, hxu, hne, Ne.symm hne]
    · by_cases hxv : x = v
      · simp [boundary_mk_iff, hxv, hne, Ne.symm hne]
      · have hux : u ≠ x := fun h => hxu h.symm
        have hvx : v ≠ x := fun h => hxv h.symm
        simp [boundary_mk_iff, hxu, hxv, hux, hvx]
  calc
    (∑ x ∈ C,
        if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        (∑ x ∈ C, if x = u then (1 / 2 : ℚ) else 0) +
          ∑ x ∈ C, if x = v then (1 / 2 : ℚ) else 0 := by
            rw [← Finset.sum_add_distrib]
            exact Finset.sum_congr rfl hpoint
    _ = _ := by
      simp only [Finset.sum_ite_eq']

theorem half_singleton_boundary_sum (C : Finset V) {u v : V}
    (hne : u ≠ v) (hu : u ∈ C) (hv : v ∈ C) :
    (∑ x ∈ C,
      if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0) = 1 := by
  rw [half_singleton_boundary_sum_eq C hne]
  simp [hu, hv]
  norm_num

theorem half_singleton_boundary_sum_one (C : Finset V) {u v : V}
    (hne : u ≠ v) (hcross : edgeBoundary C s(u, v) = true) :
    (∑ x ∈ C,
      if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0) =
        1 / 2 := by
  rw [half_singleton_boundary_sum_eq C hne]
  by_cases hu : u ∈ C <;> by_cases hv : v ∈ C
  · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hu, hv] at hcross
  · simp [hu, hv]
  · simp [hu, hv]
  · simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hu, hv] at hcross

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

theorem bad_mem_deltaM_singleton_iff (s : V → Bool) {u v x : V}
    (hadj : G.Adj u v) (hmono : s u = s v) :
    s(u, v) ∈ deltaM G s ({x} : Finset V) ↔
      edgeBoundary ({x} : Finset V) s(u, v) = true := by
  have hcut : edgeCut s s(u, v) = false := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hmono]
  have hedge : s(u, v) ∈ G.edgeFinset := by
    rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet]
    exact hadj
  simp [deltaM, hedge, hcut]

theorem cut_mem_deltaB_singleton_iff (s : V → Bool) {u v x : V}
    (hadj : G.Adj u v) (hcutuv : s u ≠ s v) :
    s(u, v) ∈ deltaB G s ({x} : Finset V) ↔
      edgeBoundary ({x} : Finset V) s(u, v) = true := by
  have hcut : edgeCut s s(u, v) = true := by
    simp [edgeCut, edgeBool, Sym2.lift_mk, hcutuv]
  have hedge : s(u, v) ∈ G.edgeFinset := by
    rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet]
    exact hadj
  simp [deltaB, hedge, hcut]

theorem singleton_bad_coverage (s : V → Bool) (C : Finset V) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hbad : edgeCut s e = false)
    (hcore : e ∈ C.sym2) :
    (∑ x ∈ C,
      if e ∈ deltaM G s ({x} : Finset V) then (1 / 2 : ℚ) else 0) = 1 := by
  revert heG hbad hcore
  refine Sym2.inductionOn e ?_
  intro u v heG hbad hcore
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  rw [Finset.mk_mem_sym2_iff] at hcore
  have hne : u ≠ v := G.ne_of_adj heG
  have hmono : s u = s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hbad
  calc
    (∑ x ∈ C,
        if s(u, v) ∈ deltaM G s ({x} : Finset V) then (1 / 2 : ℚ) else 0) =
        ∑ x ∈ C,
          if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro x _hx
            have hiff := bad_mem_deltaM_singleton_iff G s (x := x) heG hmono
            by_cases hm : s(u, v) ∈ deltaM G s ({x} : Finset V)
            · have hb := hiff.mp hm
              simp [hm, hb]
            · have hb : edgeBoundary ({x} : Finset V) s(u, v) ≠ true :=
                fun hb => hm (hiff.mpr hb)
              simp [hm, hb]
    _ = 1 := half_singleton_boundary_sum C hne hcore.1 hcore.2

theorem singleton_cut_congestion (s : V → Bool) (C : Finset V) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true)
    (hcore : e ∈ C.sym2) :
    (∑ x ∈ C,
      if e ∈ deltaB G s ({x} : Finset V) then (1 / 2 : ℚ) else 0) = 1 := by
  revert heG hcut hcore
  refine Sym2.inductionOn e ?_
  intro u v heG hcut hcore
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  rw [Finset.mk_mem_sym2_iff] at hcore
  have hne : u ≠ v := G.ne_of_adj heG
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  calc
    (∑ x ∈ C,
        if s(u, v) ∈ deltaB G s ({x} : Finset V) then (1 / 2 : ℚ) else 0) =
        ∑ x ∈ C,
          if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro x _hx
            have hiff := cut_mem_deltaB_singleton_iff G s (x := x) heG hcutuv
            by_cases hm : s(u, v) ∈ deltaB G s ({x} : Finset V)
            · have hb := hiff.mp hm
              simp [hm, hb]
            · have hb : edgeBoundary ({x} : Finset V) s(u, v) ≠ true :=
                fun hb => hm (hiff.mpr hb)
              simp [hm, hb]
    _ = 1 := half_singleton_boundary_sum C hne hcore.1 hcore.2

def halfWeight (_x : V) : ℚ := 1 / 2

/-- Route half of an off-support edge's singleton load to each endpoint. -/
def endpointQ (e : Sym2 V) (x : V) : ℚ :=
  if x ∈ e then 1 / 2 else 0

theorem endpointQ_nonneg (e : Sym2 V) (x : V) : 0 ≤ endpointQ e x := by
  unfold endpointQ
  split <;> norm_num

theorem sum_endpointQ_eq_singleton_load
    (s : V → Bool) (C : Finset V) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true) :
    (∑ x ∈ C, endpointQ e x) =
      RelaxedCutCover.load C halfWeight
        (fun x => deltaB G s ({x} : Finset V)) e := by
  revert heG hcut
  refine Sym2.inductionOn e ?_
  intro u v heG hcut
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  have hne : u ≠ v := G.ne_of_adj heG
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  have hendpoint :
      (∑ x ∈ C, endpointQ s(u, v) x) =
        (if u ∈ C then (1 / 2 : ℚ) else 0) +
          (if v ∈ C then (1 / 2 : ℚ) else 0) := by
    have hpoint : ∀ x ∈ C,
        endpointQ s(u, v) x =
          (if x = u then (1 / 2 : ℚ) else 0) +
            (if x = v then (1 / 2 : ℚ) else 0) := by
      intro x _hx
      by_cases hxu : x = u
      · simp [endpointQ, hxu, hne]
      · by_cases hxv : x = v
        · simp [endpointQ, hxv, Ne.symm hne]
        · simp [endpointQ, hxu, hxv]
    calc
      (∑ x ∈ C, endpointQ s(u, v) x) =
          (∑ x ∈ C, if x = u then (1 / 2 : ℚ) else 0) +
            ∑ x ∈ C, if x = v then (1 / 2 : ℚ) else 0 := by
              rw [← Finset.sum_add_distrib]
              exact Finset.sum_congr rfl hpoint
      _ = _ := by simp only [Finset.sum_ite_eq']
  rw [hendpoint, ← half_singleton_boundary_sum_eq C hne]
  unfold RelaxedCutCover.load halfWeight
  apply Finset.sum_congr rfl
  intro x _hx
  have hiff := cut_mem_deltaB_singleton_iff G s (x := x) heG hcutuv
  by_cases hm : s(u, v) ∈ deltaB G s ({x} : Finset V)
  · have hb := hiff.mp hm
    simp [hm, hb]
  · have hb : edgeBoundary ({x} : Finset V) s(u, v) ≠ true :=
      fun hb => hm (hiff.mpr hb)
    simp [hm, hb]

theorem sum_endpointQ_eq_half_incident_card
    (O : Finset (Sym2 V)) (x : V) :
    (∑ e ∈ O, endpointQ e x) =
      ((O.filter fun e => x ∈ e).card : ℚ) / 2 := by
  calc
    (∑ e ∈ O, endpointQ e x) =
        ∑ e ∈ O, if x ∈ e then (1 / 2 : ℚ) else 0 := rfl
    _ = ((O.filter fun e => x ∈ e).card : ℚ) / 2 := by
      rw [← Finset.sum_filter]
      simp [div_eq_mul_inv]

theorem singleton_cut_load_le_one
    (s : V → Bool) (C : Finset V) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true) :
    RelaxedCutCover.load C halfWeight
      (fun x => deltaB G s ({x} : Finset V)) e ≤ 1 := by
  rw [← sum_endpointQ_eq_singleton_load G s C heG hcut]
  revert heG
  refine Sym2.inductionOn e ?_
  intro u v heG
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  have hne : u ≠ v := G.ne_of_adj heG
  have hpoint : ∀ x ∈ C,
      endpointQ s(u, v) x =
        (if x = u then (1 / 2 : ℚ) else 0) +
          (if x = v then (1 / 2 : ℚ) else 0) := by
    intro x _hx
    by_cases hxu : x = u
    · simp [endpointQ, hxu, hne]
    · by_cases hxv : x = v
      · simp [endpointQ, hxv, Ne.symm hne]
      · simp [endpointQ, hxu, hxv]
  calc
    (∑ x ∈ C, endpointQ s(u, v) x) =
        (∑ x ∈ C, if x = u then (1 / 2 : ℚ) else 0) +
          ∑ x ∈ C, if x = v then (1 / 2 : ℚ) else 0 := by
            rw [← Finset.sum_add_distrib]
            exact Finset.sum_congr rfl hpoint
    _ ≤ 1 := by
      simp only [Finset.sum_ite_eq']
      by_cases hu : u ∈ C <;> by_cases hv : v ∈ C <;> simp [hu, hv] <;> norm_num

theorem singleton_boundary_port_load (s : V → Bool) (C : Finset V) {e : Sym2 V}
    (heG : e ∈ G.edgeFinset) (hcut : edgeCut s e = true)
    (hcross : edgeBoundary C e = true) :
    RelaxedCutCover.load C halfWeight
      (fun x => deltaB G s ({x} : Finset V)) e = 1 / 2 := by
  revert heG hcut hcross
  refine Sym2.inductionOn e ?_
  intro u v heG hcut hcross
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
  have hne : u ≠ v := G.ne_of_adj heG
  have hcutuv : s u ≠ s v := by
    simpa [edgeCut, edgeBool, Sym2.lift_mk] using hcut
  unfold RelaxedCutCover.load halfWeight
  calc
    (∑ x ∈ C,
        if s(u, v) ∈ deltaB G s ({x} : Finset V) then (1 / 2 : ℚ) else 0) =
        ∑ x ∈ C,
          if edgeBoundary ({x} : Finset V) s(u, v) = true then (1 / 2 : ℚ) else 0 := by
            apply Finset.sum_congr rfl
            intro x _hx
            have hiff := cut_mem_deltaB_singleton_iff G s (x := x) heG hcutuv
            by_cases hm : s(u, v) ∈ deltaB G s ({x} : Finset V)
            · have hb := hiff.mp hm
              simp [hm, hb]
            · have hb : edgeBoundary ({x} : Finset V) s(u, v) ≠ true :=
                fun hb => hm (hiff.mpr hb)
              simp [hm, hb]
    _ = 1 / 2 := half_singleton_boundary_sum_one C hne hcross

theorem sum_assignedSinkQ_eq_half_card
    {JT : Type*} [DecidableEq JT]
    (s : V → Bool) (C : Finset V) (O : Finset (Sym2 V))
    (sink : Sym2 V → JT) (j : JT)
    (hO : ∀ e ∈ O,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ edgeBoundary C e = true) :
    (∑ c ∈ O,
      assignedSinkQ C halfWeight
        (fun x => deltaB G s ({x} : Finset V)) sink c j) =
      ((O.filter fun c => sink c = j).card : ℚ) / 2 := by
  calc
    (∑ c ∈ O,
        assignedSinkQ C halfWeight
          (fun x => deltaB G s ({x} : Finset V)) sink c j) =
        ∑ c ∈ O, if sink c = j then (1 / 2 : ℚ) else 0 := by
          apply Finset.sum_congr rfl
          intro c hc
          obtain ⟨heG, hcut, hcross⟩ := hO c hc
          simp [assignedSinkQ,
            singleton_boundary_port_load G s C heG hcut hcross]
    _ = ((O.filter fun c => sink c = j).card : ℚ) / 2 := by
      rw [← Finset.sum_filter]
      simp [div_eq_mul_inv]

/-- Half-weight singleton cuts on a core automatically cover every bad core
edge and saturate every cut core edge.  Only legal sink assignment and the
per-sink capacity inequality remain. -/
noncomputable def certificate_of_singletonCore_assignedSink
    {JT : Type*} [DecidableEq JT]
    (s : V → Bool) (C : Finset V)
    (S F O : Finset (Sym2 V)) (J : Finset JT)
    (inc : Sym2 V → JT → Prop) (kap : JT → ℚ)
    (sink : Sym2 V → JT)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hsink : ∀ c ∈ O, sink c ∈ J)
    (hinc : ∀ c ∈ O, inc c (sink c))
    (hcap : ∀ j ∈ J,
      (∑ c ∈ O,
        assignedSinkQ C halfWeight
          (fun x => deltaB G s ({x} : Finset V)) sink c j) ≤ kap j) :
    FullBankRelaxedCoverCert S F O J C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap :=
  cert_of_assignedSink S F O J C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap halfWeight sink
    (by intro x hx; norm_num [halfWeight])
    hkap
    (by
      intro e he
      obtain ⟨heG, hbad, hcore⟩ := hS e he
      exact le_of_eq (singleton_bad_coverage G s C heG hbad hcore).symm)
    (by
      intro e he
      obtain ⟨heG, hcut, hcore⟩ := hF e he
      exact le_of_eq (singleton_cut_congestion G s C heG hcut hcore))
    hsink hinc hcap

/-- Count-form specialization: every outside edge crosses the core boundary,
so its singleton load is exactly `1/2`; checking sink capacity is only a
filtered edge count. -/
noncomputable def certificate_of_singletonCore_boundaryCount
    {JT : Type*} [DecidableEq JT]
    (s : V → Bool) (C : Finset V)
    (S F O : Finset (Sym2 V)) (J : Finset JT)
    (inc : Sym2 V → JT → Prop) (kap : JT → ℚ)
    (sink : Sym2 V → JT)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hO : ∀ e ∈ O,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ edgeBoundary C e = true)
    (hsink : ∀ c ∈ O, sink c ∈ J)
    (hinc : ∀ c ∈ O, inc c (sink c))
    (hcount : ∀ j ∈ J,
      ((O.filter fun c => sink c = j).card : ℚ) / 2 ≤ kap j) :
    FullBankRelaxedCoverCert S F O J C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap :=
  certificate_of_singletonCore_assignedSink G s C S F O J inc kap sink
    hkap hS hF hsink hinc (by
      intro j hj
      rw [sum_assignedSinkQ_eq_half_card G s C O sink j hO]
      exact hcount j hj)

/-- Canonical vertex-slack specialization. Every external edge sends `1/2`
to each endpoint lying in the core. Thus sink capacity is exactly the
off-support incidence degree divided by two; no orientation choice is needed. -/
noncomputable def certificate_of_singletonCore_vertexSlack
    (s : V → Bool) (C : Finset V)
    (S F O : Finset (Sym2 V))
    (inc : Sym2 V → V → Prop) (kap : V → ℚ)
    (hkap : ∀ x ∈ C, 0 ≤ kap x)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hO : ∀ e ∈ O, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hinc : ∀ e ∈ O, ∀ x ∈ C, x ∈ e → inc e x)
    (hdegree : ∀ x ∈ C,
      ((O.filter fun e => x ∈ e).card : ℚ) / 2 ≤ kap x) :
    FullBankRelaxedCoverCert S F O C C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap where
  lam := halfWeight
  q := endpointQ
  hlam := by intro x hx; norm_num [halfWeight]
  hq := by intro e he x hx; exact endpointQ_nonneg e x
  hkap := hkap
  hcov := by
    intro e he
    obtain ⟨heG, hbad, hcore⟩ := hS e he
    exact le_of_eq (singleton_bad_coverage G s C heG hbad hcore).symm
  hcong := by
    intro e he
    obtain ⟨heG, hcut, hcore⟩ := hF e he
    exact le_of_eq (singleton_cut_congestion G s C heG hcut hcore)
  hroute := by
    intro e he
    obtain ⟨heG, hcut⟩ := hO e he
    exact le_of_eq (sum_endpointQ_eq_singleton_load G s C heG hcut).symm
  hcap := by
    intro x hx
    rw [sum_endpointQ_eq_half_incident_card O x]
    exact hdegree x hx
  hqinc := by
    intro e he x hx hpos
    by_cases hxe : x ∈ e
    · exact hinc e he x hx hxe
    · have hzero : endpointQ e x = 0 := by simp [endpointQ, hxe]
      rw [hzero] at hpos
      linarith

/-- Door-only specialization. If every off-support cut edge has its own legal
sink with capacity at least one, half-singleton cuts always give a certificate.
Real Door tokens have capacity 25, so the mathematical burden is licensing
the edge-to-Door incidence, not its numeric capacity. -/
noncomputable def certificate_of_singletonCore_allDoors
    (s : V → Bool) (C : Finset V)
    (S F O : Finset (Sym2 V))
    (inc : Sym2 V → Sym2 V → Prop) (kap : Sym2 V → ℚ)
    (hkap : ∀ e ∈ O, 0 ≤ kap e)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hO : ∀ e ∈ O, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hinc : ∀ e ∈ O, inc e e)
    (hdoor : ∀ e ∈ O, (1 : ℚ) ≤ kap e) :
    FullBankRelaxedCoverCert S F O O C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap :=
  cert_of_assignedSink S F O O C
    (fun x => deltaM G s ({x} : Finset V))
    (fun x => deltaB G s ({x} : Finset V)) inc kap halfWeight id
    (by intro x hx; norm_num [halfWeight])
    hkap
    (by
      intro e he
      obtain ⟨heG, hbad, hcore⟩ := hS e he
      exact le_of_eq (singleton_bad_coverage G s C heG hbad hcore).symm)
    (by
      intro e he
      obtain ⟨heG, hcut, hcore⟩ := hF e he
      exact le_of_eq (singleton_cut_congestion G s C heG hcut hcore))
    (by intro e he; exact he)
    hinc
    (by
      intro j hj
      have hjdata := hO j hj
      calc
        (∑ c ∈ O,
            assignedSinkQ C halfWeight
              (fun x => deltaB G s ({x} : Finset V)) id c j) =
            RelaxedCutCover.load C halfWeight
              (fun x => deltaB G s ({x} : Finset V)) j := by
                rw [Finset.sum_eq_single j]
                · simp [assignedSinkQ]
                · intro c hc hcne
                  simp [assignedSinkQ, hcne]
                · intro hjnot
                  exact False.elim (hjnot hj)
        _ ≤ 1 := singleton_cut_load_le_one G s C hjdata.1 hjdata.2
        _ ≤ kap j := hdoor j hj)

end Graph

end SingletonProbe
end Erdos23Delta0

#print axioms Erdos23Delta0.SingletonProbe.singleton_bad_coverage
#print axioms Erdos23Delta0.SingletonProbe.singleton_cut_congestion
#print axioms Erdos23Delta0.SingletonProbe.singleton_boundary_port_load
#print axioms Erdos23Delta0.SingletonProbe.sum_assignedSinkQ_eq_half_card
#print axioms Erdos23Delta0.SingletonProbe.sum_endpointQ_eq_singleton_load
#print axioms Erdos23Delta0.SingletonProbe.sum_endpointQ_eq_half_incident_card
#print axioms Erdos23Delta0.SingletonProbe.singleton_cut_load_le_one
