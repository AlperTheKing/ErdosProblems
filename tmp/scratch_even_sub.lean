import Mathlib
example (n c : Nat) (h : Even (n + 2*c)) : Even n := by
  rcases h with ⟨k, hk⟩
  use k - c
  omega
