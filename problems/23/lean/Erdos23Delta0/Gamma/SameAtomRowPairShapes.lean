import Erdos23Delta0.CertGraph

/-!
# Intersection shapes of two length-four rows of one bad edge

Two blue length-four paths with the same bad closing edge can share internal
vertices only at equal positions.  Every misaligned identification creates a
literal triangle, using either the two adjacent path edges or the bad closing
edge.  Hence two distinct rows have exactly one of seven aligned internal
sharing masks.  This is the graph-derived first layer of the R57 finite
normalizer; it does not assume a selected row tuple or a flow.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SameAtomRowPairShapes

open CertGraph

variable {G : GraphData} {c : CutData}

/-- Two ordered blue length-four rows with common endpoints and the same bad
closing edge.  All vertices are proof-carrying graph vertices. -/
structure Pair where
  leftEndpoint : Fin G.n
  rightEndpoint : Fin G.n
  left1 : Fin G.n
  left2 : Fin G.n
  left3 : Fin G.n
  right1 : Fin G.n
  right2 : Fin G.n
  right3 : Fin G.n
  left01 : blueb G c leftEndpoint.1 left1.1 = true
  left12 : blueb G c left1.1 left2.1 = true
  left23 : blueb G c left2.1 left3.1 = true
  left34 : blueb G c left3.1 rightEndpoint.1 = true
  right01 : blueb G c leftEndpoint.1 right1.1 = true
  right12 : blueb G c right1.1 right2.1 = true
  right23 : blueb G c right2.1 right3.1 = true
  right34 : blueb G c right3.1 rightEndpoint.1 = true
  closing_bad : badb G c leftEndpoint.1 rightEndpoint.1 = true
  rows_distinct :
    left1 ≠ right1 ∨ left2 ≠ right2 ∨ left3 ≠ right3

namespace Pair

variable (P : Pair (G := G) (c := c))

private theorem adjb_of_blueb {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem adjb_of_badb {u v : Nat}
    (h : badb G c u v = true) : adjb G u v = true := by
  unfold badb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem ne_of_adjb {u v : Nat}
    (h : adjb G u v = true) : u ≠ v := by
  unfold adjb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

private theorem triangle_false
    (htri : TriangleFree G)
    (x y z : Fin G.n)
    (hxy : adjb G x.1 y.1 = true)
    (hyz : adjb G y.1 z.1 = true)
    (hxz : adjb G x.1 z.1 = true) : False :=
  htri x.1 y.1 z.1 x.isLt y.isLt z.isLt
    (ne_of_adjb hxy) (ne_of_adjb hyz) (ne_of_adjb hxz)
    ⟨hxy, hyz, hxz⟩

/-- First right internal vertex cannot equal the second left one. -/
theorem right1_ne_left2 (htri : TriangleFree G) :
    P.right1 ≠ P.left2 := by
  intro h
  have hcross :
      adjb G P.leftEndpoint.1 P.left2.1 = true := by
    simpa [h] using adjb_of_blueb P.right01
  exact triangle_false htri P.leftEndpoint P.left1 P.left2
    (adjb_of_blueb P.left01) (adjb_of_blueb P.left12)
    hcross
/-- First right internal vertex cannot equal the third left one. -/
theorem right1_ne_left3 (htri : TriangleFree G) :
    P.right1 ≠ P.left3 := by
  intro h
  have hcross :
      adjb G P.leftEndpoint.1 P.left3.1 = true := by
    simpa [h] using adjb_of_blueb P.right01
  exact triangle_false htri P.leftEndpoint P.left3 P.rightEndpoint
    hcross (adjb_of_blueb P.left34)
    (adjb_of_badb P.closing_bad)
/-- Second right internal vertex cannot equal the first left one. -/
theorem right2_ne_left1 (htri : TriangleFree G) :
    P.right2 ≠ P.left1 := by
  intro h
  have hcross : adjb G P.right1.1 P.left1.1 = true := by
    simpa [h] using adjb_of_blueb P.right12
  exact triangle_false htri P.leftEndpoint P.right1 P.left1
    (adjb_of_blueb P.right01) hcross
    (adjb_of_blueb P.left01)
/-- Second right internal vertex cannot equal the third left one. -/
theorem right2_ne_left3 (htri : TriangleFree G) :
    P.right2 ≠ P.left3 := by
  intro h
  have hcross : adjb G P.left3.1 P.right3.1 = true := by
    simpa [h] using adjb_of_blueb P.right23
  exact triangle_false htri P.left3 P.right3 P.rightEndpoint
    hcross (adjb_of_blueb P.right34)
    (adjb_of_blueb P.left34)
/-- Third right internal vertex cannot equal the first left one. -/
theorem right3_ne_left1 (htri : TriangleFree G) :
    P.right3 ≠ P.left1 := by
  intro h
  have hcross : adjb G P.left1.1 P.rightEndpoint.1 = true := by
    simpa [h] using adjb_of_blueb P.right34
  exact triangle_false htri P.leftEndpoint P.left1 P.rightEndpoint
    (adjb_of_blueb P.left01) hcross
    (adjb_of_badb P.closing_bad)
/-- Third right internal vertex cannot equal the second left one. -/
theorem right3_ne_left2 (htri : TriangleFree G) :
    P.right3 ≠ P.left2 := by
  intro h
  have hcross : adjb G P.left2.1 P.rightEndpoint.1 = true := by
    simpa [h] using adjb_of_blueb P.right34
  exact triangle_false htri P.left2 P.left3 P.rightEndpoint
    (adjb_of_blueb P.left23) (adjb_of_blueb P.left34)
    hcross
/-- Every cross-row internal identification is position-aligned. -/
theorem cross_identification_aligned
    (htri : TriangleFree G) (i j : Fin 3)
    (hij : (![P.right1, P.right2, P.right3] i) =
      (![P.left1, P.left2, P.left3] j)) : i = j := by
  fin_cases i <;> fin_cases j <;> simp at hij ⊢
  all_goals first
    | exact (P.right1_ne_left2 htri hij).elim
    | exact (P.right1_ne_left3 htri hij).elim
    | exact (P.right2_ne_left1 htri hij).elim
    | exact (P.right2_ne_left3 htri hij).elim
    | exact (P.right3_ne_left1 htri hij).elim
    | exact (P.right3_ne_left2 htri hij).elim

/-- The seven proper subsets of the three aligned internal positions. -/
def SevenAlignedShape : Prop :=
  (P.right1 ≠ P.left1 ∧ P.right2 ≠ P.left2 ∧ P.right3 ≠ P.left3) ∨
  (P.right1 = P.left1 ∧ P.right2 ≠ P.left2 ∧ P.right3 ≠ P.left3) ∨
  (P.right1 ≠ P.left1 ∧ P.right2 = P.left2 ∧ P.right3 ≠ P.left3) ∨
  (P.right1 ≠ P.left1 ∧ P.right2 ≠ P.left2 ∧ P.right3 = P.left3) ∨
  (P.right1 = P.left1 ∧ P.right2 = P.left2 ∧ P.right3 ≠ P.left3) ∨
  (P.right1 = P.left1 ∧ P.right2 ≠ P.left2 ∧ P.right3 = P.left3) ∨
  (P.right1 ≠ P.left1 ∧ P.right2 = P.left2 ∧ P.right3 = P.left3)

theorem seven_aligned_shape : P.SevenAlignedShape := by
  have hnotall :
      ¬(P.right1 = P.left1 ∧ P.right2 = P.left2 ∧
        P.right3 = P.left3) := by
    rintro ⟨h1, h2, h3⟩
    rcases P.rows_distinct with h | h | h
    · exact h h1.symm
    · exact h h2.symm
    · exact h h3.symm
  unfold SevenAlignedShape
  by_cases h1 : P.right1 = P.left1 <;>
    by_cases h2 : P.right2 = P.left2 <;>
      by_cases h3 : P.right3 = P.left3 <;> simp_all
private theorem list_eq_five_of_length {xs : List Nat}
    (h : xs.length = 5) :
    ∃ a b d e f, xs = [a, b, d, e, f] := by
  rcases xs with _ | ⟨a, xs⟩
  · simp at h
  rcases xs with _ | ⟨b, xs⟩
  · simp at h
  rcases xs with _ | ⟨d, xs⟩
  · simp at h
  rcases xs with _ | ⟨e, xs⟩
  · simp at h
  rcases xs with _ | ⟨f, xs⟩
  · simp at h
  rcases xs with _ | ⟨g, xs⟩
  · exact ⟨a, b, d, e, f, rfl⟩
  · simp at h

/-- Two literal checked rows with the same bad endpoints instantiate the
graph-only role structure used by the seven-shape classifier. -/
theorem exists_pair_of_checked_rows
    {u v : Nat} {left right : Row5}
    (hleft : checkRow5 G c u v left = true)
    (hright : checkRow5 G c u v right = true)
    (hdifferent : left.verts ≠ right.verts) :
    ∃ P : Pair (G := G) (c := c),
      left.verts =
        [P.leftEndpoint.1, P.left1.1, P.left2.1, P.left3.1,
          P.rightEndpoint.1] ∧
      right.verts =
        [P.leftEndpoint.1, P.right1.1, P.right2.1, P.right3.1,
          P.rightEndpoint.1] := by
  have hl := hleft
  have hr := hright
  unfold checkRow5 at hl hr
  simp only [Bool.and_eq_true] at hl hr
  have hllen : left.verts.length = 5 := of_decide_eq_true (by aesop)
  have hrlen : right.verts.length = 5 := of_decide_eq_true (by aesop)
  rcases list_eq_five_of_length hllen with ⟨a, l1, l2, l3, b, hL⟩
  rcases list_eq_five_of_length hrlen with ⟨a', r1, r2, r3, b', hR⟩
  have hLbounds :
      a < G.n ∧ l1 < G.n ∧ l2 < G.n ∧ l3 < G.n ∧ b < G.n := by
    rw [hL] at hl
    simp at hl
    aesop
  have hRbounds :
      a' < G.n ∧ r1 < G.n ∧ r2 < G.n ∧ r3 < G.n ∧ b' < G.n := by
    rw [hR] at hr
    simp at hr
    aesop
  have ha : a = u := by
    have h : decide (left.verts.head? = some u) = true := by aesop
    simpa [hL] using of_decide_eq_true h
  have hb : b = v := by
    have h : decide (left.verts.getLast? = some v) = true := by aesop
    simpa [hL] using of_decide_eq_true h
  have ha' : a' = u := by
    have h : decide (right.verts.head? = some u) = true := by aesop
    simpa [hR] using of_decide_eq_true h
  have hb' : b' = v := by
    have h : decide (right.verts.getLast? = some v) = true := by aesop
    simpa [hR] using of_decide_eq_true h
  have hLpath :
      blueb G c a l1 = true ∧ blueb G c l1 l2 = true ∧
        blueb G c l2 l3 = true ∧ blueb G c l3 b = true := by
    have h : (List.zip left.verts left.verts.tail).all
        (fun p => blueb G c p.1 p.2) = true := by aesop
    simpa [hL] using h
  have hRpath :
      blueb G c a' r1 = true ∧ blueb G c r1 r2 = true ∧
        blueb G c r2 r3 = true ∧ blueb G c r3 b' = true := by
    have h : (List.zip right.verts right.verts.tail).all
        (fun p => blueb G c p.1 p.2) = true := by aesop
    simpa [hR] using h
  have hbad : badb G c u v = true := by aesop
  subst a
  subst b
  subst a'
  subst b'
  have hrows : l1 ≠ r1 ∨ l2 ≠ r2 ∨ l3 ≠ r3 := by
    by_contra h
    simp only [not_or, not_ne_iff] at h
    apply hdifferent
    simpa [hL, hR, h.1, h.2.1, h.2.2]
  let P : Pair (G := G) (c := c) :=
    { leftEndpoint := ⟨u, hLbounds.1⟩
      rightEndpoint := ⟨v, hLbounds.2.2.2.2⟩
      left1 := ⟨l1, hLbounds.2.1⟩
      left2 := ⟨l2, hLbounds.2.2.1⟩
      left3 := ⟨l3, hLbounds.2.2.2.1⟩
      right1 := ⟨r1, hRbounds.2.1⟩
      right2 := ⟨r2, hRbounds.2.2.1⟩
      right3 := ⟨r3, hRbounds.2.2.2.1⟩
      left01 := hLpath.1
      left12 := hLpath.2.1
      left23 := hLpath.2.2.1
      left34 := hLpath.2.2.2
      right01 := hRpath.1
      right12 := hRpath.2.1
      right23 := hRpath.2.2.1
      right34 := hRpath.2.2.2
      closing_bad := hbad
      rows_distinct := by
        rcases hrows with h | h | h
        · exact Or.inl (fun heq => h (congrArg Fin.val heq))
        · exact Or.inr (Or.inl (fun heq => h (congrArg Fin.val heq)))
        · exact Or.inr (Or.inr (fun heq => h (congrArg Fin.val heq))) }
  exact ⟨P, by simpa [P] using hL, by simpa [P] using hR⟩

#print axioms exists_pair_of_checked_rows
#print axioms right1_ne_left2
#print axioms right1_ne_left3
#print axioms right2_ne_left1
#print axioms right2_ne_left3
#print axioms right3_ne_left1
#print axioms right3_ne_left2
#print axioms cross_identification_aligned
#print axioms seven_aligned_shape

end Pair
end SameAtomRowPairShapes
end Gamma
end Erdos23Delta0
