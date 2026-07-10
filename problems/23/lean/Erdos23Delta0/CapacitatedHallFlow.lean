import Erdos23Delta0.FiniteFarkasRatElim

namespace Erdos23Delta0

open scoped BigOperators

/-- The weighted form of Hall's inequality, proved by subtracting the least
positive left weight and applying Hall to its positive support. -/
theorem weightedHall
    {E V : Type*} [Fintype E] [Fintype V] [DecidableEq E] [DecidableEq V]
    (demand : E -> ℚ) (cap : V -> ℚ)
    (inc : E -> V -> Prop) [DecidableRel inc]
    (_hdemand : forall e, 0 <= demand e) (hcap : forall v, 0 <= cap v)
    (hall : forall T : Finset E,
      (∑ e ∈ T, demand e) <=
        ∑ v ∈ Finset.univ.filter (fun v => Exists fun e => e ∈ T ∧ inc e v), cap v)
    (a : E -> ℚ) (z : V -> ℚ)
    (ha : forall e, 0 <= a e) (hz : forall v, 0 <= z v)
    (haz : forall e v, inc e v -> a e <= z v) :
    (∑ e, demand e * a e) <= ∑ v, cap v * z v := by
  classical
  generalize hn : (Finset.univ.filter fun e => 0 < a e).card = n
  induction n using Nat.strong_induction_on generalizing a z with
  | h n ih =>
      let T : Finset E := Finset.univ.filter fun e => 0 < a e
      by_cases hT : T.Nonempty
      · let levels : Finset ℚ := T.image a
        have hlevels : levels.Nonempty := hT.image a
        let delta : ℚ := levels.min' hlevels
        have hdelta_mem : delta ∈ levels := levels.min'_mem hlevels
        have hdelta_pos : 0 < delta := by
          obtain ⟨e, heT, he⟩ := Finset.mem_image.mp hdelta_mem
          rw [← he]
          exact (Finset.mem_filter.mp heT).2
        have hdelta_le (e : E) (heT : e ∈ T) : delta <= a e := by
          apply levels.min'_le
          exact Finset.mem_image.mpr ⟨e, heT, rfl⟩
        let N : Finset V :=
          Finset.univ.filter fun v => Exists fun e => e ∈ T ∧ inc e v
        let a' : E -> ℚ := fun e => if e ∈ T then a e - delta else a e
        let z' : V -> ℚ := fun v => if v ∈ N then z v - delta else z v
        have ha' : forall e, 0 <= a' e := by
          intro e
          by_cases he : e ∈ T
          · simp [a', he, sub_nonneg.mpr (hdelta_le e he)]
          · simp [a', he, ha e]
        have hz' : forall v, 0 <= z' v := by
          intro v
          by_cases hv : v ∈ N
          · obtain ⟨e, heT, hev⟩ := (Finset.mem_filter.mp hv).2
            have hdz : delta <= z v := (hdelta_le e heT).trans (haz e v hev)
            simp [z', hv, sub_nonneg.mpr hdz]
          · simp [z', hv, hz v]
        have haz' : forall e v, inc e v -> a' e <= z' v := by
          intro e v hev
          by_cases he : e ∈ T
          · have hv : v ∈ N := by
              exact Finset.mem_filter.mpr ⟨Finset.mem_univ v, ⟨e, he, hev⟩⟩
            simpa [a', z', he, hv] using sub_le_sub_right (haz e v hev) delta
          · have hae : a e = 0 := by
              apply le_antisymm
              · apply le_of_not_gt
                intro hpos
                exact he (Finset.mem_filter.mpr ⟨Finset.mem_univ e, hpos⟩)
              · exact ha e
            simpa [a', he, hae] using hz' v
        let T' : Finset E := Finset.univ.filter fun e => 0 < a' e
        have hsub : T' ⊆ T := by
          intro e he'
          have hpos' : 0 < a' e := (Finset.mem_filter.mp he').2
          by_cases he : e ∈ T
          · exact he
          · have hpos : 0 < a e := by simpa [a', he] using hpos'
            exact (he (Finset.mem_filter.mpr ⟨Finset.mem_univ e, hpos⟩)).elim
        obtain ⟨e0, he0T, he0⟩ := Finset.mem_image.mp hdelta_mem
        have he0_not : e0 ∉ T' := by
          simp only [T', Finset.mem_filter, Finset.mem_univ, true_and]
          simp [a', he0T, he0]
        have hne : T' ≠ T := by
          intro heq
          apply he0_not
          simpa [heq] using he0T
        have hcard_lt : T'.card < n := by
          have hcard : T.card = n := by simpa [T] using hn
          calc
            T'.card < T.card :=
              Finset.card_lt_card (Finset.ssubset_iff_subset_ne.mpr ⟨hsub, hne⟩)
            _ = n := hcard
        have hrec : (∑ e, demand e * a' e) <= ∑ v, cap v * z' v := by
          apply ih T'.card hcard_lt a' z' ha' hz' haz'
          rfl
        have ha_split :
            (∑ e, demand e * a e) =
              (∑ e, demand e * a' e) + delta * (∑ e ∈ T, demand e) := by
          calc
            (∑ e, demand e * a e) =
                ∑ e, (demand e * a' e +
                  if e ∈ T then delta * demand e else 0) := by
                    apply Finset.sum_congr rfl
                    intro e _
                    by_cases he : e ∈ T
                    · simp [a', he]
                      ring
                    · simp [a', he]
            _ = (∑ e, demand e * a' e) +
                ∑ e, if e ∈ T then delta * demand e else 0 :=
                  Finset.sum_add_distrib
            _ = (∑ e, demand e * a' e) + delta * (∑ e ∈ T, demand e) := by
                  congr 1
                  rw [Finset.mul_sum]
                  simp
        have hz_split :
            (∑ v, cap v * z v) =
              (∑ v, cap v * z' v) + delta * (∑ v ∈ N, cap v) := by
          calc
            (∑ v, cap v * z v) =
                ∑ v, (cap v * z' v +
                  if v ∈ N then delta * cap v else 0) := by
                    apply Finset.sum_congr rfl
                    intro v _
                    by_cases hv : v ∈ N
                    · simp [z', hv]
                      ring
                    · simp [z', hv]
            _ = (∑ v, cap v * z' v) +
                ∑ v, if v ∈ N then delta * cap v else 0 :=
                  Finset.sum_add_distrib
            _ = (∑ v, cap v * z' v) + delta * (∑ v ∈ N, cap v) := by
                  congr 1
                  rw [Finset.mul_sum]
                  simp
        have hhall : (∑ e ∈ T, demand e) <= ∑ v ∈ N, cap v := by
          simpa [N] using hall T
        have hhall_scaled :
            delta * (∑ e ∈ T, demand e) <= delta * (∑ v ∈ N, cap v) :=
          mul_le_mul_of_nonneg_left hhall hdelta_pos.le
        rw [ha_split, hz_split]
        exact add_le_add hrec hhall_scaled
      · have ha_zero : forall e, a e = 0 := by
          intro e
          apply le_antisymm
          · apply le_of_not_gt
            intro he
            exact hT ⟨e, by simpa [T] using he⟩
          · exact ha e
        simp_rw [ha_zero]
        simp only [mul_zero, Finset.sum_const_zero]
        exact Finset.sum_nonneg fun v _ => mul_nonneg (hcap v) (hz v)

/-- Exact rational capacitated bipartite flow under the weighted Hall
conditions. -/
theorem capacitatedBipartiteFlow_exists
    {E V : Type*} [Fintype E] [Fintype V] [DecidableEq E] [DecidableEq V]
    (demand : E -> ℚ) (cap : V -> ℚ)
    (inc : E -> V -> Prop) [DecidableRel inc]
    (hdemand : forall e, 0 <= demand e) (hcap : forall v, 0 <= cap v)
    (hall : forall T : Finset E,
      (∑ e ∈ T, demand e) <=
        ∑ v ∈ Finset.univ.filter (fun v => Exists fun e => e ∈ T ∧ inc e v), cap v) :
    Exists fun flow : E -> V -> ℚ =>
      (forall e v, 0 <= flow e v) ∧
      (forall e v, Not (inc e v) -> flow e v = 0) ∧
      (forall e, demand e <= ∑ v, flow e v) ∧
      (forall v, (∑ e, flow e v) <= cap v) := by
  classical
  let A : Sum E (Sum V (E × V)) -> (E × V) -> ℚ
    | Sum.inl e, p => if p.1 = e then -1 else 0
    | Sum.inr (Sum.inl v), p => if p.2 = v then 1 else 0
    | Sum.inr (Sum.inr q), p =>
        if Not (inc q.1 q.2) ∧ p = q then 1 else 0
  let b : Sum E (Sum V (E × V)) -> ℚ
    | Sum.inl e => -demand e
    | Sum.inr (Sum.inl v) => cap v
    | Sum.inr (Sum.inr _) => 0
  have hno :
      Not (Nonempty (FiniteFarkasRat.Certificate A b)) := by
    rintro ⟨C⟩
    let a : E -> ℚ := fun e => C.y (Sum.inl e)
    let z : V -> ℚ := fun v => C.y (Sum.inr (Sum.inl v))
    have ha : forall e, 0 <= a e := fun e => C.y_nonneg (Sum.inl e)
    have hz : forall v, 0 <= z v := fun v => C.y_nonneg (Sum.inr (Sum.inl v))
    have haz : forall e v, inc e v -> a e <= z v := by
      intro e v hev
      have hcol := C.column_nonneg (e, v)
      have hsupport :
          (∑ q : E × V,
            if Not (inc q.1 q.2) ∧ (e, v) = q then
              C.y (Sum.inr (Sum.inr q)) else 0) = 0 := by
        apply Finset.sum_eq_zero
        intro q _
        by_cases hq : (e, v) = q
        · subst q
          simp [hev]
        · simp [hq]
      simp [A] at hcol
      rw [hsupport] at hcol
      simpa [a, z] using hcol
    have hw :
        (∑ e, demand e * a e) <= ∑ v, cap v * z v :=
      weightedHall demand cap inc hdemand hcap hall a z ha hz haz
    have hrhs := C.rhs_neg
    simp [b, mul_comm] at hrhs
    linarith
  obtain ⟨P⟩ :
      Nonempty (FiniteFarkasRat.Feasible A b) :=
    (FiniteFarkasRat.feasible_iff_no_certificate).2 hno
  let flow : E -> V -> ℚ := fun e v => P.x (e, v)
  refine ⟨flow, ?_, ?_, ?_, ?_⟩
  · intro e v
    exact P.x_nonneg (e, v)
  · intro e v hev
    have hrow := P.row_le (Sum.inr (Sum.inr (e, v)))
    have hle : flow e v <= 0 := by
      simpa [A, b, flow, hev, Fintype.sum_prod_type] using hrow
    exact le_antisymm hle (P.x_nonneg (e, v))
  · intro e
    have hrow := P.row_le (Sum.inl e)
    change demand e <= ∑ v, P.x (e, v)
    rw [Fintype.sum_prod_type] at hrow
    simp [A, b] at hrow
    linarith
  · intro v
    have hrow := P.row_le (Sum.inr (Sum.inl v))
    change (∑ e, P.x (e, v)) <= cap v
    simpa [A, b, Fintype.sum_prod_type] using hrow

end Erdos23Delta0
