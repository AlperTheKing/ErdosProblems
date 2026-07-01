import Mathlib

/-!
Scratch formalization for the parity part of the terminal slack gate.

The exact finite gates establish the graph-specific facts:

* `s_f(e)=0` iff `e` is a witnessed terminal exit;
* terminal path lengths have fixed parity.

This file isolates the arithmetic conclusion used by HT/EHR: once a
non-witness slack is known to be nonzero and even, it is at least `2`.
-/

namespace Erdos23
namespace SlackParity

theorem two_le_of_even_ne_zero {s : Nat}
    (heven : (2 : Nat) ∣ s)
    (hne : s ≠ 0) :
    2 ≤ s := by
  rcases heven with ⟨k, rfl⟩
  cases k with
  | zero =>
      simp at hne
  | succ k =>
      omega

theorem slack_ge_two_of_even_nonzero {D candidate s : Nat}
    (_hslack : candidate = D + s)
    (heven : (2 : Nat) ∣ s)
    (hne : s ≠ 0) :
    2 ≤ s := by
  exact two_le_of_even_ne_zero heven hne

theorem candidate_ge_D_add_two_of_even_nonzero {D candidate s : Nat}
    (hslack : candidate = D + s)
    (heven : (2 : Nat) ∣ s)
    (hne : s ≠ 0) :
    D + 2 ≤ candidate := by
  have hs : 2 ≤ s := slack_ge_two_of_even_nonzero hslack heven hne
  omega

end SlackParity
end Erdos23
