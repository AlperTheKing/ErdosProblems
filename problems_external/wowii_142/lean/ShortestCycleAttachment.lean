import Mathlib.Combinatorics.SimpleGraph.Girth

namespace SimpleGraph

open Classical

variable {α : Type*} [DecidableEq α]
variable {G : SimpleGraph α} {a b x : α}

omit [DecidableEq α] in
/-- Closing a path through a vertex outside its support gives a cycle. -/
private lemma Walk.IsPath.concat_two_isCycle
    {p : G.Walk a b} (hp : p.IsPath) (hab : a ≠ b) (hx : x ∉ p.support)
    (hbx : G.Adj b x) (hxa : G.Adj x a) :
    ((p.concat hbx).concat hxa).IsCycle := by
  have hpx : (p.concat hbx).IsPath := hp.concat hx hbx
  rw [← Walk.isCycle_reverse]
  rw [Walk.reverse_concat]
  rw [Walk.cons_isCycle_iff]
  refine ⟨(Walk.isPath_reverse_iff _).2 hpx, ?_⟩
  intro he
  have he' : s(x, a) ∈ (p.concat hbx).edges := by
    have he0 : s(a, x) ∈ (p.concat hbx).edges := by
      simpa only [Walk.edges_reverse, List.mem_reverse] using he
    rw [Sym2.eq_swap]
    exact he0
  have ha : a = (p.concat hbx).penultimate :=
    hpx.eq_penultimate_of_mem_edges he'
  exact hab (by simpa using ha)


/-- If a cycle realizes the girth and has length at least five, a vertex outside
its support has at most one neighbor on the cycle. -/
theorem Walk.IsCycle.outside_neighbor_unique_of_length_eq_girth
    {v a b x : α} {c : G.Walk v v}
    (hc : c.IsCycle) (hcLength : c.length = G.girth) (hg : 5 ≤ G.girth)
    (hx : x ∉ c.support) (ha : a ∈ c.support) (hb : b ∈ c.support)
    (hxa : G.Adj x a) (hxb : G.Adj x b) :
    a = b := by
  by_contra hab
  let r : G.Walk a a := c.rotate ha
  have hrCycle : r.IsCycle := by
    exact hc.rotate ha
  have hbR : b ∈ r.support := by
    exact (c.mem_support_rotate_iff ha).2 hb
  have hxR : x ∉ r.support := by
    intro hxmem
    exact hx ((c.mem_support_rotate_iff ha).1 hxmem)
  let p : G.Walk a b := r.takeUntil b hbR
  let q : G.Walk b a := r.dropUntil b hbR
  have hpPath : p.IsPath := by
    exact hrCycle.isPath_takeUntil hbR
  have hqPath : q.IsPath := by
    apply Walk.IsCycle.isPath_of_append_right (p := p)
      (q := q) (Walk.not_nil_of_ne hab)
    simpa [p, q] using hrCycle
  have hxP : x ∉ p.support := by
    intro hxmem
    exact hxR (r.support_takeUntil_subset hbR hxmem)
  have hxQ : x ∉ q.support := by
    intro hxmem
    exact hxR (r.support_dropUntil_subset hbR hxmem)
  have hpCycle : ((p.concat hxb.symm).concat hxa).IsCycle :=
    hpPath.concat_two_isCycle hab hxP hxb.symm hxa
  have hqCycle : ((q.concat hxa.symm).concat hxb).IsCycle :=
    hqPath.concat_two_isCycle (Ne.symm hab) hxQ hxa.symm hxb
  have hpBound : G.girth ≤ p.length + 2 := by
    simpa only [Walk.length_concat] using G.girth_le_length hpCycle
  have hqBound : G.girth ≤ q.length + 2 := by
    simpa only [Walk.length_concat] using G.girth_le_length hqCycle
  have hrLength : r.length = c.length := by
    dsimp [r, Walk.rotate]
    rw [Walk.length_append, add_comm, ← Walk.length_append, c.take_spec ha]
  have hsplit : p.length + q.length = G.girth := by
    have h0 := congrArg Walk.length (r.take_spec hbR)
    have h1 : p.length + q.length = r.length := by
      simpa only [Walk.length_append, p, q] using h0
    omega
  omega

end SimpleGraph










