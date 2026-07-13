import Erdos23Delta0.CollisionResidualIdentity

namespace Erdos23Delta0.Gamma.CheckedSoftCollisionTwoCover

open scoped BigOperators
open CollisionResidualIdentity

def n4 (x y : Fin 4) : Nat :=
  if x.1 * 4 + y.1 < 9 then 2 else 1

theorem n4_freeMass : freeMass n4 = 0 := by
  norm_num [freeMass, n4, Fin.sum_univ_succ]

theorem n4_collisionMass : collisionMass n4 = 9 := by
  norm_num [collisionMass, n4, Fin.sum_univ_succ]

theorem n4_total :
    (∑ x : Fin 4, ∑ y : Fin 4, (n4 x y : ℤ)) = 25 := by
  norm_num [n4, Fin.sum_univ_succ]

theorem n4_negative_residual :
    ¬ 0 ≤ (Fintype.card (Fin 4) : ℤ) ^ 2 - 25 * (1 : ℤ) := by
  norm_num

#print axioms n4_freeMass
#print axioms n4_collisionMass
#print axioms n4_total
#print axioms n4_negative_residual

end Erdos23Delta0.Gamma.CheckedSoftCollisionTwoCover
