import Mathlib
example (a c : Nat) (h : Even (a + 2*c)) : Even a := by omega
