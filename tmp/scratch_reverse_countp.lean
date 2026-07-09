import Mathlib
example {α} (l : List α) (P : α → Prop) [DecidablePred P] : l.reverse.countP P = l.countP P := by
  simp
