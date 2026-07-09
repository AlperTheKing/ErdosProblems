import Erdos23Delta0.WalkParity
import Erdos23Delta0.Ell5UnionCount
import Erdos23Delta0.Ell5CSReduction

namespace Erdos23Delta0
namespace ScratchT6ParityProof

open SimpleGraph Finset

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V} {u v : V}

 theorem no_three_common_edges_len4_same_endpoints
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hne : p.edges.toFinset ≠ q.edges.toFinset) :
    (p.edges.toFinset ∩ q.edges.toFinset).card ≠ 3 := by
  intro h3
  let A : Finset (Sym2 V) := p.edges.toFinset
  let B : Finset (Sym2 V) := q.edges.toFinset
  have hA : A.card = 4 := Ell5CSReduction.geodesic_len4_card_edges p hp hlp
  have hB : B.card = 4 := Ell5CSReduction.geodesic_len4_card_edges q hq hlq
  have hAp : (A \ B).card = 1 := Ell5UnionCount.sdiff_card_one_of_four_inter_three hA h3
  have hBq : (B \ A).card = 1 := by
    have h3' : (B ∩ A).card = 3 := by simpa [Finset.inter_comm] using h3
    exact Ell5UnionCount.sdiff_card_one_of_four_inter_three hB h3'
  obtain ⟨eP, hePsingle⟩ := Finset.card_eq_one.mp hAp
  obtain ⟨eQ, heQsingle⟩ := Finset.card_eq_one.mp hBq
  have hePmemA : eP ∈ A := by
    have : eP ∈ A \ B := by rw [hePsingle]; simp
    simpa using this.1
  have hePnotB : eP ∉ B := by
    have : eP ∈ A \ B := by rw [hePsingle]; simp
    simpa using this.2
  have heQmemB : eQ ∈ B := by
    have : eQ ∈ B \ A := by rw [heQsingle]; simp
    simpa using this.1
  have heQnotA : eQ ∉ A := by
    have : eQ ∈ B \ A := by rw [heQsingle]; simp
    simpa using this.2
  -- Next target: prove eP = eQ by closed-walk parity; contradiction follows.
  have heq : eP = eQ := by
    -- Need to cancel the three common doubled edges in p.append q.reverse.
    admit
  subst heq
  exact heQnotA hePmemA

end ScratchT6ParityProof
end Erdos23Delta0
