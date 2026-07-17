import Mathlib

namespace C44

theorem firstViolationJump
    {before after : Int}
    (hBefore : before ≤ 1)
    (hUpdate : after = before + 1)
    (hViolation : 2 ≤ after) :
    before = 1 ∧ after = 2 := by
  omega

theorem criticalPullbackDropsTwoRanks
    {sourceRank endpointRank predecessorRank : Nat}
    (hSource : 2 ≤ sourceRank)
    (hCritical : endpointRank + 1 = sourceRank)
    (hSeedTwo : predecessorRank + 1 ≤ endpointRank) :
    predecessorRank ≤ sourceRank - 2 := by
  omega

theorem nonSeedOddCofactorAtLeastFive
    {a : Nat}
    (hLower : 2 ≤ a)
    (hOdd : a % 2 = 1)
    (hNotThree : a ≠ 3) :
    5 ≤ a := by
  omega

theorem seedThreeChildBelowHardSource
    {q a h : Nat}
    (hQ : 2 ≤ q)
    (hA : 5 ≤ a)
    (hProduct : h + 1 = q * a) :
    3 * q - 1 < h := by
  have hFiveRaw : q * 5 ≤ q * a := Nat.mul_le_mul_left q hA
  have hFive : 5 * q ≤ h + 1 := by
    simpa [Nat.mul_comm, hProduct] using hFiveRaw
  omega

theorem hardEventResidue
    {n : Nat}
    (hEven : n % 2 = 0)
    (hAllowed : n % 3 ≠ 1) :
    n % 6 = 0 ∨ n % 6 = 2 := by
  omega

theorem targetEventResidue
    {n : Nat}
    (hOdd : n % 2 = 1)
    (hAllowed : n % 3 ≠ 1) :
    n % 6 = 3 ∨ n % 6 = 5 := by
  omega

end C44
