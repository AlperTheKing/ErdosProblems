import Erdos23Delta0.Gamma.MinimumDemandRowSelection

/-!
# Live middle swaps force a cross-outer endpoint pair

If two checked rows differ only by middle `m` versus `v`, then their common
positions `x,y` are blue neighbours of both middles, while the bad endpoints
`a,b` lie strictly outside the two middles and attach through `x,y`.
-/

namespace Erdos23Delta0
namespace Gamma
namespace LiveMiddleSwapCrossOuter

open CertGraph

private theorem checked_steps
    {G : GraphData} {c : CutData}
    (a x h y b : Fin G.n) (row : Row5)
    (hverts : row.verts = [a.1, x.1, h.1, y.1, b.1])
    (hcheck : checkRow5 G c a.1 b.1 row = true) :
    blueb G c a.1 x.1 = true ∧
      blueb G c x.1 h.1 = true ∧
      blueb G c h.1 y.1 = true ∧
      blueb G c y.1 b.1 = true := by
  have hall := hcheck
  unfold checkRow5 at hall
  rw [hverts] at hall
  simp only [Bool.and_eq_true] at hall
  have hpath :
      (List.zip [a.1, x.1, h.1, y.1, b.1]
        [a.1, x.1, h.1, y.1, b.1].tail).all
          (fun e => blueb G c e.1 e.2) = true := by
    aesop
  simpa using hpath

private theorem checked_nodup
    {G : GraphData} {c : CutData}
    (a x h y b : Fin G.n) (row : Row5)
    (hverts : row.verts = [a.1, x.1, h.1, y.1, b.1])
    (hcheck : checkRow5 G c a.1 b.1 row = true) :
    ([a.1, x.1, h.1, y.1, b.1] : List Nat).Nodup := by
  have hall := hcheck
  unfold checkRow5 at hall
  rw [hverts] at hall
  simp only [Bool.and_eq_true] at hall
  have hnodup : decide ([a.1, x.1, h.1, y.1, b.1] : List Nat).Nodup = true := by
    aesop
  exact of_decide_eq_true hnodup

/-- Checked live rows expose the cross-outer geometry needed by the exact
support-graph census. -/
theorem live_middle_swap_has_cross_outer
    {G : GraphData} {c : CutData}
    (a x m y b v : Fin G.n) (rowM rowV : Row5)
    (hmverts : rowM.verts = [a.1, x.1, m.1, y.1, b.1])
    (hvverts : rowV.verts = [a.1, x.1, v.1, y.1, b.1])
    (hmcheck : checkRow5 G c a.1 b.1 rowM = true)
    (hvcheck : checkRow5 G c a.1 b.1 rowV = true) :
    blueb G c a.1 x.1 = true ∧
      blueb G c x.1 m.1 = true ∧
      blueb G c x.1 v.1 = true ∧
      blueb G c m.1 y.1 = true ∧
      blueb G c v.1 y.1 = true ∧
      blueb G c y.1 b.1 = true ∧
      a ≠ m ∧ a ≠ v ∧ b ≠ m ∧ b ≠ v ∧ x ≠ y := by
  have hm := checked_steps a x m y b rowM hmverts hmcheck
  have hv := checked_steps a x v y b rowV hvverts hvcheck
  have hmNodup := checked_nodup a x m y b rowM hmverts hmcheck
  have hvNodup := checked_nodup a x v y b rowV hvverts hvcheck
  have ham : a ≠ m := by
    intro h
    subst m
    simp at hmNodup
  have hav : a ≠ v := by
    intro h
    subst v
    simp at hvNodup
  have hbm : b ≠ m := by
    intro h
    subst m
    simp at hmNodup
  have hbv : b ≠ v := by
    intro h
    subst v
    simp at hvNodup
  have hxy : x ≠ y := by
    intro h
    subst y
    simp at hmNodup
  exact ⟨hm.1, hm.2.1, hv.2.1, hm.2.2.1, hv.2.2.1,
    hm.2.2.2, ham, hav, hbm, hbv, hxy⟩

#print axioms live_middle_swap_has_cross_outer

end LiveMiddleSwapCrossOuter
end Gamma
end Erdos23Delta0
