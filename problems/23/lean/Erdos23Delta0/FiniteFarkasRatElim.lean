import Erdos23Delta0.FiniteFarkasRatBasic

/-!
# Constructive Fourier-Motzkin over the rationals

The elimination kernel for the finite rational Farkas theorem.  Ordinary
inequalities are eliminated one coordinate at a time; every projected row is
stored as a manifest nonnegative combination of the previous rows.
-/

namespace Erdos23Delta0
namespace FiniteFarkasRat

open scoped BigOperators

universe u

/-- A finite system of ordinary rational inequalities in `n` unrestricted
variables. -/
structure System (n : Nat) where
  Row : Type u
  rowFintype : Fintype Row
  coeff : Row -> Fin n -> ℚ
  rhs : Row -> ℚ

attribute [instance] System.rowFintype

namespace System

variable {n : Nat}

/-- A point satisfying every row of an ordinary inequality system. -/
structure Point (S : System n) where
  x : Fin n -> ℚ
  row_le : forall i, (Finset.univ.sum fun j => S.coeff i j * x j) <= S.rhs i

/-- A zero-coefficient nonnegative combination with negative right side. -/
structure ZeroCertificate (S : System n) where
  y : S.Row -> ℚ
  y_nonneg : forall i, 0 <= y i
  coeff_zero : forall j,
    (Finset.univ.sum fun i => y i * S.coeff i j) = 0
  rhs_neg : (Finset.univ.sum fun i => y i * S.rhs i) < 0

/-- A manifest nonnegative combination of rows. -/
structure Combination (S : System n) where
  weight : S.Row -> ℚ
  weight_nonneg : forall i, 0 <= weight i

namespace Combination

def coeff {S : System n} (C : Combination S) (j : Fin n) : ℚ :=
  Finset.univ.sum fun i => C.weight i * S.coeff i j

def rhs {S : System n} (C : Combination S) : ℚ :=
  Finset.univ.sum fun i => C.weight i * S.rhs i

/-- Any nonnegative row combination remains valid at a feasible point. -/
theorem valid {S : System n} (C : Combination S) (P : Point S) :
    (Finset.univ.sum fun j => C.coeff j * P.x j) <= C.rhs := by
  have hrows :
      (Finset.univ.sum fun i =>
          C.weight i * (Finset.univ.sum fun j => S.coeff i j * P.x j))
        <= Finset.univ.sum fun i => C.weight i * S.rhs i := by
    exact Finset.sum_le_sum fun i _ =>
      mul_le_mul_of_nonneg_left (P.row_le i) (C.weight_nonneg i)
  have hswap :
      (Finset.univ.sum fun j => C.coeff j * P.x j) =
        Finset.univ.sum fun i =>
          C.weight i * (Finset.univ.sum fun j => S.coeff i j * P.x j) := by
    simp only [coeff, Finset.sum_mul, Finset.mul_sum, mul_assoc]
    rw [Finset.sum_comm]
  simpa only [hswap, rhs] using hrows

end Combination

variable (S : System (n + 1))

abbrev ZeroRow := {i : S.Row // S.coeff i 0 = 0}
abbrev PosRow := {i : S.Row // 0 < S.coeff i 0}
abbrev NegRow := {i : S.Row // S.coeff i 0 < 0}

noncomputable instance zeroRowFintype : Fintype (ZeroRow S) := Fintype.ofFinite _
noncomputable instance posRowFintype : Fintype (PosRow S) := Fintype.ofFinite _
noncomputable instance negRowFintype : Fintype (NegRow S) := Fintype.ofFinite _

/-- Projected rows: unchanged zero-head rows and every positive/negative pair. -/
abbrev ElimRow := Sum (ZeroRow S) (PosRow S × NegRow S)

/-- The nonnegative old-row combination represented by one projected row. -/
noncomputable def elimCombination (r : ElimRow S) : Combination S := by
  classical
  cases r with
  | inl z =>
      exact
        { weight := fun i => if i = z.1 then 1 else 0
          weight_nonneg := by
            intro i
            by_cases h : i = z.1 <;> simp [h] }
  | inr pq =>
      exact
        { weight := fun i =>
            (if i = pq.1.1 then -S.coeff pq.2.1 0 else 0) +
              (if i = pq.2.1 then S.coeff pq.1.1 0 else 0)
          weight_nonneg := by
            intro i
            have hn : 0 <= -S.coeff pq.2.1 0 := neg_nonneg.mpr pq.2.2.le
            have hp : 0 <= S.coeff pq.1.1 0 := pq.1.2.le
            have hpq : pq.1.1 ≠ pq.2.1 := by
              intro h
              have hp' := pq.1.2
              rw [h] at hp'
              exact (not_lt_of_ge pq.2.2.le) hp'
            by_cases hpi : i = pq.1.1
            · subst i
              simp [hpq, hn]
            · by_cases hni : i = pq.2.1
              · subst i
                simp [hpq.symm, hp]
              · simp [hpi, hni] }

@[simp] theorem elimCombination_zero_coeff (z : ZeroRow S) (j : Fin (n + 1)) :
    (elimCombination S (Sum.inl z)).coeff j = S.coeff z.1 j := by
  classical
  simp [elimCombination, Combination.coeff]

@[simp] theorem elimCombination_pair_coeff
    (p : PosRow S) (q : NegRow S) (j : Fin (n + 1)) :
    (elimCombination S (Sum.inr (p, q))).coeff j =
      (-S.coeff q.1 0) * S.coeff p.1 j +
        S.coeff p.1 0 * S.coeff q.1 j := by
  classical
  simp [elimCombination, Combination.coeff, add_mul, Finset.sum_add_distrib]

@[simp] theorem elimCombination_zero_rhs (z : ZeroRow S) :
    (elimCombination S (Sum.inl z)).rhs = S.rhs z.1 := by
  classical
  simp [elimCombination, Combination.rhs]

@[simp] theorem elimCombination_pair_rhs (p : PosRow S) (q : NegRow S) :
    (elimCombination S (Sum.inr (p, q))).rhs =
      (-S.coeff q.1 0) * S.rhs p.1 + S.coeff p.1 0 * S.rhs q.1 := by
  classical
  simp [elimCombination, Combination.rhs, add_mul, Finset.sum_add_distrib]

/-- Every projected combination cancels the eliminated coordinate. -/
theorem elimCombination_head_zero (r : ElimRow S) :
    (elimCombination S r).coeff 0 = 0 := by
  rcases r with z | ⟨p, q⟩
  · simpa using z.2
  · simp
    ring

/-- Eliminate coordinate zero. -/
noncomputable def eliminate : System n where
  Row := ElimRow S
  rowFintype := inferInstance
  coeff r j := (elimCombination S r).coeff j.succ
  rhs r := (elimCombination S r).rhs

/-- A feasible point projects to the eliminated system. -/
noncomputable def Point.project (P : Point S) : Point (eliminate S) where
  x j := P.x j.succ
  row_le r := by
    have h := (elimCombination S r).valid P
    rw [Fin.sum_univ_succ, elimCombination_head_zero S r, zero_mul, zero_add] at h
    exact h

/-- Tail contribution of an old row at a projected point. -/
def tailValue (P : Point (eliminate S)) (i : S.Row) : ℚ :=
  Finset.univ.sum fun j => S.coeff i j.succ * P.x j

/-- The head-coordinate bound represented by a nonzero-head row. -/
def headBound (P : Point (eliminate S)) (i : S.Row) : ℚ :=
  (S.rhs i - tailValue S P i) / S.coeff i 0

/-- A projected positive/negative pair says that its lower bound is below its
upper bound. -/
theorem neg_headBound_le_pos_headBound
    (P : Point (eliminate S)) (p : PosRow S) (q : NegRow S) :
    headBound S P q.1 <= headBound S P p.1 := by
  have hpair := P.row_le (Sum.inr (p, q))
  have hp0 : S.coeff p.1 0 ≠ 0 := ne_of_gt p.2
  have hq0 : S.coeff q.1 0 ≠ 0 := ne_of_lt q.2
  have hpEq :
      headBound S P p.1 * S.coeff p.1 0 =
        S.rhs p.1 - tailValue S P p.1 := by
    exact div_mul_cancel₀ _ hp0
  have hqEq :
      headBound S P q.1 * S.coeff q.1 0 =
        S.rhs q.1 - tailValue S P q.1 := by
    exact div_mul_cancel₀ _ hq0
  have hpair' :
      (-S.coeff q.1 0) * tailValue S P p.1 +
          S.coeff p.1 0 * tailValue S P q.1 <=
        (-S.coeff q.1 0) * S.rhs p.1 + S.coeff p.1 0 * S.rhs q.1 := by
    simpa [eliminate, tailValue, add_mul, Finset.sum_add_distrib,
      Finset.mul_sum, mul_assoc] using hpair
  have hp := p.2
  have hq := q.2
  have hcore :
      S.coeff p.1 0 * (S.tailValue P q.1 - S.rhs q.1) <=
        (-S.coeff q.1 0) * (S.rhs p.1 - S.tailValue P p.1) := by
    nlinarith [hpair']
  have hscaled :
      (-S.coeff q.1 0) * (headBound S P q.1 * S.coeff p.1 0) <=
        (-S.coeff q.1 0) * (headBound S P p.1 * S.coeff p.1 0) := by
    calc
      (-S.coeff q.1 0) * (headBound S P q.1 * S.coeff p.1 0)
          = -S.coeff p.1 0 * (headBound S P q.1 * S.coeff q.1 0) := by
              ring
      _ = -S.coeff p.1 0 * (S.rhs q.1 - S.tailValue P q.1) := by
              rw [hqEq]
      _ = S.coeff p.1 0 * (S.tailValue P q.1 - S.rhs q.1) := by
              ring
      _ <= (-S.coeff q.1 0) * (S.rhs p.1 - S.tailValue P p.1) := hcore
      _ = (-S.coeff q.1 0) * (headBound S P p.1 * S.coeff p.1 0) := by
              rw [hpEq]
  have htimes :
      headBound S P q.1 * S.coeff p.1 0 <=
        headBound S P p.1 * S.coeff p.1 0 :=
    le_of_mul_le_mul_left hscaled (neg_pos.mpr hq)
  exact le_of_mul_le_mul_right htimes hp

/-- Reconstruct a full point from one head value satisfying all lower and
upper bounds. -/
noncomputable def Point.ofHeadBounds
    (P : Point (eliminate S)) (t : ℚ)
    (hneg : forall q : NegRow S, headBound S P q.1 <= t)
    (hpos : forall p : PosRow S, t <= headBound S P p.1) : Point S where
  x := Fin.cases t P.x
  row_le i := by
    classical
    by_cases hz : S.coeff i 0 = 0
    · let z : ZeroRow S := ⟨i, hz⟩
      have hrow := P.row_le (Sum.inl z)
      simpa [eliminate, tailValue, Fin.sum_univ_succ, hz] using hrow
    · by_cases hp : 0 < S.coeff i 0
      · let p : PosRow S := ⟨i, hp⟩
        have hub := hpos p
        have heq :
            headBound S P i * S.coeff i 0 = S.rhs i - tailValue S P i :=
          div_mul_cancel₀ _ hz
        rw [Fin.sum_univ_succ]
        simp only [Fin.cases_zero, Fin.cases_succ]
        change S.coeff i 0 * t + tailValue S P i <= S.rhs i
        nlinarith
      · have hn : S.coeff i 0 < 0 := lt_of_le_of_ne (le_of_not_gt hp) hz
        let q : NegRow S := ⟨i, hn⟩
        have hlb := hneg q
        have heq :
            headBound S P i * S.coeff i 0 = S.rhs i - tailValue S P i :=
          div_mul_cancel₀ _ hz
        rw [Fin.sum_univ_succ]
        simp only [Fin.cases_zero, Fin.cases_succ]
        change S.coeff i 0 * t + tailValue S P i <= S.rhs i
        nlinarith

/-- Every feasible projected system lifts to the original system. -/
noncomputable def Point.unproject (P : Point (eliminate S)) : Point S := by
  classical
  by_cases hneg : Nonempty (NegRow S)
  · let vals : Finset ℚ :=
      Finset.univ.image fun q : NegRow S => headBound S P q.1
    have hvals : vals.Nonempty := by
      exact Finset.image_nonempty.mpr Finset.univ_nonempty
    let t : ℚ := vals.max' hvals
    apply Point.ofHeadBounds S P t
    · intro q
      apply vals.le_max'
      exact Finset.mem_image.mpr ⟨q, Finset.mem_univ q, rfl⟩
    · intro p
      have htmem : t ∈ vals := vals.max'_mem hvals
      obtain ⟨q, _, hq⟩ := Finset.mem_image.mp htmem
      calc
        t = headBound S P q.1 := hq.symm
        _ <= headBound S P p.1 := neg_headBound_le_pos_headBound S P p q
  · by_cases hpos : Nonempty (PosRow S)
    · let vals : Finset ℚ :=
        Finset.univ.image fun p : PosRow S => headBound S P p.1
      have hvals : vals.Nonempty := by
        exact Finset.image_nonempty.mpr Finset.univ_nonempty
      let t : ℚ := vals.min' hvals
      apply Point.ofHeadBounds S P t
      · intro q
        exact False.elim (hneg ⟨q⟩)
      · intro p
        apply vals.min'_le
        exact Finset.mem_image.mpr ⟨p, Finset.mem_univ p, rfl⟩
    · apply Point.ofHeadBounds S P 0
      · intro q
        exact False.elim (hneg ⟨q⟩)
      · intro p
        exact False.elim (hpos ⟨p⟩)

/-- Lift a zero certificate for the projected system through the manifest row
combinations. -/
noncomputable def ZeroCertificate.lift
    (C : ZeroCertificate (eliminate S)) : ZeroCertificate S := by
  classical
  let y : S.Row -> ℚ := fun i =>
    Finset.univ.sum fun r => C.y r * (elimCombination S r).weight i
  have hy_nonneg : forall i, 0 <= y i := by
    intro i
    exact Finset.sum_nonneg fun r _ =>
      mul_nonneg (C.y_nonneg r) ((elimCombination S r).weight_nonneg i)
  have hswapCoeff : forall j : Fin (n + 1),
      (Finset.univ.sum fun i => y i * S.coeff i j) =
        Finset.univ.sum fun r => C.y r * (elimCombination S r).coeff j := by
    intro j
    simp only [y, Combination.coeff, Finset.sum_mul, Finset.mul_sum, mul_assoc]
    rw [Finset.sum_comm]
  have hswapRhs :
      (Finset.univ.sum fun i => y i * S.rhs i) =
        Finset.univ.sum fun r => C.y r * (elimCombination S r).rhs := by
    simp only [y, Combination.rhs, Finset.sum_mul, Finset.mul_sum, mul_assoc]
    rw [Finset.sum_comm]
  refine
    { y := y
      y_nonneg := hy_nonneg
      coeff_zero := ?_
      rhs_neg := ?_ }
  · intro j
    refine Fin.cases ?_ (fun k => ?_) j
    · rw [hswapCoeff]
      simp [elimCombination_head_zero S]
    · rw [hswapCoeff]
      simpa [eliminate] using C.coeff_zero k
  · rw [hswapRhs]
    simpa [eliminate] using C.rhs_neg

/-- At dimension zero, a negative row is already a zero certificate. -/
noncomputable def zeroCertificateOfNegativeRow
    (S : System 0) (i0 : S.Row) (hi0 : S.rhs i0 < 0) :
    ZeroCertificate S := by
  classical
  exact
    { y := fun i => if i = i0 then 1 else 0
      y_nonneg := by
        intro i
        by_cases h : i = i0 <;> simp [h]
      coeff_zero := fun j => Fin.elim0 j
      rhs_neg := by simpa using hi0 }

/-- An infeasible zero-dimensional system has a negative row. -/
theorem negativeRow_of_not_point
    (S : System 0) (hpoint : Not (Nonempty (Point S))) :
    Exists fun i => S.rhs i < 0 := by
  classical
  by_contra hnone
  apply hpoint
  refine ⟨{ x := fun j => Fin.elim0 j, row_le := ?_ }⟩
  intro i
  have hi : 0 <= S.rhs i := le_of_not_gt fun hlt => hnone ⟨i, hlt⟩
  simpa using hi

/-- Constructive ordinary Farkas alternative, by recursion on the number of
variables. -/
theorem zeroCertificate_of_not_point :
    forall n (S : System n),
      Not (Nonempty (Point S)) -> Nonempty (ZeroCertificate S)
  | 0, S, hpoint => by
      obtain ⟨i, hi⟩ := negativeRow_of_not_point S hpoint
      exact ⟨zeroCertificateOfNegativeRow S i hi⟩
  | n + 1, S, hpoint => by
      have helim : Not (Nonempty (Point (eliminate S))) := by
        rintro ⟨P⟩
        exact hpoint ⟨P.unproject⟩
      obtain ⟨C⟩ := zeroCertificate_of_not_point n (eliminate S) helim
      exact ⟨C.lift⟩

end System

section NonnegativeFin

variable {Row : Type*} [Fintype Row] {n : Nat}

/-- Add the rows `-x_j <= 0`, converting nonnegative feasibility into an
ordinary inequality system. -/
noncomputable def augmentedSystem
    (A : Row -> Fin n -> ℚ) (b : Row -> ℚ) : System n where
  Row := Sum Row (Fin n)
  rowFintype := inferInstance
  coeff r j := match r with
    | Sum.inl i => A i j
    | Sum.inr k => if j = k then -1 else 0
  rhs r := match r with
    | Sum.inl i => b i
    | Sum.inr _ => 0

noncomputable def Feasible.toAugmentedPoint
    {A : Row -> Fin n -> ℚ} {b : Row -> ℚ}
    (P : Feasible A b) : System.Point (augmentedSystem A b) where
  x := P.x
  row_le r := by
    classical
    cases r with
    | inl i => simpa [augmentedSystem] using P.row_le i
    | inr k =>
        simpa [augmentedSystem] using neg_nonpos.mpr (P.x_nonneg k)

noncomputable def System.Point.toFeasible
    {A : Row -> Fin n -> ℚ} {b : Row -> ℚ}
    (P : System.Point (augmentedSystem A b)) : Feasible A b where
  x := P.x
  x_nonneg j := by
    have h := P.row_le (Sum.inr j)
    simpa [augmentedSystem] using h
  row_le i := by
    simpa [augmentedSystem] using P.row_le (Sum.inl i)

/-- Remove the multipliers of the appended nonnegativity rows. -/
noncomputable def System.ZeroCertificate.toNonnegativeCertificate
    {A : Row -> Fin n -> ℚ} {b : Row -> ℚ}
    (C : System.ZeroCertificate (augmentedSystem A b)) : Certificate A b := by
  classical
  refine
    { y := fun i => C.y (Sum.inl i)
      y_nonneg := fun i => C.y_nonneg (Sum.inl i)
      column_nonneg := ?_
      rhs_neg := ?_ }
  · intro j
    have hz := C.coeff_zero j
    have hnonneg := C.y_nonneg (Sum.inr j)
    simp [augmentedSystem] at hz
    linarith
  · simpa [augmentedSystem] using C.rhs_neg

/-- Hard direction of finite Farkas for variables indexed by `Fin n`. -/
theorem certificate_of_not_feasible_fin
    {A : Row -> Fin n -> ℚ} {b : Row -> ℚ}
    (h : Not (Nonempty (Feasible A b))) :
    Nonempty (Certificate A b) := by
  have hpoint : Not (Nonempty (System.Point (augmentedSystem A b))) := by
    rintro ⟨P⟩
    exact h ⟨P.toFeasible⟩
  obtain ⟨C⟩ := System.zeroCertificate_of_not_point n (augmentedSystem A b) hpoint
  exact ⟨C.toNonnegativeCertificate⟩

end NonnegativeFin

section NonnegativeFinite

variable {Row Var : Type*} [Fintype Row] [Fintype Var]

/-- Hard direction of finite rational Farkas for arbitrary finite variable
types. -/
theorem certificate_of_not_feasible
    {A : Row -> Var -> ℚ} {b : Row -> ℚ}
    (h : Not (Nonempty (Feasible A b))) :
    Nonempty (Certificate A b) := by
  classical
  let e : Var ≃ Fin (Fintype.card Var) := Fintype.equivFin Var
  let A' : Row -> Fin (Fintype.card Var) -> ℚ := fun i j => A i (e.symm j)
  have hfin : Not (Nonempty (Feasible A' b)) := by
    rintro ⟨P⟩
    apply h
    refine
      ⟨{ x := fun v => P.x (e v)
         x_nonneg := fun v => P.x_nonneg (e v)
         row_le := ?_ }⟩
    intro i
    have hsum :
        (Finset.univ.sum fun v => A i v * P.x (e v)) =
          Finset.univ.sum fun j => A' i j * P.x j := by
      exact Fintype.sum_equiv e _ _ fun v => by simp [A']
    exact hsum.trans_le (P.row_le i)
  obtain ⟨C⟩ := certificate_of_not_feasible_fin hfin
  refine
    ⟨{ y := C.y
       y_nonneg := C.y_nonneg
       column_nonneg := ?_
       rhs_neg := C.rhs_neg }⟩
  intro v
  simpa [A'] using C.column_nonneg (e v)

/-- Exact finite rational theorem of alternatives. -/
theorem feasible_iff_no_certificate
    {A : Row -> Var -> ℚ} {b : Row -> ℚ} :
    Nonempty (Feasible A b) <-> Not (Nonempty (Certificate A b)) := by
  constructor
  · rintro ⟨P⟩
    exact P.no_certificate
  · intro hcert
    by_contra hfeas
    obtain ⟨C⟩ := certificate_of_not_feasible hfeas
    exact hcert ⟨C⟩

end NonnegativeFinite

end FiniteFarkasRat
end Erdos23Delta0
