import Erdos23Delta0.Gamma.SaturatedRotorSupportPersistence

/-!
# Bad-star vertex-cover obstruction to a covered active/support probe

This is the row-local graph core of the `t = 3` K3,3 exclusion.  If every
bad row lies on the owner's cut shore and one endpoint is either the owner or
its bad neighbour, then a checked row cannot contain two blue neighbours of
that owner while one of those owner edges remains active/off-support.
-/

namespace Erdos23Delta0
namespace Gamma
namespace BadStarCoverFreeness

open CertGraph
open MinimumDemandRowSelection

private theorem adjb_of_blueb
    {G : GraphData} {c : CutData} {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem adjb_of_badb
    {G : GraphData} {c : CutData} {u v : Nat}
    (h : badb G c u v = true) : adjb G u v = true := by
  unfold badb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem ne_of_adjb
    {G : GraphData} {u v : Nat} (h : adjb G u v = true) : u ≠ v := by
  unfold adjb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

private theorem side_ne_of_blueb
    {G : GraphData} {c : CutData} {u v : Nat}
    (h : blueb G c u v = true) : sideb c u ≠ sideb c v := by
  unfold blueb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.2

private theorem checked_five_row_steps
    {G : GraphData} {c : CutData}
    (u p h q w : Fin G.n)
    (row : Row5)
    (hverts : row.verts = [u.1, p.1, h.1, q.1, w.1])
    (hcheck : checkRow5 G c u.1 w.1 row = true) :
    blueb G c u.1 p.1 = true ∧
      blueb G c p.1 h.1 = true ∧
      blueb G c h.1 q.1 = true ∧
      blueb G c q.1 w.1 = true := by
  have hall := hcheck
  unfold checkRow5 at hall
  rw [hverts] at hall
  simp only [Bool.and_eq_true] at hall
  have hpath :
      (List.zip [u.1, p.1, h.1, q.1, w.1]
        [u.1, p.1, h.1, q.1, w.1].tail).all
          (fun e => blueb G c e.1 e.2) = true := by
    aesop
  simpa using hpath

private theorem opposite_members_are_odd_positions
    {G : GraphData} {c : CutData}
    (v u p h q w x s : Fin G.n)
    (hpath : blueb G c u.1 p.1 = true ∧
      blueb G c p.1 h.1 = true ∧
      blueb G c h.1 q.1 = true ∧
      blueb G c q.1 w.1 = true)
    (huv : sideb c u.1 = sideb c v.1)
    (hwv : sideb c w.1 = sideb c v.1)
    (hvx : blueb G c v.1 x.1 = true)
    (hvs : blueb G c v.1 s.1 = true)
    (hxs : x ≠ s)
    (hxmem : x.1 ∈ [u.1, p.1, h.1, q.1, w.1])
    (hsmem : s.1 ∈ [u.1, p.1, h.1, q.1, w.1]) :
    (p = x ∧ q = s) ∨ (p = s ∧ q = x) := by
  have hup := side_ne_of_blueb hpath.1
  have hph := side_ne_of_blueb hpath.2.1
  have hhq := side_ne_of_blueb hpath.2.2.1
  have hqw := side_ne_of_blueb hpath.2.2.2
  have hvxSide := side_ne_of_blueb hvx
  have hvsSide := side_ne_of_blueb hvs
  have hhu : sideb c h.1 = sideb c u.1 := by
    revert hup hph
    cases sideb c u.1 <;> cases sideb c p.1 <;>
      cases sideb c h.1 <;> simp_all
  have hqu : sideb c q.1 ≠ sideb c u.1 := by
    rw [← hhu]
    exact hhq.symm
  have hwu : sideb c w.1 = sideb c u.1 := by
    exact hwv.trans huv.symm
  have hxOdd : x = p ∨ x = q := by
    simp at hxmem
    rcases hxmem with hx | hx | hx | hx | hx
    · exfalso
      have : sideb c x.1 = sideb c v.1 := by simpa [hx] using huv
      exact hvxSide this.symm
    · exact Or.inl (Fin.ext hx)
    · exfalso
      have : sideb c x.1 = sideb c v.1 := by
        rw [hx, hhu, huv]
      exact hvxSide this.symm
    · exact Or.inr (Fin.ext hx)
    · exfalso
      have : sideb c x.1 = sideb c v.1 := by
        rw [hx]
        exact hwv
      exact hvxSide this.symm
  have hsOdd : s = p ∨ s = q := by
    simp at hsmem
    rcases hsmem with hs | hs | hs | hs | hs
    · exfalso
      have : sideb c s.1 = sideb c v.1 := by simpa [hs] using huv
      exact hvsSide this.symm
    · exact Or.inl (Fin.ext hs)
    · exfalso
      have : sideb c s.1 = sideb c v.1 := by
        rw [hs, hhu, huv]
      exact hvsSide this.symm
    · exact Or.inr (Fin.ext hs)
    · exfalso
      have : sideb c s.1 = sideb c v.1 := by
        rw [hs]
        exact hwv
      exact hvsSide this.symm
  rcases hxOdd with hxp | hxq <;> rcases hsOdd with hsp | hsq
  · exact False.elim (hxs (hxp.trans hsp.symm))
  · exact Or.inl ⟨hxp.symm, hsq.symm⟩
  · exact Or.inr ⟨hsp.symm, hxq.symm⟩
  · exact False.elim (hxs (hxq.trans hsq.symm))

/-- A checked row of a bad edge covered by the closed bad star at `v` cannot
contain the active/support pair `x,s`. -/
theorem bad_star_cover_row_impossible
    {G : GraphData} {c : CutData}
    (v u p h q w x s : Fin G.n) (row : Row5)
    (htri : TriangleFree G)
    (hverts : row.verts = [u.1, p.1, h.1, q.1, w.1])
    (hcheck : checkRow5 G c u.1 w.1 row = true)
    (huv : sideb c u.1 = sideb c v.1)
    (hwv : sideb c w.1 = sideb c v.1)
    (hvx : blueb G c v.1 x.1 = true)
    (hvs : blueb G c v.1 s.1 = true)
    (hxs : x ≠ s)
    (hxmem : x.1 ∈ row.verts) (hsmem : s.1 ∈ row.verts)
    (hcover : v = u ∨ v = w ∨
      badb G c v.1 u.1 = true ∨ badb G c v.1 w.1 = true)
    (hxOffSupport : normEdge v.1 x.1 ∉ rowPathEdges row) : False := by
  have hpath := checked_five_row_steps u p h q w row hverts hcheck
  have hpositions := opposite_members_are_odd_positions
    v u p h q w x s hpath huv hwv hvx hvs hxs
    (by simpa [hverts] using hxmem) (by simpa [hverts] using hsmem)
  rcases hpositions with hpositions | hpositions
  · rcases hpositions with ⟨hp, hq⟩
    subst p
    subst q
    rcases hcover with rfl | rfl | hbad | hbad
    · exact hxOffSupport <|
        SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge htri hcheck
          (by simp [hverts]) (by simp [hverts]) hvx
    · exact hxOffSupport <|
        SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge htri hcheck
          (by simp [hverts]) (by simp [hverts]) hvx
    · have hvu := adjb_of_badb hbad
      have hup := adjb_of_blueb hpath.1
      exact htri v.1 u.1 x.1 v.isLt u.isLt x.isLt
        (ne_of_adjb hvu) (ne_of_adjb hup) (ne_of_adjb (adjb_of_blueb hvx))
        ⟨hvu, hup, adjb_of_blueb hvx⟩
    · have hvw := adjb_of_badb hbad
      have hws : adjb G w.1 s.1 = true := by
        rw [adjb_comm]
        exact adjb_of_blueb hpath.2.2.2
      exact htri v.1 w.1 s.1 v.isLt w.isLt s.isLt
        (ne_of_adjb hvw) (ne_of_adjb hws) (ne_of_adjb (adjb_of_blueb hvs))
        ⟨hvw, hws, adjb_of_blueb hvs⟩
  · rcases hpositions with ⟨hp, hq⟩
    subst p
    subst q
    rcases hcover with rfl | rfl | hbad | hbad
    · exact hxOffSupport <|
        SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge htri hcheck
          (by simp [hverts]) (by simp [hverts]) hvx
    · exact hxOffSupport <|
        SaturatedRotorSupportPersistence.checkedRow_blue_cooccur_implies_pathEdge htri hcheck
          (by simp [hverts]) (by simp [hverts]) hvx
    · have hvu := adjb_of_badb hbad
      have hus := adjb_of_blueb hpath.1
      exact htri v.1 u.1 s.1 v.isLt u.isLt s.isLt
        (ne_of_adjb hvu) (ne_of_adjb hus) (ne_of_adjb (adjb_of_blueb hvs))
        ⟨hvu, hus, adjb_of_blueb hvs⟩
    · have hvw := adjb_of_badb hbad
      have hwx : adjb G w.1 x.1 = true := by
        rw [adjb_comm]
        exact adjb_of_blueb hpath.2.2.2
      exact htri v.1 w.1 x.1 v.isLt w.isLt x.isLt
        (ne_of_adjb hvw) (ne_of_adjb hwx) (ne_of_adjb (adjb_of_blueb hvx))
        ⟨hvw, hwx, adjb_of_blueb hvx⟩

#print axioms bad_star_cover_row_impossible

end BadStarCoverFreeness
end Gamma
end Erdos23Delta0
