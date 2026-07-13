import agent_r7_strong_split_v3

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- Once a dual/crossing argument supplies a proper complementary restriction,
all-length-five purity gives the compiled pure-lens split automatically. -/
theorem pureLensCageSplit_of_all_ell5_proper
    (F : BankFrame (V := V)) (C : AmbientCage G c) (U : Finset V)
    (hell5 : forall a, a ∈ C.atoms -> Distances.ell G c a.u a.v = 5)
    (hLeft : ProperRelative C (restrict C U))
    (hRight : ProperRelative C (restrictCompl C U)) :
    Ell5PureLensCageInterface.PureLensCageSplit
      (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
      C (restrict C U) (restrictCompl C U) := by
  apply concretePureLensCageSplit F C U hLeft hRight
    (strongPureLensAtomSplit_of_all_ell5 C U hell5)
  change Disjoint U (C.verts \ U)
  rw [Finset.disjoint_left]
  intro x hxU hxRight
  exact (Finset.mem_sdiff.mp hxRight).2 hxU

#print axioms pureLensCageSplit_of_all_ell5_proper

end ConcreteCage
end Ell5
end Erdos23Delta0
