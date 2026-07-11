import Erdos23Delta0.Gamma.CollisionOwnerLoadReduction

/-!
# Exact owner-balance turnover under one row incidence

The collision contribution of a pair of multiplicity `k` is
`2 * (k - 1)`.  A zero pair supplies two same-first halves, or one when the
pair is an active edge and half zero is reserved.  Decreasing a nonactive
positive multiplicity by one therefore improves source-minus-demand balance
by exactly two, independently of `k`.  The active path case improves it by
one.  These arithmetic atoms give the six/eight unit turnover used by the
R43 source-swap analysis.
-/

namespace Erdos23Delta0
namespace Gamma
namespace OwnerBalanceTurnover

def collisionContribution (k : Nat) : Nat := 2 * (k - 1)

def zeroPairCapacity (reserved : Bool) (k : Nat) : Nat :=
  if k = 0 then 2 - reserved.toNat else 0

def balanceContribution (reserved : Bool) (k : Nat) : Int :=
  (zeroPairCapacity reserved k : Int) - collisionContribution k

theorem leaving_nonactive_pair_gain (k : Nat) (hk : 1 ≤ k) :
    balanceContribution false (k - 1) - balanceContribution false k = 2 := by
  cases k with
  | zero => omega
  | succ k =>
      cases k with
      | zero => norm_num [balanceContribution, zeroPairCapacity,
          collisionContribution]
      | succ k =>
          simp [balanceContribution, zeroPairCapacity, collisionContribution]
          omega

theorem leaving_path_pair_gain :
    balanceContribution true 0 - balanceContribution false 1 = 1 := by
  decide

theorem entering_nonactive_pair_loss (k : Nat) :
    balanceContribution false (k + 1) - balanceContribution false k = -2 := by
  cases k with
  | zero => norm_num [balanceContribution, zeroPairCapacity,
      collisionContribution]
  | succ k =>
      simp [balanceContribution, zeroPairCapacity, collisionContribution]
      omega

theorem entering_path_pair_loss :
    balanceContribution false 1 - balanceContribution true 0 = -1 := by
  decide

def diagonalBalance (k : Nat) : Int := -(collisionContribution k : Int)

theorem leaving_diagonal_gain (k : Nat) (hk : 1 ≤ k) :
    diagonalBalance (k - 1) - diagonalBalance k =
      if 2 ≤ k then 2 else 0 := by
  unfold diagonalBalance collisionContribution
  omega

theorem entering_diagonal_loss (k : Nat) :
    diagonalBalance (k + 1) - diagonalBalance k =
      if 1 ≤ k then -2 else 0 := by
  unfold diagonalBalance collisionContribution
  omega

theorem leaving_middle_gain (rowCount : Nat) (hrow : 1 ≤ rowCount) :
    2 * (balanceContribution false 0 - balanceContribution false 1) +
        2 * (balanceContribution true 0 - balanceContribution false 1) +
        (diagonalBalance (rowCount - 1) - diagonalBalance rowCount) =
      6 + if 2 ≤ rowCount then 2 else 0 := by
  rw [leaving_nonactive_pair_gain 1 (by omega), leaving_path_pair_gain,
    leaving_diagonal_gain rowCount hrow]
  omega

theorem entering_middle_loss (rowCount : Nat) :
    2 * (balanceContribution false 1 - balanceContribution false 0) +
        2 * (balanceContribution false 1 - balanceContribution true 0) +
        (diagonalBalance (rowCount + 1) - diagonalBalance rowCount) =
      -6 + if 1 ≤ rowCount then -2 else 0 := by
  rw [entering_nonactive_pair_loss 0, entering_path_pair_loss,
    entering_diagonal_loss rowCount]
  omega

#print axioms leaving_nonactive_pair_gain
#print axioms leaving_middle_gain
#print axioms entering_middle_loss

end OwnerBalanceTurnover
end Gamma
end Erdos23Delta0
