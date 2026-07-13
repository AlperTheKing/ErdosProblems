import Erdos23Delta0.Gamma.LiveDetourEndpointSource

/-!
# Additivity of switch loss on a nonedge

For distinct nonadjacent vertices, no graph edge crosses both singleton
switches.  Hence blue and bad boundary counts add separately, and so does
`sigma`.  This is the graph identity used by the live high-slack rotor escape.
-/

namespace Erdos23Delta0
namespace Gamma
namespace SingletonPairSigma

open CertGraph

private theorem crosses_pair_eq_xor
    (u v : Nat) (huv : u ≠ v) (e : Nat × Nat) :
    crossesSet [u, v] e = (crossesSet [u] e != crossesSet [v] e) := by
  by_cases h1 : e.1 = u <;>
    by_cases h2 : e.1 = v <;>
    by_cases h3 : e.2 = u <;>
    by_cases h4 : e.2 = v <;>
    simp_all [crossesSet]

private theorem filter_xor_length_eq_add
    {alpha : Type*} (items : List alpha) (r p q : alpha → Bool)
    (hdisjoint : ∀ a ∈ items, ¬(p a = true ∧ q a = true)) :
    (items.filter fun a => r a && (p a != q a)).length =
      (items.filter fun a => r a && p a).length +
        (items.filter fun a => r a && q a).length := by
  induction items with
  | nil => simp
  | cons a tail ih =>
      have ha := hdisjoint a (by simp)
      have htail : ∀ b ∈ tail, ¬(p b = true ∧ q b = true) := by
        intro b hb
        exact hdisjoint b (by simp [hb])
      have hi := ih htail
      cases hr : r a <;> cases hp : p a <;> cases hq : q a <;>
        simp_all <;> omega

private theorem singleton_crossings_disjoint_of_nonadjacent
    (G : GraphData) (hG : checkGraph G = true)
    (u v : Nat) (huv : u ≠ v) (hnonadj : adjb G u v = false) :
    ∀ e ∈ G.edges,
      ¬(crossesSet [u] e = true ∧ crossesSet [v] e = true) := by
  intro e he hcross
  have hrange := checkGraph_edge_range G hG e he
  have hnorm : normEdge e.1 e.2 = e := by
    unfold normEdge
    simp [hrange.1]
  have hedge : normEdge u v ∈ G.edges := by
    rcases hcross with ⟨hu, hv⟩
    by_cases h1 : e.1 = u <;>
      by_cases h2 : e.1 = v <;>
      by_cases h3 : e.2 = u <;>
      by_cases h4 : e.2 = v <;>
      simp_all [crossesSet, normEdge] <;>
      try
        have hnot : ¬u < v := by omega
        simp [hnot, he]
  have hadj : adjb G u v = true := by
    unfold adjb
    simp [huv, hedge]
  exact Bool.false_ne_true (hnonadj.symm.trans hadj)

theorem dB_pair_eq_add_singletons_of_nonadjacent
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (u v : Nat) (huv : u ≠ v) (hnonadj : adjb G u v = false) :
    dB G c [u, v] = dB G c [u] + dB G c [v] := by
  unfold dB
  have hdisjoint :=
    singleton_crossings_disjoint_of_nonadjacent G hG u v huv hnonadj
  rw [show (G.edges.filter fun e => blueb G c e.1 e.2 && crossesSet [u, v] e) =
      G.edges.filter (fun e => blueb G c e.1 e.2 &&
        (crossesSet [u] e != crossesSet [v] e)) by
    apply List.filter_congr
    intro e _
    rw [crosses_pair_eq_xor u v huv e]]
  exact filter_xor_length_eq_add G.edges
    (fun e => blueb G c e.1 e.2)
    (crossesSet [u]) (crossesSet [v]) hdisjoint

theorem dM_pair_eq_add_singletons_of_nonadjacent
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (u v : Nat) (huv : u ≠ v) (hnonadj : adjb G u v = false) :
    dM G c [u, v] = dM G c [u] + dM G c [v] := by
  unfold dM
  have hdisjoint :=
    singleton_crossings_disjoint_of_nonadjacent G hG u v huv hnonadj
  rw [show (G.edges.filter fun e => badb G c e.1 e.2 && crossesSet [u, v] e) =
      G.edges.filter (fun e => badb G c e.1 e.2 &&
        (crossesSet [u] e != crossesSet [v] e)) by
    apply List.filter_congr
    intro e _
    rw [crosses_pair_eq_xor u v huv e]]
  exact filter_xor_length_eq_add G.edges
    (fun e => badb G c e.1 e.2)
    (crossesSet [u]) (crossesSet [v]) hdisjoint

/-- Exact signed switch-loss additivity on a graph nonedge. -/
theorem sigma_pair_eq_add_singletons_of_nonadjacent
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (u v : Nat) (huv : u ≠ v) (hnonadj : adjb G u v = false) :
    sigma G c [u, v] = sigma G c [u] + sigma G c [v] := by
  unfold sigma
  rw [dB_pair_eq_add_singletons_of_nonadjacent G c hG u v huv hnonadj,
    dM_pair_eq_add_singletons_of_nonadjacent G c hG u v huv hnonadj]
  omega

/-- A loss-two vertex paired with a nonnegative-loss nonneighbor gives the
literal production common-blue threshold. -/
theorem two_le_sigma_pair_of_two_le_left
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (u v : Nat) (huv : u ≠ v) (hnonadj : adjb G u v = false)
    (hu : (2 : Int) ≤ sigma G c [u])
    (hv : (0 : Int) ≤ sigma G c [v]) :
    (2 : Int) ≤ sigma G c [u, v] := by
  rw [sigma_pair_eq_add_singletons_of_nonadjacent G c hG u v huv hnonadj]
  omega

private theorem adjb_of_blueb
    {G : GraphData} {c : CutData} {u v : Nat}
    (h : blueb G c u v = true) : adjb G u v = true := by
  unfold blueb at h
  simp only [Bool.and_eq_true] at h
  exact h.1

private theorem ne_of_adjb
    {G : GraphData} {u v : Nat} (h : adjb G u v = true) : u ≠ v := by
  unfold adjb at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

/-- Two distinct blue neighbours of one vertex are nonadjacent in a
triangle-free graph. -/
theorem nonadjacent_of_common_blue
    {G : GraphData} {c : CutData} (htri : TriangleFree G)
    (left owner right : Fin G.n) (hlr : left ≠ right)
    (hleft : blueb G c left.1 owner.1 = true)
    (hright : blueb G c right.1 owner.1 = true) :
    adjb G left.1 right.1 = false := by
  have hlo : adjb G left.1 owner.1 = true := adjb_of_blueb hleft
  have hro : adjb G right.1 owner.1 = true := adjb_of_blueb hright
  have hor : adjb G owner.1 right.1 = true := by
    rw [adjb_comm]
    exact hro
  have hlone : left.1 ≠ owner.1 := ne_of_adjb hlo
  have horne : owner.1 ≠ right.1 := ne_of_adjb hor
  cases hcross : adjb G left.1 right.1 with
  | false => rfl
  | true =>
      exact False.elim <| htri left.1 owner.1 right.1
        left.isLt owner.isLt right.isLt hlone horne
        (Fin.val_injective.ne hlr) ⟨hlo, hor, hcross⟩

/-- Every singleton switch has nonnegative loss at a checked maximum cut. -/
theorem singleton_sigma_nonneg_of_isMaxCut
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (hmax : IsMaxCut G c) (v : Fin G.n) :
    (0 : Int) ≤ sigma G c [v.1] := by
  exact sigmaNonneg_of_badCount_min G c hG hmax.valid hmax.min_bad [v.1]

/-- Graph-complete strong-pair premise: a loss-two blue neighbour and any
other distinct blue neighbour form a nonedge of pair loss at least two. -/
theorem common_blue_pair_two_le_of_left_loss
    {G : GraphData} {c : CutData} (hG : checkGraph G = true)
    (htri : TriangleFree G) (hmax : IsMaxCut G c)
    (left owner right : Fin G.n) (hlr : left ≠ right)
    (hleft : blueb G c left.1 owner.1 = true)
    (hright : blueb G c right.1 owner.1 = true)
    (hloss : (2 : Int) ≤ sigma G c [left.1]) :
    (2 : Int) ≤ sigma G c [left.1, right.1] := by
  have hnonadj := nonadjacent_of_common_blue htri left owner right hlr hleft hright
  have hrightLoss := singleton_sigma_nonneg_of_isMaxCut G c hG hmax right
  exact two_le_sigma_pair_of_two_le_left G c hG left.1 right.1
    (Fin.val_injective.ne hlr) hnonadj hloss hrightLoss

#print axioms sigma_pair_eq_add_singletons_of_nonadjacent
#print axioms two_le_sigma_pair_of_two_le_left
#print axioms nonadjacent_of_common_blue
#print axioms singleton_sigma_nonneg_of_isMaxCut
#print axioms common_blue_pair_two_le_of_left_loss

end SingletonPairSigma
end Gamma
end Erdos23Delta0
